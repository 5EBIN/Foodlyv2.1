// src/screens/LoginScreen.tsx
import React, { useState } from 'react';
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  StyleSheet,
  KeyboardAvoidingView,
  Platform,
  ActivityIndicator,
  Alert,
  ScrollView,
} from 'react-native';
import { useMutation } from '@tanstack/react-query';
import { apiService } from '../services/api';
import { Ionicons } from '@expo/vector-icons';

export default function LoginScreen({ navigation, route }: any) {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const userType = route?.params?.userType || 'customer';

  const loginMutation = useMutation({
    mutationFn: (credentials: { username: string; password: string; userType: string }) =>
      apiService.login(credentials),
    onSuccess: (data) => {
      // Use user_type from response, fallback to route param
      const finalUserType = data?.user_type || userType;
      navigation.replace('Main', { userType: finalUserType });
    },
    onError: (error: any) => {
      Alert.alert('Login Failed', error.message || 'Please try again');
    },
  });

  const handleLogin = () => {
    if (!username || !password) {
      Alert.alert('Error', 'Please enter username and password');
      return;
    }
    loginMutation.mutate({ username, password, userType });
  };

  const handleBack = () => {
    navigation.goBack();
  };

  return (
    <KeyboardAvoidingView
      style={styles.container}
      behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
    >
      {/* Decorative elements */}
      <View style={styles.decorativeCircle1} />
      <View style={styles.decorativeCircle2} />
      <View style={styles.decorativeCircle3} />
      <View style={styles.decorativeCircle4} />
      <View style={styles.decorativeWave1} />
      <View style={styles.decorativeWave2} />

      <ScrollView
        contentContainerStyle={styles.scrollContent}
        showsVerticalScrollIndicator={false}
        keyboardShouldPersistTaps="handled"
      >
        <View style={styles.content}>
          {/* Back Button */}
          <TouchableOpacity
            style={styles.backButton}
            onPress={handleBack}
            activeOpacity={0.7}
          >
            <Ionicons name="arrow-back" size={20} color="#374151" />
            <Text style={styles.backButtonText}>Back</Text>
          </TouchableOpacity>

          {/* Main Card */}
          <View style={styles.card}>
            {/* Brand Header */}
            <View style={styles.brandHeader}>
              <View style={styles.brandIcon}>
                <Ionicons name="person" size={28} color="#fff" />
              </View>
            </View>

            {/* Hero Image Section */}
            <View style={styles.heroImageContainer}>
              <View style={styles.heroImageBackground} />
              <View style={styles.heroImage}>
                <Ionicons name="person" size={128} color="#D1D5DB" />
              </View>
              {/* Decorative elements on image */}
              <View style={styles.heroDecorative1} />
              <View style={styles.heroDecorative2} />
              <View style={styles.heroDecorative3} />
            </View>

            {/* Title */}
            <Text style={styles.title}>
              Get your food delivered fast
            </Text>

            <Text style={styles.subtitle}>
              A convenient delivery solution that helps protect the environment and is fair for all.
            </Text>

            {/* Form */}
            <View style={styles.form}>
              <TextInput
                style={styles.input}
                placeholder="Username"
                placeholderTextColor="#9CA3AF"
                value={username}
                onChangeText={setUsername}
                autoCapitalize="none"
                editable={!loginMutation.isPending}
              />

              <View style={styles.passwordContainer}>
                <TextInput
                  style={styles.passwordInput}
                  placeholder="Password"
                  placeholderTextColor="#9CA3AF"
                  value={password}
                  onChangeText={setPassword}
                  secureTextEntry={!showPassword}
                  editable={!loginMutation.isPending}
                />
                <TouchableOpacity
                  style={styles.eyeButton}
                  onPress={() => setShowPassword(!showPassword)}
                  activeOpacity={0.7}
                >
                  <Ionicons
                    name={showPassword ? 'eye-off' : 'eye'}
                    size={20}
                    color="#9CA3AF"
                  />
                </TouchableOpacity>
              </View>
            </View>

            {/* Login Button */}
            <TouchableOpacity
              style={[
                styles.loginButton,
                loginMutation.isPending && styles.loginButtonDisabled,
              ]}
              onPress={handleLogin}
              disabled={loginMutation.isPending}
              activeOpacity={0.8}
            >
              {loginMutation.isPending ? (
                <ActivityIndicator color="#fff" size="small" />
              ) : (
                <Text style={styles.loginButtonText}>Let's Start</Text>
              )}
            </TouchableOpacity>

            {/* Demo Text */}
            <Text style={styles.demoText}>
              Test: {userType === 'agent' ? 'agent1' : 'customer1'} / password123
            </Text>

            {/* Footer Link */}
            <Text style={styles.footerText}>
              Already a user?{' '}
              <Text style={styles.footerLink}>Login</Text>
            </Text>
          </View>

          {/* Bottom decorative dots */}
          <View style={styles.dotsContainer}>
            <View style={styles.dotActive} />
            <View style={styles.dot} />
            <View style={styles.dot} />
          </View>
        </View>
      </ScrollView>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#FFF7ED', // orange-50 equivalent
    position: 'relative',
    overflow: 'hidden',
  },
  scrollContent: {
    flexGrow: 1,
    justifyContent: 'center',
    padding: 16,
    paddingTop: 60,
    paddingBottom: 40,
  },
  content: {
    width: '100%',
    maxWidth: 400,
    alignSelf: 'center',
    position: 'relative',
    zIndex: 10,
  },
  // Decorative elements
  decorativeCircle1: {
    position: 'absolute',
    top: 0,
    left: 0,
    width: 128,
    height: 128,
    backgroundColor: '#C4B5FD', // purple-300
    borderRadius: 64,
    opacity: 0.6,
    transform: [{ translateX: -64 }, { translateY: -64 }],
  },
  decorativeCircle2: {
    position: 'absolute',
    top: 40,
    right: 40,
    width: 96,
    height: 96,
    backgroundColor: '#6EE7B7', // emerald-300
    borderRadius: 48,
    opacity: 0.5,
  },
  decorativeCircle3: {
    position: 'absolute',
    bottom: 40,
    left: 40,
    width: 80,
    height: 80,
    backgroundColor: '#FDBA74', // orange-300
    borderRadius: 40,
    opacity: 0.6,
  },
  decorativeCircle4: {
    position: 'absolute',
    bottom: 0,
    right: 0,
    width: 160,
    height: 160,
    backgroundColor: '#C4B5FD', // purple-300
    borderRadius: 80,
    opacity: 0.5,
    transform: [{ translateX: 80 }, { translateY: 80 }],
  },
  decorativeWave1: {
    position: 'absolute',
    top: 80,
    right: 128,
    width: 64,
    height: 4,
    backgroundColor: '#A78BFA', // purple-400
    borderRadius: 2,
    transform: [{ rotate: '45deg' }],
  },
  decorativeWave2: {
    position: 'absolute',
    top: 96,
    right: 112,
    width: 64,
    height: 4,
    backgroundColor: '#A78BFA', // purple-400
    borderRadius: 2,
    transform: [{ rotate: '45deg' }],
  },
  // Back Button
  backButton: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
    marginBottom: 24,
    alignSelf: 'flex-start',
  },
  backButtonText: {
    color: '#374151',
    fontSize: 16,
    fontWeight: '600',
  },
  // Main Card
  card: {
    backgroundColor: '#fff',
    borderRadius: 24,
    padding: 32,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 10 },
    shadowOpacity: 0.15,
    shadowRadius: 20,
    elevation: 10,
    position: 'relative',
    overflow: 'hidden',
  },
  // Brand Header
  brandHeader: {
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: 24,
  },
  brandIcon: {
    width: 48,
    height: 48,
    backgroundColor: '#10B981', // emerald-500
    borderRadius: 16,
    justifyContent: 'center',
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.2,
    shadowRadius: 8,
    elevation: 5,
  },
  // Hero Image Section
  heroImageContainer: {
    position: 'relative',
    marginBottom: 24,
    alignItems: 'center',
  },
  heroImageBackground: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    backgroundColor: '#E9D5FF', // purple-200 equivalent
    borderRadius: 24,
    transform: [{ rotate: '-3deg' }],
  },
  heroImage: {
    backgroundColor: '#F3F4F6',
    borderRadius: 24,
    padding: 32,
    height: 192,
    width: '100%',
    justifyContent: 'center',
    alignItems: 'center',
    position: 'relative',
    zIndex: 10,
  },
  heroDecorative1: {
    position: 'absolute',
    top: 16,
    left: 16,
    width: 32,
    height: 32,
    backgroundColor: '#34D399', // emerald-400
    borderRadius: 16,
    opacity: 0.7,
    zIndex: 20,
  },
  heroDecorative2: {
    position: 'absolute',
    top: 24,
    right: 24,
    width: 64,
    height: 4,
    backgroundColor: '#A78BFA', // purple-400
    borderRadius: 2,
    transform: [{ rotate: '-45deg' }],
    zIndex: 20,
  },
  heroDecorative3: {
    position: 'absolute',
    bottom: 16,
    right: 16,
    width: 48,
    height: 4,
    backgroundColor: '#A78BFA', // purple-400
    borderRadius: 2,
    transform: [{ rotate: '12deg' }],
    zIndex: 20,
  },
  // Title
  title: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#111827',
    textAlign: 'center',
    marginBottom: 12,
  },
  subtitle: {
    textAlign: 'center',
    color: '#6B7280',
    marginBottom: 32,
    fontSize: 14,
    lineHeight: 20,
  },
  // Form
  form: {
    marginBottom: 24,
    gap: 16,
  },
  input: {
    width: '100%',
    paddingHorizontal: 16,
    paddingVertical: 16,
    backgroundColor: '#F9FAFB', // gray-50
    borderWidth: 1,
    borderColor: '#E5E7EB', // gray-200
    borderRadius: 16,
    fontSize: 16,
    color: '#111827',
  },
  passwordContainer: {
    position: 'relative',
    width: '100%',
  },
  passwordInput: {
    width: '100%',
    paddingHorizontal: 16,
    paddingVertical: 16,
    paddingRight: 48,
    backgroundColor: '#F9FAFB', // gray-50
    borderWidth: 1,
    borderColor: '#E5E7EB', // gray-200
    borderRadius: 16,
    fontSize: 16,
    color: '#111827',
  },
  eyeButton: {
    position: 'absolute',
    right: 16,
    top: 16,
    padding: 4,
  },
  // Login Button
  loginButton: {
    width: '100%',
    backgroundColor: '#10B981', // emerald-500
    borderRadius: 16,
    paddingVertical: 16,
    alignItems: 'center',
    justifyContent: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: 8,
    elevation: 5,
  },
  loginButtonDisabled: {
    opacity: 0.5,
  },
  loginButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
  },
  // Demo Text
  demoText: {
    textAlign: 'center',
    color: '#6B7280',
    marginTop: 16,
    fontSize: 12,
  },
  // Footer
  footerText: {
    textAlign: 'center',
    color: '#6B7280',
    fontSize: 14,
    marginTop: 24,
  },
  footerLink: {
    color: '#10B981',
    fontWeight: '600',
  },
  // Dots
  dotsContainer: {
    flexDirection: 'row',
    justifyContent: 'center',
    gap: 8,
    marginTop: 24,
  },
  dot: {
    width: 8,
    height: 8,
    borderRadius: 4,
    backgroundColor: '#D1D5DB', // gray-300
  },
  dotActive: {
    width: 8,
    height: 8,
    borderRadius: 4,
    backgroundColor: '#10B981', // emerald-400
  },
});
