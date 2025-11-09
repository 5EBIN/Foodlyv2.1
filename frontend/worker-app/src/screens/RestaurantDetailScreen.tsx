import React from 'react';
import {
  View,
  Text,
  StyleSheet,
  Image,
  TouchableOpacity,
  ScrollView,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';

export default function RestaurantDetailScreen({ route, navigation }: any) {
  const { restaurant } = route.params;

  // Fixed order amount as per requirements
  const ORDER_AMOUNT = 25;

  const handleOrderNow = () => {
    navigation.navigate('OrderConfirmation', {
      restaurant,
      amount: ORDER_AMOUNT,
    });
  };

  return (
    <View style={styles.container}>
      <ScrollView style={styles.scrollView} showsVerticalScrollIndicator={false}>
        {/* Restaurant Image */}
        <Image
          source={{
            uri: restaurant.image_url || 'https://via.placeholder.com/400x300/E23744/FFFFFF?text=Restaurant',
          }}
          style={styles.headerImage}
        />

        {/* Restaurant Info Card */}
        <View style={styles.infoCard}>
          <Text style={styles.restaurantName}>{restaurant.name}</Text>
          <Text style={styles.cuisineType}>{restaurant.cuisine_type}</Text>

          {/* Meta Information */}
          <View style={styles.metaContainer}>
            <View style={styles.metaItem}>
              <Ionicons name="star" size={20} color="#FFA500" />
              <Text style={styles.metaText}>{restaurant.rating.toFixed(1)} Rating</Text>
            </View>

            <View style={styles.metaItem}>
              <Ionicons name="time-outline" size={20} color="#E23744" />
              <Text style={styles.metaText}>{restaurant.delivery_time} mins</Text>
            </View>

            {restaurant.distance && (
              <View style={styles.metaItem}>
                <Ionicons name="location-outline" size={20} color="#3B82F6" />
                <Text style={styles.metaText}>{restaurant.distance.toFixed(1)} km away</Text>
              </View>
            )}
          </View>

          {/* Address */}
          <View style={styles.addressContainer}>
            <Ionicons name="map-outline" size={20} color="#6B7280" />
            <Text style={styles.addressText}>{restaurant.address}</Text>
          </View>

          {/* Delivery Info */}
          <View style={styles.deliveryInfoCard}>
            <Ionicons name="bicycle" size={24} color="#10B981" />
            <View style={styles.deliveryTextContainer}>
              <Text style={styles.deliveryTitle}>Fast Delivery</Text>
              <Text style={styles.deliverySubtext}>
                Our ML-powered system ensures fair and efficient delivery
              </Text>
            </View>
          </View>

          {/* Order Details */}
          <View style={styles.orderDetailsCard}>
            <Text style={styles.orderDetailsTitle}>Order Details</Text>
            <View style={styles.orderDetailRow}>
              <Text style={styles.orderDetailLabel}>Standard Order</Text>
              <Text style={styles.orderDetailValue}>${ORDER_AMOUNT.toFixed(2)}</Text>
            </View>
            <View style={styles.divider} />
            <View style={styles.orderDetailRow}>
              <Text style={styles.totalLabel}>Total Amount</Text>
              <Text style={styles.totalValue}>${ORDER_AMOUNT.toFixed(2)}</Text>
            </View>
          </View>
        </View>
      </ScrollView>

      {/* Fixed Order Button at Bottom */}
      <View style={styles.bottomContainer}>
        <TouchableOpacity style={styles.orderButton} onPress={handleOrderNow}>
          <Ionicons name="cart" size={24} color="#fff" />
          <Text style={styles.orderButtonText}>Order Now - ${ORDER_AMOUNT}</Text>
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
  headerImage: {
    width: '100%',
    height: 250,
    backgroundColor: '#E5E7EB',
  },
  infoCard: {
    backgroundColor: '#fff',
    borderTopLeftRadius: 24,
    borderTopRightRadius: 24,
    marginTop: -24,
    padding: 20,
  },
  restaurantName: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#1F2937',
    marginBottom: 4,
  },
  cuisineType: {
    fontSize: 16,
    color: '#6B7280',
    marginBottom: 16,
  },
  metaContainer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 16,
    paddingBottom: 16,
    borderBottomWidth: 1,
    borderBottomColor: '#E5E7EB',
  },
  metaItem: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 6,
  },
  metaText: {
    fontSize: 14,
    color: '#4B5563',
    fontWeight: '600',
  },
  addressContainer: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    gap: 8,
    marginBottom: 16,
  },
  addressText: {
    flex: 1,
    fontSize: 14,
    color: '#6B7280',
    lineHeight: 20,
  },
  deliveryInfoCard: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#ECFDF5',
    padding: 16,
    borderRadius: 12,
    marginBottom: 16,
    gap: 12,
  },
  deliveryTextContainer: {
    flex: 1,
  },
  deliveryTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#065F46',
    marginBottom: 4,
  },
  deliverySubtext: {
    fontSize: 13,
    color: '#047857',
    lineHeight: 18,
  },
  orderDetailsCard: {
    backgroundColor: '#F9FAFB',
    padding: 16,
    borderRadius: 12,
    marginBottom: 80,
  },
  orderDetailsTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#1F2937',
    marginBottom: 12,
  },
  orderDetailRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  orderDetailLabel: {
    fontSize: 15,
    color: '#6B7280',
  },
  orderDetailValue: {
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
    fontSize: 17,
    fontWeight: 'bold',
    color: '#1F2937',
  },
  totalValue: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#E23744',
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
  orderButton: {
    backgroundColor: '#E23744',
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 16,
    borderRadius: 12,
    gap: 12,
  },
  orderButtonText: {
    color: '#fff',
    fontSize: 18,
    fontWeight: 'bold',
  },
});
