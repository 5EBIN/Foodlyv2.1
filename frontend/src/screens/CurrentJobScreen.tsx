// src/screens/CurrentJobScreen.tsx
import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  TouchableOpacity,
  StyleSheet,
  ActivityIndicator,
  Alert,
} from 'react-native';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { Ionicons } from '@expo/vector-icons';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { apiService } from '../services/api';

export default function CurrentJobScreen() {
  const [currentJob, setCurrentJob] = useState<any>(null);
  const [timer, setTimer] = useState(0);
  const queryClient = useQueryClient();

  useEffect(() => {
    loadCurrentJob();
  }, []);

  useEffect(() => {
    if (currentJob) {
      const interval = setInterval(() => {
        setTimer((prev) => prev + 1);
      }, 1000);
      return () => clearInterval(interval);
    }
  }, [currentJob]);

  const loadCurrentJob = async () => {
    const jobStr = await AsyncStorage.getItem('current_job');
    if (jobStr) {
      setCurrentJob(JSON.parse(jobStr));
    }
  };

  const completeJobMutation = useMutation({
    mutationFn: async (orderId: string) => {
      await apiService.completeOrder(orderId);
      await AsyncStorage.removeItem('current_job');
    },
    onSuccess: () => {
      setCurrentJob(null);
      setTimer(0);
      queryClient.invalidateQueries({ queryKey: ['orders'] });
      queryClient.invalidateQueries({ queryKey: ['earnings'] });
      Alert.alert('Success', 'Job completed successfully!');
    },
    onError: (error: any) => {
      Alert.alert('Error', error.message || 'Failed to complete job');
    },
  });

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  if (!currentJob) {
    return (
      <View style={styles.emptyContainer}>
        <Ionicons name="briefcase-outline" size={64} color="#D1D5DB" />
        <Text style={styles.emptyText}>No active job</Text>
        <Text style={styles.emptySubtext}>
          Accept an order from the Orders tab
        </Text>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <View style={styles.content}>
        <View style={styles.timerContainer}>
          <Text style={styles.timerLabel}>Time on Job</Text>
          <Text style={styles.timerText}>{formatTime(timer)}</Text>
        </View>
        <View style={styles.jobCard}>
          <View style={styles.jobHeader}>
            <Ionicons name="checkmark-circle" size={32} color="#10B981" />
            <Text style={styles.jobStatus}>Job In Progress</Text>
          </View>
          <View style={styles.divider} />
          <View style={styles.locationSection}>
            <View style={styles.locationRow}>
              <View style={styles.iconContainer}>
                <Ionicons name="location" size={24} color="#3B82F6" />
              </View>
              <View style={styles.locationDetails}>
                <Text style={styles.locationLabel}>Pickup Location</Text>
                <Text style={styles.locationValue}>{currentJob.pickup}</Text>
              </View>
            </View>
            <View style={styles.routeLine} />
            <View style={styles.locationRow}>
              <View style={styles.iconContainer}>
                <Ionicons name="flag" size={24} color="#EF4444" />
              </View>
              <View style={styles.locationDetails}>
                <Text style={styles.locationLabel}>Dropoff Location</Text>
                <Text style={styles.locationValue}>{currentJob.dropoff}</Text>
              </View>
            </View>
          </View>
          <View style={styles.detailsSection}>
            <View style={styles.detailItem}>
              <Ionicons name="time-outline" size={20} color="#6B7280" />
              <Text style={styles.detailText}>
                Estimated: {currentJob.eta} min
              </Text>
            </View>
            {currentJob.g_mean && (
              <View style={styles.detailItem}>
                <Ionicons name="analytics-outline" size={20} color="#6B7280" />
                <Text style={styles.detailText}>
                  G-Value: {currentJob.g_mean.toFixed(2)}
                </Text>
              </View>
            )}
          </View>
        </View>
        <TouchableOpacity
          style={[
            styles.completeButton,
            completeJobMutation.isPending && styles.buttonDisabled,
          ]}
          onPress={() => completeJobMutation.mutate(currentJob.id)}
          disabled={completeJobMutation.isPending}
        >
          {completeJobMutation.isPending ? (
            <ActivityIndicator color="#fff" />
          ) : (
            <>
              <Ionicons name="checkmark-done" size={24} color="#fff" />
              <Text style={styles.completeButtonText}>Complete Job</Text>
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
  content: {
    flex: 1,
    padding: 16,
  },
  emptyContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 32,
    backgroundColor: '#F3F4F6',
  },
  emptyText: {
    fontSize: 20,
    fontWeight: '600',
    color: '#6B7280',
    marginTop: 16,
  },
  emptySubtext: {
    fontSize: 14,
    color: '#9CA3AF',
    marginTop: 8,
    textAlign: 'center',
  },
  timerContainer: {
    backgroundColor: '#fff',
    borderRadius: 12,
    padding: 24,
    alignItems: 'center',
    marginBottom: 16,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  timerLabel: {
    fontSize: 14,
    color: '#6B7280',
    marginBottom: 8,
  },
  timerText: {
    fontSize: 48,
    fontWeight: 'bold',
    color: '#3B82F6',
    fontVariant: ['tabular-nums'],
  },
  jobCard: {
    backgroundColor: '#fff',
    borderRadius: 12,
    padding: 20,
    marginBottom: 16,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  jobHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 16,
  },
  jobStatus: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#10B981',
    marginLeft: 12,
  },
  divider: {
    height: 1,
    backgroundColor: '#E5E7EB',
    marginBottom: 20,
  },
  locationSection: {
    marginBottom: 20,
  },
  locationRow: {
    flexDirection: 'row',
    alignItems: 'flex-start',
  },
  iconContainer: {
    width: 40,
    alignItems: 'center',
  },
  routeLine: {
    width: 2,
    height: 24,
    backgroundColor: '#D1D5DB',
    marginLeft: 19,
    marginVertical: 8,
  },
  locationDetails: {
    flex: 1,
    marginLeft: 12,
  },
  locationLabel: {
    fontSize: 12,
    color: '#9CA3AF',
    marginBottom: 4,
  },
  locationValue: {
    fontSize: 16,
    color: '#1F2937',
    fontWeight: '500',
  },
  detailsSection: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    paddingTop: 16,
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
  completeButton: {
    backgroundColor: '#10B981',
    borderRadius: 12,
    padding: 18,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.2,
    shadowRadius: 6,
    elevation: 4,
  },
  buttonDisabled: {
    opacity: 0.6,
  },
  completeButtonText: {
    color: '#fff',
    fontSize: 18,
    fontWeight: 'bold',
    marginLeft: 12,
  },
});
