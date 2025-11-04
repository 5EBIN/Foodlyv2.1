// src/screens/OrdersScreen.tsx
import React from 'react';
import {
  View,
  Text,
  FlatList,
  TouchableOpacity,
  StyleSheet,
  RefreshControl,
  ActivityIndicator,
} from 'react-native';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Ionicons } from '@expo/vector-icons';
import { apiService } from '../services/api';
import type { Order } from '../types';

export default function OrdersScreen() {
  const queryClient = useQueryClient();

  const { data: orders = [], isLoading, refetch, isRefetching } = useQuery({
    queryKey: ['orders'],
    queryFn: apiService.getOrders,
    refetchInterval: 30000,
  });

  const acceptOrderMutation = useMutation({
    mutationFn: apiService.acceptOrder,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['orders'] });
      queryClient.invalidateQueries({ queryKey: ['currentJob'] });
    },
  });

  const renderOrder = ({ item }: { item: Order }) => {
    const gValueColor = item.g_mean 
      ? item.g_mean > 0.7 ? '#10B981' 
      : item.g_mean > 0.4 ? '#F59E0B' 
      : '#EF4444'
      : '#9CA3AF';

    return (
      <View style={styles.orderCard}>
        <View style={styles.orderHeader}>
          <View style={styles.locationContainer}>
            <Ionicons name="location" size={20} color="#3B82F6" />
            <View style={styles.locationText}>
              <Text style={styles.locationLabel}>From:</Text>
              <Text style={styles.locationValue}>{item.pickup}</Text>
            </View>
          </View>
          <View style={styles.locationContainer}>
            <Ionicons name="flag" size={20} color="#EF4444" />
            <View style={styles.locationText}>
              <Text style={styles.locationLabel}>To:</Text>
              <Text style={styles.locationValue}>{item.dropoff}</Text>
            </View>
          </View>
        </View>
        <View style={styles.orderDetails}>
          <View style={styles.detailItem}>
            <Ionicons name="time" size={18} color="#6B7280" />
            <Text style={styles.detailText}>{item.eta} min ETA</Text>
          </View>
          {item.g_mean !== undefined && (
            <View style={styles.gValueContainer}>
              <Text style={styles.gValueLabel}>G-Value:</Text>
              <View style={[styles.gValueBadge, { backgroundColor: gValueColor }]}>
                <Text style={styles.gValueText}>
                  {item.g_mean.toFixed(2)}
                </Text>
              </View>
              {item.g_var !== undefined && (
                <Text style={styles.varianceText}>
                  ±{Math.sqrt(item.g_var).toFixed(3)}
                </Text>
              )}
            </View>
          )}
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
            <ActivityIndicator color="#fff" size="small" />
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

  if (isLoading) {
    return (
      <View style={styles.centerContainer}>
        <ActivityIndicator size="large" color="#3B82F6" />
        <Text style={styles.loadingText}>Loading orders...</Text>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <FlatList
        data={orders}
        renderItem={renderOrder}
        keyExtractor={(item) => item.id}
        contentContainerStyle={styles.listContent}
        refreshControl={
          <RefreshControl refreshing={isRefetching} onRefresh={refetch} />
        }
        ListEmptyComponent={
          <View style={styles.emptyContainer}>
            <Ionicons name="clipboard-outline" size={64} color="#D1D5DB" />
            <Text style={styles.emptyText}>No available orders</Text>
            <Text style={styles.emptySubtext}>Pull down to refresh</Text>
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
  centerContainer: {
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
  listContent: {
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
    marginBottom: 12,
  },
  locationContainer: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    marginBottom: 8,
  },
  locationText: {
    marginLeft: 8,
    flex: 1,
  },
  locationLabel: {
    fontSize: 12,
    color: '#9CA3AF',
    marginBottom: 2,
  },
  locationValue: {
    fontSize: 16,
    color: '#1F2937',
    fontWeight: '500',
  },
  orderDetails: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 12,
    paddingTop: 12,
    borderTopWidth: 1,
    borderTopColor: '#E5E7EB',
  },
  detailItem: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  detailText: {
    marginLeft: 6,
    fontSize: 14,
    color: '#6B7280',
  },
  gValueContainer: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  gValueLabel: {
    fontSize: 12,
    color: '#6B7280',
    marginRight: 6,
  },
  gValueBadge: {
    paddingHorizontal: 10,
    paddingVertical: 4,
    borderRadius: 12,
  },
  gValueText: {
    color: '#fff',
    fontSize: 14,
    fontWeight: 'bold',
  },
  varianceText: {
    fontSize: 11,
    color: '#9CA3AF',
    marginLeft: 4,
  },
  acceptButton: {
    backgroundColor: '#3B82F6',
    borderRadius: 8,
    padding: 12,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
  },
  acceptButtonDisabled: {
    opacity: 0.6,
  },
  acceptButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
    marginLeft: 8,
  },
  emptyContainer: {
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 64,
  },
  emptyText: {
    fontSize: 18,
    color: '#6B7280',
    marginTop: 16,
    fontWeight: '500',
  },
  emptySubtext: {
    fontSize: 14,
    color: '#9CA3AF',
    marginTop: 4,
  },
});
