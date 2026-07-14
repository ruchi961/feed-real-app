import React, { useEffect, useState } from 'react';
import { SafeAreaView, StatusBar } from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';
import axios from 'axios';
import FeedScreen from './src/screens/FeedScreen';
import LoginScreen from './src/screens/LoginScreen';

export default function App() {
  const [token, setToken] = useState(null);

 useEffect(() => {

    const loadToken = async () => {

        const token = await AsyncStorage.getItem("auth_token");

        if (!token) {
            setLoading(false);
            return;
        }

        axios.defaults.headers.common.Authorization =
            `Bearer ${token}`;

        try {

            await axios.get(`${BASE_URL}/me`);

            setToken(token);

        } catch {

            await AsyncStorage.removeItem("auth_token");

            delete axios.defaults.headers.common.Authorization;

            setToken(null);
        }

        setLoading(false);
    };

    loadToken();

}, []);

  const handleLogin = async (t) => {
    setToken(t);
    await AsyncStorage.setItem('auth_token', t);
  };

  return (
    <SafeAreaView style={{ flex: 1 }}>
      <StatusBar barStyle="dark-content" />
      {token ? <FeedScreen /> : <LoginScreen onLogin={handleLogin} />}
    </SafeAreaView>
  );
}
