import React, { useState, useEffect } from 'react';
import { View, Text, TouchableOpacity, ScrollView, ActivityIndicator } from 'react-native';
import axios from 'axios';

export default function AdminDashboard() {
  const [stats, setStats] = useState<any>(null);
  const [batches, setBatches] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);

  // In RN, localStorage isn't native; this matches original snippet intention.
  // For a production RN admin app, replace with AsyncStorage.
  // @ts-ignore
  const token = global.localStorage?.getItem?.('adminToken') || '';
  const api = axios.create({
    headers: token ? { Authorization: `Bearer ${token}` } : {},
  });

  useEffect(() => {
    fetchDashboardData();
    const interval = setInterval(fetchDashboardData, 30000);
    return () => clearInterval(interval);
  }, []);

  const fetchDashboardData = async () => {
    try {
      const [statsRes, batchesRes] = await Promise.all([
        api.get('/api/admin/batch/current-stats'),
        api.get('/api/admin/batch/history'),
      ]);
      setStats(statsRes.data);
      setBatches(batchesRes.data);
    } catch (err) {
      // eslint-disable-next-line no-console
      console.error('Failed to fetch admin dashboard data', err);
    }
  };

  const triggerBatch = async () => {
    setLoading(true);
    try {
      await api.post('/api/admin/batch/trigger');
      fetchDashboardData();
    } catch (err) {
      // ignore
    }
    setLoading(false);
  };

  const finalizePayments = async () => {
    setLoading(true);
    try {
      await api.post('/api/admin/payments/finalize');
      fetchDashboardData();
    } catch (err) {
      // ignore
    }
    setLoading(false);
  };

  if (!stats) {
    return (
      <View style={{ flex: 1, justifyContent: 'center', alignItems: 'center' }}>
        <ActivityIndicator />
        <Text style={{ marginTop: 8 }}>Loading...</Text>
      </View>
    );
  }

  return (
    <ScrollView style={{ flex: 1, backgroundColor: '#f3f4f6', padding: 16 }}>
      <View style={{ marginBottom: 16, flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center' }}>
        <Text style={{ fontSize: 24, fontWeight: 'bold' }}>WORK4FOOD Admin Dashboard</Text>
        <TouchableOpacity
          onPress={() => {
            // @ts-ignore
            global.localStorage?.removeItem?.('adminToken');
          }}
        >
          <Text style={{ color: '#dc2626', fontWeight: '600' }}>Logout</Text>
        </TouchableOpacity>
      </View>

      <View style={{ backgroundColor: '#fff', borderRadius: 12, padding: 16, marginBottom: 16 }}>
        <Text style={{ fontSize: 18, fontWeight: 'bold', marginBottom: 12 }}>Current Batch Window</Text>
        <View style={{ flexDirection: 'row', justifyContent: 'space-between' }}>
          <View>
            <Text style={{ color: '#6b7280' }}>Pending Orders</Text>
            <Text style={{ fontSize: 24, fontWeight: 'bold' }}>{stats.pending_orders}</Text>
          </View>
          <View>
            <Text style={{ color: '#6b7280' }}>Available Agents</Text>
            <Text style={{ fontSize: 24, fontWeight: 'bold' }}>{stats.available_agents}</Text>
          </View>
        </View>
        <TouchableOpacity
          onPress={triggerBatch}
          disabled={loading}
          style={{
            marginTop: 12,
            backgroundColor: '#2563eb',
            padding: 10,
            borderRadius: 8,
            opacity: loading ? 0.6 : 1,
          }}
        >
          <Text style={{ color: '#fff', textAlign: 'center', fontWeight: '600' }}>
            {loading ? 'Triggering...' : 'Trigger Batch Now'}
          </Text>
        </TouchableOpacity>
      </View>

      <View style={{ backgroundColor: '#fff', borderRadius: 12, padding: 16, marginBottom: 16 }}>
        <Text style={{ fontSize: 18, fontWeight: 'bold', marginBottom: 12 }}>Recent Batches</Text>
        <View>
          {batches.slice(0, 10).map((batch: any) => (
            <View key={batch.batch_id} style={{ flexDirection: 'row', justifyContent: 'space-between', paddingVertical: 8, borderBottomWidth: 1, borderBottomColor: '#f3f4f6' }}>
              <Text style={{ fontFamily: 'monospace' }}>{batch.batch_id}</Text>
              <Text>{batch.assigned_orders}/{batch.total_orders} assigned</Text>
              <Text style={{ color: '#6b7280' }}>ω {Number(batch.guarantee_ratio || 0).toFixed(3)}</Text>
            </View>
          ))}
        </View>
      </View>

      <View style={{ backgroundColor: '#fff', borderRadius: 12, padding: 16 }}>
        <Text style={{ fontSize: 18, fontWeight: 'bold', marginBottom: 12 }}>Payment Management</Text>
        <Text style={{ color: '#6b7280', marginBottom: 8 }}>
          Run at end of day to calculate handouts for agents below guarantee
        </Text>
        <TouchableOpacity
          onPress={finalizePayments}
          disabled={loading}
          style={{
            backgroundColor: '#16a34a',
            padding: 10,
            borderRadius: 8,
            opacity: loading ? 0.6 : 1,
          }}
        >
          <Text style={{ color: '#fff', textAlign: 'center', fontWeight: '600' }}>
            {loading ? 'Processing...' : 'Finalize Payments'}
          </Text>
        </TouchableOpacity>
      </View>
    </ScrollView>
  );
}


