import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  ScrollView,
  TextInput,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';

export default function OrderConfirmationScreen({ route, navigation }: any) {
  const { restaurant, amount } = route.params;

  // Mock user delivery address (can be enhanced with actual user data)
  const [deliveryAddress, setDeliveryAddress] = useState('123 Main St, New York, NY 10001');
  const [deliveryLat] = useState(40.7489);
  const [deliveryLng] = useState(-73.9680);

  const handleProceedToPayment = () => {
    navigation.navigate('MockPayment', {
      restaurant,
      amount,
      deliveryAddress,
      deliveryLat,
      deliveryLng,
    });
  };

  return (
    <View style={styles.container}>
      <ScrollView style={styles.scrollView} showsVerticalScrollIndicator={false}>
        {/* Header */}
        <View style={styles.header}>
          <Ionicons name="checkmark-circle" size={64} color="#10B981" />
          <Text style={styles.headerTitle}>Confirm Your Order</Text>
          <Text style={styles.headerSubtitle}>Review details before proceeding</Text>
        </View>

        {/* Restaurant Info Card */}
        <View style={styles.card}>
          <Text style={styles.cardTitle}>Restaurant</Text>
          <View style={styles.restaurantInfo}>
            <Ionicons name="restaurant" size={24} color="#E23744" />
            <View style={styles.restaurantTextContainer}>
              <Text style={styles.restaurantName}>{restaurant.name}</Text>
              <Text style={styles.restaurantCuisine}>{restaurant.cuisine_type}</Text>
            </View>
          </View>
        </View>

        {/* Delivery Address Card */}
        <View style={styles.card}>
          <Text style={styles.cardTitle}>Delivery Address</Text>
          <View style={styles.addressInputContainer}>
            <Ionicons name="location" size={24} color="#3B82F6" />
            <TextInput
              style={styles.addressInput}
              value={deliveryAddress}
              onChangeText={setDeliveryAddress}
              multiline
              placeholder="Enter delivery address"
            />
          </View>
        </View>

        {/* Delivery Time Card */}
        <View style={styles.card}>
          <Text style={styles.cardTitle}>Estimated Delivery</Text>
          <View style={styles.deliveryTimeInfo}>
            <Ionicons name="time" size={24} color="#F59E0B" />
            <View style={styles.deliveryTimeTextContainer}>
              <Text style={styles.deliveryTimeValue}>{restaurant.delivery_time} minutes</Text>
              <Text style={styles.deliveryTimeSubtext}>After order is accepted</Text>
            </View>
          </View>
        </View>

        {/* Order Summary Card */}
        <View style={styles.card}>
          <Text style={styles.cardTitle}>Order Summary</Text>
          <View style={styles.summaryRow}>
            <Text style={styles.summaryLabel}>Standard Order</Text>
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

        {/* ML Assignment Info */}
        <View style={styles.mlInfoCard}>
          <Ionicons name="sparkles" size={24} color="#8B5CF6" />
          <View style={styles.mlInfoTextContainer}>
            <Text style={styles.mlInfoTitle}>Fair AI Assignment</Text>
            <Text style={styles.mlInfoSubtext}>
              Our ML algorithm ensures fair distribution of orders to delivery agents
            </Text>
          </View>
        </View>

        {/* Spacer for button */}
        <View style={styles.bottomSpacer} />
      </ScrollView>

      {/* Fixed Proceed Button at Bottom */}
      <View style={styles.bottomContainer}>
        <TouchableOpacity style={styles.proceedButton} onPress={handleProceedToPayment}>
          <Text style={styles.proceedButtonText}>Proceed to Payment</Text>
          <Ionicons name="arrow-forward" size={24} color="#fff" />
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
    fontSize: 16,
    fontWeight: 'bold',
    color: '#1F2937',
    marginBottom: 12,
  },
  restaurantInfo: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 12,
  },
  restaurantTextContainer: {
    flex: 1,
  },
  restaurantName: {
    fontSize: 18,
    fontWeight: '600',
    color: '#1F2937',
  },
  restaurantCuisine: {
    fontSize: 14,
    color: '#6B7280',
    marginTop: 2,
  },
  addressInputContainer: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    gap: 12,
  },
  addressInput: {
    flex: 1,
    fontSize: 15,
    color: '#1F2937',
    paddingVertical: 4,
    minHeight: 40,
  },
  deliveryTimeInfo: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 12,
  },
  deliveryTimeTextContainer: {
    flex: 1,
  },
  deliveryTimeValue: {
    fontSize: 18,
    fontWeight: '600',
    color: '#1F2937',
  },
  deliveryTimeSubtext: {
    fontSize: 13,
    color: '#6B7280',
    marginTop: 2,
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
  mlInfoCard: {
    flexDirection: 'row',
    alignItems: 'center',
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
    marginBottom: 4,
  },
  mlInfoSubtext: {
    fontSize: 13,
    color: '#7C3AED',
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
  proceedButton: {
    backgroundColor: '#E23744',
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 16,
    borderRadius: 12,
    gap: 12,
  },
  proceedButtonText: {
    color: '#fff',
    fontSize: 18,
    fontWeight: 'bold',
  },
});
