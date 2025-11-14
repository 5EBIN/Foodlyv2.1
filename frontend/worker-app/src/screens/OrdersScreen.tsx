import React from 'react';
import {
  View,
  Text,
  FlatList,
  TouchableOpacity,
  StyleSheet,
  ActivityIndicator,
  RefreshControl,
} from 'react-native';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiService } from '../services/api';
import { Ionicons } from '@expo/vector-icons';

export default function OrdersScreen({ navigation }: any) {
  const queryClient = useQueryClient();

  const { data: orders, isLoading, error, refetch, isRefreshing } = useQuery({
    queryKey: ['availableOrders'],
    queryFn: () => apiService.getAvailableOrders(),
    refetchInterval: 5000, // Poll every 5 seconds for new orders
  });

  const acceptOrderMutation = useMutation({
    mutationFn: (orderId: number) => apiService.acceptOrder(orderId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['availableOrders'] });
      queryClient.invalidateQueries({ queryKey: ['currentJob'] });
      navigation.navigate('CurrentJob');
    },
  });

  const renderOrder = ({ item }: any) => {
    const customerOrder = item.customer_order;

    return (
      <View style={styles.orderCard}>
        <View style={styles.orderHeader}>
          <View style={styles.orderIdContainer}>
            <Ionicons name="receipt-outline" size={20} color="#3B82F6" />
            <Text style={styles.orderId}>Order #{item.id}</Text>
          </View>
          <View style={styles.amountBadge}>
            <Text style={styles.amountText}>${item.amount.toFixed(2)}</Text>
          </View>
        </View>

        {/* Restaurant or Customer Order Info */}
        {customerOrder ? (
          <View style={styles.orderInfo}>
            <View style={styles.infoRow}>
              <Ionicons name="restaurant-outline" size={18} color="#6B7280" />
              <Text style={styles.infoLabel}>Restaurant:</Text>
              <Text style={styles.infoValue}>{customerOrder.restaurant?.name || 'N/A'}</Text>
            </View>
            <View style={styles.infoRow}>
              <Ionicons name="person-outline" size={18} color="#6B7280" />
              <Text style={styles.infoLabel}>Customer:</Text>
              <Text style={styles.infoValue}>Customer #{customerOrder.customer_id}</Text>
            </View>
            <View style={styles.infoRow}>
              <Ionicons name="location-outline" size={18} color="#6B7280" />
              <Text style={styles.infoLabel}>Delivery:</Text>
              <Text style={styles.infoValue} numberOfLines={1}>{customerOrder.delivery_address}</Text>
            </View>
          </View>
        ) : (
          <View style={styles.orderInfo}>
            <View style={styles.infoRow}>
              <Ionicons name="location-outline" size={18} color="#6B7280" />
              <Text style={styles.infoLabel}>Pickup:</Text>
              <Text style={styles.infoValue} numberOfLines={1}>{item.pickup_location}</Text>
            </View>
            <View style={styles.infoRow}>
              <Ionicons name="navigate-outline" size={18} color="#6B7280" />
              <Text style={styles.infoLabel}>Dropoff:</Text>
              <Text style={styles.infoValue} numberOfLines={1}>{item.dropoff_location}</Text>
            </View>
          </View>
        )}

        {/* ML Assignment Info */}
        <View style={styles.mlBadge}>
          <Ionicons name="sparkles" size={16} color="#8B5CF6" />
          <Text style={styles.mlBadgeText}>Fair ML Assignment Available</Text>
        </View>

        <TouchableOpacity
          style={[
            styles.acceptButton,
            acceptOrderMutation.isPending && styles.acceptButtonDisabled,
          ]}
          onPress={() => acceptOrderMutation.mutate(item.id)}
          disabled={acceptOrderMutation.isPending}
        >
          {acceptOrderMutation.isPending ? (
            <>
              <ActivityIndicator color="#fff" size="small" />
              <Text style={styles.acceptButtonText}>Accepting...</Text>
            </>
          ) : (
            <>
              <Ionicons name="checkmark-circle" size={20} color="#fff" />
              <Text style={styles.acceptButtonText}>Accept Order</Text>
            </>
          )}
        </TouchableOpacity>
      </View>
    );
  };

  if (isLoading && !orders) {
    return (
      <View style={styles.loading}>
        <ActivityIndicator size="large" color="#10B981" />
        <Text style={styles.loadingText}>Loading available orders...</Text>
      </View>
    );
  }

  if (error) {
    return (
      <View style={styles.error}>
        <Ionicons name="alert-circle-outline" size={48} color="#EF4444" />
        <Text style={styles.errorText}>Failed to load orders</Text>
        <TouchableOpacity style={styles.retryButton} onPress={() => refetch()}>
          <Text style={styles.retryButtonText}>Retry</Text>
        </TouchableOpacity>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <FlatList
        data={orders}
        renderItem={renderOrder}
        keyExtractor={(item) => item.id.toString()}
        contentContainerStyle={styles.list}
        refreshControl={
          <RefreshControl refreshing={isRefreshing} onRefresh={refetch} colors={['#10B981']} />
        }
        ListEmptyComponent={
          <View style={styles.empty}>
            <Ionicons name="bicycle-outline" size={64} color="#9CA3AF" />
            <Text style={styles.emptyText}>No Orders Available</Text>
            <Text style={styles.emptySubtext}>New delivery orders will appear here</Text>
          </View>
        }
      />
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
  retryButton: {
    marginTop: 16,
    backgroundColor: '#10B981',
    paddingVertical: 12,
    paddingHorizontal: 24,
    borderRadius: 8,
  },
  retryButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
  },
  list: {
    padding: 16,
  },
  orderCard: {
    backgroundColor: '#fff',
    borderRadius: 12,
    padding: 16,
    marginBottom: 16,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  orderHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 12,
  },
  orderIdContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
  },
  orderId: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#1F2937',
  },
  amountBadge: {
    backgroundColor: '#ECFDF5',
    paddingVertical: 4,
    paddingHorizontal: 12,
    borderRadius: 16,
  },
  amountText: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#059669',
  },
  orderInfo: {
    gap: 8,
    marginBottom: 12,
  },
  infoRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
  },
  infoLabel: {
    fontSize: 14,
    color: '#6B7280',
    width: 80,
  },
  infoValue: {
    flex: 1,
    fontSize: 14,
    color: '#1F2937',
    fontWeight: '500',
  },
  mlBadge: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#F5F3FF',
    paddingVertical: 8,
    paddingHorizontal: 12,
    borderRadius: 8,
    gap: 6,
    marginBottom: 12,
  },
  mlBadgeText: {
    fontSize: 12,
    color: '#7C3AED',
    fontWeight: '600',
  },
  acceptButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: '#10B981',
    paddingVertical: 12,
    borderRadius: 8,
    gap: 8,
  },
  acceptButtonDisabled: {
    backgroundColor: '#9CA3AF',
  },
  acceptButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold',
  },
  empty: {
    alignItems: 'center',
    paddingVertical: 64,
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
