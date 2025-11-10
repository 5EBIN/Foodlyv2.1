// src/navigation/AppNavigator.tsx
import React from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { Ionicons } from '@expo/vector-icons';
import LandingScreen from '../screens/LandingScreen';
import LoginScreen from '../screens/LoginScreen';
// Agent Screens
import OrdersScreen from '../screens/OrdersScreen';
import CurrentJobScreen from '../screens/CurrentJobScreen';
import EarningsScreen from '../screens/EarningsScreen';
// Customer Screens
import RestaurantListScreen from '../screens/RestaurantListScreen';
import RestaurantDetailScreen from '../screens/RestaurantDetailScreen';
import OrderConfirmationScreen from '../screens/OrderConfirmationScreen';
import MockPaymentScreen from '../screens/MockPaymentScreen';
import ActiveOrderScreen from '../screens/ActiveOrderScreen';
import ProfileScreen from '../screens/ProfileScreen';

const Stack = createNativeStackNavigator();
const Tab = createBottomTabNavigator();

// Agent Bottom Tabs
function AgentTabs() {
  return (
    <Tab.Navigator
      screenOptions={({ route }) => ({
        tabBarIcon: ({ focused, color, size }) => {
          let iconName: keyof typeof Ionicons.glyphMap;
          if (route.name === 'Orders') {
            iconName = focused ? 'list' : 'list-outline';
          } else if (route.name === 'CurrentJob') {
            iconName = focused ? 'briefcase' : 'briefcase-outline';
          } else if (route.name === 'Earnings') {
            iconName = focused ? 'wallet' : 'wallet-outline';
          } else if (route.name === 'Profile') {
            iconName = focused ? 'person' : 'person-outline';
          } else {
            iconName = 'ellipse';
          }
          return <Ionicons name={iconName} size={size} color={color} />;
        },
        tabBarActiveTintColor: '#10B981',
        tabBarInactiveTintColor: '#9CA3AF',
        headerShown: true,
      })}
    >
      <Tab.Screen
        name="Orders"
        component={OrdersScreen}
        options={{ title: 'Available Orders' }}
      />
      <Tab.Screen
        name="CurrentJob"
        component={CurrentJobScreen}
        options={{ title: 'Current Job' }}
      />
      <Tab.Screen
        name="Earnings"
        component={EarningsScreen}
        options={{ title: 'My Earnings' }}
      />
      <Tab.Screen
        name="Profile"
        component={ProfileScreen}
        options={{ title: 'Profile' }}
      />
    </Tab.Navigator>
  );
}

// Customer Bottom Tabs
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
        component={ProfileScreen}
        options={{ title: 'Profile' }}
      />
    </Tab.Navigator>
  );
}

// Main component that decides which tabs to show based on userType
function MainScreen({ route }: any) {
  const userType = route?.params?.userType || 'customer';

  // Show different tabs based on user type
  return userType === 'agent' ? <AgentTabs /> : <CustomerTabs />;
}

export default function AppNavigator() {
  return (
    <NavigationContainer>
      <Stack.Navigator screenOptions={{ headerShown: false }}>
        <Stack.Screen name="Landing" component={LandingScreen} />
        <Stack.Screen name="Login" component={LoginScreen} />
        <Stack.Screen name="Main" component={MainScreen} />
        {/* Customer Stack Screens */}
        <Stack.Screen
          name="RestaurantDetail"
          component={RestaurantDetailScreen}
          options={{ headerShown: true, title: 'Restaurant Details' }}
        />
        <Stack.Screen
          name="OrderConfirmation"
          component={OrderConfirmationScreen}
          options={{ headerShown: true, title: 'Confirm Order' }}
        />
        <Stack.Screen
          name="MockPayment"
          component={MockPaymentScreen}
          options={{ headerShown: true, title: 'Payment' }}
        />
        <Stack.Screen
          name="ActiveOrder"
          component={ActiveOrderScreen}
          options={{ headerShown: true, title: 'Order Status' }}
        />
      </Stack.Navigator>
    </NavigationContainer>
  );
}
