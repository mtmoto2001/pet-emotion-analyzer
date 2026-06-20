import React, { useEffect, useState } from 'react';
import { StyleSheet, Text, View, Image, TouchableOpacity, ScrollView, TextInput, ActivityIndicator, Alert, Share, Clipboard, Linking } from 'react-native';
import { useRouter } from 'expo-router';
import AsyncStorage from '@react-native-async-storage/async-storage';
import * as ImagePicker from 'expo-image-picker';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Video, ResizeMode } from 'expo-av';
import * as ImageManipulator from 'expo-image-manipulator';

export default function AlbumScreen() {
  const router = useRouter();
  const [profile, setProfile] = useState<any>(null);
  const [imageUri, setImageUri] = useState<string | null>(null);
  const [imageBase64, setImageBase64] = useState<string | null>(null);
  const [storyMode, setStoryMode] = useState<'novel' | 'chat'>('novel');
  const [genre, setGenre] = useState('ほのぼの日常風');
  const [proxyUrl, setProxyUrl] = useState('https://script.google.com/macros/s/AKfycby_yneEPDfmGGpGrZwCgEWt3KIQxZ_5V5LgX_8z9ItloS_Pg0p-SxsAqBW0OFdWa_WFog/exec');
  const [mockMode, setMockMode] = useState(false);

  // 生成結果用State
  const [loading, setLoading] = useState(false);
  const [feelings, setFeelings] = useState('');
  const [story, setStory] = useState('');
  const [mangaPrompt, setMangaPrompt] = useState('');
  const [videoPrompt, setVideoPrompt] = useState('');

  useEffect(() => {
    async function loadConfigAndProfile() {
      try {
        const savedProfileRaw = await AsyncStorage.getItem('pet_profile');
        let parsedProfile = null;
        if (savedProfileRaw) {
          parsedProfile = JSON.parse(savedProfileRaw);
          setProfile(parsedProfile);
        } else {
          router.replace('/register');
          return;
        }

        // ストーリーのスタイルと小説ジャンルの復元
        const savedStoryMode = await AsyncStorage.getItem('pet_story_mode');
        if (savedStoryMode) {
          setStoryMode(savedStoryMode as 'novel' | 'chat');
        }

        const savedGenre = await AsyncStorage.getItem('pet_story_genre');
        if (savedGenre) {
          setGenre(savedGenre);
        }

        // モックモードの読み込み
        const savedMockMode = await AsyncStorage.getItem('mock_mode');
        if (savedMockMode) {
          setMockMode(savedMockMode === 'true');
        }

        // ★ 既存のスマホ内データをPC管理ダッシュボードへ起動時に一括自動同期 ★
        const savedUserId = await AsyncStorage.getItem('pet_user_id');
        const savedHistoryRaw = await AsyncStorage.getItem('pet_history_items');
        let parsedHistory = [];
        if (savedHistoryRaw) {
          parsedHistory = JSON.parse(savedHistoryRaw);
        }

        if (savedUserId && parsedProfile) {
          try {
            // プロフィールの自動同期
            fetch(proxyUrl, {
              method: 'POST',
              headers: {
                'Content-Type': 'application/json',
              },
              body: JSON.stringify({
                action: 'save_profile',
                user_id: savedUserId,
                profile: parsedProfile
              }),
            }).catch(() => {});

            // 過去に思い出を生成した履歴が1枚以上あれば、ダッシュボードの統計に1発自動送信してマージ
            if (parsedHistory.length > 0) {
              fetch(proxyUrl, {
                method: 'POST',
                headers: {
                  'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                  action: 'log_usage',
                  user_id: savedUserId,
                  pet_name: parsedProfile.name,
                  pet_type: parsedProfile.pet_type,
                  story_mode: savedStoryMode || 'novel',
                  genre: savedGenre || 'ほのぼの日常風',
                  duration_ms: 1800,
                  status: 'SUCCESS'
                }),
              }).catch(() => {});
            }
          } catch (syncErr) {
            console.warn('DB同期連携スキップ:', syncErr);
          }
        }
      } catch (e) {
        console.error(e);
      }
    }
    loadConfigAndProfile();
  }, []);

  const handleSaveStoryMode = async (mode: 'novel' | 'chat') => {
    setStoryMode(mode);
    await AsyncStorage.setItem('pet_story_mode', mode);
  };

  const handleSaveGenre = async (text: string) => {
    setGenre(text);
    await AsyncStorage.setItem('pet_story_genre', text);
  };

  // 画像の選択（かつサイズ圧縮）
  const pickImage = async () => {
    const { status } = await ImagePicker.requestMediaLibraryPermissionsAsync();
    if (status !== 'granted') {
      Alert.alert('写真のアクセス許可', '写真の読み込み許可が必要です🐾');
      return;
    }

    const result = await ImagePicker.launchImageLibraryAsync({
      mediaTypes: ['images'],
      allowsEditing: true,
      quality: 0.8,
    });

    if (!result.canceled && result.assets && result.assets[0]) {
      const selectedUri = result.assets[0].uri;
      setImageUri(selectedUri);
      
      // 画像圧縮処理を追加（Gemini APIへの転送速度向上）
      try {
        const manipResult = await ImageManipulator.manipulateAsync(
          selectedUri,
          [{ resize: { width: 800 } }], // 横幅800pxに縮小
          { compress: 0.7, format: ImageManipulator.SaveFormat.JPEG, base64: true }
        );
        if (manipResult.base64) {
          setImageBase64(manipResult.base64);
        }
      } catch (err) {
        console.error('画像圧縮エラー:', err);
      }
    }
  };

  // ストーリー生成
  const generateStory = async () => {
    if (!imageUri || !imageBase64) {
      Alert.alert('画像未選択', '📸 愛犬・愛猫のお写真を選んでください🐾');
      return;
    }
    const startTime = Date.now();
    const profileUserId = await AsyncStorage.getItem('pet_user_id') || 'unknown';

    // Mock Mode Check
    if (mockMode) {
      setLoading(true);
      setTimeout(async () => {
        const mockFeelings = `【テスト分析】${profile?.name || 'うちのコ'}ちゃんは、あなたが左手に持っているおもちゃの「かすかな摩擦音」を耳をピクッとさせて聞きつけています。ただ喜んでいるのではなく、『これはいつものおやつが入る袋の音とは異なるが、間違いなく私の知的好奇心を刺激する音だ』と、瞳を輝かせて物理的解析を試みている真っ最中なのです🐾`;
        const mockStory = `【テストストーリー】いつも優しい${profile?.owner_call || 'パパ'}へ🐾\n\nねえねえ、その手に持っているもの、なあに？カサカサって音がしたの、${profile?.pronoun || 'ボク'}ちゃんと聞き逃さなかったよ！おやつかな？それとも新しいおもちゃかな？\n好奇心で胸がいっぱいになって、思わずおめめがキラキラしちゃうんだ。何であれ、${profile?.owner_call || 'パパ'}が${profile?.pronoun || 'ボク'}ちゃんのために用意してくれた時間なら、それだけで世界一幸せな瞬間なんだよ🐾`;
        const mockManga = `Visual Profile: A lovely ${profile?.breed || 'dog'} with ${profile?.color || 'golden'} hair, wearing a cute pink collar. Looking intensely at the owner's hand with sparkling eyes.\n\n4-panel manga layout in a soft watercolor style:\nPanel 1: The pet sits on the rug, tilting its head as it hears a rustling sound.\nPanel 2: Close up on the pet's sparkling eyes and perked up ears, showing high curiosity. Include a speech bubble in Japanese saying "なんの音？🐾"\nPanel 3: The owner reveals a small new squeaky toy. The pet gets excited.\nPanel 4: The pet is happily playing with the toy next to the owner's legs. Speech bubble in Japanese: "${profile?.owner_call || 'パパ'}、大好き！🐾"`;
        const mockVideo = `A cinematic close-up video of a cute ${profile?.breed || 'dog'}, breathing softly and wagging its tail, looking with sparkling eyes at the owner. Soft warm sunbeams lighting, extremely natural motion, 4k resolution.`;

        setFeelings(mockFeelings);
        setStory(mockStory);
        setMangaPrompt(mockManga);
        setVideoPrompt(mockVideo);

        // Save history item in mock mode
        try {
          const savedHistoryRaw = await AsyncStorage.getItem('pet_history_items');
          const currentHistory = savedHistoryRaw ? JSON.parse(savedHistoryRaw) : [];
          const newHistoryItem = {
            id: Date.now().toString(),
            date: new Date().toLocaleDateString('ja-JP', { year: 'numeric', month: 'long', day: 'numeric' }),
            imageUri: imageUri,
            feelings: mockFeelings,
            story: mockStory,
            manga_prompt: mockManga,
            video_prompt: mockVideo,
          };
          currentHistory.unshift(newHistoryItem);
          if (currentHistory.length > 10) {
            currentHistory.pop();
          }
          await AsyncStorage.setItem('pet_history_items', JSON.stringify(currentHistory));
          await AsyncStorage.removeItem('generated_newspaper'); // clear cache
        } catch (hErr) {
          console.error('履歴保存エラー:', hErr);
        }

        setLoading(false);
        Alert.alert('テスト生成完了', 'テスト用モックモードでのストーリー作成に成功しました！🐾');
      }, 1500);
      return;
    }

    setLoading(true);
    try {
      const genderDisplay = profile.gender === '男の子' ? '男の子' : '女の子';
      const modePrompt = storyMode === 'novel' 
        ? `【絵本小説風】\n- 語り手は客観的な視点から描写しつつ、${profile.name}ちゃんの心の声やセリフを「」書きで効果的に挿入してください。\n- ジャンル: ${genre}\n- 記号や見出しを使わず、美しい日本語の段落分けだけで執筆してください。`
        : `【おしゃべり風】\n- 最初から最後まで100% ${profile.name}ちゃん自身の一人称（${profile.pronoun}）だけで語り、${profile.owner_call}に胸の本音を語りかけてください。\n- 性格傾向「${profile.personality}」とエピソード「${profile.personality_detail}」を完璧に守ってください。`;

      const prompt = `
        あなたはペットの表情や周囲の状況から深層心理を120%読み解く「世界最高峰の動物感情翻訳家」であり、その本音をもとに珠玉の物語を紡ぐ「天才文学作家」です。
        提供された画像とペット情報をもとに、以下の4つのコンテンツを極めてエモーショナルに生成してください。

        【最重要・思考プロセスと執筆の鉄則（必ずこの順番で思考し、出力に反映してください）】
        1. **視覚的特徴の超ディープな観察と感情分析**:
           - 画像に写っている${profile.name}ちゃんの「視線の向き」「耳の角度」「口元の緊張・弛緩や舌の状態」「尻尾の位置・ニュアンス」「姿勢（甘え、伏せ、探索、興奮など）」「背景にあるおもちゃやカーペット, 家具などのオブジェクト」を徹底的に読み取ってください。
        2. **独自の心の声 (feelings) の抽出**:
           - 上記で分析した具体的かつユニークな視覚的特徴（ディテール）とペット情報（性格等）のみをもとに、${profile.name}ちゃんの【本当の深層心理】を抽出します。
           - ※※最重要※※ 思い出ストーリー（story）で創作・脚色されるドラマチックな展開やフィクションの内容に【絶対に引っ張られることなく】、あくまで登録されているペット情報（性格など）と写真のペットの状況（客観的な表情・姿勢）だけを冷静に分析・ブレンドし、その瞬間にペットが感じていた本当の深層心理・本音の心の声を出力してください。
           - 「嬉しい」「眠い」「遊んで」などの単純で安直な一般化分類は【絶対に禁止】します。それをしてしまうと、毎回似たような心の声になってしまい飼い主様が飽きてしまいます。
           - 例：「${profile.owner_call}がスマホを構える瞬間の手の動きから、これが特別な撮影だと理解し張りてポーズを作っている知性」「ラグの特定の繊維の匂いから独自の宇宙を感じ取っている超ディープな探索心」など、その写真特有の具体的かつリアルな心の声（日本語、150〜200文字）にしてください。
        3. **心の声をベースにした新鮮なストーリー (story) の構築**:
           - 上記でディープに分析した「心の声」と「基本情報」を入力とし、それをさらに膨らませた思い出ストーリーを執筆します。
           - 「ある晴れた日の午後、${profile.name}ちゃんはおやつをもらって喜びました」といった、使い回しのテンプレート的な展開は【完全厳禁】です。
           - ある時は${profile.name}ちゃんが熱い情熱を語りかけるドラマ風、ある時は飼い主の行動パターンを冷静に分析する探偵小説風など、今回の「心の声」に最も合致するユニークな文体・切り口を毎回完全にゼロから新規に考案して執筆してください。作成するたびに「ああ、こう思っていたのかー！」と新しい発見と驚きを飼い主様に提供してください。
        4. **ト書きの排除**:
           - カッコ書きによる自分の物理的動作描写（「（しっぽをパタパタさせながら）」等）は【絶対に一切出力しないでください】。

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
        1. ペットの気持ち分析 (feelings): 上記の鉄則に従い、思い出ストーリーの創作的な脚色や展開に【絶対に引っ張られることなく】、写真特有の視覚的ディテールとペット情報（性格など）のみからディープに読み解いた、その瞬間における本当の深層心理（本音の心の声）を執筆（日本語、150〜200文字程度）
        2. ストーリー (story): 上記の鉄則に従い、ユニークに抽出された「心の声」に100%基づいた、毎回全く異なる新鮮で感動的（またはコミカル）な思い出ストーリー。 ${modePrompt}（日本語、250〜350文字程度）
        3. GPT用4コマ漫画生成プロンプト (manga_prompt): ChatGPT（DALL-E 3）向けの超詳細な4コマ漫画生成プロンプトを構築してください。
           - ※※最重要※※ 4コマ漫画は、アップロードされた写真の状況をそのままなぞったり模写したりするのではなく、作成した【思い出ストーリー (story) の内容と流れ】を最重視し、そのストーリーに基づいた『起・承・転・結』のドラマチックな展開を4コマ（Panel 1〜4）で美しく表現する構成にしてください。場面設定や描写は、写真の単純なコピーではなく、ストーリーの展開に沿ってよりドラマチックで豊かなビジュアル表現になるよう、各コマの状況を工夫して詳細に指示してください。
           - プロンプト記述自体は英語で構築しますが、吹き出し（speech bubbles / text labels）内のセリフは絶対に英語に翻訳せず、ペットの一人称や口調を忠実に反映した【日本語のテキスト（例: "ひらがな・漢字のセリフ"）】のまま指定するように強く指示してください。冒頭に【Visual Profile】を設定し、コマごとのセリフ指示を含めてください。
        4. 最先端動画生成AI用プロンプト (video_prompt): Luma Dream MachineやRunway Gen-3などの最先端動画生成AIに入力し、この思い出の一瞬が「本物の魔法のように美しく滑らかに動き出す」ための英語プロンプトを生成してください。ペットの品種（${profile.breed}）、特徴・毛色（${profile.color}）、および送られた画像のシチュエーションを踏まえ、カメラワーク（slow pan, zoom inなど）、光の表現（warm cinematic lighting, soft sunbeams）、リアルで滑らかな物理的挙動（wagging tail, breathing softly, blinking eyes, extremely natural pet motion）を盛り込み、4秒〜5秒の高品質でシネマティックな実写/3D風動画になる詳細プロンプトにしてください。文字数は50〜80単語程度。

        必ず以下のJSONスキーマに従ってJSONテキストのみを出力してください。余計な装飾は含めないでください。

        {
            "feelings": "ペットの気持ちの執筆テキスト（日本語）",
            "story": "ストーリーの執筆テキスト（日本語。見出し記号は絶対に入れないこと）",
            "manga_prompt": "ChatGPTにそのままコピペして使用できる、吹き出しのセリフが日本語で指定された高品質な4コマ漫画用プロ仕様英語プロンプト",
            "video_prompt": "動画生成AIにそのまま貼り付けて、この思い出の一瞬を完璧に動かせる高品質な英語動画プロンプト"
        }
      `;

      // GASのCORSプレフライトエラー(OPTIONSブロック)を完全に回避するため、Content-Typeをtext/plainに設定
      const response = await fetch(proxyUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'text/plain',
        },
        body: JSON.stringify({
          prompt: prompt,
          imageBase64: imageBase64,
        }),
      });

      if (!response.ok) {
        const errData = await response.json().catch(() => ({}));
        throw new Error(errData.error || '中継サーバーとの通信に失敗しました🐾');
      }

      const resData = await response.json();
      if (resData.error) {
        throw new Error(resData.error);
      }
      const textResult = resData.candidates?.[0]?.content?.parts?.[0]?.text || 
                         resData.candidates?.[0]?.part?.text;

      if (!textResult) {
        throw new Error('AIからの応答テキストが空でした🐾');
      }

      // JSONのマークダウン囲みや前後の余分なテキストを完全に除去し、最初の「{」から最後の「}」までを安全に抽出
      let cleanedText = textResult.trim();
      const jsonMatch = cleanedText.match(/\{[\s\S]*\}/);
      if (jsonMatch) {
        cleanedText = jsonMatch[0];
      }

      // JSON文字列内の不正な改行やタブのエスケープ処理
      let sanitized = '';
      let inString = false;
      let escapeNext = false;
      for (let i = 0; i < cleanedText.length; i++) {
        const char = cleanedText[i];
        if (escapeNext) {
          sanitized += char;
          escapeNext = false;
        } else if (char === '\\') {
          sanitized += char;
          escapeNext = true;
        } else if (char === '"') {
          sanitized += char;
          inString = !inString;
        } else if (inString && char === '\n') {
          sanitized += '\\n';
        } else if (inString && char === '\r') {
          sanitized += '\\r';
        } else if (inString && char === '\t') {
          sanitized += '\\t';
        } else {
          sanitized += char;
        }
      }
      cleanedText = sanitized;

      const parsedResult = JSON.parse(cleanedText);

      const resFeelings = parsedResult.feelings || '';
      const resStory = parsedResult.story || '';
      const resManga = parsedResult.manga_prompt || '';
      const resVideo = parsedResult.video_prompt || '';

      setFeelings(resFeelings);
      setStory(resStory);
      setMangaPrompt(resManga);
      setVideoPrompt(resVideo);

      // 思い出履歴の永続化保存
      try {
        const savedHistoryRaw = await AsyncStorage.getItem('pet_history_items');
        const currentHistory = savedHistoryRaw ? JSON.parse(savedHistoryRaw) : [];
        const newHistoryItem = {
          id: Date.now().toString(),
          date: new Date().toLocaleDateString('ja-JP', { year: 'numeric', month: 'long', day: 'numeric' }),
          imageUri: imageUri,
          feelings: resFeelings,
          story: resStory,
          manga_prompt: resManga,
          video_prompt: resVideo,
        };
        currentHistory.unshift(newHistoryItem);
        if (currentHistory.length > 10) {
          currentHistory.pop();
        }
        await AsyncStorage.setItem('pet_history_items', JSON.stringify(currentHistory));
        await AsyncStorage.removeItem('generated_newspaper'); // clear cache
      } catch (hErr) {
        console.error('履歴保存エラー:', hErr);
      }

      // ★ スプレッドシートDBへのログ同期 ★
      try {
        const duration = Date.now() - startTime;
        fetch(proxyUrl, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            action: 'log_usage',
            user_id: profileUserId,
            pet_name: profile.name,
            pet_type: profile.pet_type,
            story_mode: storyMode,
            genre: storyMode === 'novel' ? genre : 'おしゃべり風',
            duration_ms: duration,
            status: 'SUCCESS'
          }),
        }).catch(() => {});
      } catch (logErr) {
        console.warn('DB利用ログ同期スキップ:', logErr);
      }

      Alert.alert('生成完了', '愛犬・愛猫の心の声とストーリーが紡ぎ出されました🐾');
    } catch (e: any) {
      console.error(e);
      let friendlyMessage = '通信状況等をご確認ください🐾';
      if (e.message) {
        if (e.message.includes('503') || e.message.includes('demand') || e.message.includes('UNAVAILABLE')) {
          friendlyMessage = `ただいまAIの文筆家が少しお昼寝中（アクセスが集中して大変混雑）のようです💤\n\n少し時間をおいてからもう一度お試しいただくか、管理者に連絡して一時的に『テスト用モックモード』に切り替えてもらうと、待ち時間やコストなしで今すぐ体験できますよ🐾`;
        } else {
          friendlyMessage = e.message;
        }
      }
      Alert.alert('ストーリーのつむぎ出しに失敗しました🐾', friendlyMessage);
    } finally {
      setLoading(false);
    }
  };

  const handleCopyPrompt = () => {
    if (!mangaPrompt) return;
    Clipboard.setString(mangaPrompt);
    Alert.alert(
      'コピー完了',
      '🐾 4コマ漫画用プロンプトをコピーしました！\n\nChatGPT(DALL-E 3)の入力欄に貼り付けて送信すると、可愛い4コマ漫画が生成されます🎨'
    );
  };

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
          <View style={styles.headerBannerLeft}>
            {profile?.avatarBase64 ? (
              <Image
                source={{ uri: `data:image/jpeg;base64,${profile.avatarBase64}` }}
                style={styles.headerAvatar}
              />
            ) : (
              <View style={[styles.headerAvatar, styles.headerAvatarPlaceholder]}>
                <Text style={styles.headerAvatarPlaceholderText}>🐾</Text>
              </View>
            )}
            <View style={styles.headerTextContainer}>
              <Text style={styles.headerTitle}>おかえりなさい！🐾</Text>
              <Text style={styles.headerSubtitle}>
                {profile?.owner_name || '飼い主'} 様 ＆ {profile?.name || 'ペット'} ちゃんのお部屋
              </Text>
            </View>
          </View>
          {/* アクションボタン群 */}
          <View style={{ flexDirection: 'column', gap: 6, alignItems: 'stretch' }}>
            <TouchableOpacity
              style={styles.newspaperLinkBtn}
              onPress={() => router.push('/newspaper')}
              activeOpacity={0.7}
            >
              <Text style={styles.newspaperLinkText}>📰 新聞</Text>
            </TouchableOpacity>
            <TouchableOpacity
              style={[styles.newspaperLinkBtn, { backgroundColor: '#FF8DA1' }]}
              onPress={() => router.push('/voice_settings' as any)}
              activeOpacity={0.7}
            >
              <Text style={styles.newspaperLinkText}>🔊 声設定</Text>
            </TouchableOpacity>
          </View>
        </View>

        {/* 新聞発行への導線バナーカード */}
        <TouchableOpacity 
          style={styles.newspaperBannerCard} 
          onPress={() => router.push('/newspaper')}
          activeOpacity={0.8}
        >
          <View style={styles.newspaperBannerHeader}>
            <Text style={styles.newspaperBannerIcon}>📰</Text>
            <View style={styles.newspaperBannerTitleCol}>
              <Text style={styles.newspaperBannerTitle}>週刊・うちのコ日常新聞を発行 🐾</Text>
              <Text style={styles.newspaperBannerSubtitle}>
                写真とAI感情分析から、特別な思い出新聞を自動レイアウト！
              </Text>
            </View>
          </View>
          <Text style={styles.newspaperBannerArrow}>今週の新聞を読む 🗞️ ➔</Text>
        </TouchableOpacity>

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
                onPress={() => handleSaveStoryMode('novel')}
              >
                <Text style={[styles.choiceText, storyMode === 'novel' && styles.choiceTextActive]}>絵本小説風</Text>
              </TouchableOpacity>
              <TouchableOpacity
                style={[styles.choiceBtn, storyMode === 'chat' && styles.choiceBtnActive]}
                onPress={() => handleSaveStoryMode('chat')}
              >
                <Text style={[styles.choiceText, storyMode === 'chat' && styles.choiceTextActive]}>おしゃべり風</Text>
              </TouchableOpacity>
            </View>
          </View>

          {storyMode === 'novel' && (
            <View style={styles.inputGroup}>
              <Text style={styles.label}>📚 小説のジャンルを選択</Text>
              
              <View style={styles.genreChipsContainer}>
                {[
                  { name: 'ほのぼの日常風', icon: '🌸' },
                  { name: '恋愛小説風', icon: '💖' },
                  { name: '冒険小説風', icon: '🧭' },
                  { name: 'ミステリー風', icon: '🔍' },
                  { name: '異世界転生風', icon: '🌀' },
                  { name: '学園小説風', icon: '🏫' },
                ].map((item) => {
                  const isActive = genre === item.name;
                  return (
                    <TouchableOpacity
                      key={item.name}
                      style={[
                        styles.genreChip,
                        isActive && styles.genreChipActive
                      ]}
                      onPress={() => handleSaveGenre(item.name)}
                      activeOpacity={0.7}
                    >
                      <Text style={[
                        styles.genreChipText,
                        isActive && styles.genreChipTextActive
                      ]}>
                        {item.icon} {item.name}
                      </Text>
                    </TouchableOpacity>
                  );
                })}
              </View>

              <Text style={styles.subLabel}>✍️ 自由に入力・調整もできます🐾</Text>
              <TextInput 
                style={styles.input} 
                value={genre} 
                onChangeText={handleSaveGenre} 
                placeholder="例: ほのぼの日常風, 恋愛小説風" 
              />
            </View>
          )}

          {loading ? (
            <View style={styles.loadingBox}>
              <Video
                source={require('../assets/loading_animation.mp4')}
                rate={1.0}
                volume={0.0}
                isMuted={true}
                resizeMode={ResizeMode.CONTAIN}
                shouldPlay
                isLooping
                style={styles.loadingVideo}
              />
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

                <TouchableOpacity style={styles.btnChatGpt} onPress={() => Linking.openURL('https://chatgpt.com/')}>
                  <Text style={styles.btnChatGptText}>🚀 ChatGPTで4コマ漫画生成</Text>
                </TouchableOpacity>
              </View>
            )}

            <TouchableOpacity style={styles.btnShare} onPress={handleShare}>
              <Text style={styles.btnShareText}>🔗 家族やSNSにストーリーを共有する</Text>
            </TouchableOpacity>
          </View>
        )}

        {/* 別のペットを登録するためのリセットリンク */}
        <TouchableOpacity 
          style={styles.btnResetProfile} 
          onPress={() => {
            Alert.alert('ログアウト', '登録データを削除して、別のペットを新しく登録し直しますか？', [
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
          <Text style={styles.btnResetProfileText}>🔄 別のペットを登録・ログインする</Text>
        </TouchableOpacity>

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
    backgroundColor: '#FFE4E8',
    borderWidth: 1.5,
    borderColor: '#FFB8C4',
    borderRadius: 20,
    padding: 16,
    marginBottom: 16,
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    shadowColor: 'rgba(255, 128, 150, 0.12)',
    shadowOffset: { width: 0, height: 6 },
    shadowOpacity: 1,
    shadowRadius: 16,
    elevation: 3,
  },
  headerBannerLeft: {
    flexDirection: 'row',
    alignItems: 'center',
    flex: 1,
    paddingRight: 8,
  },
  headerAvatar: {
    width: 48,
    height: 48,
    borderRadius: 24,
    borderWidth: 2,
    borderColor: '#FFA0B0',
  },
  headerAvatarPlaceholder: {
    backgroundColor: '#FFE9EC',
    justifyContent: 'center',
    alignItems: 'center',
  },
  headerAvatarPlaceholderText: {
    fontSize: 20,
  },
  headerTextContainer: {
    marginLeft: 12,
    flex: 1,
  },
  headerTitle: {
    color: '#C72C48',
    fontSize: 18,
    fontWeight: 'bold',
  },
  headerSubtitle: {
    color: '#3D2D2D',
    fontSize: 12,
    marginTop: 4,
    fontWeight: '700',
  },
  newspaperLinkBtn: {
    backgroundColor: '#C72C48',
    paddingVertical: 8,
    paddingHorizontal: 12,
    borderRadius: 12,
    minWidth: 80,
    alignItems: 'center',
    justifyContent: 'center',
    shadowColor: 'rgba(199, 44, 72, 0.2)',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 1,
    shadowRadius: 8,
    elevation: 2,
  },
  newspaperLinkText: {
    color: '#FFF',
    fontWeight: 'bold',
    fontSize: 12,
    textAlign: 'center',
  },
  btnResetProfile: {
    paddingVertical: 12,
    alignItems: 'center',
    marginTop: 20,
    marginBottom: 10,
  },
  btnResetProfileText: {
    color: '#8E7A7A',
    fontSize: 12,
    textDecorationLine: 'underline',
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
  btnChatGpt: {
    backgroundColor: '#10a37f',
    paddingVertical: 12,
    borderRadius: 8,
    alignItems: 'center',
    marginTop: 8,
  },
  btnChatGptText: {
    color: '#FFF',
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
  loadingVideo: {
    width: '100%',
    height: 180,
    borderRadius: 16,
    marginBottom: 12,
  },
  genreChipsContainer: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    marginBottom: 12,
  },
  genreChip: {
    backgroundColor: '#FFF',
    borderWidth: 1,
    borderColor: '#FFD0D6',
    borderRadius: 20,
    paddingVertical: 8,
    paddingHorizontal: 12,
    marginRight: 8,
    marginBottom: 8,
  },
  genreChipActive: {
    backgroundColor: '#C72C48',
    borderColor: '#C72C48',
  },
  genreChipText: {
    color: '#7D6363',
    fontSize: 12,
    fontWeight: '600',
  },
  genreChipTextActive: {
    color: '#FFF',
  },
  newspaperBannerCard: {
    backgroundColor: '#FFF0F2',
    borderWidth: 1,
    borderColor: '#FFA0B0',
    borderRadius: 20,
    padding: 16,
    marginBottom: 16,
    shadowColor: 'rgba(255, 128, 150, 0.08)',
    shadowOffset: { width: 0, height: 6 },
    shadowOpacity: 1,
    shadowRadius: 16,
    elevation: 3,
  },
  newspaperBannerHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 12,
  },
  newspaperBannerIcon: {
    fontSize: 32,
    marginRight: 12,
  },
  newspaperBannerTitleCol: {
    flex: 1,
  },
  newspaperBannerTitle: {
    color: '#C72C48',
    fontSize: 16,
    fontWeight: 'bold',
  },
  newspaperBannerSubtitle: {
    color: '#7D6363',
    fontSize: 11,
    marginTop: 4,
    lineHeight: 15,
  },
  newspaperBannerArrow: {
    color: '#C72C48',
    fontSize: 13,
    fontWeight: 'bold',
    textAlign: 'right',
    borderTopWidth: 1,
    borderTopColor: 'rgba(199, 44, 72, 0.08)',
    paddingTop: 8,
  },
  subLabel: {
    color: '#7D6363',
    fontSize: 12,
    fontWeight: 'bold',
    marginBottom: 6,
  },
});
