import React, { useState } from 'react';
import { View, Text, StyleSheet, Image, TouchableOpacity, Alert } from 'react-native';
import dayjs from 'dayjs';
import axios from 'axios';
import { BASE_URL } from '../config';

export default function PostCard({ post }) {
  const [commenting, setCommenting] = useState(false);
  const username = post.author?.name || post.author_name || 'Unknown';
  const text = post.text || '';
  const created = post.created_at || '';
  const avatar = post.avatar || '';
  const images = post.images || '';
  const sendReaction = async (reactionType) => {
    try {
      await axios.post(`${BASE_URL}/interactions`, { post_id: post.post_id || post.id, type: 'reaction', payload: { reaction_type: reactionType } });
      Alert.alert('Reacted', `You reacted with ${reactionType}`);
    } catch (err) {
      console.error(err);
      Alert.alert('Error', err.response?.data?.message || 'Could not send reaction');
    }
  };

  const sendComment = async (comment) => {
    try {
      await axios.post(`${BASE_URL}/interactions`, { post_id: post.post_id || post.id, type: 'comment', payload: { comment } });
      Alert.alert('Commented', 'Your comment was posted');
    } catch (err) {
      console.error(err);
      Alert.alert('Error', err.response?.data?.message || 'Could not post comment');
    }
  };

  return (
    <View style={styles.card}>
        <View style={styles.header}>
        <View style={styles.avatar}>

<Image
  source={   avatar ? { uri: avatar } : require('../../assets/images/avatar.PNG') }
  
  style={styles.avatar}
/></View>
        <View style={{ flex: 1 }}>
          <Text style={styles.username}>{username}</Text>
          <Text style={styles.time}>{created}</Text>
        </View>
        
      </View>
      <View style={styles.content}>
        <Text style={styles.text}>{text}</Text>
      </View>
      <View style={styles.content}>
        <Image
  source={   images ? { uri: images } : require('../../assets/images/images.PNG') }
  
  style={styles.images}
/>
      </View>
      <View style={styles.actions}>
        <TouchableOpacity onPress={() => sendReaction('like')} style={styles.actionBtn}><Text>👍</Text></TouchableOpacity>
        <TouchableOpacity onPress={() => sendReaction('love')} style={styles.actionBtn}><Text>❤️</Text></TouchableOpacity>
        <TouchableOpacity onPress={() => sendReaction('laugh')} style={styles.actionBtn}><Text>😂</Text></TouchableOpacity>
        <TouchableOpacity onPress={() => sendReaction('wow')} style={styles.actionBtn}><Text>😮</Text></TouchableOpacity>
        <TouchableOpacity onPress={() => {
          const comment = typeof window !== 'undefined' && window.prompt ? window.prompt('Write a comment') : null;
          if (comment && comment.trim()) sendComment(comment.trim());
        }} style={styles.actionBtn}><Text>💬</Text></TouchableOpacity>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({

  card: {

    backgroundColor: '#FFFFFF',

    marginHorizontal: 16,

    marginVertical: 10,

    borderRadius: 22,

    padding: 18,

    shadowColor: '#000',

    shadowOpacity: 0.08,

    shadowRadius: 15,

    shadowOffset: {
      width: 0,
      height: 6,
    },

    elevation: 6,
  },

  header: {

    flexDirection: 'row',

    alignItems: 'center',

    marginBottom: 14,

  },

  avatar: {

    width: 52,

    height: 52,

    borderRadius: 26,

    backgroundColor: '#D8DCE8',

    marginRight: 14,

    borderWidth: 2,

    borderColor: '#EEF2F7',

  },
images: {
  width: '100%',
  height: 200,
  borderRadius: 18,
  marginTop: 14,
  resizeMode: 'cover',
  backgroundColor: '#F3F4F6',
},
  username: {

    fontSize: 17,

    fontWeight: '700',

    color: '#1F2937',

  },

  time: {

    marginTop: 3,

    fontSize: 13,

    color: '#9CA3AF',

  },

  content: {

    marginTop: 6,

  },

  text: {

    fontSize: 16,

    lineHeight: 26,

    color: '#374151',

    letterSpacing: 0.2,

  },

  actions: {

    flexDirection: 'row',

    justifyContent: 'space-between',

    alignItems: 'center',

    marginTop: 20,

    borderTopWidth: 1,

    borderTopColor: '#F1F3F6',

    paddingTop: 16,

  },

  actionBtn: {

    width: 46,

    height: 46,

    borderRadius: 23,

    justifyContent: 'center',

    alignItems: 'center',

    backgroundColor: '#F7F9FC',

  },

  reactBtn: {

    width: 42,

    height: 42,

    borderRadius: 21,

    justifyContent: 'center',

    alignItems: 'center',

    backgroundColor: '#FFF0F3',

  },

  reactText: {

    fontSize: 22,

  },

});
