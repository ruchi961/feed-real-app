import React, { useState } from 'react';
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  StyleSheet,
  ActivityIndicator,
  Alert,
  KeyboardAvoidingView,
  Platform,
} from 'react-native';
import axios from 'axios';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { BASE_URL } from '../config';

export default function LoginScreen({ onLogin }) {
  const [email, setEmail] = useState('alice@example.com');
  const [password, setPassword] = useState('password');
  const [loading, setLoading] = useState(false);

  const doLogin = async () => {
    setLoading(true);

    try {
      const resp = await axios.post(`${BASE_URL}/login`, {
        email,
        password,
      });

      const token = resp.data?.token;

      if (!token) throw new Error('No token returned');

      await AsyncStorage.setItem('auth_token', token);

      axios.defaults.headers.common[
        'Authorization'
      ] = `Bearer ${token}`;

      onLogin(token);
    } catch (err) {
      console.log(err);

      Alert.alert(
        'Login Failed',
        err.response?.data?.message ||
          err.message ||
          'Something went wrong.'
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <KeyboardAvoidingView
      style={styles.container}
      behavior={
        Platform.OS === 'ios'
          ? 'padding'
          : undefined
      }
    >
      <View style={styles.card}>

        <Text style={styles.logo}>FeedAI</Text>

        <Text style={styles.subtitle}>
          Welcome Back 👋
        </Text>

        <Text style={styles.description}>
          Sign in to continue exploring your
          personalized social feed.
        </Text>

        <TextInput
          style={styles.input}
          placeholder="Email Address"
          placeholderTextColor="#999"
          value={email}
          onChangeText={setEmail}
          autoCapitalize="none"
          keyboardType="email-address"
        />

        <TextInput
          style={styles.input}
          placeholder="Password"
          placeholderTextColor="#999"
          value={password}
          onChangeText={setPassword}
          secureTextEntry
        />

        <TouchableOpacity
          style={styles.button}
          onPress={doLogin}
          disabled={loading}
          activeOpacity={0.8}
        >
          {loading ? (
            <ActivityIndicator color="#FFF" />
          ) : (
            <Text style={styles.buttonText}>
              Sign In
            </Text>
          )}
        </TouchableOpacity>

      </View>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({

  container: {
    flex: 1,
    backgroundColor: '#F4F7FC',
    justifyContent: 'center',
    paddingHorizontal: 24,
  },

  card: {
    backgroundColor: '#FFF',
    borderRadius: 24,
    padding: 28,

    shadowColor: '#000',
    shadowOpacity: 0.08,
    shadowRadius: 20,
    shadowOffset: {
      width: 0,
      height: 10,
    },

    elevation: 8,
  },

  logo: {
    fontSize: 34,
    fontWeight: '800',
    color: '#3B82F6',
    textAlign: 'center',
  },

  subtitle: {
    marginTop: 20,
    fontSize: 28,
    fontWeight: '700',
    color: '#222',
    textAlign: 'center',
  },

  description: {
    marginTop: 10,
    marginBottom: 28,
    color: '#777',
    textAlign: 'center',
    fontSize: 15,
    lineHeight: 22,
  },

  input: {
    backgroundColor: '#F6F7FB',
    borderRadius: 14,
    paddingHorizontal: 18,
    paddingVertical: 16,
    fontSize: 16,
    marginBottom: 16,

    borderWidth: 1,
    borderColor: '#E8EAF1',
  },

  button: {
    backgroundColor: '#e2ffd7',
    paddingVertical: 17,
    borderRadius: 14,
    alignItems: 'center',
    marginTop: 8,

    shadowColor: '#d9fed8',
    shadowOpacity: 0.35,
    shadowRadius: 10,
    shadowOffset: {
      width: 0,
      height: 5,
    },

    elevation: 5,
  },

  buttonText: {
    color: '#FFF',
    fontSize: 17,
    fontWeight: '700',
    letterSpacing: 0.4,
  },

});