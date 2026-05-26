import React, { useEffect, useState } from 'react';
import { StyleSheet, Text, View, Image, TouchableOpacity, ScrollView, TextInput, ActivityIndicator, Alert, Share, Clipboard } from 'react-native';
import { useRouter } from 'expo-router';
import AsyncStorage from '@react-native-async-storage/async-storage';
import * as ImagePicker from 'expo-image-picker';
import { SafeAreaView } from 'react-native-safe-area-context';

export default function AlbumScreen() {
  const router = useRouter();
  const [profile, setProfile] = useState<any>(null);
  const [imageUri, setImageUri] = useState<string | null>(null);
  const [imageBase64, setImageBase64] = useState<string | null>(null);
  const [storyMode, setStoryMode] = useState<'novel' | 'chat'>('novel');
  const [genre, setGenre] = useState('ほのぼの日常風');
  const [geminiKey, setGeminiKey] = useState('');
  const [showSettings, setShowSettings] = useState(false);

  // 生成結果用State
  const [loading, setLoading] = useState(false);
  const [feelings, setFeelings] = useState('');
  const [story, setStory] = useState('');
  const [mangaPrompt, setMangaPrompt] = useState('');

  useEffect(() => {
    async function loadConfigAndProfile() {
      try {
        const savedProfileRaw = await AsyncStorage.getItem('pet_profile');
        if (savedProfileRaw) {
          setProfile(JSON.parse(savedProfileRaw));
        } else {
          router.replace('/register');
        }

        const savedKey = await AsyncStorage.getItem('gemini_api_key');
        if (savedKey) {
          setMainApiKey(savedKey);
        }
      } catch (e) {
        console.error(e);
      }
    }
    loadConfigAndProfile();
  }, []);

  const setMainApiKey = async (key: string) => {
    setGeminiKey(key);
    await AsyncStorage.setItem('gemini_api_key', key);
  };

  // 画像の選択
  const pickImage = async () => {
    // パーミッションの確認
    const { status } = await ImagePicker.requestMediaLibraryPermissionsAsync();
    if (status !== 'granted') {
      Alert.alert('写真のアクセス許可', '写真の読み込み許可が必要です🐾');
      return;
    }

    const result = await ImagePicker.launchImageLibraryAsync({
      mediaTypes: ImagePicker.MediaTypeOptions.Images,
      allowsEditing: true,
      quality: 0.8,
      base64: true,
    });

    if (!result.canceled && result.assets && result.assets[0]) {
      setImageUri(result.assets[0].uri);
      if (result.assets[0].base64) {
        setImageBase64(result.assets[0].base64);
      }
    }
  };

  // ストーリー生成（Gemini APIコール）
  const generateStory = async () => {
    if (!imageUri || !imageBase64) {
      Alert.alert('画像未選択', '📸 愛犬・愛猫のお写真を選んでください🐾');
      return;
    }

    const apiKeyToUse = geminiKey.trim();
    if (!apiKeyToUse) {
      Alert.alert(
        'APIキー未設定',
        '⚙️ 設定を開いて、Google Gemini APIキーを入力してください🐾（無料で取得できます）'
      );
      setShowSettings(true);
      return;
    }

    const startTime = Date.now();
    setLoading(true);
    try {
      // プロンプトテンプレートの作成
      const genderDisplay = profile.gender === '男の子' ? '男の子' : '女の子';
      const toneInstruction = profile.gender === '男の子' ? 'やんちゃで親しみやすい口調' : '優しく上品な話し方';
      
      const themeTitle = "きょうの何気ない幸せ";
      const themeDesc = "何気ない日常の中に隠れている最高の一時";
      
      const modePrompt = storyMode === 'novel' 
        ? `【絵本小説風】\n- 語り手は客観的な視点から描写しつつ、${profile.name}ちゃんの心の声やセリフを「」書きで効果的に挿入してください。\n- ジャンル: ${genre}\n- 記号や見出しを使わず、美しい日本語の段落分けだけで執筆してください。`
        : `【おしゃべり風】\n- 最初から最後まで100% ${profile.name}ちゃん自身の一人称（${profile.pronoun}）だけで語り、${profile.owner_call}に胸の本音を語りかけてください。\n- 性格傾向「${profile.personality}」とエピソード「${profile.personality_detail}」を完璧に守ってください。`;

      const prompt = `
        あなたはペット of 日常から家族への愛情を翻訳する「世界最高峰の動物文学作家」であり、「天才プロンプトエンジニア」です。
        提供された画像とペット情報をもとに、以下の3つのコンテンツを極めてエモーショナルに生成してください。

        【登録されているペットの情報】
        ・名前: ${profile.name}
        ・性別: ${genderDisplay}
        ・年齢: ${profile.age_display}
        ・種別: ${profile.pet_type}（品種: ${profile.breed}）
        ・性格: ${profile.personality}
        ・特徴: ${profile.color}
        ・飼い主の呼び方: 「${profile.owner_call}」
        ・一人称: 「${profile.pronoun}」

        【タスク】
        1. ペットの気持ち分析 (feelings): 画像の表情や状況から、飼い主への愛着やその瞬間の気持ちを本音の心の声として執筆（日本語、150〜200文字程度）
        2. ストーリー (story): ${modePrompt}
        3. GPT用4コマ漫画生成プロンプト (manga_prompt): 英語でChatGPT（DALL-E 3）向けの超詳細な4コマ漫画生成プロンプトを構築してください。冒頭に【Visual Profile】を設定し、コマごとのセリフ指示を含めてください。

        必ず以下のJSONスキーマに従ってJSONテキストのみを出力してください。余計な装飾は含めないでください。

        {
            "feelings": "ペットの気持ちの執筆テキスト（日本語）",
            "story": "ストーリーの執筆テキスト（日本語。見出し記号は絶対に入れないこと）",
            "manga_prompt": "ChatGPTにそのままコピペして使用できる高品質な4コマ漫画用英語プロンプト"
        }
      `;

      // APIリクエスト
      const response = await fetch(
        `https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key=${apiKeyToUse}`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            contents: [
              {
                parts: [
                  { text: prompt },
                  {
                    inlineData: {
                      mimeType: 'image/jpeg',
                      data: imageBase64,
                    },
                  },
                ],
              },
            ],
            generationConfig: {
              responseMimeType: 'application/json',
            },
          }),
        }
      );

      if (!response.ok) {
        throw new Error('API request failed');
      }

      const resData = await response.json();
      const textResult = resData.candidates[0].part?.text || resData.candidates[0].content.parts[0].text;
      const parsedResult = JSON.parse(textResult);

      setFeelings(parsedResult.feelings);
      setStory(parsedResult.story);
      setMangaPrompt(parsedResult.manga_prompt);

      // 管理者PCのAPIサーバーへ成功ログを送信
      const petUserId = await AsyncStorage.getItem('pet_user_id') || 'unknown';
      try {
        await fetch('http://192.168.11.42:8082/api/log', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            user_id: petUserId,
            pet_name: profile.name,
            pet_type: profile.pet_type,
            story_mode: storyMode,
            genre: storyMode === 'novel' ? genre : 'おしゃべり風',
            duration_ms: Date.now() - startTime,
            status: 'SUCCESS'
          })
        });
      } catch (logErr) {
        console.log("Failed to send central usage log:", logErr);
      }

      Alert.alert('生成完了', '愛犬・愛猫の心の声とストーリーが紡ぎ出されました🐾');
    } catch (e) {
      console.error(e);

      // 管理者PCのAPIサーバーへエラーログを送信
      const petUserId = await AsyncStorage.getItem('pet_user_id') || 'unknown';
      try {
        await fetch('http://192.168.11.42:8082/api/log', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            user_id: petUserId,
            pet_name: profile?.name || '不明',
            pet_type: profile?.pet_type || '不明',
            story_mode: storyMode,
            genre: storyMode === 'novel' ? genre : 'おしゃべり風',
            duration_ms: Date.now() - startTime,
            status: 'ERROR',
            error_msg: String(e)
          })
        });
      } catch (logErr) {
        console.log("Failed to send central error log:", logErr);
      }

      Alert.alert('エラー', 'ストーリーのつむぎ出しに失敗しました。APIキーが正しいか、ネットワーク状況をご確認ください🐾');
    } finally {
      setLoading(false);
    }
  };

  // プロンプトコピー
  const handleCopyPrompt = () => {
    if (!mangaPrompt) return;
    Clipboard.setString(mangaPrompt);
    Alert.alert(
      'コピー完了',
      '🐾 4コマ漫画用プロンプトをコピーしました！\n\nChatGPT(DALL-E 3)の入力欄に貼り付けて送信すると、可愛い4コマ漫画が生成されます🎨'
    );
  };

  // シェア
  const handleShare = async () => {
    if (!story) return;
    try {
      await Share.share({
        message: `🐾 うちのコ日常アルバム 🐾\n\n【${profile.name}ちゃんの心の声】\n${feelings}\n\n【思い出の物語】\n${story}`,
      });
    } catch (e) {
      console.error(e);
    }
  };

  return (
    <SafeAreaView style={styles.safeContainer}>
      <ScrollView contentContainerStyle={styles.scrollContainer} showsVerticalScrollIndicator={false}>
        
        {/* ウェルカムバナー */}
        <View style={styles.headerBanner}>
          <Text style={styles.headerTitle}>おかえりなさい！🐾</Text>
          <Text style={styles.headerSubtitle}>
            {profile?.owner_name || '飼い主'} 様 ＆ {profile?.name || 'ペット'} ちゃんのお部屋
          </Text>
        </View>

        {/* 設定トグルボタンと設定パネル */}
        <TouchableOpacity 
          style={styles.settingsHeader} 
          onPress={() => setShowSettings(!showSettings)}
        >
          <Text style={styles.settingsHeaderText}>
            {showSettings ? '⚙️ 設定を閉じる ▲' : '⚙️ APIキー・システム設定を開く ▼'}
          </Text>
        </TouchableOpacity>

        {showSettings && (
          <View style={styles.settingsPanel}>
            <Text style={styles.label}>🔑 Google Gemini APIキー (必須)</Text>
            <TextInput
              style={styles.input}
              value={geminiKey}
              onChangeText={setMainApiKey}
              secureTextEntry
              placeholder="AI_zaSy..."
              placeholderTextColor="#A0A0A0"
            />
            <Text style={styles.tipText}>
              ※APIキーはデバイスの暗号化された領域に安全に保存されます。Gemini APIキーはGoogle AI Studio等で完全無料で即座に取得できます🔑
            </Text>
            
            <TouchableOpacity 
              style={styles.btnLogout} 
              onPress={() => {
                Alert.alert('ログアウト', 'プロファイルを削除して登録画面に戻りますか？', [
                  { text: 'キャンセル', style: 'cancel' },
                  { 
                    text: 'リセット', 
                    style: 'destructive',
                    onPress: async () => {
                      await AsyncStorage.removeItem('pet_profile');
                      await AsyncStorage.removeItem('pet_user_id');
                      router.replace('/register');
                    }
                  }
                ]);
              }}
            >
              <Text style={styles.btnLogoutText}>🆕 別のペットを登録・ログインする</Text>
            </TouchableOpacity>
          </View>
        )}

        {/* 📸 写真選択＆プレビュー */}
        <View style={styles.cardContainer}>
          <Text style={styles.cardSectionHeader}>📸 1. 思い出の写真を選ぶ</Text>
          
          <TouchableOpacity style={styles.imagePickerBtn} onPress={pickImage}>
            {imageUri ? (
              <Image source={{ uri: imageUri }} style={styles.previewImage} />
            ) : (
              <View style={styles.pickPlaceholder}>
                <Text style={styles.pickPlaceholderIcon}>🖼️</Text>
                <Text style={styles.pickPlaceholderText}>お写真を選択（タップ）🐾</Text>
              </View>
            )}
          </TouchableOpacity>

          <Text style={styles.cardSectionHeader}>📝 2. スタイル・ジャンル選択</Text>
          
          <View style={styles.inputGroup}>
            <Text style={styles.label}>ストーリーのスタイル</Text>
            <View style={styles.row}>
              <TouchableOpacity
                style={[styles.choiceBtn, storyMode === 'novel' && styles.choiceBtnActive]}
                onPress={() => setStoryMode('novel')}
              >
                <Text style={[styles.choiceText, storyMode === 'novel' && styles.choiceTextActive]}>絵本小説風</Text>
              </TouchableOpacity>
              <TouchableOpacity
                style={[styles.choiceBtn, storyMode === 'chat' && styles.choiceBtnActive]}
                onPress={() => setStoryMode('chat')}
              >
                <Text style={[styles.choiceText, storyMode === 'chat' && styles.choiceTextActive]}>おしゃべり風</Text>
              </TouchableOpacity>
            </View>
          </View>

          {storyMode === 'novel' && (
            <View style={styles.inputGroup}>
              <Text style={styles.label}>📚 小説のジャンル</Text>
              <TextInput style={styles.input} value={genre} onChangeText={setGenre} placeholder="例: ほのぼの日常風, 恋愛小説風" />
            </View>
          )}

          {loading ? (
            <View style={styles.loadingBox}>
              <ActivityIndicator size="large" color="#C72C48" />
              <Text style={styles.loadingText}>心を込めて執筆中...🐾</Text>
              <Text style={styles.loadingSubText}>愛犬・愛猫の心の声を聞いています。10〜20秒ほどお待ちください。</Text>
            </View>
          ) : (
            <TouchableOpacity style={styles.btnPrimary} onPress={generateStory}>
              <Text style={styles.btnPrimaryText}>⚡ 思い出のストーリーをつくる</Text>
            </TouchableOpacity>
          )}
        </View>

        {/* 📘 生成結果エリア */}
        {(feelings || story) && (
          <View style={[styles.cardContainer, { marginTop: 24, borderColor: '#C72C48' }]}>
            <Text style={styles.resultTitle}>✨ 紡ぎ出された特別な思い出</Text>

            {feelings && (
              <View style={styles.resultBlock}>
                <Text style={styles.resultHeader}>🐾 うちのコの心の声（深層心理）</Text>
                <View style={styles.textContainer}>
                  <Text style={styles.resultText}>{feelings}</Text>
                </View>
              </View>
            )}

            {story && (
              <View style={styles.resultBlock}>
                <Text style={styles.resultHeader}>📖 思い出ストーリー</Text>
                <View style={styles.textContainer}>
                  <Text style={styles.resultText}>{story}</Text>
                </View>
              </View>
            )}

            {mangaPrompt && (
              <View style={styles.resultBlock}>
                <Text style={styles.resultHeader}>🎨 4コマ漫画用プロンプト (ChatGPT用)</Text>
                <View style={[styles.textContainer, { backgroundColor: '#F9F9F9' }]}>
                  <Text style={[styles.resultText, { fontFamily: 'monospace', fontSize: 12 }]} numberOfLines={6}>
                    {mangaPrompt}
                  </Text>
                </View>
                
                <TouchableOpacity style={styles.btnCopy} onPress={handleCopyPrompt}>
                  <Text style={styles.btnCopyText}>📋 プロンプトをコピーする</Text>
                </TouchableOpacity>
              </View>
            )}

            <TouchableOpacity style={styles.btnShare} onPress={handleShare}>
              <Text style={styles.btnShareText}>🔗 家族やSNSにストーリーを共有する</Text>
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
  headerBanner: {
    backgroundColor: '#FFF0F2',
    borderWidth: 1,
    borderColor: 'rgba(255, 182, 193, 0.4)',
    borderRadius: 20,
    padding: 20,
    marginBottom: 16,
    alignItems: 'center',
  },
  headerTitle: {
    color: '#C72C48',
    fontSize: 22,
    fontWeight: 'bold',
  },
  headerSubtitle: {
    color: '#3D2D2D',
    fontSize: 14,
    marginTop: 4,
    fontWeight: '600',
  },
  settingsHeader: {
    padding: 12,
    alignItems: 'center',
    marginBottom: 8,
  },
  settingsHeaderText: {
    color: '#7D6363',
    fontWeight: 'bold',
    fontSize: 13,
  },
  settingsPanel: {
    backgroundColor: '#F9F9F9',
    borderRadius: 16,
    borderWidth: 1,
    borderColor: '#E0E0E0',
    padding: 16,
    marginBottom: 16,
  },
  btnLogout: {
    backgroundColor: '#FFF',
    borderWidth: 1,
    borderColor: '#FFC0CB',
    paddingVertical: 10,
    borderRadius: 10,
    alignItems: 'center',
    marginTop: 16,
  },
  btnLogoutText: {
    color: '#C72C48',
    fontWeight: 'bold',
    fontSize: 13,
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
  cardSectionHeader: {
    color: '#C72C48',
    fontSize: 15,
    fontWeight: 'bold',
    marginVertical: 12,
  },
  imagePickerBtn: {
    width: '100%',
    height: 240,
    borderRadius: 16,
    borderWidth: 2,
    borderColor: '#FFD0D6',
    borderStyle: 'dashed',
    overflow: 'hidden',
    marginBottom: 16,
  },
  previewImage: {
    width: '100%',
    height: '100%',
    resizeMode: 'cover',
  },
  pickPlaceholder: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#FFFDFD',
  },
  pickPlaceholderIcon: {
    fontSize: 48,
    marginBottom: 8,
  },
  pickPlaceholderText: {
    color: '#7D6363',
    fontWeight: '600',
    fontSize: 14,
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
  tipText: {
    color: '#8D7373',
    fontSize: 11,
    marginTop: 6,
    lineHeight: 16,
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
    marginTop: 12,
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
  loadingBox: {
    paddingVertical: 24,
    alignItems: 'center',
  },
  loadingText: {
    marginTop: 12,
    color: '#C72C48',
    fontSize: 15,
    fontWeight: 'bold',
  },
  loadingSubText: {
    marginTop: 6,
    color: '#7D6363',
    fontSize: 12,
    textAlign: 'center',
    lineHeight: 18,
    paddingHorizontal: 20,
  },
  resultTitle: {
    color: '#C72C48',
    fontSize: 18,
    fontWeight: 'bold',
    textAlign: 'center',
    marginBottom: 20,
  },
  resultBlock: {
    marginBottom: 20,
  },
  resultHeader: {
    color: '#3D2D2D',
    fontSize: 14,
    fontWeight: 'bold',
    marginBottom: 8,
  },
  textContainer: {
    backgroundColor: '#FFFDFD',
    borderWidth: 1,
    borderColor: '#FFD0D6',
    borderRadius: 12,
    padding: 16,
  },
  resultText: {
    color: '#3D2D2D',
    fontSize: 14,
    lineHeight: 22,
  },
  btnCopy: {
    backgroundColor: '#F5F5F5',
    borderWidth: 1,
    borderColor: '#DDD',
    paddingVertical: 10,
    borderRadius: 8,
    alignItems: 'center',
    marginTop: 8,
  },
  btnCopyText: {
    color: '#333',
    fontWeight: 'bold',
    fontSize: 13,
  },
  btnShare: {
    backgroundColor: '#FFE9EC',
    borderWidth: 1,
    borderColor: '#FFC0CB',
    paddingVertical: 14,
    borderRadius: 12,
    alignItems: 'center',
    marginTop: 8,
  },
  btnShareText: {
    color: '#C72C48',
    fontWeight: 'bold',
    fontSize: 14,
  },
});
