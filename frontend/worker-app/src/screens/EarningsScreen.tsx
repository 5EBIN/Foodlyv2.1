import React from 'react';
import {
  View,
  Text,
  FlatList,
  StyleSheet,
  ActivityIndicator,
  RefreshControl,
} from 'react-native';
import { useQuery } from '@tanstack/react-query';
import { apiService } from '../services/api';
import { Ionicons } from '@expo/vector-icons';

export default function EarningsScreen() {
  const { data: earnings, isLoading, error, refetch, isRefreshing } = useQuery({
    queryKey: ['earnings'],
    queryFn: () => apiService.getEarnings(),
  });

  const renderEarning = ({ item }: any) => (
    <View style={styles.earningCard}>
      <View style={styles.earningHeader}>
        <View style={styles.orderInfo}>
          <Ionicons name="receipt-outline" size={20} color="#3B82F6" />
          <Text style={styles.orderId}>Order #{item.order_id}</Text>
        </View>
        <Text style={styles.date}>{new Date(item.created_at).toLocaleDateString()}</Text>
      </View>

      <View style={styles.earningDetails}>
        <View style={styles.earningRow}>
          <Text style={styles.earningLabel}>Amount Earned</Text>
          <Text style={styles.earningAmount}>${item.amount.toFixed(2)}</Text>
        </View>

        {item.customer_order && (
          <View style={styles.orderMeta}>
            <Ionicons name="restaurant-outline" size={16} color="#6B7280" />
            <Text style={styles.orderMetaText}>
              {item.customer_order.restaurant?.name || 'Restaurant'}
            </Text>
          </View>
        )}

        <View style={styles.statusBadge}>
          <Ionicons
            name={item.paid_out ? 'checkmark-circle' : 'time-outline'}
            size={16}
            color={item.paid_out ? '#059669' : '#F59E0B'}
          />
          <Text style={[styles.statusText, item.paid_out && styles.statusTextPaid]}>
            {item.paid_out ? 'Paid Out' : 'Pending'}
          </Text>
        </View>
      </View>
    </View>
  );

  // Calculate total earnings
  const totalEarnings = earnings?.reduce((sum: number, item: any) => sum + item.amount, 0) || 0;
  const paidOut = earnings?.reduce((sum: number, item: any) => sum + (item.paid_out ? item.amount : 0), 0) || 0;
  const pending = totalEarnings - paidOut;

  if (isLoading) {
    return (
      <View style={styles.loading}>
        <ActivityIndicator size="large" color="#10B981" />
        <Text style={styles.loadingText}>Loading earnings...</Text>
      </View>
    );
  }

  if (error) {
    return (
      <View style={styles.error}>
        <Ionicons name="alert-circle-outline" size={48} color="#EF4444" />
        <Text style={styles.errorText}>Failed to load earnings</Text>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      {/* Summary Cards */}
      <View style={styles.summaryContainer}>
        <View style={[styles.summaryCard, styles.totalCard]}>
          <Ionicons name="wallet" size={32} color="#fff" />
          <Text style={styles.summaryLabel}>Total Earned</Text>
          <Text style={styles.summaryValue}>${totalEarnings.toFixed(2)}</Text>
        </View>

        <View style={styles.summaryRow}>
          <View style={[styles.summaryCard, styles.paidCard]}>
            <Ionicons name="checkmark-circle-outline" size={24} color="#059669" />
            <Text style={styles.summaryLabelSmall}>Paid Out</Text>
            <Text style={styles.summaryValueSmall}>${paidOut.toFixed(2)}</Text>
          </View>

          <View style={[styles.summaryCard, styles.pendingCard]}>
            <Ionicons name="time-outline" size={24} color="#F59E0B" />
            <Text style={styles.summaryLabelSmall}>Pending</Text>
            <Text style={styles.summaryValueSmall}>${pending.toFixed(2)}</Text>
          </View>
        </View>
      </View>

      {/* ML Info */}
      <View style={styles.mlInfoCard}>
        <Ionicons name="sparkles" size={20} color="#8B5CF6" />
        <Text style={styles.mlInfoText}>
          Fair earnings distributed through our ML algorithm
        </Text>
      </View>

      {/* Earnings List */}
      <View style={styles.listContainer}>
        <Text style={styles.listTitle}>Earnings History</Text>
        <FlatList
          data={earnings}
          renderItem={renderEarning}
          keyExtractor={(item) => item.id.toString()}
          contentContainerStyle={styles.list}
          refreshControl={
            <RefreshControl refreshing={isRefreshing} onRefresh={refetch} colors={['#10B981']} />
          }
          ListEmptyComponent={
            <View style={styles.empty}>
              <Ionicons name="wallet-outline" size={48} color="#9CA3AF" />
              <Text style={styles.emptyText}>No Earnings Yet</Text>
              <Text style={styles.emptySubtext}>Complete deliveries to start earning</Text>
            </View>
          }
        />
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F3F4F6',
  },
  loading: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#F3F4F6',
  },
  loadingText: {
    marginTop: 12,
    fontSize: 16,
    color: '#6B7280',
  },
  error: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#F3F4F6',
    padding: 24,
  },
  errorText: {
    marginTop: 12,
    fontSize: 18,
    fontWeight: 'bold',
    color: '#1F2937',
  },
  summaryContainer: {
    padding: 16,
  },
  summaryCard: {
    backgroundColor: '#fff',
    borderRadius: 16,
    padding: 20,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  totalCard: {
    backgroundColor: '#10B981',
    marginBottom: 16,
    alignItems: 'center',
  },
  summaryLabel: {
    fontSize: 16,
    color: '#fff',
    marginTop: 12,
    opacity: 0.9,
  },
  summaryValue: {
    fontSize: 36,
    fontWeight: 'bold',
    color: '#fff',
    marginTop: 8,
  },
  summaryRow: {
    flexDirection: 'row',
    gap: 12,
  },
  paidCard: {
    flex: 1,
    borderWidth: 2,
    borderColor: '#D1FAE5',
  },
  pendingCard: {
    flex: 1,
    borderWidth: 2,
    borderColor: '#FEF3C7',
  },
  summaryLabelSmall: {
    fontSize: 13,
    color: '#6B7280',
    marginTop: 8,
  },
  summaryValueSmall: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#1F2937',
    marginTop: 4,
  },
  mlInfoCard: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#F5F3FF',
    marginHorizontal: 16,
    marginBottom: 16,
    padding: 12,
    borderRadius: 12,
    gap: 8,
  },
  mlInfoText: {
    flex: 1,
    fontSize: 13,
    color: '#7C3AED',
    fontWeight: '500',
  },
  listContainer: {
    flex: 1,
    backgroundColor: '#fff',
    borderTopLeftRadius: 24,
    borderTopRightRadius: 24,
    paddingTop: 20,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: -2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 5,
  },
  listTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#1F2937',
    paddingHorizontal: 16,
    marginBottom: 12,
  },
  list: {
    paddingHorizontal: 16,
    paddingBottom: 16,
  },
  earningCard: {
    backgroundColor: '#F9FAFB',
    borderRadius: 12,
    padding: 16,
    marginBottom: 12,
    borderWidth: 1,
    borderColor: '#E5E7EB',
  },
  earningHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 12,
  },
  orderInfo: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
  },
  orderId: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#1F2937',
  },
  date: {
    fontSize: 13,
    color: '#9CA3AF',
  },
  earningDetails: {
    gap: 8,
  },
  earningRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  earningLabel: {
    fontSize: 14,
    color: '#6B7280',
  },
  earningAmount: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#10B981',
  },
  orderMeta: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 6,
  },
  orderMetaText: {
    fontSize: 13,
    color: '#6B7280',
  },
  statusBadge: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 6,
    alignSelf: 'flex-start',
    paddingVertical: 4,
    paddingHorizontal: 10,
    backgroundColor: '#FEF3C7',
    borderRadius: 12,
  },
  statusText: {
    fontSize: 12,
    fontWeight: '600',
    color: '#92400E',
  },
  statusTextPaid: {
    color: '#065F46',
  },
  empty: {
    alignItems: 'center',
    paddingVertical: 48,
  },
  emptyText: {
    marginTop: 16,
    fontSize: 18,
    fontWeight: 'bold',
    color: '#6B7280',
  },
  emptySubtext: {
    marginTop: 8,
    fontSize: 14,
    color: '#9CA3AF',
  },
});
