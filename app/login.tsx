import React, { useEffect, useState } from 'react';
import { StyleSheet, Text, View, TextInput, TouchableOpacity, Alert, ActivityIndicator } from 'react-native';
import { useRouter } from 'expo-router';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { SafeAreaView } from 'react-native-safe-area-context';

export default function LoginScreen() {
  const router = useRouter();
  const [profile, setProfile] = useState<{ owner_name: string; name: string; pin_code: string } | null>(null);
  const [pinInput, setPinInput] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadProfile() {
      try {
        const savedProfileRaw = await AsyncStorage.getItem('pet_profile');
        if (savedProfileRaw) {
          setProfile(JSON.parse(savedProfileRaw));
        } else {
          router.replace('/register');
        }
      } catch (e) {
        console.error(e);
        router.replace('/register');
      } finally {
        setLoading(false);
      }
    }
    loadProfile();
  }, []);

  const handleLogin = () => {
    if (!profile) return;
    if (pinInput.trim() === profile.pin_code.trim()) {
      Alert.alert('ログイン成功', '🟢 アルバムを開きます🐾', [
        { text: 'OK', onPress: () => router.replace('/album') }
      ]);
    } else {
      Alert.alert('暗証番号エラー', '❌ 暗証番号が正しくありません🐾');
    }
  };

  const handleResetProfile = () => {
    Alert.alert(
      'データの消去と再登録',
      'デバイスに保存されている情報を削除して、新しいペットの登録画面に戻ります。よろしいですか？',
      [
        { text: 'キャンセル', style: 'cancel' },
        { 
          text: '削除してリセット', 
          style: 'destructive',
          onPress: async () => {
            try {
              await AsyncStorage.removeItem('pet_profile');
              await AsyncStorage.removeItem('pet_user_id');
              router.replace('/register');
            } catch (e) {
              console.error(e);
            }
          }
        }
      ]
    );
  };

  if (loading) {
    return (
      <View style={styles.centerContainer}>
        <ActivityIndicator size="large" color="#C72C48" />
        <Text style={styles.loadingText}>読み込み中...</Text>
      </View>
    );
  }

  return (
    <SafeAreaView style={styles.safeContainer}>
      <View style={styles.cardContainer}>
        <View style={styles.cardHeader}>
          <Text style={styles.cardTitle}>🔑 ログイン</Text>
          <Text style={styles.petNames}>
            {profile?.owner_name || '飼い主'} 様 ＆ {profile?.name || 'ペット'} ちゃん
          </Text>
          <Text style={styles.cardSubtitle}>
            登録した4桁の暗証番号 (PIN) を入力してください🔑
          </Text>
        </View>

        <View style={styles.inputGroup}>
          <TextInput
            style={styles.input}
            value={pinInput}
            onChangeText={setPinInput}
            secureTextEntry
            keyboardType="numeric"
            maxLength={4}
            placeholder="4桁の暗証番号 (PIN)"
            placeholderTextColor="#A0A0A0"
            textAlign="center"
          />
        </View>

        <TouchableOpacity style={styles.btnPrimary} onPress={handleLogin}>
          <Text style={styles.btnPrimaryText}>🐾 ログインしてアルバムを開く</Text>
        </TouchableOpacity>

        <View style={styles.divider} />
        
        <TouchableOpacity style={styles.btnReset} onPress={handleResetProfile}>
          <Text style={styles.btnResetText}>🆕 別のペットを登録・ログインする</Text>
        </TouchableOpacity>
      </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safeContainer: {
    flex: 1,
    backgroundColor: '#FFFBFB',
    justifyContent: 'center',
    padding: 16,
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
  cardContainer: {
    backgroundColor: '#FFFBFB',
    borderRadius: 20,
    borderWidth: 1,
    borderColor: 'rgba(255, 182, 193, 0.5)',
    padding: 24,
    shadowColor: 'rgba(255, 128, 150, 0.08)',
    shadowOffset: { width: 0, height: 8 },
    shadowOpacity: 1,
    shadowRadius: 32,
    elevation: 4,
  },
  cardHeader: {
    alignItems: 'center',
    marginBottom: 24,
  },
  cardTitle: {
    color: '#C72C48',
    fontWeight: 'bold',
    fontSize: 24,
    marginBottom: 8,
  },
  petNames: {
    color: '#3D2D2D',
    fontWeight: 'bold',
    fontSize: 18,
    marginBottom: 8,
  },
  cardSubtitle: {
    color: '#7D6363',
    fontSize: 13,
    textAlign: 'center',
  },
  inputGroup: {
    marginBottom: 20,
  },
  input: {
    backgroundColor: '#FFF',
    borderWidth: 1,
    borderColor: '#FFD0D6',
    borderRadius: 12,
    paddingVertical: 14,
    fontSize: 18,
    fontWeight: 'bold',
    color: '#3D2D2D',
    letterSpacing: 8,
  },
  btnPrimary: {
    backgroundColor: '#C72C48',
    paddingVertical: 16,
    borderRadius: 12,
    alignItems: 'center',
    shadowColor: 'rgba(199, 44, 72, 0.3)',
    shadowOffset: { width: 0, height: 6 },
    shadowOpacity: 1,
    shadowRadius: 16,
    elevation: 4,
  },
  btnPrimaryText: {
    color: '#FFF',
    fontWeight: 'bold',
    fontSize: 16,
  },
  divider: {
    height: 1,
    backgroundColor: '#EAEAEA',
    marginVertical: 24,
  },
  btnReset: {
    backgroundColor: '#F5F5F5',
    borderWidth: 1,
    borderColor: '#DDD',
    paddingVertical: 14,
    borderRadius: 12,
    alignItems: 'center',
  },
  btnResetText: {
    color: '#555',
    fontWeight: 'bold',
    fontSize: 14,
  },
});
