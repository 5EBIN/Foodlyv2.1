import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  ScrollView,
  Alert,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { CommonActions } from '@react-navigation/native';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { useQueryClient } from '@tanstack/react-query';
import { apiService } from '../services/api';

export default function ProfileScreen({ navigation, route }: any) {
  const [userType, setUserType] = useState<'agent' | 'customer'>('customer');
  const [username, setUsername] = useState('');
  const queryClient = useQueryClient();

  useEffect(() => {
    // Get user type from AsyncStorage
    const loadUserInfo = async () => {
      const storedUserType = await AsyncStorage.getItem('user_type');
      if (storedUserType) {
        setUserType(storedUserType as 'agent' | 'customer');
      }
      // Try to get username from route params or use default
      const routeUserType = route?.params?.userType;
      if (routeUserType) {
        setUserType(routeUserType);
      }
    };
    loadUserInfo();
  }, []);

  const handleLogout = async () => {
    Alert.alert(
      'Logout',
      'Are you sure you want to logout?',
      [
        {
          text: 'Cancel',
          style: 'cancel',
        },
        {
          text: 'Logout',
          style: 'destructive',
          onPress: async () => {
            try {
              // Clear all auth data
              await apiService.logout();
              // Clear any other stored data
              await AsyncStorage.removeItem('current_job');
              // Clear React Query cache
              queryClient.clear();
              
              // Navigate to Landing screen - get root navigator
              let rootNav = navigation;
              while (rootNav.getParent()) {
                rootNav = rootNav.getParent();
              }
              
              // Reset navigation stack to Landing screen
              rootNav.dispatch(
                CommonActions.reset({
                  index: 0,
                  routes: [{ name: 'Landing' }],
                })
              );
            } catch (error) {
              console.error('Logout error:', error);
              // Still try to navigate even if logout fails
              queryClient.clear();
              let rootNav = navigation;
              while (rootNav.getParent()) {
                rootNav = rootNav.getParent();
              }
              rootNav.dispatch(
                CommonActions.reset({
                  index: 0,
                  routes: [{ name: 'Landing' }],
                })
              );
            }
          },
        },
      ]
    );
  };

  const isAgent = userType === 'agent';

  return (
    <ScrollView style={styles.container} showsVerticalScrollIndicator={false}>
      {/* Profile Header */}
      <View style={styles.header}>
        <View style={[styles.avatarContainer, isAgent && styles.avatarContainerAgent]}>
          <Ionicons name={isAgent ? "bicycle" : "person"} size={64} color="#fff" />
        </View>
        <Text style={styles.userName}>{isAgent ? 'Delivery Agent' : 'Customer User'}</Text>
        <Text style={styles.userEmail}>{isAgent ? 'agent@work4food.com' : 'customer@work4food.com'}</Text>
        <View style={styles.roleBadge}>
          <Text style={styles.roleText}>{isAgent ? 'AGENT' : 'CUSTOMER'}</Text>
        </View>
      </View>

      {/* Menu Items - Different for Agent vs Customer */}
      {isAgent ? (
        <>
          <View style={styles.menuSection}>
            <Text style={styles.sectionTitle}>Account</Text>

            <TouchableOpacity style={styles.menuItem}>
              <Ionicons name="person-outline" size={24} color="#6B7280" />
              <Text style={styles.menuItemText}>Edit Profile</Text>
              <Ionicons name="chevron-forward" size={20} color="#9CA3AF" />
            </TouchableOpacity>

            <TouchableOpacity style={styles.menuItem}>
              <Ionicons name="bicycle-outline" size={24} color="#6B7280" />
              <Text style={styles.menuItemText}>Vehicle Information</Text>
              <Ionicons name="chevron-forward" size={20} color="#9CA3AF" />
            </TouchableOpacity>

            <TouchableOpacity style={styles.menuItem}>
              <Ionicons name="location-outline" size={24} color="#6B7280" />
              <Text style={styles.menuItemText}>Location Settings</Text>
              <Ionicons name="chevron-forward" size={20} color="#9CA3AF" />
            </TouchableOpacity>
          </View>

          <View style={styles.menuSection}>
            <Text style={styles.sectionTitle}>Work</Text>

            <TouchableOpacity style={styles.menuItem}>
              <Ionicons name="time-outline" size={24} color="#6B7280" />
              <Text style={styles.menuItemText}>Delivery History</Text>
              <Ionicons name="chevron-forward" size={20} color="#9CA3AF" />
            </TouchableOpacity>

            <TouchableOpacity style={styles.menuItem}>
              <Ionicons name="stats-chart-outline" size={24} color="#6B7280" />
              <Text style={styles.menuItemText}>Performance Stats</Text>
              <Ionicons name="chevron-forward" size={20} color="#9CA3AF" />
            </TouchableOpacity>
          </View>
        </>
      ) : (
        <>
          <View style={styles.menuSection}>
            <Text style={styles.sectionTitle}>Account</Text>

            <TouchableOpacity style={styles.menuItem}>
              <Ionicons name="person-outline" size={24} color="#6B7280" />
              <Text style={styles.menuItemText}>Edit Profile</Text>
              <Ionicons name="chevron-forward" size={20} color="#9CA3AF" />
            </TouchableOpacity>

            <TouchableOpacity style={styles.menuItem}>
              <Ionicons name="location-outline" size={24} color="#6B7280" />
              <Text style={styles.menuItemText}>Delivery Addresses</Text>
              <Ionicons name="chevron-forward" size={20} color="#9CA3AF" />
            </TouchableOpacity>

            <TouchableOpacity style={styles.menuItem}>
              <Ionicons name="card-outline" size={24} color="#6B7280" />
              <Text style={styles.menuItemText}>Payment Methods</Text>
              <Ionicons name="chevron-forward" size={20} color="#9CA3AF" />
            </TouchableOpacity>
          </View>

          <View style={styles.menuSection}>
            <Text style={styles.sectionTitle}>Orders</Text>

            <TouchableOpacity style={styles.menuItem}>
              <Ionicons name="time-outline" size={24} color="#6B7280" />
              <Text style={styles.menuItemText}>Order History</Text>
              <Ionicons name="chevron-forward" size={20} color="#9CA3AF" />
            </TouchableOpacity>

            <TouchableOpacity style={styles.menuItem}>
              <Ionicons name="heart-outline" size={24} color="#6B7280" />
              <Text style={styles.menuItemText}>Favorite Restaurants</Text>
              <Ionicons name="chevron-forward" size={20} color="#9CA3AF" />
            </TouchableOpacity>
          </View>
        </>
      )}

      <View style={styles.menuSection}>
        <Text style={styles.sectionTitle}>Support</Text>

        <TouchableOpacity style={styles.menuItem}>
          <Ionicons name="help-circle-outline" size={24} color="#6B7280" />
          <Text style={styles.menuItemText}>Help Center</Text>
          <Ionicons name="chevron-forward" size={20} color="#9CA3AF" />
        </TouchableOpacity>

        <TouchableOpacity style={styles.menuItem}>
          <Ionicons name="chatbubble-outline" size={24} color="#6B7280" />
          <Text style={styles.menuItemText}>Contact Us</Text>
          <Ionicons name="chevron-forward" size={20} color="#9CA3AF" />
        </TouchableOpacity>

        <TouchableOpacity style={styles.menuItem}>
          <Ionicons name="information-circle-outline" size={24} color="#6B7280" />
          <Text style={styles.menuItemText}>About</Text>
          <Ionicons name="chevron-forward" size={20} color="#9CA3AF" />
        </TouchableOpacity>
      </View>

      {/* ML Info Card */}
      <View style={styles.mlInfoCard}>
        <Ionicons name="sparkles" size={24} color="#8B5CF6" />
        <View style={styles.mlInfoTextContainer}>
          <Text style={styles.mlInfoTitle}>Powered by Fair AI</Text>
          <Text style={styles.mlInfoText}>
            Our ML algorithm ensures fair distribution of orders to all delivery agents
          </Text>
        </View>
      </View>

      {/* Logout Button */}
      <TouchableOpacity style={styles.logoutButton} onPress={handleLogout}>
        <Ionicons name="log-out-outline" size={24} color="#EF4444" />
        <Text style={styles.logoutText}>Logout</Text>
      </TouchableOpacity>

      <View style={styles.bottomSpacer} />
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F3F4F6',
  },
  header: {
    alignItems: 'center',
    paddingVertical: 32,
    backgroundColor: '#fff',
    borderBottomWidth: 1,
    borderBottomColor: '#E5E7EB',
  },
  avatarContainer: {
    width: 100,
    height: 100,
    borderRadius: 50,
    backgroundColor: '#E23744',
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: 16,
  },
  avatarContainerAgent: {
    backgroundColor: '#10B981',
  },
  roleBadge: {
    marginTop: 8,
    paddingHorizontal: 12,
    paddingVertical: 4,
    backgroundColor: '#F3F4F6',
    borderRadius: 12,
  },
  roleText: {
    fontSize: 12,
    fontWeight: 'bold',
    color: '#6B7280',
    letterSpacing: 1,
  },
  userName: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#1F2937',
    marginBottom: 4,
  },
  userEmail: {
    fontSize: 14,
    color: '#6B7280',
  },
  menuSection: {
    marginTop: 16,
    backgroundColor: '#fff',
    paddingHorizontal: 16,
    paddingTop: 16,
    paddingBottom: 8,
  },
  sectionTitle: {
    fontSize: 14,
    fontWeight: 'bold',
    color: '#9CA3AF',
    marginBottom: 12,
    textTransform: 'uppercase',
  },
  menuItem: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 12,
    borderBottomWidth: 1,
    borderBottomColor: '#F3F4F6',
  },
  menuItemText: {
    flex: 1,
    fontSize: 16,
    color: '#1F2937',
    marginLeft: 12,
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
    marginBottom: 4,
  },
  mlInfoText: {
    fontSize: 13,
    color: '#7C3AED',
    lineHeight: 18,
  },
  logoutButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: '#fff',
    marginHorizontal: 16,
    marginTop: 16,
    paddingVertical: 16,
    borderRadius: 12,
    gap: 8,
    borderWidth: 1,
    borderColor: '#FEE2E2',
  },
  logoutText: {
    fontSize: 16,
    fontWeight: '600',
    color: '#EF4444',
  },
  bottomSpacer: {
    height: 32,
  },
});
