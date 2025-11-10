import React, { useState } from 'react';
import { useNavigation } from '@react-navigation/native';
import axios from 'axios';
import { View, Text, TextInput, TouchableOpacity } from 'react-native';

export default function AdminLogin() {
  // Simple RN version for worker-app context (no react-router here)
  const navigation: any = useNavigation();
  const [email, setEmail] = useState('admin_test@foodly.com');
  const [password, setPassword] = useState('admin123');
  const [error, setError] = useState('');

  const handleLogin = async () => {
    try {
      const response = await axios.post('/api/auth/login', { username: email, password });
      // Store admin token in localStorage-like storage (fallback)
      // In RN, you could use AsyncStorage; keeping parity with original snippet:
      // @ts-ignore
      global.localStorage?.setItem?.('adminToken', response.data.access_token);
      // Navigate to a placeholder screen or just confirm
      // @ts-ignore
      navigation.navigate('Landing');
    } catch (err) {
      setError('Invalid admin credentials');
    }
  };

  return (
    <View style={{ flex: 1, justifyContent: 'center', alignItems: 'center', backgroundColor: '#f3f4f6' }}>
      <View style={{ backgroundColor: '#fff', padding: 24, borderRadius: 12, width: 320 }}>
        <Text style={{ fontSize: 20, fontWeight: 'bold', textAlign: 'center', marginBottom: 16 }}>
          WORK4FOOD Admin
        </Text>
        {!!error && (
          <View style={{ backgroundColor: '#fee2e2', padding: 8, borderRadius: 6, marginBottom: 12 }}>
            <Text style={{ color: '#991b1b' }}>{error}</Text>
          </View>
        )}
        <TextInput
          placeholder="Admin Email"
          value={email}
          onChangeText={setEmail}
          style={{ borderWidth: 1, borderColor: '#e5e7eb', borderRadius: 6, padding: 12, marginBottom: 12 }}
        />
        <TextInput
          placeholder="Password"
          value={password}
          onChangeText={setPassword}
          secureTextEntry
          style={{ borderWidth: 1, borderColor: '#e5e7eb', borderRadius: 6, padding: 12, marginBottom: 12 }}
        />
        <TouchableOpacity onPress={handleLogin} style={{ backgroundColor: '#2563eb', padding: 12, borderRadius: 6 }}>
          <Text style={{ color: '#fff', textAlign: 'center', fontWeight: '600' }}>Login</Text>
        </TouchableOpacity>
      </View>
    </View>
  );
}


