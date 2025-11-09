import React, { useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  ActivityIndicator,
} from 'react-native';
import { useQuery } from '@tanstack/react-query';
import { apiService } from '../services/api';
import { Ionicons } from '@expo/vector-icons';

const STATUS_CONFIG = {
  pending: {
    icon: 'time-outline',
    color: '#F59E0B',
    label: 'Order Pending',
    description: 'Finding the best delivery agent for you...',
    step: 1,
  },
  assigned: {
    icon: 'person-outline',
    color: '#3B82F6',
    label: 'Agent Assigned',
    description: 'Your delivery agent is on the way to the restaurant',
    step: 2,
  },
  picked_up: {
    icon: 'bag-check-outline',
    color: '#8B5CF6',
    label: 'Order Picked Up',
    description: 'Agent has collected your order',
    step: 3,
  },
  in_transit: {
    icon: 'bicycle-outline',
    color: '#10B981',
    label: 'On the Way',
    description: 'Your order is being delivered',
    step: 4,
  },
  delivered: {
    icon: 'checkmark-circle-outline',
    color: '#059669',
    label: 'Delivered',
    description: 'Order has been delivered successfully!',
    step: 5,
  },
  cancelled: {
    icon: 'close-circle-outline',
    color: '#EF4444',
    label: 'Cancelled',
    description: 'Order was cancelled',
    step: 0,
  },
};

export default function ActiveOrderScreen({ route, navigation }: any) {
  const orderId = route?.params?.orderId;

  // Poll the active order every 3 seconds
  const { data: order, isLoading, error, refetch } = useQuery({
    queryKey: ['activeOrder', orderId],
    queryFn: () => apiService.getActiveOrder(),
    refetchInterval: 3000, // Poll every 3 seconds
  });

  // Update navigation title when order status changes
  useEffect(() => {
    if (order?.status) {
      navigation.setOptions({
        title: STATUS_CONFIG[order.status]?.label || 'Order Status',
      });
    }
  }, [order?.status, navigation]);

  if (isLoading && !order) {
    return (
      <View style={styles.loading}>
        <ActivityIndicator size="large" color="#E23744" />
        <Text style={styles.loadingText}>Loading order details...</Text>
      </View>
    );
  }

  if (error || !order) {
    return (
      <View style={styles.error}>
        <Ionicons name="alert-circle-outline" size={48} color="#EF4444" />
        <Text style={styles.errorText}>No Active Order</Text>
        <Text style={styles.errorSubtext}>
          You don't have any active orders at the moment
        </Text>
      </View>
    );
  }

  const statusInfo = STATUS_CONFIG[order.status] || STATUS_CONFIG.pending;

  return (
    <ScrollView style={styles.container} showsVerticalScrollIndicator={false}>
      {/* Status Header */}
      <View style={[styles.statusHeader, { backgroundColor: statusInfo.color }]}>
        <Ionicons name={statusInfo.icon as any} size={64} color="#fff" />
        <Text style={styles.statusTitle}>{statusInfo.label}</Text>
        <Text style={styles.statusDescription}>{statusInfo.description}</Text>
      </View>

      {/* Progress Steps */}
      <View style={styles.progressContainer}>
        {[1, 2, 3, 4, 5].map((step) => (
          <View key={step} style={styles.progressStep}>
            <View
              style={[
                styles.progressCircle,
                statusInfo.step >= step && styles.progressCircleActive,
                statusInfo.step === step && styles.progressCircleCurrent,
              ]}
            >
              {statusInfo.step > step ? (
                <Ionicons name="checkmark" size={16} color="#fff" />
              ) : (
                <Text
                  style={[
                    styles.progressNumber,
                    statusInfo.step >= step && styles.progressNumberActive,
                  ]}
                >
                  {step}
                </Text>
              )}
            </View>
            {step < 5 && (
              <View
                style={[
                  styles.progressLine,
                  statusInfo.step > step && styles.progressLineActive,
                ]}
              />
            )}
          </View>
        ))}
      </View>

      {/* Order Details Card */}
      <View style={styles.card}>
        <Text style={styles.cardTitle}>Order Details</Text>
        <View style={styles.detailRow}>
          <Ionicons name="receipt-outline" size={20} color="#6B7280" />
          <Text style={styles.detailLabel}>Order ID</Text>
          <Text style={styles.detailValue}>#{order.id}</Text>
        </View>
        <View style={styles.detailRow}>
          <Ionicons name="restaurant-outline" size={20} color="#E23744" />
          <Text style={styles.detailLabel}>Restaurant</Text>
          <Text style={styles.detailValue}>{order.restaurant?.name || 'N/A'}</Text>
        </View>
        <View style={styles.detailRow}>
          <Ionicons name="cash-outline" size={20} color="#10B981" />
          <Text style={styles.detailLabel}>Amount</Text>
          <Text style={styles.detailValue}>${order.amount.toFixed(2)}</Text>
        </View>
      </View>

      {/* Delivery Agent Card */}
      {order.assigned_agent_id && (
        <View style={styles.card}>
          <Text style={styles.cardTitle}>Delivery Agent</Text>
          <View style={styles.agentInfo}>
            <View style={styles.agentAvatar}>
              <Ionicons name="person" size={32} color="#fff" />
            </View>
            <View style={styles.agentDetails}>
              <Text style={styles.agentName}>{order.agent_name || 'Agent'}</Text>
              <View style={styles.agentMeta}>
                <Ionicons name="star" size={14} color="#FFA500" />
                <Text style={styles.agentRating}>4.8</Text>
              </View>
            </View>
          </View>
          {order.assignment_score && (
            <View style={styles.mlBadge}>
              <Ionicons name="sparkles" size={16} color="#8B5CF6" />
              <Text style={styles.mlBadgeText}>
                ML Score: {order.assignment_score.toFixed(2)}
              </Text>
            </View>
          )}
        </View>
      )}

      {/* Delivery Address Card */}
      <View style={styles.card}>
        <Text style={styles.cardTitle}>Delivery Address</Text>
        <View style={styles.addressContainer}>
          <Ionicons name="location" size={24} color="#E23744" />
          <Text style={styles.addressText}>{order.delivery_address}</Text>
        </View>
      </View>

      {/* ML Info Card */}
      <View style={styles.mlInfoCard}>
        <Ionicons name="sparkles" size={24} color="#8B5CF6" />
        <View style={styles.mlInfoTextContainer}>
          <Text style={styles.mlInfoTitle}>Fair AI Assignment</Text>
          <Text style={styles.mlInfoText}>
            This order was assigned using our machine learning algorithm that ensures fair
            distribution of deliveries among all agents.
          </Text>
        </View>
      </View>

      {/* Order Timeline */}
      <View style={styles.card}>
        <Text style={styles.cardTitle}>Order Timeline</Text>
        <View style={styles.timeline}>
          <TimelineItem
            icon="receipt-outline"
            title="Order Placed"
            time={new Date(order.created_at).toLocaleTimeString()}
            completed
          />
          {order.status !== 'pending' && (
            <TimelineItem
              icon="person-outline"
              title="Agent Assigned"
              time={order.assigned_agent_id ? 'Just now' : '-'}
              completed
            />
          )}
          {['picked_up', 'in_transit', 'delivered'].includes(order.status) && (
            <TimelineItem
              icon="bag-check-outline"
              title="Order Picked Up"
              time="-"
              completed={order.status !== 'assigned'}
            />
          )}
          {['in_transit', 'delivered'].includes(order.status) && (
            <TimelineItem
              icon="bicycle-outline"
              title="Out for Delivery"
              time="-"
              completed={order.status !== 'picked_up'}
            />
          )}
          <TimelineItem
            icon="checkmark-circle-outline"
            title="Delivered"
            time="-"
            completed={order.status === 'delivered'}
          />
        </View>
      </View>

      <View style={styles.bottomSpacer} />
    </ScrollView>
  );
}

function TimelineItem({
  icon,
  title,
  time,
  completed,
}: {
  icon: string;
  title: string;
  time: string;
  completed: boolean;
}) {
  return (
    <View style={styles.timelineItem}>
      <View
        style={[styles.timelineIcon, completed && styles.timelineIconCompleted]}
      >
        <Ionicons
          name={icon as any}
          size={20}
          color={completed ? '#fff' : '#9CA3AF'}
        />
      </View>
      <View style={styles.timelineContent}>
        <Text style={[styles.timelineTitle, completed && styles.timelineTitleCompleted]}>
          {title}
        </Text>
        <Text style={styles.timelineTime}>{time}</Text>
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
  errorSubtext: {
    marginTop: 8,
    fontSize: 14,
    color: '#6B7280',
    textAlign: 'center',
  },
  statusHeader: {
    alignItems: 'center',
    paddingVertical: 32,
    paddingHorizontal: 24,
  },
  statusTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#fff',
    marginTop: 16,
  },
  statusDescription: {
    fontSize: 14,
    color: '#fff',
    marginTop: 8,
    textAlign: 'center',
    opacity: 0.9,
  },
  progressContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 24,
    paddingHorizontal: 16,
    backgroundColor: '#fff',
    marginBottom: 16,
  },
  progressStep: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  progressCircle: {
    width: 32,
    height: 32,
    borderRadius: 16,
    backgroundColor: '#E5E7EB',
    alignItems: 'center',
    justifyContent: 'center',
  },
  progressCircleActive: {
    backgroundColor: '#10B981',
  },
  progressCircleCurrent: {
    backgroundColor: '#E23744',
    shadowColor: '#E23744',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.3,
    shadowRadius: 4,
    elevation: 4,
  },
  progressNumber: {
    fontSize: 12,
    fontWeight: 'bold',
    color: '#9CA3AF',
  },
  progressNumberActive: {
    color: '#fff',
  },
  progressLine: {
    width: 24,
    height: 2,
    backgroundColor: '#E5E7EB',
  },
  progressLineActive: {
    backgroundColor: '#10B981',
  },
  card: {
    backgroundColor: '#fff',
    marginHorizontal: 16,
    marginBottom: 16,
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
    marginBottom: 16,
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
  agentInfo: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 12,
    marginBottom: 12,
  },
  agentAvatar: {
    width: 56,
    height: 56,
    borderRadius: 28,
    backgroundColor: '#3B82F6',
    alignItems: 'center',
    justifyContent: 'center',
  },
  agentDetails: {
    flex: 1,
  },
  agentName: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#1F2937',
    marginBottom: 4,
  },
  agentMeta: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 4,
  },
  agentRating: {
    fontSize: 14,
    color: '#6B7280',
  },
  mlBadge: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#F5F3FF',
    paddingVertical: 8,
    paddingHorizontal: 12,
    borderRadius: 8,
    gap: 6,
  },
  mlBadgeText: {
    fontSize: 13,
    color: '#7C3AED',
    fontWeight: '600',
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
    marginBottom: 16,
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
  timeline: {
    gap: 16,
  },
  timelineItem: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    gap: 12,
  },
  timelineIcon: {
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: '#E5E7EB',
    alignItems: 'center',
    justifyContent: 'center',
  },
  timelineIconCompleted: {
    backgroundColor: '#10B981',
  },
  timelineContent: {
    flex: 1,
  },
  timelineTitle: {
    fontSize: 15,
    color: '#9CA3AF',
    marginBottom: 2,
  },
  timelineTitleCompleted: {
    color: '#1F2937',
    fontWeight: '600',
  },
  timelineTime: {
    fontSize: 13,
    color: '#9CA3AF',
  },
  bottomSpacer: {
    height: 24,
  },
});
