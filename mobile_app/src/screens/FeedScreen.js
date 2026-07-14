import React, { useEffect, useState, useCallback } from 'react';
import { View, Text, FlatList, ActivityIndicator, StyleSheet, TextInput, TouchableOpacity, Alert } from 'react-native';
import axios from 'axios';
import PostCard from '../components/PostCard';
import dayjs from 'dayjs';

import { BASE_URL } from '../config';
// If you need to test with a token quickly, uncomment and paste it here (not recommended for production):
// axios.defaults.headers.common['Authorization'] = 'Bearer <your_token_here>';

export default function FeedScreen() {
  const [posts, setPosts] = useState([]);
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(false);
  const [loadingMore, setLoadingMore] = useState(false);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [searching, setSearching] = useState(false);
  const [searchResults, setSearchResults] = useState([]);

  const fetchFeed = useCallback(async (p = 1, append = false) => {
    try {
      if (p === 1) setLoading(true);
      else setLoadingMore(true);
      setError(null);

      const resp = await axios.get(`${BASE_URL}/feed`, { params: { page: p } });
      const data = resp.data || [];
      setPosts(prev => (append ? [...prev, ...data] : data));
      setPage(p);
    } catch (err) {
      console.error(err);
      setError('Could not load feed');
    } finally {
      setLoading(false);
      setLoadingMore(false);
      setRefreshing(false);
    }
  }, []);

  useEffect(() => {
    fetchFeed(1, false);
  }, [fetchFeed]);

  const loadMore = () => {
    if (loadingMore) return;
    const next = page + 1;
    fetchFeed(next, true);
  };

  const onRefresh = () => {
    setRefreshing(true);
    fetchFeed(1, false);
  };

  const onSearch = async (q) => {
    setSearchQuery(q);
    if (!q || q.trim().length === 0) {
      setSearchResults([]);
      setSearching(false);
      return;
    }
    setSearching(true);
    try {
      const resp = await axios.get(`${BASE_URL}/search`, { params: { q } });
      setSearchResults(resp.data || []);
    } catch (err) {
      console.error(err);
      Alert.alert('Search error', 'Could not perform search');
    } finally {
      setSearching(false);
    }
  };



  const renderFooter = () => {
    if (!loadingMore) return null;
    return <ActivityIndicator style={{ margin: 12 }} />;
  };

  if (loading) {
    return (
      <View style={styles.center}>
        <ActivityIndicator size="large" />
      </View>
    );
  }

  if (error) {
    return (
      <View style={styles.center}>
        <Text>{error}</Text>
        <TouchableOpacity onPress={() => fetchFeed(1, false)} style={styles.button}>
          <Text style={styles.buttonText}>Retry</Text>
        </TouchableOpacity>
      </View>
    );
  }

  const dataToShow = searchResults.length > 0 ? searchResults : posts;

  return (
    <View style={styles.container}>
      <View style={styles.searchContainer}>
        <TextInput
          placeholder="Search posts..."
          value={searchQuery}
          onChangeText={onSearch}
          style={styles.searchInput}
        />
      </View>

      {searching && (
        <View style={styles.center}><ActivityIndicator /></View>
      )}

      {dataToShow.length === 0 && !loading && (
        <View style={styles.center}><Text>No posts found</Text></View>
      )}

      <FlatList
        data={dataToShow}
        keyExtractor={(item) => String(item.post_id || item.id)}
        renderItem={({ item }) => (
          <PostCard
            post={item}
          />
        )}
        onEndReached={() => loadMore()}
        onEndReachedThreshold={0.5}
        ListFooterComponent={renderFooter}
        refreshing={refreshing}
        onRefresh={onRefresh}
      />
    </View>
  );
}

const styles = StyleSheet.create({

  container: {
    flex: 1,
    backgroundColor: '#F5F7FB',
  },

  center: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },

  searchContainer: {
    paddingHorizontal: 18,
    paddingTop: 18,
    paddingBottom: 12,
    backgroundColor: '#F5F7FB',
  },

  searchInput: {
    backgroundColor: '#FFFFFF',

    height: 52,

    borderRadius: 18,

    paddingHorizontal: 18,

    fontSize: 16,

    borderWidth: 1,

    borderColor: '#E8ECF4',

    shadowColor: '#000',

    shadowOpacity: 0.06,

    shadowRadius: 12,

    shadowOffset: {
      width: 0,
      height: 5,
    },

    elevation: 3,
  },

  button: {

    marginTop: 20,

    backgroundColor: '#4F7CFF',

    paddingVertical: 14,

    paddingHorizontal: 28,

    borderRadius: 14,

    shadowColor: '#4F7CFF',

    shadowOpacity: 0.25,

    shadowRadius: 10,

    shadowOffset: {
      width: 0,
      height: 5,
    },

    elevation: 5,

  },

  buttonText: {
    color: '#FFF',
    fontSize: 16,
    fontWeight: '700',
  },

});