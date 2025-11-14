import React from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  ScrollView,
  ActivityIndicator,
  Alert,
} from 'react-native';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiService } from '../services/api';
import { Ionicons } from '@expo/vector-icons';

export default function CurrentJobScreen() {
  const queryClient = useQueryClient();

  const { data: currentJob, isLoading, error } = useQuery({
    queryKey: ['currentJob'],
    queryFn: () => apiService.getCurrentJob(),
    refetchInterval: 3000, // Poll every 3 seconds
  });

  const completeOrderMutation = useMutation({
    mutationFn: (orderId: number) => apiService.completeOrder(orderId),
    onSuccess: () => {
      Alert.alert('Success', 'Order completed successfully!');
      queryClient.invalidateQueries({ queryKey: ['currentJob'] });
      queryClient.invalidateQueries({ queryKey: ['earnings'] });
    },
  });

  if (isLoading) {
    return (
      <View style={styles.loading}>
        <ActivityIndicator size="large" color="#10B981" />
        <Text style={styles.loadingText}>Loading current job...</Text>
      </View>
    );
  }

  if (error || !currentJob) {
    return (
      <View style={styles.empty}>
        <Ionicons name="briefcase-outline" size={64} color="#9CA3AF" />
        <Text style={styles.emptyText}>No Active Job</Text>
        <Text style={styles.emptySubtext}>Accept an order to start delivering</Text>
      </View>
    );
  }

  const customerOrder = currentJob.customer_order;

  return (
    <ScrollView style={styles.container} showsVerticalScrollIndicator={false}>
      {/* Job Header */}
      <View style={styles.header}>
        <View style={styles.jobIdContainer}>
          <Ionicons name="briefcase" size={32} color="#fff" />
          <Text style={styles.jobId}>Order #{currentJob.id}</Text>
        </View>
        <View style={styles.amountBadge}>
          <Text style={styles.amountText}>${currentJob.amount.toFixed(2)}</Text>
        </View>
      </View>

      {/* Status Card */}
      <View style={styles.card}>
        <Text style={styles.cardTitle}>Current Status</Text>
        <View style={styles.statusBadge}>
          <Ionicons name="time" size={20} color="#F59E0B" />
          <Text style={styles.statusText}>{currentJob.status.toUpperCase()}</Text>
        </View>
      </View>

      {/* Order Details */}
      {customerOrder && (
        <View style={styles.card}>
          <Text style={styles.cardTitle}>Order Details</Text>
          <View style={styles.detailRow}>
            <Ionicons name="restaurant-outline" size={20} color="#6B7280" />
            <Text style={styles.detailLabel}>Restaurant</Text>
            <Text style={styles.detailValue}>{customerOrder.restaurant?.name || 'N/A'}</Text>
          </View>
          <View style={styles.detailRow}>
            <Ionicons name="person-outline" size={20} color="#6B7280" />
            <Text style={styles.detailLabel}>Customer</Text>
            <Text style={styles.detailValue}>Customer #{customerOrder.customer_id}</Text>
          </View>
          <View style={styles.detailRow}>
            <Ionicons name="cash-outline" size={20} color="#6B7280" />
            <Text style={styles.detailLabel}>Amount</Text>
            <Text style={styles.detailValue}>${customerOrder.amount.toFixed(2)}</Text>
          </View>
        </View>
      )}

      {/* Delivery Address */}
      {customerOrder && (
        <View style={styles.card}>
          <Text style={styles.cardTitle}>Delivery Address</Text>
          <View style={styles.addressContainer}>
            <Ionicons name="location" size={24} color="#E23744" />
            <Text style={styles.addressText}>{customerOrder.delivery_address}</Text>
          </View>
        </View>
      )}

      {/* Pickup/Dropoff for non-customer orders */}
      {!customerOrder && (
        <View style={styles.card}>
          <Text style={styles.cardTitle}>Delivery Details</Text>
          <View style={styles.detailRow}>
            <Ionicons name="location-outline" size={20} color="#6B7280" />
            <Text style={styles.detailLabel}>Pickup</Text>
            <Text style={styles.detailValue}>{currentJob.pickup_location}</Text>
          </View>
          <View style={styles.detailRow}>
            <Ionicons name="navigate-outline" size={20} color="#6B7280" />
            <Text style={styles.detailLabel}>Dropoff</Text>
            <Text style={styles.detailValue}>{currentJob.dropoff_location}</Text>
          </View>
        </View>
      )}

      {/* ML Info */}
      <View style={styles.mlInfoCard}>
        <Ionicons name="sparkles" size={24} color="#8B5CF6" />
        <View style={styles.mlInfoTextContainer}>
          <Text style={styles.mlInfoTitle}>Fair AI Assignment</Text>
          <Text style={styles.mlInfoText}>
            This delivery was assigned to you using our ML algorithm that ensures fair
            distribution of work opportunities.
          </Text>
        </View>
      </View>

      {/* Complete Order Button */}
      <View style={styles.buttonContainer}>
        <TouchableOpacity
          style={[
            styles.completeButton,
            completeOrderMutation.isPending && styles.completeButtonDisabled,
          ]}
          onPress={() => {
            Alert.alert(
              'Complete Order',
              'Have you delivered the order?',
              [
                { text: 'Cancel', style: 'cancel' },
                {
                  text: 'Complete',
                  onPress: () => completeOrderMutation.mutate(currentJob.id),
                },
              ]
            );
          }}
          disabled={completeOrderMutation.isPending}
        >
          {completeOrderMutation.isPending ? (
            <>
              <ActivityIndicator color="#fff" />
              <Text style={styles.completeButtonText}>Completing...</Text>
            </>
          ) : (
            <>
              <Ionicons name="checkmark-done" size={24} color="#fff" />
              <Text style={styles.completeButtonText}>Complete Delivery</Text>
            </>
          )}
        </TouchableOpacity>
      </View>

      <View style={styles.bottomSpacer} />
    </ScrollView>
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
  empty: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#F3F4F6',
    padding: 24,
  },
  emptyText: {
    marginTop: 16,
    fontSize: 20,
    fontWeight: 'bold',
    color: '#6B7280',
  },
  emptySubtext: {
    marginTop: 8,
    fontSize: 14,
    color: '#9CA3AF',
  },
  header: {
    backgroundColor: '#10B981',
    padding: 24,
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  jobIdContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 12,
  },
  jobId: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#fff',
  },
  amountBadge: {
    backgroundColor: '#ECFDF5',
    paddingVertical: 8,
    paddingHorizontal: 16,
    borderRadius: 20,
  },
  amountText: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#059669',
  },
  card: {
    backgroundColor: '#fff',
    marginHorizontal: 16,
    marginTop: 16,
    padding: 16,
    borderRadius: 12,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  cardTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#1F2937',
    marginBottom: 12,
  },
  statusBadge: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#FEF3C7',
    paddingVertical: 12,
    paddingHorizontal: 16,
    borderRadius: 8,
    gap: 8,
  },
  statusText: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#92400E',
  },
  detailRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 12,
    gap: 8,
  },
  detailLabel: {
    flex: 1,
    fontSize: 15,
    color: '#6B7280',
  },
  detailValue: {
    fontSize: 15,
    fontWeight: '600',
    color: '#1F2937',
  },
  addressContainer: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    gap: 12,
  },
  addressText: {
    flex: 1,
    fontSize: 15,
    color: '#1F2937',
    lineHeight: 22,
  },
  mlInfoCard: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    backgroundColor: '#F5F3FF',
    marginHorizontal: 16,
    marginTop: 16,
    padding: 16,
    borderRadius: 12,
    gap: 12,
  },
  mlInfoTextContainer: {
    flex: 1,
  },
  mlInfoTitle: {
    fontSize: 15,
    fontWeight: 'bold',
    color: '#6D28D9',
    marginBottom: 6,
  },
  mlInfoText: {
    fontSize: 13,
    color: '#7C3AED',
    lineHeight: 18,
  },
  buttonContainer: {
    marginHorizontal: 16,
    marginTop: 24,
  },
  completeButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: '#10B981',
    paddingVertical: 16,
    borderRadius: 12,
    gap: 12,
  },
  completeButtonDisabled: {
    backgroundColor: '#9CA3AF',
  },
  completeButtonText: {
    color: '#fff',
    fontSize: 18,
    fontWeight: 'bold',
  },
  bottomSpacer: {
    height: 32,
  },
});
