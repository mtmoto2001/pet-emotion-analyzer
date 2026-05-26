import React, { useState } from 'react';
import { StyleSheet, Text, View, TextInput, TouchableOpacity, ScrollView, Alert } from 'react-native';
import { useRouter } from 'expo-router';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { SafeAreaView } from 'react-native-safe-area-context';

export default function RegisterScreen() {
  const router = useRouter();
  const [pageMode, setPageMode] = useState<'register' | 'restore'>('register');

  // 新規登録フォーム用State
  const [ownerName, setOwnerName] = useState('');
  const [pinCode, setPinCode] = useState('');
  const [petName, setPetName] = useState('ベル');
  const [petType, setPetType] = useState<'犬' | '猫'>('犬');
  const [breed, setBreed] = useState('ミニチュアダックスフンド');
  const [color, setColor] = useState('レッド');
  const [gender, setGender] = useState<'男の子' | '女の子'>('女の子');
  const [pronoun, setPronoun] = useState('わたし');
  const [birthYear, setBirthYear] = useState('2023');
  const [birthMonth, setBirthMonth] = useState('1');
  const [personality, setPersonality] = useState('元気いっぱいでやんちゃ');
  const [personalityDetail, setPersonalityDetail] = useState('お気に入りのおもちゃをくわえて、得意げに部屋中を走り回っていたこと。');
  const [ownerCall, setOwnerCall] = useState('パパ');

  // データ復元用State
  const [restoreName, setRestoreName] = useState('');
  const [restorePin, setRestorePin] = useState('');

  // 新規登録処理
  const handleRegister = async () => {
    const oName = ownerName.trim();
    const pin = pinCode.trim();

    if (!oName) {
      Alert.alert('入力エラー', '⚠️ 飼い主のおなまえを入力してください🐾');
      return;
    }
    if (!pin || pin.length !== 4 || isNaN(Number(pin))) {
      Alert.alert('入力エラー', '⚠️ 暗証番号は4桁の数字を入力してください🐾');
      return;
    }

    try {
      // 年齢の自動計算
      const currentYear = 2026;
      const currentMonth = 5;
      const totalMonths = (currentYear - Number(birthYear)) * 12 + currentMonth - Number(birthMonth);
      let ageDisplay = '';
      if (totalMonths < 0) ageDisplay = '生後0ヶ月';
      else if (totalMonths < 12) ageDisplay = `子犬/子猫期（生後 ${totalMonths} ヶ月）`;
      else ageDisplay = `成犬/成猫期（ ${Math.floor(totalMonths / 12)} 歳 ${totalMonths % 12} ヶ月）`;

      const profileData = {
        owner_name: oName,
        pin_code: pin,
        name: petName,
        pet_type: petType,
        breed,
        color,
        gender,
        pronoun,
        birth_y: birthYear,
        birth_m: birthMonth,
        personality,
        personality_detail: personalityDetail,
        owner_call: ownerCall,
        age_display: ageDisplay
      };

      // 安定ハッシュIDの生成
      let hash = 0;
      const str = oName + pin;
      for (let i = 0; i < str.length; i++) {
        hash = (hash << 5) - hash + str.charCodeAt(i);
        hash |= 0;
      }
      const registeredUserId = 'user_' + Math.abs(hash).toString(36).substring(0, 8);

      // 管理者PCのAPIサーバーへプロファイルを同期保存
      try {
        await fetch('http://192.168.11.42:8082/api/profile', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            user_id: registeredUserId,
            profile: profileData
          })
        });
      } catch (postErr) {
        console.log("Failed to sync profile to central server:", postErr);
      }

      // AsyncStorageに保存
      await AsyncStorage.setItem('pet_profile', JSON.stringify(profileData));
      await AsyncStorage.setItem('pet_user_id', registeredUserId);

      Alert.alert('登録完了', 'ペットの登録が完了しました🐾', [
        { text: 'OK', onPress: () => router.replace('/album') }
      ]);
    } catch (e) {
      console.error(e);
      Alert.alert('エラー', '登録処理中にエラーが発生しました🐾');
    }
  };

  // 以前のデータ復元処理
  const handleRestore = async () => {
    const oName = restoreName.trim();
    const pin = restorePin.trim();

    if (!oName) {
      Alert.alert('入力エラー', '⚠️ お名前を入力してください🐾');
      return;
    }
    if (!pin || pin.length !== 4) {
      Alert.alert('入力エラー', '⚠️ 暗証番号は4桁の数字を入力してください🐾');
      return;
    }

    try {
      // 登録時と同じIDを生成
      let hash = 0;
      const str = oName + pin;
      for (let i = 0; i < str.length; i++) {
        hash = (hash << 5) - hash + str.charCodeAt(i);
        hash |= 0;
      }
      const loginUserId = 'user_' + Math.abs(hash).toString(36).substring(0, 8);

      // 管理者PCのAPIサーバーからデータを検索・復元
      let restoredProfile = null;
      try {
        const response = await fetch(`http://192.168.11.42:8082/api/profile/${loginUserId}`);
        if (response.ok) {
          restoredProfile = await response.json();
        }
      } catch (fetchErr) {
        console.log("Failed to fetch profile from central server:", fetchErr);
      }

      if (!restoredProfile) {
        Alert.alert('復元失敗', '⚠️ 指定されたお名前と暗証番号に一致する登録データが管理者PC内に見つかりません🐾');
        return;
      }

      await AsyncStorage.setItem('pet_profile', JSON.stringify(restoredProfile));
      await AsyncStorage.setItem('pet_user_id', loginUserId);

      Alert.alert('復元完了', '以前のデータを復元しログインしました🐾', [
        { text: 'OK', onPress: () => router.replace('/album') }
      ]);
    } catch (e) {
      console.error(e);
      Alert.alert('エラー', '復元処理中にエラーが発生しました🐾');
    }
  };

  return (
    <SafeAreaView style={styles.safeContainer}>
      <ScrollView contentContainerStyle={styles.scrollContainer} showsVerticalScrollIndicator={false}>
        {pageMode === 'restore' ? (
          // --- データ復元 ログイン画面 ---
          <View style={styles.cardContainer}>
            <View style={styles.cardHeader}>
              <Text style={styles.cardTitle}>🔑 データ復元 ログイン</Text>
              <Text style={styles.cardSubtitle}>以前登録したお名前と暗証番号からデータを完全に復元します🐾</Text>
            </View>

            <View style={styles.inputGroup}>
              <Text style={styles.label}>👤 飼い主のおなまえ</Text>
              <TextInput
                style={styles.input}
                value={restoreName}
                onChangeText={setRestoreName}
                placeholder="例: 佐藤美咲"
                placeholderTextColor="#A0A0A0"
              />
            </View>

            <View style={styles.inputGroup}>
              <Text style={styles.label}>🔑 4桁の暗証番号 (PIN)</Text>
              <TextInput
                style={styles.input}
                value={restorePin}
                onChangeText={setRestorePin}
                secureTextEntry
                keyboardType="numeric"
                maxLength={4}
                placeholder="例: 1234"
                placeholderTextColor="#A0A0A0"
              />
            </View>

            <TouchableOpacity style={styles.btnPrimary} onPress={handleRestore}>
              <Text style={styles.btnPrimaryText}>🔑 ログインしてデータを復元する</Text>
            </TouchableOpacity>

            <View style={styles.divider} />
            <TouchableOpacity style={styles.btnSecondary} onPress={() => setPageMode('register')}>
              <Text style={styles.btnSecondaryText}>👋 新規登録に戻る</Text>
            </TouchableOpacity>
          </View>
        ) : (
          // --- はじめてのペット登録画面 ---
          <View style={styles.cardContainer}>
            <View style={styles.cardHeader}>
              <Text style={styles.cardTitle}>🐾 👋 はじめてのペット登録</Text>
              <Text style={styles.cardSubtitle}>愛するうちのコの基本設定を行って、アルバムを開始しましょう🐾</Text>
            </View>

            <Text style={styles.sectionHeader}>👤 1. 飼い主さまとログイン設定 (必須)</Text>
            <View style={styles.inputGroup}>
              <Text style={styles.label}>飼い主のおなまえ</Text>
              <TextInput
                style={styles.input}
                value={ownerName}
                onChangeText={setOwnerName}
                placeholder="例: 佐藤美咲"
                placeholderTextColor="#A0A0A0"
              />
            </View>
            <View style={styles.inputGroup}>
              <Text style={styles.label}>4桁の暗証番号 (例: 1234)</Text>
              <TextInput
                style={styles.input}
                value={pinCode}
                onChangeText={setPinCode}
                secureTextEntry
                keyboardType="numeric"
                maxLength={4}
                placeholder="1234"
                placeholderTextColor="#A0A0A0"
              />
            </View>

            <Text style={styles.sectionHeader}>🐶 2. うちのコの情報</Text>
            <View style={styles.inputGroup}>
              <Text style={styles.label}>ペットの名前</Text>
              <TextInput style={styles.input} value={petName} onChangeText={setPetName} />
            </View>

            <View style={styles.inputGroup}>
              <Text style={styles.label}>動物の種別</Text>
              <View style={styles.row}>
                <TouchableOpacity
                  style={[styles.choiceBtn, petType === '犬' && styles.choiceBtnActive]}
                  onPress={() => setPetType('犬')}
                >
                  <Text style={[styles.choiceText, petType === '犬' && styles.choiceTextActive]}>犬</Text>
                </TouchableOpacity>
                <TouchableOpacity
                  style={[styles.choiceBtn, petType === '猫' && styles.choiceBtnActive]}
                  onPress={() => setPetType('猫')}
                >
                  <Text style={[styles.choiceText, petType === '猫' && styles.choiceTextActive]}>猫</Text>
                </TouchableOpacity>
              </View>
            </View>

            <View style={styles.inputGroup}>
              <Text style={styles.label}>犬種・猫種</Text>
              <TextInput style={styles.input} value={breed} onChangeText={setBreed} />
            </View>

            <View style={styles.inputGroup}>
              <Text style={styles.label}>毛色・特徴</Text>
              <TextInput style={styles.input} value={color} onChangeText={setColor} />
            </View>

            <View style={styles.inputGroup}>
              <Text style={styles.label}>性別</Text>
              <View style={styles.row}>
                <TouchableOpacity
                  style={[styles.choiceBtn, gender === '男の子' && styles.choiceBtnActive]}
                  onPress={() => {
                    setGender('男の子');
                    setPronoun('ボク');
                  }}
                >
                  <Text style={[styles.choiceText, gender === '男の子' && styles.choiceTextActive]}>男の子</Text>
                </TouchableOpacity>
                <TouchableOpacity
                  style={[styles.choiceBtn, gender === '女の子' && styles.choiceBtnActive]}
                  onPress={() => {
                    setGender('女の子');
                    setPronoun('わたし');
                  }}
                >
                  <Text style={[styles.choiceText, gender === '女の子' && styles.choiceTextActive]}>女の子</Text>
                </TouchableOpacity>
              </View>
            </View>

            <View style={styles.inputGroup}>
              <Text style={styles.label}>うちのコの一人称</Text>
              <TextInput style={styles.input} value={pronoun} onChangeText={setPronoun} placeholder="ボク, わたし, あたし など" />
            </View>

            <View style={styles.inputGroup}>
              <Text style={styles.label}>飼い主さんの呼び方</Text>
              <TextInput style={styles.input} value={ownerCall} onChangeText={setOwnerCall} placeholder="パパ, ママ, お姉ちゃん など" />
            </View>

            <View style={styles.row}>
              <View style={[styles.inputGroup, { flex: 1, marginRight: 8 }]}>
                <Text style={styles.label}>誕生年</Text>
                <TextInput style={styles.input} value={birthYear} onChangeText={setBirthYear} keyboardType="numeric" />
              </View>
              <View style={[styles.inputGroup, { flex: 1 }]}>
                <Text style={styles.label}>誕生月</Text>
                <TextInput style={styles.input} value={birthMonth} onChangeText={setBirthMonth} keyboardType="numeric" />
              </View>
            </View>

            <View style={styles.inputGroup}>
              <Text style={styles.label}>性格傾向</Text>
              <TextInput style={styles.input} value={personality} onChangeText={setPersonality} />
            </View>

            <View style={styles.inputGroup}>
              <Text style={styles.label}>具体的なエピソード</Text>
              <TextInput
                style={[styles.input, styles.textArea]}
                value={personalityDetail}
                onChangeText={setPersonalityDetail}
                multiline
                numberOfLines={3}
              />
            </View>

            <TouchableOpacity style={styles.btnPrimary} onPress={handleRegister}>
              <Text style={styles.btnPrimaryText}>💾 この内容で登録する</Text>
            </TouchableOpacity>

            <View style={styles.divider} />
            <Text style={styles.bottomTip}>💡 すでに以前ペットを登録したデータをお持ちですか？</Text>
            <TouchableOpacity style={styles.btnSecondary} onPress={() => setPageMode('restore')}>
              <Text style={styles.btnSecondaryText}>🔑 登録済みデータから復元・ログインする</Text>
            </TouchableOpacity>
          </View>
        )}
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safeContainer: {
    flex: 1,
    backgroundColor: '#FFFBFB',
  },
  scrollContainer: {
    padding: 16,
    paddingBottom: 40,
  },
  cardContainer: {
    backgroundColor: '#FFFBFB',
    borderRadius: 20,
    borderWidth: 1,
    borderColor: 'rgba(255, 182, 193, 0.4)',
    padding: 20,
    shadowColor: 'rgba(255, 128, 150, 0.08)',
    shadowOffset: { width: 0, height: 8 },
    shadowOpacity: 1,
    shadowRadius: 32,
    elevation: 4,
  },
  cardHeader: {
    backgroundColor: '#FFF0F2',
    borderRadius: 16,
    borderWidth: 1,
    borderColor: 'rgba(255, 182, 193, 0.4)',
    padding: 16,
    marginBottom: 20,
    alignItems: 'center',
  },
  cardTitle: {
    color: '#C72C48',
    fontWeight: 'bold',
    fontSize: 20,
    textAlign: 'center',
  },
  cardSubtitle: {
    color: '#7D6363',
    fontSize: 13,
    marginTop: 6,
    textAlign: 'center',
    lineHeight: 18,
  },
  sectionHeader: {
    color: '#C72C48',
    fontSize: 15,
    fontWeight: 'bold',
    marginVertical: 12,
  },
  inputGroup: {
    marginBottom: 16,
  },
  label: {
    color: '#555',
    fontSize: 13,
    fontWeight: 'bold',
    marginBottom: 6,
  },
  input: {
    backgroundColor: '#FFF',
    borderWidth: 1,
    borderColor: '#FFD0D6',
    borderRadius: 12,
    paddingVertical: 12,
    paddingHorizontal: 16,
    color: '#3D2D2D',
    fontSize: 15,
  },
  textArea: {
    height: 80,
    textAlignVertical: 'top',
  },
  row: {
    flexDirection: 'row',
  },
  choiceBtn: {
    flex: 1,
    backgroundColor: '#FFF',
    borderWidth: 1,
    borderColor: '#FFD0D6',
    borderRadius: 12,
    paddingVertical: 12,
    alignItems: 'center',
    marginRight: 8,
  },
  choiceBtnActive: {
    backgroundColor: '#C72C48',
    borderColor: '#C72C48',
  },
  choiceText: {
    color: '#7D6363',
    fontWeight: 'bold',
  },
  choiceTextActive: {
    color: '#FFF',
  },
  btnPrimary: {
    backgroundColor: '#C72C48',
    paddingVertical: 16,
    borderRadius: 12,
    alignItems: 'center',
    marginTop: 20,
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
  btnSecondary: {
    backgroundColor: '#F5F5F5',
    borderWidth: 1,
    borderColor: '#DDD',
    paddingVertical: 14,
    borderRadius: 12,
    alignItems: 'center',
    marginTop: 10,
  },
  btnSecondaryText: {
    color: '#555',
    fontWeight: 'bold',
    fontSize: 14,
  },
  divider: {
    height: 1,
    backgroundColor: '#EAEAEA',
    marginVertical: 24,
  },
  bottomTip: {
    color: '#7D6363',
    fontSize: 13,
    textAlign: 'center',
    marginBottom: 8,
  },
});
