import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  ScrollView,
  ActivityIndicator,
  Alert,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useMutation } from '@tanstack/react-query';
import { apiService } from '../services/api';

export default function MockPaymentScreen({ route, navigation }: any) {
  const { restaurant, amount, deliveryAddress, deliveryLat, deliveryLng } = route.params;

  const [selectedPayment, setSelectedPayment] = useState<'card' | 'cash'>('card');

  const createOrderMutation = useMutation({
    mutationFn: (orderData: any) => apiService.createCustomerOrder(orderData),
    onSuccess: (data) => {
      // Navigate to active order tracking screen
      navigation.reset({
        index: 0,
        routes: [
          { name: 'Main' },
          { name: 'ActiveOrder', params: { orderId: data.id } },
        ],
      });
    },
    onError: (error: any) => {
      Alert.alert(
        'Order Failed',
        error.response?.data?.detail || 'Failed to create order. Please try again.',
        [{ text: 'OK' }]
      );
    },
  });

  const handlePayAndConfirm = () => {
    // Create the order
    const orderData = {
      restaurant_id: restaurant.id,
      amount: amount,
      delivery_address: deliveryAddress,
      delivery_lat: deliveryLat,
      delivery_lng: deliveryLng,
    };

    createOrderMutation.mutate(orderData);
  };

  return (
    <View style={styles.container}>
      <ScrollView style={styles.scrollView} showsVerticalScrollIndicator={false}>
        {/* Header */}
        <View style={styles.header}>
          <Ionicons name="card" size={64} color="#3B82F6" />
          <Text style={styles.headerTitle}>Payment</Text>
          <Text style={styles.headerSubtitle}>Complete your order</Text>
        </View>

        {/* Payment Methods */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Select Payment Method</Text>

          {/* Credit Card Option */}
          <TouchableOpacity
            style={[
              styles.paymentCard,
              selectedPayment === 'card' && styles.paymentCardSelected,
            ]}
            onPress={() => setSelectedPayment('card')}
          >
            <View style={styles.paymentCardContent}>
              <Ionicons
                name="card"
                size={28}
                color={selectedPayment === 'card' ? '#3B82F6' : '#6B7280'}
              />
              <View style={styles.paymentTextContainer}>
                <Text style={styles.paymentTitle}>Credit/Debit Card</Text>
                <Text style={styles.paymentSubtext}>Mock payment - No real charge</Text>
              </View>
            </View>
            {selectedPayment === 'card' && (
              <Ionicons name="checkmark-circle" size={28} color="#3B82F6" />
            )}
          </TouchableOpacity>

          {/* Cash Option */}
          <TouchableOpacity
            style={[
              styles.paymentCard,
              selectedPayment === 'cash' && styles.paymentCardSelected,
            ]}
            onPress={() => setSelectedPayment('cash')}
          >
            <View style={styles.paymentCardContent}>
              <Ionicons
                name="cash"
                size={28}
                color={selectedPayment === 'cash' ? '#10B981' : '#6B7280'}
              />
              <View style={styles.paymentTextContainer}>
                <Text style={styles.paymentTitle}>Cash on Delivery</Text>
                <Text style={styles.paymentSubtext}>Pay when you receive</Text>
              </View>
            </View>
            {selectedPayment === 'cash' && (
              <Ionicons name="checkmark-circle" size={28} color="#10B981" />
            )}
          </TouchableOpacity>
        </View>

        {/* Order Summary */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Order Summary</Text>
          <View style={styles.summaryCard}>
            <View style={styles.summaryRow}>
              <Text style={styles.summaryLabel}>Restaurant</Text>
              <Text style={styles.summaryValue}>{restaurant.name}</Text>
            </View>
            <View style={styles.summaryRow}>
              <Text style={styles.summaryLabel}>Order Amount</Text>
              <Text style={styles.summaryValue}>${amount.toFixed(2)}</Text>
            </View>
            <View style={styles.summaryRow}>
              <Text style={styles.summaryLabel}>Delivery Fee</Text>
              <Text style={styles.summaryValue}>$0.00</Text>
            </View>
            <View style={styles.divider} />
            <View style={styles.summaryRow}>
              <Text style={styles.totalLabel}>Total</Text>
              <Text style={styles.totalValue}>${amount.toFixed(2)}</Text>
            </View>
          </View>
        </View>

        {/* Mock Payment Notice */}
        <View style={styles.noticeCard}>
          <Ionicons name="information-circle" size={24} color="#3B82F6" />
          <View style={styles.noticeTextContainer}>
            <Text style={styles.noticeTitle}>Mock Payment System</Text>
            <Text style={styles.noticeText}>
              This is a demonstration. No real payment will be processed.
            </Text>
          </View>
        </View>

        {/* Spacer for button */}
        <View style={styles.bottomSpacer} />
      </ScrollView>

      {/* Fixed Payment Button at Bottom */}
      <View style={styles.bottomContainer}>
        <TouchableOpacity
          style={[
            styles.payButton,
            createOrderMutation.isPending && styles.payButtonDisabled,
          ]}
          onPress={handlePayAndConfirm}
          disabled={createOrderMutation.isPending}
        >
          {createOrderMutation.isPending ? (
            <>
              <ActivityIndicator color="#fff" />
              <Text style={styles.payButtonText}>Processing...</Text>
            </>
          ) : (
            <>
              <Ionicons name="checkmark-circle" size={24} color="#fff" />
              <Text style={styles.payButtonText}>Pay & Confirm Order</Text>
            </>
          )}
        </TouchableOpacity>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F3F4F6',
  },
  scrollView: {
    flex: 1,
  },
  header: {
    alignItems: 'center',
    paddingVertical: 32,
    backgroundColor: '#fff',
    borderBottomWidth: 1,
    borderBottomColor: '#E5E7EB',
  },
  headerTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#1F2937',
    marginTop: 16,
  },
  headerSubtitle: {
    fontSize: 14,
    color: '#6B7280',
    marginTop: 4,
  },
  section: {
    marginTop: 16,
    paddingHorizontal: 16,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#1F2937',
    marginBottom: 12,
  },
  paymentCard: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    backgroundColor: '#fff',
    padding: 16,
    borderRadius: 12,
    marginBottom: 12,
    borderWidth: 2,
    borderColor: '#E5E7EB',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.05,
    shadowRadius: 4,
    elevation: 2,
  },
  paymentCardSelected: {
    borderColor: '#3B82F6',
    backgroundColor: '#EFF6FF',
  },
  paymentCardContent: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 12,
    flex: 1,
  },
  paymentTextContainer: {
    flex: 1,
  },
  paymentTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#1F2937',
  },
  paymentSubtext: {
    fontSize: 13,
    color: '#6B7280',
    marginTop: 2,
  },
  summaryCard: {
    backgroundColor: '#fff',
    padding: 16,
    borderRadius: 12,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  summaryRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  summaryLabel: {
    fontSize: 15,
    color: '#6B7280',
  },
  summaryValue: {
    fontSize: 15,
    color: '#1F2937',
    fontWeight: '600',
  },
  divider: {
    height: 1,
    backgroundColor: '#E5E7EB',
    marginVertical: 12,
  },
  totalLabel: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#1F2937',
  },
  totalValue: {
    fontSize: 22,
    fontWeight: 'bold',
    color: '#E23744',
  },
  noticeCard: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#EFF6FF',
    marginHorizontal: 16,
    marginTop: 16,
    padding: 16,
    borderRadius: 12,
    gap: 12,
  },
  noticeTextContainer: {
    flex: 1,
  },
  noticeTitle: {
    fontSize: 15,
    fontWeight: 'bold',
    color: '#1E40AF',
    marginBottom: 4,
  },
  noticeText: {
    fontSize: 13,
    color: '#3B82F6',
    lineHeight: 18,
  },
  bottomSpacer: {
    height: 100,
  },
  bottomContainer: {
    position: 'absolute',
    bottom: 0,
    left: 0,
    right: 0,
    backgroundColor: '#fff',
    padding: 16,
    borderTopWidth: 1,
    borderTopColor: '#E5E7EB',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: -2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 5,
  },
  payButton: {
    backgroundColor: '#10B981',
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 16,
    borderRadius: 12,
    gap: 12,
  },
  payButtonDisabled: {
    backgroundColor: '#9CA3AF',
  },
  payButtonText: {
    color: '#fff',
    fontSize: 18,
    fontWeight: 'bold',
  },
});
