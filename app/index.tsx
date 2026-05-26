import React, { useEffect, useState } from 'react';
import { StyleSheet, Text, View, TouchableOpacity, ActivityIndicator } from 'react-native';
import { useRouter } from 'expo-router';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { SafeAreaView } from 'react-native-safe-area-context';

export default function WelcomeGate() {
  const router = useRouter();
  const [loading, setLoading] = useState(true);
  const [profile, setProfile] = useState<{ owner_name: string; name: string } | null>(null);

  useEffect(() => {
    async function checkLocalStorage() {
      try {
        const savedUserId = await AsyncStorage.getItem('pet_user_id');
        const savedProfileRaw = await AsyncStorage.getItem('pet_profile');
        
        if (savedUserId && savedProfileRaw) {
          const parsed = JSON.parse(savedProfileRaw);
          setProfile(parsed);
          setLoading(false);
        } else {
          // 初回ユーザーは新規登録画面へ直接リダイレクト
          router.replace('/register');
        }
      } catch (e) {
        console.error('Failed to load profile from AsyncStorage:', e);
        router.replace('/register');
      }
    }
    checkLocalStorage();
  }, []);

  if (loading) {
    return (
      <View style={styles.centerContainer}>
        <ActivityIndicator size="large" color="#C72C48" />
        <Text style={styles.loadingText}>読み込み中...🐾</Text>
      </View>
    );
  }

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.welcomeCard}>
        <Text style={styles.iconBadge}>🐾</Text>
        <Text style={styles.title}>おかえりなさい！</Text>
        <Text style={styles.subtitle}>
          {profile?.owner_name || '飼い主'} 様 ＆ {profile?.name || 'ペット'} ちゃんのお部屋🐾
        </Text>
        
        <TouchableOpacity 
          style={styles.btnRestore}
          onPress={() => router.replace('/login')}
        >
          <Text style={styles.btnRestoreText}>ログインへ 🚀</Text>
        </TouchableOpacity>
      </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#FFFBFB',
    justifyContent: 'center',
    alignItems: 'center',
    padding: 20,
  },
  centerContainer: {
    flex: 1,
    backgroundColor: '#FFFBFB',
    justifyContent: 'center',
    alignItems: 'center',
  },
  loadingText: {
    marginTop: 12,
    color: '#7D6363',
    fontSize: 14,
  },
  welcomeCard: {
    backgroundColor: '#FFF0F2',
    borderWidth: 2,
    borderColor: 'rgba(255, 182, 193, 0.5)',
    borderRadius: 24,
    paddingVertical: 40,
    paddingHorizontal: 24,
    textAlign: 'center',
    shadowColor: 'rgba(255, 128, 150, 0.12)',
    shadowOffset: { width: 0, height: 12 },
    shadowOpacity: 1,
    shadowRadius: 40,
    elevation: 8,
    maxWidth: 480,
    width: '100%',
    alignItems: 'center',
  },
  iconBadge: {
    fontSize: 48,
    marginBottom: 16,
  },
  title: {
    color: '#C72C48',
    fontWeight: 'bold',
    fontSize: 26,
    marginBottom: 8,
    textAlign: 'center',
  },
  subtitle: {
    color: '#3D2D2D',
    fontWeight: '600',
    fontSize: 18,
    marginBottom: 36,
    lineHeight: 26,
    textAlign: 'center',
  },
  btnRestore: {
    paddingVertical: 16,
    paddingHorizontal: 36,
    backgroundColor: '#C72C48',
    borderRadius: 50,
    shadowColor: 'rgba(199, 44, 72, 0.3)',
    shadowOffset: { width: 0, height: 6 },
    shadowOpacity: 1,
    shadowRadius: 20,
    elevation: 6,
    width: '100%',
    alignItems: 'center',
  },
  btnRestoreText: {
    color: '#FFFFFF',
    fontSize: 16,
    fontWeight: 'bold',
  },
});
