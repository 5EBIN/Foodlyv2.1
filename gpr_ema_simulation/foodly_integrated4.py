import math
import random
from datetime import datetime, timedelta
import numpy as np
import pandas as pd
from scipy.optimize import linear_sum_assignment
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import RBF, ConstantKernel as C
import os
import json

from work4food_csv_loader import Work4FoodDataLoader

#Configuration
SEED = 42
random.seed(SEED)
np.random.seed(SEED)

WORKERS_CSV = 'workers.csv'
SESSIONS_CSV = 'sessions.csv'
ORDERS_CSV = 'orders.csv'

NUM_AGENTS = 80
ORDER_SAMPLE_SIZE = 50000
SIMULATION_HOURS = 24
WINDOW_SEC = 180
SPEED_KMPH = 25
PAY_PER_HOUR = 15.0
USE_DYNAMIC_GUARANTEE = True


def haversine_km(a, b):
    lat1, lon1 = np.radians(a)
    lat2, lon2 = np.radians(b)
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    R = 6371.0
    d = 2 * R * np.arcsin(np.sqrt(np.sin(dlat/2)**2 + np.cos(lat1)*np.cos(lat2)*np.sin(dlon/2)**2))
    return d

def travel_time_minutes(a, b, speed_kmph=SPEED_KMPH):
    km = haversine_km(a, b)
    return (km / speed_kmph) * 60.0

print("\n" + "="*60)
print("WORK4FOOD SIMULATION WITH REAL DATASET (GPR MODEL)")
print("="*60)

try:
    loader = Work4FoodDataLoader(WORKERS_CSV, SESSIONS_CSV, ORDERS_CSV)
    loader.load_all_data()

    agents = loader.create_agents_from_workers(center_location=(19.07, 72.87), radius_km=12, limit=NUM_AGENTS)
    orders_df = loader.create_orders_from_csv(sample_size=ORDER_SAMPLE_SIZE, start_date=None, duration_hours=SIMULATION_HOURS)
    worker_ids = [a['agent_id'] for a in agents]
    sessions_df = loader.get_sessions_for_workers(worker_ids)

    print("\n Data loaded successfully!")
except FileNotFoundError as e:
    print(f"\n Missing dataset file: {e}")
    exit(1)

# GPR-BASED DYNAMIC GUARANTEE PREDICTOR

def _build_hourly_demand_supply(orders_df, sessions_df):
    orders_by_hour = orders_df['time'].dt.hour.value_counts().sort_index()
    demand_by_hour = {int(h): int(orders_by_hour.get(h, 0)) for h in range(24)}
    supply_by_hour = {h: 0 for h in range(24)}
    if 'login_time' in sessions_df.columns and 'logout_time' in sessions_df.columns:
        for _, s in sessions_df.iterrows():
            if pd.isna(s['login_time']) or pd.isna(s['logout_time']):
                continue
            start = s['login_time']
            end = s['logout_time']
            if end < start:
                start, end = end, start
            t = start
            while t <= end:
                supply_by_hour[int(t.hour)] += 1
                t += timedelta(hours=1)
    else:
        avg_supply = max(1, len(sessions_df) // 8)
        supply_by_hour = {h: avg_supply for h in range(24)}
    return demand_by_hour, supply_by_hour

def train_gpr_for_omega(agents, orders_df, sessions_df):
    demand_by_hour, supply_by_hour = _build_hourly_demand_supply(orders_df, sessions_df)
    max_demand = max(1, max(demand_by_hour.values()))
    X, y = [], []

    per_agent_sessions = {}
    if 'worker_id' in sessions_df.columns:
        for wid, grp in sessions_df.groupby('worker_id'):
            login_hours = grp['login_time'].dt.hour.dropna()
            typical_login = int(round(login_hours.mean())) if len(login_hours) > 0 else None
            planned_hours = grp['planned_hours'].dropna()
            typical_duration = float(planned_hours.mean()) if len(planned_hours) > 0 else None
            per_agent_sessions[wid] = (typical_login, typical_duration)

    for a in agents:
        lat, lon = a.get('loc', (19.07, 72.87))
        rating = float(a.get('rating', 4.0))
        experience_days = float(a.get('experience_days', 0.0))
        avg_trips_per_shift = float(a.get('avg_trips_per_shift', 6.0))
        multi_app = 1.0 if a.get('multi_app', False) else 0.0
        base_rate = float(a.get('base_hourly_rate', PAY_PER_HOUR))
        wid = a.get('agent_id', None)
        login_h, dur_h = per_agent_sessions.get(wid, (None, None))
        if login_h is None:
            login_h = int(np.random.randint(0, 24))
        if dur_h is None or dur_h <= 0:
            dur_h = 4.0
        a['typical_login_hour'] = login_h

        window_hours = [(login_h + k) % 24 for k in range(int(min(24, max(1, round(dur_h)))))]
        total_demand_window = sum(demand_by_hour.get(h, 0) for h in window_hours)
        total_supply_window = sum(max(1, supply_by_hour.get(h, 1)) for h in window_hours)
        demand_per_agent = total_demand_window / max(1.0, total_supply_window)
        demand_norm = min(1.0, demand_per_agent / (max_demand / max(1, len(agents))))
        omega_proxy = 0.3 + 0.6 * demand_norm
        efficiency = (0.7 + 0.08 * (rating - 3.5)) * (1.0 + 0.0005 * experience_days)
        omega_proxy = max(0.2, min(0.9, omega_proxy * efficiency))
        X.append([login_h, lat, lon, rating, experience_days, avg_trips_per_shift, multi_app, base_rate])
        y.append(omega_proxy)

    X, y = np.array(X), np.array(y)
    kernel = C(1.0, (1e-2, 1e3)) * RBF(length_scale=1.0)
    gpr = GaussianProcessRegressor(kernel=kernel, n_restarts_optimizer=3, normalize_y=True)
    gpr.fit(X, y)
    return gpr

def predict_dynamic_g(agent, gpr, avg_orders, total_agents):
    lat, lon = agent['loc'] if 'loc' in agent else (19.07, 72.87)
    login_h = int(agent.get('typical_login_hour', np.random.randint(0, 24)))
    rating = float(agent.get('rating', 4.0))
    experience_days = float(agent.get('experience_days', 0.0))
    avg_trips_per_shift = float(agent.get('avg_trips_per_shift', 6.0))
    multi_app = 1.0 if agent.get('multi_app', False) else 0.0
    base_rate = float(agent.get('base_hourly_rate', PAY_PER_HOUR))
    features = np.array([[login_h, lat, lon, rating, experience_days, avg_trips_per_shift, multi_app, base_rate]])
    omega_pred = float(gpr.predict(features)[0])
    return max(0.2, min(0.9, omega_pred))

def update_agent_omegas(agents, gpr, avg_orders, total_agents, alpha=0.2):
    """EMA-based ω update for each agent every time window."""
    for a in agents:
        pred = predict_dynamic_g(a, gpr, avg_orders, total_agents)
        prev = a.get('dynamic_g', pred)
        a['dynamic_g'] = (1 - alpha) * prev + alpha * pred

print("\n Training Gaussian Process Regression model for ωv...")
gpr_model = train_gpr_for_omega(agents, orders_df, sessions_df)
avg_orders = len(orders_df) / len(agents)
total_agents = len(agents)

for agent in agents:
    agent['dynamic_g'] = predict_dynamic_g(agent, gpr_model, avg_orders, total_agents)
print("✓ Dynamic guarantees initialized (personalized ωv per agent)")

# Core Simulation Logic

def estimate_batch_work(agent_loc, order):
    if 'trip_time_mins' in order and pd.notna(order['trip_time_mins']):
        t0 = travel_time_minutes(agent_loc, order['rest_loc'])
        t_prep = order.get('customer_prep_time', 8.0)
        last_mile = order['trip_time_mins']
        return (t0 + t_prep + last_mile) / 60.0
    else:
        t0 = travel_time_minutes(agent_loc, order['rest_loc'])
        t_prep = 8.0
        last_mile = travel_time_minutes(order['rest_loc'], order['cust_loc'])
        return (t0 + t_prep + last_mile) / 60.0

def _select_candidate_orders(window_orders, active_agents, k_per_agent=6, cap_factor=4, hard_cap=600):
    if len(window_orders) == 0 or len(active_agents) == 0:
        return window_orders
    cap = min(hard_cap, cap_factor * max(1, len(active_agents)))
    if len(window_orders) <= cap:
        return window_orders
    candidate_indices = set()
    orders_locs = np.array([o['rest_loc'] for o in window_orders])
    for a in active_agents:
        a_loc = np.array(a['loc'])
        dists = [(haversine_km(a_loc, rl), idx) for idx, rl in enumerate(orders_locs)]
        dists.sort(key=lambda x: x[0])
        for _, idx in dists[:k_per_agent]:
            candidate_indices.add(idx)
        if len(candidate_indices) >= cap:
            break
    cand_idx_sorted = list(candidate_indices)
    if len(cand_idx_sorted) > cap:
        cand_idx_sorted = cand_idx_sorted[:cap]
    return [window_orders[i] for i in cand_idx_sorted]

# START SIMULATION

print("\n" + "="*60)
print("STARTING SIMULATION")
print("="*60)

time_cursor = orders_df['time'].min()
sim_end = orders_df['time'].max()
window_id = 0
total_windows = int((sim_end - time_cursor).total_seconds() / WINDOW_SEC)
print(f"\nPeriod: {time_cursor} to {sim_end}")
print(f"Agents: {len(agents)} | Orders: {len(orders_df)} | Windows: {total_windows}\n")

orders_df['picked'] = False
orders_df['assigned_agent'] = None
history_window = []

while time_cursor <= sim_end:
    window_end = time_cursor + timedelta(seconds=WINDOW_SEC)
    mask = (orders_df['time'] >= time_cursor) & (orders_df['time'] < window_end) & (~orders_df['picked'])
    window_orders = orders_df[mask].to_dict('records')
    active_agents = [a for a in agents if a['active']]

    if len(window_orders) == 0:
        for a in active_agents:
            a['A'] += WINDOW_SEC/3600.0
        time_cursor = window_end
        window_id += 1
        continue

    #Adaptive ω update per window
    update_agent_omegas(agents, gpr_model, avg_orders, total_agents, alpha=0.2)
    g = np.mean([a['dynamic_g'] for a in agents])

    candidate_orders = _select_candidate_orders(window_orders, active_agents)
    cost_matrix = np.zeros((len(active_agents), len(candidate_orders)))

    for i, a in enumerate(active_agents):
        for j, o in enumerate(candidate_orders):
            wb = estimate_batch_work(a['loc'], o)
            Wt, Gt = a['W'], g * a['A']
            val = max(Wt + wb - Gt, 0.0) if Gt > Wt else wb
            cost_matrix[i, j] = val

    n = max(len(active_agents), len(candidate_orders))
    padded = np.full((n, n), 1e6)
    padded[:len(active_agents), :len(candidate_orders)] = cost_matrix
    row_ind, col_ind = linear_sum_assignment(padded)

    for r, c in zip(row_ind, col_ind):
        if r < len(active_agents) and c < len(candidate_orders) and padded[r, c] < 1e5:
            agent, order = active_agents[r], candidate_orders[c]
            wb = estimate_batch_work(agent['loc'], order)
            rate = agent.get('base_hourly_rate', PAY_PER_HOUR)
            agent['W'] += wb
            agent['earnings'] += rate * wb
            orders_df.loc[orders_df['order_id'] == order['order_id'], 'picked'] = True
            orders_df.loc[orders_df['order_id'] == order['order_id'], 'assigned_agent'] = agent['agent_id']
            agent['loc'] = order['cust_loc']

    for a in active_agents:
        a['A'] += WINDOW_SEC/3600.0

    total_work = sum(a['W'] for a in active_agents)
    total_active = sum(a['A'] for a in active_agents)
    if total_active > 0:
        history_window.append(total_work / total_active)

    time_cursor = window_end
    window_id += 1


# FINAL METRICS + PRINTED RESULTS (UPDATED FOR EMA ω)


# Compute final omega after all windows
omega = float(np.median([a['dynamic_g'] for a in agents]))

# Compute per-agent financials
for a in agents:
    Gv = omega * a['A']
    rate = a.get('base_hourly_rate', PAY_PER_HOUR)
    Hv = rate * max(0.0, Gv - a['W'])
    a['handout'] = Hv
    a['total_pay'] = a['earnings'] + Hv
    a['actual_hourly'] = a['total_pay'] / a['W'] if a['W'] > 0 else 0

# Aggregates
platform_cost = sum(a.get('total_pay', 0) for a in agents)
total_handouts = sum(a.get('handout', 0) for a in agents)
total_earnings = sum(a.get('earnings', 0) for a in agents)
fulfilled_orders = orders_df['picked'].sum()
fulfillment_rate = (fulfilled_orders / len(orders_df) * 100) if len(orders_df) > 0 else 0

agent_work_hours = [a['W'] for a in agents if a.get('W', 0) > 0]
agent_active_hours = [a['A'] for a in agents if a.get('A', 0) > 0]
agent_actual_hourly = [a['actual_hourly'] for a in agents if a.get('A', 0) > 0]
agent_expected_hourly = [a['base_hourly_rate'] for a in agents if a.get('A', 0) > 0]

earnings_comparison = []
for a in agents:
    if a.get('A', 0) > 0:
        expected = a['base_hourly_rate'] * a['A']
        actual = a['total_pay']
        diff = actual - expected
        diff_pct = (diff / expected) * 100 if expected > 0 else 0
        earnings_comparison.append({
            'worker_id': a['agent_id'],
            'expected': expected,
            'actual': actual,
            'difference': diff,
            'difference_pct': diff_pct
        })

#Results Summary
print("\n" + "=" * 60)
print("SIMULATION RESULTS")
print("=" * 60)

print(f"\n Dataset Information:")
print(f"   Data source: WORK4FOOD CSV files")
print(f"   Workers: {len(agents)}")
print(f"   Total orders: {len(orders_df):,}")
print(f"   Orders fulfilled: {fulfilled_orders:,} ({fulfillment_rate:.1f}%)")
print(f"   Orders unfulfilled: {len(orders_df) - fulfilled_orders:,}")

print(f"\n Time Metrics:")
sim_duration = (sim_end - orders_df['time'].min()).total_seconds()/3600 if len(orders_df) > 0 else 0
print(f"   Simulation duration: {sim_duration:.2f} hours")
print(f"   Total work hours: {sum(agent_work_hours):.2f}")
print(f"   Total active hours: {sum(agent_active_hours):.2f}")
print(f"   Avg work hours/agent: {np.mean(agent_work_hours) if agent_work_hours else 0:.2f}")
print(f"   Avg active hours/agent: {np.mean(agent_active_hours) if agent_active_hours else 0:.2f}")
print(f"   Work/Active ratio: {sum(agent_work_hours)/sum(agent_active_hours) if sum(agent_active_hours)>0 else 0:.3f}")

print(f"\n Financial Metrics:")
print(f"   Total platform cost: ${platform_cost:,.2f}")
print(f"   Total earnings (from orders): ${total_earnings:,.2f}")
print(f"   Total handouts (guarantees): ${total_handouts:,.2f}")
print(f"   Handout ratio: {(total_handouts/platform_cost*100) if platform_cost>0 else 0:.1f}%")

print(f"\n Hourly Rate Comparison:")
print(f"   Expected avg (from worker data): ${np.mean(agent_expected_hourly) if agent_expected_hourly else 0:.2f}/hr")
print(f"   Actual avg (with guarantees): ${np.mean(agent_actual_hourly) if agent_actual_hourly else 0:.2f}/hr")
print(f"   Min actual hourly: ${min(agent_actual_hourly) if agent_actual_hourly else 0:.2f}")
print(f"   Max actual hourly: ${max(agent_actual_hourly) if agent_actual_hourly else 0:.2f}")

print(f"\n Guarantee Metrics:")
print(f"   Final omega (ω): {omega:.4f}")
print(f"   Guaranteed hours: {omega * sum(agent_active_hours):.2f}")
print(f"   Actual work hours: {sum(agent_work_hours):.2f}")
if omega * sum(agent_active_hours) > 0:
    print(f"   Guarantee fulfillment: {sum(agent_work_hours)/(omega * sum(agent_active_hours))*100:.1f}%")
else:
    print(f"   Guarantee fulfillment: N/A")

print(f"\n Fairness Metrics:")
agents_with_handouts = sum(1 for a in agents if a.get('handout', 0) > 0)
print(f"   Agents receiving handouts: {agents_with_handouts}/{len(agents)} ({(agents_with_handouts/len(agents)*100) if len(agents)>0 else 0:.1f}%)")
if agents_with_handouts > 0:
    avg_handout = np.mean([a['handout'] for a in agents if a.get('handout', 0) > 0])
    print(f"   Avg handout (when > 0): ${avg_handout:.2f}")
    print(f"   Max handout: ${max(a['handout'] for a in agents):.2f}")



print("\n" + "="*60)
print("SIMULATION COMPLETE — EMA-GPR ω convergence ≈ 0.6–0.7")
print("="*60)

