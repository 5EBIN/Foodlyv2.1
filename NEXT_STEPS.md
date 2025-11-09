# 🚀 NEXT STEPS - Customer App Implementation

## ✅ COMPLETED SO FAR

### Backend (100% Done!)
- ✅ Restaurant & CustomerOrder database models
- ✅ Pydantic schemas for all entities
- ✅ Restaurant API (`/api/restaurants`)
- ✅ Customer Orders API (`/api/customer/orders`)
- ✅ ML-based agent assignment (basic implementation)
- ✅ 15 dummy restaurants seeded

### Test Your Backend Now!
Open: http://localhost:8000/docs

Try these endpoints:
1. Login: POST `/api/auth/login` with `{username: "customer1", password: "password123"}`
2. Get restaurants: GET `/api/restaurants?lat=40.7128&lng=-74.0060`
3. Create order: POST `/api/customer/orders`

---

## 📱 FRONTEND IMPLEMENTATION

### Current Status
- ✅ Landing screen (Customer/Agent choice)
- ✅ Login screen (username/password)
- ⏳ Need to build 5 new screens

### Files to Create

#### 1. **RestaurantListScreen.tsx** (HOME SCREEN FOR CUSTOMERS)
```tsx
Location: frontend/src/screens/RestaurantListScreen.tsx

Features:
- Fetch restaurants from API
- Display in grid/list with cards
- Show: name, cuisine, distance, rating, delivery time
- Click restaurant → Navigate to RestaurantDetailScreen

API Call:
GET /api/restaurants?lat={userLat}&lng={userLng}
```

#### 2. **RestaurantDetailScreen.tsx**
```tsx
Location: frontend/src/screens/RestaurantDetailScreen.tsx

Features:
- Show restaurant full details
- Large "Order Now - $25" button
- Estimated delivery time
- Click → Navigate to OrderConfirmationScreen with restaurant data
```

#### 3. **OrderConfirmationScreen.tsx**
```tsx
Location: frontend/src/screens/OrderConfirmationScreen.tsx

Features:
- Show order summary
- Restaurant name, amount, delivery address
- "Proceed to Payment" button
- Click → Navigate to MockPaymentScreen
```

#### 4. **MockPaymentScreen.tsx**
```tsx
Location: frontend/src/screens/MockPaymentScreen.tsx

Features:
- Simple mock payment UI
- "Pay & Confirm Order" button
- On click:
  1. Call POST /api/customer/orders
  2. Navigate to ActiveOrderScreen
```

#### 5. **ActiveOrderScreen.tsx**
```tsx
Location: frontend/src/screens/ActiveOrderScreen.tsx

Features:
- Poll GET /api/customer/orders/active every 3 seconds
- Show order status with progress indicator
- Display restaurant name, assigned agent (if any)
- Status: pending → assigned → picked_up → in_transit → delivered
```

---

## 🔧 Update Navigation

### frontend/src/navigation/AppNavigator.tsx

**REPLACE MainTabs function with:**

```tsx
function CustomerTabs() {
  return (
    <Tab.Navigator
      screenOptions={({ route }) => ({
        tabBarIcon: ({ focused, color, size }) => {
          let iconName: keyof typeof Ionicons.glyphMap;
          if (route.name === 'Restaurants') {
            iconName = focused ? 'restaurant' : 'restaurant-outline';
          } else if (route.name === 'MyOrders') {
            iconName = focused ? 'list' : 'list-outline';
          } else if (route.name === 'Profile') {
            iconName = focused ? 'person' : 'person-outline';
          } else {
            iconName = 'ellipse';
          }
          return <Ionicons name={iconName} size={size} color={color} />;
        },
        tabBarActiveTintColor: '#E23744',
        tabBarInactiveTintColor: '#9CA3AF',
        headerShown: true,
      })}
    >
      <Tab.Screen
        name="Restaurants"
        component={RestaurantListScreen}
        options={{ title: 'Restaurants' }}
      />
      <Tab.Screen
        name="MyOrders"
        component={ActiveOrderScreen}
        options={{ title: 'My Orders' }}
      />
      <Tab.Screen
        name="Profile"
        component={ProfileScreen}  // Create simple profile screen
        options={{ title: 'Profile' }}
      />
    </Tab.Navigator>
  );
}

// Then in Stack.Navigator, add new screens:
<Stack.Screen name="RestaurantDetail" component={RestaurantDetailScreen} />
<Stack.Screen name="OrderConfirmation" component={OrderConfirmationScreen} />
<Stack.Screen name="MockPayment" component={MockPaymentScreen} />
```

---

## 📡 Update API Service

### frontend/src/services/api.ts

**ADD these new functions:**

```tsx
// Get restaurants
async getRestaurants(lat?: number, lng?: number) {
  const params = new URLSearchParams();
  if (lat) params.append('lat', lat.toString());
  if (lng) params.append('lng', lng.toString());

  const response = await apiClient.get(`/restaurants?${params}`);
  return response.data;
},

// Get single restaurant
async getRestaurant(id: number, lat?: number, lng?: number) {
  const params = new URLSearchParams();
  if (lat) params.append('lat', lat.toString());
  if (lng) params.append('lng', lng.toString());

  const response = await apiClient.get(`/restaurants/${id}?${params}`);
  return response.data;
},

// Create customer order
async createCustomerOrder(orderData: {
  restaurant_id: number;
  amount: number;
  delivery_address: string;
  delivery_lat: number;
  delivery_lng: number;
}) {
  const response = await apiClient.post('/customer/orders', orderData);
  return response.data;
},

// Get active order
async getActiveOrder() {
  const response = await apiClient.get('/customer/orders/active');
  return response.data;
},

// Get order history
async getOrderHistory() {
  const response = await apiClient.get('/customer/orders/history');
  return response.data;
},
```

---

## 🎨 Sample Screen Implementation

### RestaurantListScreen.tsx (COMPLETE EXAMPLE)

```tsx
import React from 'react';
import {
  View,
  Text,
  FlatList,
  TouchableOpacity,
  StyleSheet,
  Image,
  ActivityIndicator,
} from 'react-native';
import { useQuery } from '@tanstack/react-query';
import { apiService } from '../services/api';
import { Ionicons } from '@expo/vector-icons';

export default function RestaurantListScreen({ navigation }: any) {
  // Mock user location (NYC)
  const userLat = 40.7128;
  const userLng = -74.0060;

  const { data: restaurants, isLoading } = useQuery({
    queryKey: ['restaurants'],
    queryFn: () => apiService.getRestaurants(userLat, userLng),
  });

  const renderRestaurant = ({ item }: any) => (
    <TouchableOpacity
      style={styles.card}
      onPress={() => navigation.navigate('RestaurantDetail', { restaurant: item })}
    >
      <Image
        source={{ uri: item.image_url || 'https://via.placeholder.com/150' }}
        style={styles.image}
      />
      <View style={styles.info}>
        <Text style={styles.name}>{item.name}</Text>
        <Text style={styles.cuisine}>{item.cuisine_type}</Text>

        <View style={styles.meta}>
          <View style={styles.metaItem}>
            <Ionicons name="star" size={16} color="#FFA500" />
            <Text style={styles.metaText}>{item.rating}</Text>
          </View>

          <View style={styles.metaItem}>
            <Ionicons name="time-outline" size={16} color="#666" />
            <Text style={styles.metaText}>{item.delivery_time} min</Text>
          </View>

          {item.distance && (
            <View style={styles.metaItem}>
              <Ionicons name="location-outline" size={16} color="#666" />
              <Text style={styles.metaText}>{item.distance.toFixed(1)} km</Text>
            </View>
          )}
        </View>
      </View>
    </TouchableOpacity>
  );

  if (isLoading) {
    return (
      <View style={styles.loading}>
        <ActivityIndicator size="large" color="#E23744" />
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <FlatList
        data={restaurants}
        renderItem={renderRestaurant}
        keyExtractor={(item) => item.id.toString()}
        contentContainerStyle={styles.list}
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
  },
  list: {
    padding: 16,
  },
  card: {
    backgroundColor: '#fff',
    borderRadius: 12,
    marginBottom: 16,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
    overflow: 'hidden',
  },
  image: {
    width: '100%',
    height: 150,
    backgroundColor: '#E5E7EB',
  },
  info: {
    padding: 12,
  },
  name: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#1F2937',
    marginBottom: 4,
  },
  cuisine: {
    fontSize: 14,
    color: '#6B7280',
    marginBottom: 8,
  },
  meta: {
    flexDirection: 'row',
    gap: 12,
  },
  metaItem: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 4,
  },
  metaText: {
    fontSize: 12,
    color: '#6B7280',
  },
});
```

---

## ⚡ Quick Implementation Guide

1. **Create the 5 screens** (use the example above as template)
2. **Update navigation** to include new screens and tabs
3. **Add API functions** to services/api.ts
4. **Test the flow:**
   - Login as customer1
   - See restaurant list
   - Click restaurant
   - Place order
   - See active order with status

---

## 🔥 Priority Order (What to Build Next)

1. ✅ RestaurantListScreen (MOST IMPORTANT - home screen)
2. ✅ RestaurantDetailScreen
3. ✅ MockPaymentScreen (can combine with OrderConfirmation)
4. ✅ ActiveOrderScreen
5. ⏳ Update Navigation

---

Would you like me to:
A) Continue building the frontend screens one by one?
B) Give you complete code for all 5 screens at once?
C) Focus on testing the backend APIs first?
