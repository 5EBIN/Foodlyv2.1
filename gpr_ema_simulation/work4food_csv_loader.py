"""
Data Loader for WORK4FOOD Simulation
Integrates workers.csv, sessions.csv, and orders.csv with work4food.py
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json

class Work4FoodDataLoader:
    def __init__(self, workers_path='workers.csv', 
                 sessions_path='sessions.csv', 
                 orders_path='orders.csv'):
        """
        Initialize loader with CSV file paths
        
        Args:
            workers_path: Path to workers.csv
            sessions_path: Path to sessions.csv  
            orders_path: Path to orders.csv
        """
        self.workers_path = workers_path
        self.sessions_path = sessions_path
        self.orders_path = orders_path
        
        # Data containers
        self.workers_df = None
        self.sessions_df = None
        self.orders_df = None
        
        # Processed data
        self.agents = None
        self.orders = None
    
    def load_all_data(self):
        """Load all CSV files"""
        print("=" * 60)
        print("LOADING WORK4FOOD DATASET")
        print("=" * 60)
        
        # Load workers
        print(f"\n1. Loading workers from {self.workers_path}...")
        self.workers_df = pd.read_csv(self.workers_path)
        print(f"   ✓ Loaded {len(self.workers_df):,} workers")
        print(f"   Columns: {list(self.workers_df.columns)}")
        
        # Load sessions
        print(f"\n2. Loading sessions from {self.sessions_path}...")
        self.sessions_df = pd.read_csv(self.sessions_path)
        print(f"   ✓ Loaded {len(self.sessions_df):,} sessions")
        print(f"   Columns: {list(self.sessions_df.columns)}")
        
        # Load orders
        print(f"\n3. Loading orders from {self.orders_path}...")
        self.orders_df = pd.read_csv(self.orders_path)
        print(f"   ✓ Loaded {len(self.orders_df):,} orders")
        print(f"   Columns: {list(self.orders_df.columns)}")
        
        return self.workers_df, self.sessions_df, self.orders_df
    
    def create_agents_from_workers(self, center_location=(19.07, 72.87), 
                                   radius_km=12, limit=None):
        """
        Convert workers.csv to agent format for simulation
        
        Args:
            center_location: City center coordinates (lat, lon)
            radius_km: Operating radius
            limit: Limit number of agents (None = all)
        
        Returns:
            List of agent dictionaries
        """
        print("\n" + "=" * 60)
        print("CREATING AGENTS FROM WORKERS")
        print("=" * 60)
        
        if self.workers_df is None:
            self.load_all_data()
        
        # Sample workers if limit specified
        workers_sample = self.workers_df.head(limit) if limit else self.workers_df
        
        agents = []
        for idx, worker in workers_sample.iterrows():
            # Generate random starting location
            bearing = np.random.random() * 2 * np.pi
            r = radius_km * np.sqrt(np.random.random())
            dx = r * np.cos(bearing)
            dy = r * np.sin(bearing)
            lat = center_location[0] + dy / 111.0
            lon = center_location[1] + dx / (111.0 * np.cos(np.radians(center_location[0])))
            
            # Create agent with worker profile
            agent = {
                'agent_id': worker['worker_id'],
                'loc': (lat, lon),
                'W': 0.0,   # work hours (accumulated during simulation)
                'A': 0.0,   # active hours (accumulated during simulation)
                'earnings': 0.0,
                'handout': 0.0,
                'total_pay': 0.0,
                'active': True,
                
                # Worker profile from dataset
                'age_group': worker['age_group'],
                'gender': worker['gender'],
                'education': worker['education'],
                'base_hourly_rate': worker['hourly_rate'],
                'expense_per_hour': worker['expense_per_hour'],
                'net_hourly': worker['net_hourly'],
                'multi_app': worker['multi_apping'],
                'avg_trips_per_shift': worker['avg_trips_per_hour'] * worker['planned_hours'] if 'planned_hours' in worker else worker['avg_trips_per_hour'] * 4,
                'experience_days': worker['experience_weeks'] * 7,
                'rating': worker['rating'],
                'home_zone': worker['home_zone']
            }
            
            agents.append(agent)
        
        self.agents = agents
        print(f"✓ Created {len(agents)} agents")
        
        # Statistics
        multi_app_count = sum(1 for a in agents if a['multi_app'])
        print(f"\nAgent Statistics:")
        print(f"  - Multi-apping: {multi_app_count}/{len(agents)} ({multi_app_count/len(agents)*100:.1f}%)")
        print(f"  - Avg hourly rate: ${np.mean([a['base_hourly_rate'] for a in agents]):.2f}")
        print(f"  - Avg net hourly: ${np.mean([a['net_hourly'] for a in agents]):.2f}")
        print(f"  - Avg experience: {np.mean([a['experience_days'] for a in agents]):.1f} days")
        print(f"  - Avg rating: {np.mean([a['rating'] for a in agents]):.2f}/5.0")
        
        return agents
    
    def create_orders_from_csv(self, sample_size=None, start_date=None, 
                               duration_hours=None):
        """
        Convert orders.csv to format needed for simulation
        
        Args:
            sample_size: Number of orders to use (None = all)
            start_date: Start date for simulation (None = use earliest)
            duration_hours: Limit to N hours from start (None = all)
        
        Returns:
            DataFrame with orders
        """
        print("\n" + "=" * 60)
        print("PROCESSING ORDERS")
        print("=" * 60)
        
        if self.orders_df is None:
            self.load_all_data()
        
        orders = self.orders_df.copy()
        
        # Convert timestamp to datetime
        print("\n1. Converting timestamps...")
        orders['timestamp'] = pd.to_datetime(orders['timestamp'], errors='coerce')
        
        # Remove any rows with invalid timestamps
        orders = orders.dropna(subset=['timestamp'])
        orders = orders.sort_values('timestamp').reset_index(drop=True)
        
        print(f"   ✓ Valid orders: {len(orders):,}")
        print(f"   Time range: {orders['timestamp'].min()} to {orders['timestamp'].max()}")
        
        # Filter by date if specified
        if start_date:
            if duration_hours:
                end_date = start_date + timedelta(hours=duration_hours)
                orders = orders[(orders['timestamp'] >= start_date) & 
                              (orders['timestamp'] < end_date)]
            else:
                orders = orders[orders['timestamp'] >= start_date]
            print(f"\n2. Filtered by date: {len(orders):,} orders")
        
        # Sample if specified
        if sample_size and sample_size < len(orders):
            orders = orders.sample(n=sample_size, random_state=42)
            print(f"\n3. Sampled: {sample_size:,} orders")
        
        # Convert to simulation format
        print("\n4. Converting to simulation format...")
        
        # Generate coordinates from zones
        # For now, use zone IDs to create locations around city center
        def zone_to_location(zone_id, center=(19.07, 72.87), radius=15):
            """Convert zone ID to approximate lat/lon"""
            # Use zone ID as seed for consistent locations
            np.random.seed(int(zone_id))
            bearing = np.random.random() * 2 * np.pi
            r = (zone_id % 100) / 100.0 * radius  # Map zone to radius
            dx = r * np.cos(bearing)
            dy = r * np.sin(bearing)
            lat = center[0] + dy / 111.0
            lon = center[1] + dx / (111.0 * np.cos(np.radians(center[0])))
            return (lat, lon)
        
        processed_orders = []
        for idx, row in orders.iterrows():
            # Restaurant location (from restaurant zone)
            rest_loc = zone_to_location(row['restaurant_zone'])
            
            # Customer location (from customer zone)  
            cust_loc = zone_to_location(row['customer_zone'])
            
            processed_orders.append({
                'order_id': row['order_id'],
                'time': row['timestamp'],
                'rest_loc': rest_loc,
                'cust_loc': cust_loc,
                'picked': False,
                'assigned_agent': None,
                
                # Additional order info
                'distance_km': row.get('distance_km', row.get('distance_miles', 0) * 1.60934),
                'trip_time_mins': row.get('trip_time_mins', row.get('trip_time_seconds', 0) / 60),
                'base_fare': row['base_fare'],
                'customer_prep_time': row.get('customer_prep_time', row.get('prep_time_mins', 0)),
                'expected_delivery_mins': row['expected_delivery_mins']
            })
            
            if len(processed_orders) % 10000 == 0:
                print(f"   Processed {len(processed_orders):,} orders...")
        
        orders_df = pd.DataFrame(processed_orders)
        self.orders = orders_df
        
        print(f"   ✓ Processed {len(orders_df):,} orders")
        print(f"\nOrder Statistics:")
        print(f"  - Avg distance: {orders_df['distance_km'].mean():.2f} km")
        print(f"  - Avg trip time: {orders_df['trip_time_mins'].mean():.1f} mins")
        print(f"  - Avg base fare: ${orders_df['base_fare'].mean():.2f}")
        print(f"  - Avg delivery time: {orders_df['expected_delivery_mins'].mean():.1f} mins")
        
        return orders_df
    
    def get_sessions_for_workers(self, worker_ids=None):
        """
        Get session data for specified workers
        
        Args:
            worker_ids: List of worker IDs (None = all)
        
        Returns:
            DataFrame with sessions
        """
        if self.sessions_df is None:
            self.load_all_data()
        
        sessions = self.sessions_df.copy()
        
        if worker_ids:
            sessions = sessions[sessions['worker_id'].isin(worker_ids)]
        
        # Convert times
        sessions['login_time'] = pd.to_datetime(sessions['login_time'], errors='coerce')
        sessions['logout_time'] = pd.to_datetime(sessions['logout_time'], errors='coerce')
        
        # Calculate session duration
        sessions['duration_hours'] = sessions['planned_hours']
        
        print(f"\nSession Statistics for {len(sessions)} sessions:")
        print(f"  - Avg planned hours: {sessions['planned_hours'].mean():.2f}")
        print(f"  - Avg hourly rate: ${sessions['hourly_rate'].mean():.2f}")
        print(f"  - Avg expense rate: ${sessions['expense_rate'].mean():.2f}")
        
        return sessions
    
    def save_processed_data(self, output_dir='./processed_data'):
        """Save processed agents and orders"""
        import os
        os.makedirs(output_dir, exist_ok=True)
        
        if self.agents:
            agents_df = pd.DataFrame(self.agents)
            agents_df.to_csv(f'{output_dir}/agents.csv', index=False)
            print(f"✓ Saved agents to {output_dir}/agents.csv")
        
        if self.orders is not None:
            self.orders.to_csv(f'{output_dir}/orders.csv', index=False)
            print(f"✓ Saved orders to {output_dir}/orders.csv")
        
        # Save summary
        summary = {
            'num_agents': len(self.agents) if self.agents else 0,
            'num_orders': len(self.orders) if self.orders is not None else 0,
            'data_source': 'WORK4FOOD dataset (workers.csv, sessions.csv, orders.csv)',
            'processed_date': datetime.now().isoformat()
        }
        
        with open(f'{output_dir}/summary.json', 'w') as f:
            json.dump(summary, f, indent=2)
        
        print(f"✓ Saved summary to {output_dir}/summary.json")


# Example usage
if __name__ == "__main__":
    # Initialize loader
    loader = Work4FoodDataLoader(
        workers_path='workers.csv',
        sessions_path='sessions.csv',
        orders_path='orders.csv'
    )
    
    # Load all data
    loader.load_all_data()
    
    # Create agents (limit to 80 for simulation)
    agents = loader.create_agents_from_workers(
        center_location=(19.07, 72.87),  # Mumbai coordinates
        radius_km=12,
        limit=80  # Match NUM_AGENTS in simulation
    )
    
    # Process orders (sample 50k orders from first day)
    orders_df = loader.create_orders_from_csv(
        sample_size=50000,
        start_date=None,  # Use earliest date in dataset
        duration_hours=24  # One day
    )
    
    # Get session info for these workers
    worker_ids = [a['agent_id'] for a in agents]
    sessions = loader.get_sessions_for_workers(worker_ids)
    
    # Save processed data
    loader.save_processed_data()
    
    print("\n" + "=" * 60)
    print("✅ DATA LOADING COMPLETE")
    print("=" * 60)
    print(f"Ready to run simulation with:")
    print(f"  - {len(agents)} agents")
    print(f"  - {len(orders_df):,} orders")
    print(f"  - {len(sessions)} sessions")