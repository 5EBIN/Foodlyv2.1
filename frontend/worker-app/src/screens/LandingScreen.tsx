// src/screens/LandingScreen.tsx
import React from 'react';
import {
  View,
  Text,
  TouchableOpacity,
  StyleSheet,
  Dimensions,
  ScrollView,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';

const { width, height } = Dimensions.get('window');

export default function LandingScreen({ navigation }: any) {
  const handleCustomerLogin = () => {
    navigation.navigate('Login', { userType: 'customer' });
  };

  const handleAgentLogin = () => {
    navigation.navigate('Login', { userType: 'agent' });
  };

  return (
    <View style={styles.container}>
      {/* Decorative circles */}
      <View style={styles.decorativeCircle1} />
      <View style={styles.decorativeCircle2} />
      <View style={styles.decorativeCircle3} />
      <View style={styles.decorativeCircle4} />
      <View style={styles.decorativeCircle5} />

      <ScrollView 
        contentContainerStyle={styles.scrollContent}
        showsVerticalScrollIndicator={false}
      >
        <View style={styles.content}>
          {/* Header */}
          <View style={styles.header}>
            <Text style={styles.headerText}>Work4Food.</Text>
          </View>

          {/* Hero Section */}
          <View style={styles.heroSection}>
            <Text style={styles.heroTitle}>
              Fastest{'\n'}
              <Text style={styles.heroTitleAccent}>Delivery</Text> &{'\n'}
              Easy <Text style={styles.heroTitleAccent}>Pickup</Text>
            </Text>

            {/* Image Container */}
            <View style={styles.imageContainer}>
              <View style={styles.imageBackgroundCircle} />
              <View style={styles.imageCircle}>
                <Ionicons name="person" size={128} color="#9CA3AF" />
              </View>
              {/* Decorative elements */}
              <View style={styles.decorativeLine1} />
              <View style={styles.decorativeLine2} />
            </View>

            {/* Customer Login Button */}
            <TouchableOpacity
              style={styles.customerButton}
              onPress={handleCustomerLogin}
              activeOpacity={0.8}
            >
              <Ionicons name="search" size={20} color="#fff" />
              <Text style={styles.customerButtonText}>Customer Login</Text>
            </TouchableOpacity>
            <Text style={styles.customerButtonSubtext}>Order now</Text>
          </View>

          {/* Avatar with message */}
          <View style={styles.messageContainer}>
            <View style={styles.avatar}>
              <Ionicons name="person" size={24} color="#fff" />
            </View>
            <View style={styles.messageBubble}>
              <Text style={styles.messageText}>
                When you are too lazy to cook, we are just a click away!
              </Text>
            </View>
          </View>
        </View>
      </ScrollView>

      {/* Agent Button - Bottom Right Corner */}
      <View style={styles.agentButtonContainer}>
        <TouchableOpacity
          style={styles.agentButton}
          onPress={handleAgentLogin}
          activeOpacity={0.8}
        >
          <Ionicons name="bicycle" size={20} color="#1F2937" />
          <Text style={styles.agentButtonText}>I am an Agent</Text>
        </TouchableOpacity>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#fff',
    position: 'relative',
    overflow: 'hidden',
  },
  scrollContent: {
    flexGrow: 1,
    justifyContent: 'center',
    padding: 16,
    paddingBottom: 100,
  },
  content: {
    width: '100%',
    maxWidth: 400,
    alignSelf: 'center',
    position: 'relative',
    zIndex: 10,
  },
  // Decorative circles
  decorativeCircle1: {
    position: 'absolute',
    top: 80,
    right: 40,
    width: 128,
    height: 128,
    backgroundColor: '#FCD34D',
    borderRadius: 64,
    opacity: 0.8,
  },
  decorativeCircle2: {
    position: 'absolute',
    top: 160,
    right: 128,
    width: 80,
    height: 80,
    backgroundColor: '#34D399',
    borderRadius: 40,
    opacity: 0.6,
  },
  decorativeCircle3: {
    position: 'absolute',
    bottom: 128,
    left: 40,
    width: 96,
    height: 96,
    backgroundColor: '#FB923C',
    borderRadius: 48,
    opacity: 0.7,
  },
  decorativeCircle4: {
    position: 'absolute',
    bottom: 16,
    right: 128,
    width: 64,
    height: 64,
    backgroundColor: '#34D399',
    borderRadius: 32,
    opacity: 0.7,
  },
  decorativeCircle5: {
    position: 'absolute',
    bottom: 16,
    right: 80,
    width: 48,
    height: 48,
    backgroundColor: '#FCD34D',
    borderRadius: 24,
    opacity: 0.8,
  },
  // Header
  header: {
    backgroundColor: '#111827',
    borderRadius: 24,
    paddingHorizontal: 24,
    paddingVertical: 16,
    marginBottom: 32,
    alignSelf: 'flex-start',
  },
  headerText: {
    color: '#fff',
    fontSize: 24,
    fontWeight: 'bold',
  },
  // Hero Section
  heroSection: {
    marginBottom: 32,
  },
  heroTitle: {
    fontSize: 48,
    fontWeight: 'bold',
    color: '#111827',
    lineHeight: 56,
    marginBottom: 24,
  },
  heroTitleAccent: {
    color: '#F97316',
  },
  // Image Container
  imageContainer: {
    position: 'relative',
    marginBottom: 32,
    alignItems: 'center',
  },
  imageBackgroundCircle: {
    position: 'absolute',
    left: -32,
    top: 0,
    width: 256,
    height: 256,
    backgroundColor: '#FCD34D',
    borderRadius: 128,
    opacity: 0.8,
  },
  imageCircle: {
    width: 256,
    height: 256,
    backgroundColor: '#E5E7EB',
    borderRadius: 128,
    justifyContent: 'center',
    alignItems: 'center',
    position: 'relative',
    zIndex: 10,
  },
  decorativeLine1: {
    position: 'absolute',
    top: 40,
    left: -16,
    width: 64,
    height: 4,
    backgroundColor: '#F97316',
    borderRadius: 2,
    transform: [{ rotate: '-45deg' }],
  },
  decorativeLine2: {
    position: 'absolute',
    bottom: 80,
    right: 0,
    width: 80,
    height: 8,
    backgroundColor: '#10B981',
    borderRadius: 4,
    transform: [{ rotate: '12deg' }],
  },
  // Customer Button
  customerButton: {
    width: '100%',
    backgroundColor: '#10B981',
    borderRadius: 32,
    paddingVertical: 16,
    paddingHorizontal: 32,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    gap: 12,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: 8,
    elevation: 5,
  },
  customerButtonText: {
    color: '#fff',
    fontSize: 18,
    fontWeight: '600',
  },
  customerButtonSubtext: {
    textAlign: 'center',
    color: '#6B7280',
    marginTop: 12,
    fontSize: 14,
  },
  // Message Container
  messageContainer: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    gap: 12,
    marginTop: 32,
  },
  avatar: {
    width: 48,
    height: 48,
    backgroundColor: '#FB923C',
    borderRadius: 24,
    justifyContent: 'center',
    alignItems: 'center',
    flexShrink: 0,
  },
  messageBubble: {
    backgroundColor: '#F3F4F6',
    borderRadius: 16,
    borderTopLeftRadius: 0,
    paddingHorizontal: 16,
    paddingVertical: 12,
    flex: 1,
  },
  messageText: {
    color: '#374151',
    fontSize: 14,
    lineHeight: 20,
  },
  // Agent Button
  agentButtonContainer: {
    position: 'absolute',
    bottom: 24,
    right: 24,
    zIndex: 20,
  },
  agentButton: {
    backgroundColor: '#FCD34D',
    borderRadius: 32,
    paddingVertical: 16,
    paddingHorizontal: 32,
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: 8,
    elevation: 5,
  },
  agentButtonText: {
    color: '#111827',
    fontSize: 16,
    fontWeight: '600',
  },
});
