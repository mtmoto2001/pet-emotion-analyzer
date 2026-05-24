import requests
import json
import os
import time
import streamlit as st

def run_ai_factory(google_key, pet_info, temp_file_path, story_mode, genre, progress_bar, status_text):
    """
    Google Gemini API (gemini-2.5-flash) を使用して、画像から
    ① 心情分析、② 指定されたジャンルの美しい日本語ショートストーリー、③ DALL-E 3(ChatGPT)向け超高精細4コマ漫画プロンプト
    を1パスで同時設計する engine
    """
    ext = os.path.splitext(temp_file_path)[1].lower()

    try:
        # ----------------------------------------------------------------
        # 【STEP 1】メディアデータ（画像）の準備
        # ----------------------------------------------------------------
        progress_bar.progress(20)
        
        # --- 画像のインライン送信で超高速化 ---
        import base64
        status_text.info("📸 1/2: 画像データを最適化中...")
        with open(temp_file_path, "rb") as f:
            img_bytes = f.read()
        base64_img = base64.b64encode(img_bytes).decode("utf-8")
        
        mime_type = "image/png" if ext == ".png" else "image/jpeg"
        media_part = {
            "inlineData": {
                "mimeType": mime_type,
                "data": base64_img
            }
        }
        progress_bar.progress(50)

        # ----------------------------------------------------------------
        # 【STEP 2】1パス一体型リクエストによる解析・執筆・最高のプロンプト設計
        # ----------------------------------------------------------------
        status_text.info("📝 2/2: 最先端AI (Gemini 2.5 Flash) が画像からペットの姿と情景を読み解き、ストーリーを執筆中...")
        progress_bar.progress(70)

        # --- ストーリーのマンネリ化を防ぐ心理テーマシャッフルシステム (10種のプレミアムプロット) ---
        import random
        themes = [
            ("感謝と日常の喜び", "『パパ/ママがそばにいてくれる当たり前の日常がどれほど尊く幸せか、心からの感謝を伝える』テーマ。ペットの心の声から飼い主への無条件の純粋な愛がじんわりと伝わります。"),
            ("お留守番と再会", "『少し寂しかったお留守番の時間と、パパ/ママが帰宅した瞬間の爆発するような再会の喜び』テーマ。健気にお家を守って待っていた愛らしい姿を描きます。"),
            ("秘密の警護任務", "『実は自分がお家とパパ/ママを守る優秀なSPであり、パトロール任務や警護を一生懸命こなしているつもり』というユーモラスで愛おしいテーマ。"),
            ("スマホを構えるパパ/ママの観察", "『パパ/ママが自分にスマホを構えて嬉しそうに見つめてくる姿を、ペットならではの解釈（『またボクの可愛さにやられてるなー』『パパの宝物にしていいよ！』など）で温かく見つめ返している』テーマ。"),
            ("おやつおねだり大作戦", "『どうしてもオヤツが欲しい！そのために小さな頭で一生懸命に可愛いポーズを考え、パパ/ママと愛らしい駆け引きを行う』ユーモラスな知能戦テーマ。"),
            ("季節の風と五感の幸せ", "『日だまりのあたたかさ、窓辺の風の匂い、季節のちょっとした変化を五感で最大限に楽しんでいるペットの瑞々しい感性』テーマ。非常に詩的で美しい描写になります。"),
            ("実は私がパパ/ママをお世話している", "『パパ/ママが自分をお世話しているのではなく、実は自分がパパ/ママを日々お世話して、癒やし、甘えさせてあげているという誇り高い優しさ』テーマ。優しいギャップが胸を打ちます。"),
            ("お家の中のヒミツの聖域", "『ソファの隙間、お布団の中、キャットタワーの最上階などが、どれほど特別なパラダイス（王国）であるか、そこで過ごす極上の幸福感』テーマ。"),
            ("日常の小さな大事件", "『ルンバの起動、段ボール箱の出現、おもちゃがソファの下に入ったことなどの些細な出来さを、ペットの主観から見た「巨大な大冒険・大ハプニング」としてパパ/ママと乗り越えた絆』テーマ。"),
            ("夢の中のワンダーランド", "『眠っている時の夢の中で、どれほど楽しくパパ/ママとお花畑を駆け回ったり、空を飛んだりして大冒険をしていたか、その温かい残り香』テーマ。")
        ]
        selected_theme_title, selected_theme_desc = random.choice(themes)

        # 一人称（pronoun）と口調の指示を組み立て
        gender_display = pet_info.get('gender', '女の子')
        pronoun = pet_info.get('pronoun', 'ボク' if gender_display == '男の子' else 'わたし')
        
        # 性格や一人称に連動したトーンの指示を動的に定義
        tone_detail = "自然で愛らしいトーン（「〜だよ」「〜だね」など）"
        if pronoun == "拙者":
            tone_detail = "「〜でござる」「〜に候」「〜つかまつる」などの忠義の武士・侍口調（非常に義理堅く、真面目で、飼い主さんを『主君』や『主（あるじ）』と崇めるような厳かで愛らしい口調）"
        elif pronoun == "世":
            tone_detail = "「〜である」「〜ではないか」「〜の辞書に〜はない」などの尊大で高貴な王様・皇帝口調（我が家を統治する偉大な王としての誇り高さと、実は隠しきれない甘えん坊さを融合させた魅力的な口調）"
        elif pronoun == "あちき":
            tone_detail = "「〜でありんす」「〜なんし」「〜おくれやす」などの吉原の花魁・廓詞（くるわことば）風の、上品で艶やか、かつミステリアスに飼い主さんを手のひらで転がすような大人っぽいお姉様口調"
        elif pronoun == "ぼく" and gender_display == '女の子':
            tone_detail = "女の子ですが一人称「ぼく」を使用する、元気でボーイッシュな僕っこ口調（サバサバしながらも、時折見せる素直な甘えが非常に愛らしい、ギャップのあるトーン）"
        elif pronoun in ["オレ", "おれ"]:
            tone_detail = "「〜だぜ」「〜だよな」などのやんちゃで活発、ちょっと強がりな元気いっぱいの男の子口調"
        elif pronoun == "ぼくちゃん":
            tone_detail = "あざと可愛く、極限まで甘やかされた赤ちゃんのような「〜でちゅ」「〜なの」といった極上の甘えん坊口調"
        elif pronoun == "自分":
            tone_detail = "「〜であります」「〜っす」などの、真面目で少し不器用、かつ非常に忠実で従順な番犬・部下のような口調"
        elif pronoun == "あたい":
            tone_detail = "少し生意気で強がりなツンデレ風の「〜だよ」「〜だし」といったおてんば娘口調"
        elif pronoun == "うち":
            tone_detail = "関西風の親しみやすさやフレンドリーさのある「〜やで」「〜なん？」といった気さくな相棒口調"
        elif pronoun == pet_info.get('name'):
            tone_detail = f"自分の名前（「{pet_info.get('name')}」）を一人称とし、非常に幼く無邪気なパピー・キティちゃんのような無防備で愛らしい語り口"
        elif pronoun in ["わたし", "私"]:
            tone_detail = "上品で優しく、少し大人びて飼い主さんをそっと温かく見守るようなお姉さん口調"
        elif pronoun in ["あたし"]:
            tone_detail = "甘えん坊で天真爛漫、チャーミングでおねだりが得意な小悪魔的な女の子口調"

        tone_instruction = (
            f"今回のペットは「{gender_display}」で、一人称は「{pronoun}」です。\n"
            f"指示するトーン: {tone_detail} を完全に再現し、最初から最後までこの一人称と言葉遣いを徹底してください。\n"
            f"登録されたペットの性格（{pet_info.get('personality', '元気')}、詳細: {pet_info.get('personality_detail', '')}）や年齢（{pet_info.get('age_display', '不明')}）も加味し、"
            f"その子自身の魂が宿ったようなリアリティのあるオリジナルの口調で執筆してください。"
        )

        if story_mode == "絵本小説風（客観的な視点から）":
            if genre == "恋愛小説風":
                genre_instruction = f"""
                【恋愛小説風世界観（飼い主さん＝温かい親目線・視聴者目線で見守る特別な恋愛劇）】
                {pet_info['name']}ちゃんが、近所のお友達ペットやお気に入りのぬいぐるみ等に対して、生まれて初めての純粋な恋心（恋愛）を抱き、一生懸命にアピールしたり照れたりしている健気で可愛い様子を描いてください。
                この恋愛模様を、飼い主である「{pet_info['owner_call']}」がまるで「温かい親のような優しい目線」や「ドラマをハラハラドキドキしながら見守る視聴者のような目線」でそっと見守り、心から応援したり、きゅんとしたり、愛おしさで胸がいっぱいになったりする姿をストーリーの中に美しく組み込んでください。
                飼い主がその恋愛を温かい親・視聴者目線でしっかりと見て感じていることが、読者（飼い主）にダイレクトに伝わる、最高品質の甘酸っぱい恋愛小説に仕立ててください。
                """
            elif genre == "冒険小説風":
                genre_instruction = f"""
                【冒険小説風世界観】
                リビングのラグを「果てしない大平原」、キャットタワーや家具を「そびえ立つ天空の牙城」、おもちゃを「伝説の秘宝」に見立てるなど、日常の光景をファンタジー調 of 壮大な冒険として描いてください。
                {pet_info['name']}ちゃんが勇敢な旅人として、一番の相棒である「{pet_info['owner_call']}」と共に未知のワクワクに立ち向かう、手に汗握るスリリングな旅路を描写してください。
                """
            elif genre == "ほのぼの日常風":
                genre_instruction = f"""
                【ほのぼの日常風世界観】
                日だまりの温かさ、お昼寝の静けさ、肉球の香ばしい匂い、静かに流れる穏やかな時間。
                言葉は交わさなくても、お互いの存在がそこにあるだけで世界が満たされるような、慈愛と穏やかなユーモアに満ちた極上の日常風景を紡ぎ出してください。
                """
            elif genre == "ミステリー（世にも奇妙な物語風）":
                genre_instruction = f"""
                【ミステリー/世にも奇妙な物語風世界観】
                「{pet_info['owner_call']}」がふと目を離した瞬間に起こる、不思議でちょっと不気味なできごと。
                鏡の向こうの影、勝手に動くおやつの袋、ペットにだけ見えている「透明なお客様」など、少し不思議でユーモラス、かつゾクゾクと引き込まれるスリリングなサスペンス調の構成で描いてください。
                """
            elif genre == "異世界転生風":
                genre_instruction = f"""
                【異世界転生風世界観】
                実は{pet_info['name']}ちゃんは「かつて異世界を救った伝説の超聖獣」や「伝説の大魔導士」が、愛する「{pet_info['owner_call']}」に溺愛されるためにこの世界に転生してきたという設定で描いてください。
                心の中（心の声）では極めて冷静で誇り高く知性的な大人の語り口でありながら、飼い主の前では愛らしさに負けてつい野生を忘れてデレデレに甘えてしまう最高のギャップを、ライトノベル風の軽快なタッチで描いてください。
                """
            elif genre in ["学園小説風", "学校小説風"]:
                genre_instruction = f"""
                【学校・学園小説風世界観（飼い主さん＝「懐かしいなー」としみじみしたり「胸キュン」する体験）】
                ペットたちが通う不思議で愛らしい「ペット学園」を舞台に、授業、休み時間、放課後の部活動、友情や甘酸っぱい青春など、そこで起こる様々な日常のドラマを描いてください。
                {pet_info['name']}ちゃんが一生懸命に学園生活を送り、友達と助け合ったり成長したりする瑞々しいストーリーを描写してください。
                それを読んだ飼い主である「{pet_info['owner_call']}」が、自分の学生時代の夕暮れや甘酸っぱさを思い出して「あぁ、懐かしいなー」としみじみノスタルジーに浸ったり、青春を全力で駆け抜ける{pet_info['name']}ちゃんのひたむきな姿にギュッと「胸キュン」して愛おしさがこみ上げてくるような、最高品質の青春成長ストーリーに仕立ててください。
                """
            
            mode_prompt = f"""
            {genre_instruction}
            - 語り手は客観的な視点から描写しつつ、{pet_info['name']}ちゃんの心の声やセリフを「」書きで効果的に挿入し、感情のピークを作ってください。
            - 選ばれたジャンルの世界観と、ペットの情報、および写真から解析した「ペットの気持ち」を完全に融合させ、一流の作家が執筆したかのような最高峰のクオリティに仕上げてください。
            - 【最重要ルール】: 「【起】」「【承】」「【転】」「【結】」や「シーン1」といった見出し・構成記号・数字は【絶対に一切出力しないでください】。
            - 記号や見出しを使わず、自然な日本語の段落分け（空白行を挟む）のみを用いて、最初から最後まで美しく流れるような一本の洗練された文芸ショートストーリーとして執筆してください。
            """
        else:
            mode_prompt = f"""
            【おしゃべり風（うちのコの一人称本音スタイル）】
            - 最初から最後まで100% {pet_info['name']}ちゃん自身の一人称（{pronoun}）だけで語り尽くさせ、{pet_info['owner_call']}に向かって胸の奥の溢れんばかりの本音をたくさん伝える文章にしてください。
            - 本日の物語の深層心理テーマ：『{selected_theme_title}』（詳細：{selected_theme_desc}）を主軸にしたストーリーを展開してください。
            - {pronoun}という一人称と言葉遣い（{tone_detail}）を極めて忠実に再現し、さらに登録されている具体的な性格詳細エピソード（{pet_info['personality_detail']}）と一貫したペットの個性を完全に守りながら執筆してください。
            - 単調なハッピー日常だけでなく、デザイン思考に基づくドラマ構造（小さな戸惑いやハプニングから、ペットらしい健気な解釈を経て、飼い主さんへの深い愛着と絆に収束する美しい心の変化）を持たせてください。
            - 【最重要ルール】: 「【起】」「【承】」「【転】」「【結】」や「シーン1」といった見出し・構成記号・数字は【絶対に一切出力しないでください】。
            - 記号や見出しを使わず、自然な段落分けのみを用いて、最初から最後まで{pet_info['name']}ちゃんの一人称の美しい独白ストーリーとして執筆してください。
            """

        prompt = f"""
        あなたはペットの何気ない日常のできごとから家族への溢れる愛情を翻訳する「世界最高峰 of 動物文学作家」であり、画像生成AI（DALL-E 3）の動作原理を熟知した「天才プロンプトエンジニア」です。
        提供されたメディア（画像）と登録されたペット情報をもとに、以下の3つのコンテンツを極めてエモーショナルかつ最高品質で生成してください。

        【登録されているペットの基本情報】
        ・名前: {pet_info['name']}
        ・性別: {gender_display}
        ・年齢: {pet_info['age_display']}
        ・種別: {pet_info['pet_type']}（品種: {pet_info.get('breed', '')}）
        ・毛色/特徴: {pet_info['color']}
        ・基本性格: {pet_info['personality']}
        ・具体的な性格詳細: {pet_info['personality_detail']}
        ・飼い主の呼び方: 「{pet_info['owner_call']}」
        ・話し方のトーン指定: {tone_instruction}

        【最重要：最高品質の日本語執筆および設定反映ルール（厳守）】
        1. ペットの一人称「{pronoun}」および口調設定の完全なる再現（厳守）：
           - 今回のペットは「{gender_display}」で、一人称は「{pronoun}」です。
           - 心の声やセリフ、独白での一人称は必ず「{pronoun}」で統一してください。
           - 口調指示（{tone_detail}）を完璧にシミュレートし、そのコ独自の個性を完全に体現してください。
           - 特に一人称が「拙者」なら侍口調（〜ござる）、「世」なら皇帝口調（〜である）、「あちき」なら花魁口調（〜でありんす）、「ぼく」（女の子）なら元気な僕っこ口調を完璧に維持してください。設定された一人称から逸脱した語尾や一人称は【絶対に厳禁】です。
        2. プロの文学作品に相応しい、極めて美しく自然な日本語表現：
           - 機械翻訳風のぎこちないフレーズ、不自然な語尾、あるいは日本語以外の助詞（例：韓国語の「의」など）の混入は一切排除してください。
           - 日本の第一線で活躍するプロの児童文学作家・絵本作家が書き下ろしたような、流麗で感情豊かな美しい日本語表現のみを使用してください。
        3. 日本語の動詞の正しい活用と「てにをは（助詞）」の完全性：
           - 動詞の活用を完全に正確にしてください。例えば、「膨らむでいく」は文法的な間違いです。「膨らんでいく（ふくらんでいく）」のように正しい音便・活用を徹底してください。
           - 「時間ずっと」などのように言葉が抜けた不自然なフレーズではなく、「この時間がずっと」などのように適切な指示代名詞や助詞を完全に補ってください。
        4. 文脈の完璧な整合性と矛盾ワードの徹底排除：
           - 幸せで温かいシチュエーションの中に、突然文脈から乖離した不調和な言葉（例：芝生でのリラックス中の「恐怖」や、温かい触れ合いの中での「悩み」など）を混入させることは【絶対に厳禁】とします。
           - 「感触」「温もり」「眼差し」「香り」など、前後の文脈と情緒的なトーンに100%調和する、必然性のある言葉だけを慎重に選定して執筆してください。
           - 意味不明なフレーズ（「みが陽光があって」など）を出力せず、最初から最後まで論理的かつ最高品質の文芸作品として通用する文章にしてください。
        5. 登録されているペット情報の完全なる融合：
           - メディア（画像）から分析したその瞬間の「ペットの気持ち」をベースにしながら、登録されている性格や特徴をブレンドし、設定との完璧な整合性を保ってください。

        【生成するコンテンツと執筆ルール（厳守）】

        1. ペットの気持ち分析 (feelings):
           - 提供された画像を極めて精密にディテール分析してください（ペットの視線の向き、耳の立ち方、口元の表情、リラックス度、体の体勢、背景の環境などから、その瞬間のミクロな感情を完璧に推測すること）。
           - 分析した本当の気持ちや感情、{pet_info['owner_call']}へのまっすぐな愛着を、その子自身の本当の心の声として、温かく語りかけるように執筆してください（日本語、150〜200文字程度。圧倒的な文芸クオリティで）。
           - 今回選定された心理テーマ『{selected_theme_title}』のニュアンスも効果的にブレンドしてください。

        2. ストーリー (story):
           - {mode_prompt}

        3. GPT用4コマ漫画生成プロンプト (manga_prompt):
           - 上記で作成したストーリーのセリフやシチュエーションを完全に反映させた、高品質な4コマ漫画（4-panel manga comic strip）をChatGPT/GPT（DALL-E 3）で一発で美しく生成するための英語の超詳細プロンプトを構築してください。
           - プロンプトの冒頭に、必ず【Visual Profile (Character Consistency Guide)】というセクションを設け、アップロードされた写真から分析したペットの精密な外見特徴（具体的なポーズ、表情、毛並み、特徴的なパーツ、身につけているアクセサリーや首輪、背景の色彩や環境など）を詳細な英語で記載してください。
           - プロンプト内には以下の要素を必ず含めてください：
             - 上記の【Visual Profile】に基づき、4つのコマすべてでキャラクターの一貫性を完全に維持するための指示。
             - 画風のスタイル指定（例: "A beautiful colored 4-panel manga layout", "warm and soft watercolor tones", "children picture book illustration style", "masterpiece"）
             - 4つのコマ（Panel 1, Panel 2, Panel 3, Panel 4）ごとの具体的な構図、表情、アクション、背景の英語による緻密な描写
             - 各コマに配置する日本語のセリフ（吹き出し用のセリフテキスト）を正確に描写指示すること（例: 'Include a speech bubble in Japanese saying "..."'）

        【出力フォーマット】
        必ず以下のJSONスキーマに従って出力してください。キー名は完全に一致させてください。余計なマークダウン装飾（```jsonなど）は一切含めず、純粋なJSONテキストだけを返してください。

        {{
            "feelings": "ペットの気持ちの執筆テキスト（日本語、150〜200文字程度）",
            "story": "起承転結ストーリーの執筆テキスト（日本語、美しい文章のみ。見出しや【起承転結】記号は絶対に入れないこと）",
            "manga_prompt": "ChatGPTにそのままコピー＆ペーストして使用できる、高品質な4コマ漫画生成用のプロ仕様英語プロンプト"
        }}
        """

        gemini_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={google_key}"
        
        payload = {
            "contents": [
                {
                    "parts": [
                        {"text": prompt},
                        media_part
                    ]
                }
            ],
            "generationConfig": {
                "responseMimeType": "application/json",
                "temperature": 0.4
            }
        }

        progress_bar.progress(90)
        res_gemini = requests.post(gemini_url, json=payload, timeout=120)
        
        if res_gemini.status_code != 200:
            raise RuntimeError(f"Gemini APIエラー: HTTP {res_gemini.status_code} / {res_gemini.text}")

        res_data = res_gemini.json()
        try:
            raw_text = res_data["candidates"][0]["content"]["parts"][0]["text"].strip()
            data = json.loads(raw_text)
        except (KeyError, IndexError, json.JSONDecodeError) as e:
            raise RuntimeError(f"Geminiレスポンスの解析に失敗しました: {e}。生データ: {res_data}")

        progress_bar.progress(100)
        status_text.success("✨ 心情分析、ストーリー、最高のプロンプトがすべて完成しました！🐾")
        time.sleep(1)

        return data.get("feelings", ""), data.get("story", ""), data.get("manga_prompt", "")

    except Exception as e:
        progress_bar.empty()
        return None, None, f"AIファクトリー稼働エラー: {e}"

    finally:
        pass

def run_lightweight_test(google_key):
    """
    Gemini APIへの軽量な接続確認テスト
    """
    import requests
    gemini_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={google_key}"
    payload = {
        "contents": [
            {
                "parts": [
                    {"text": "こんにちは、接続テストです。応答として、絵文字を含めた短い挨拶を1単語で日本語で出力してください。"}
                ]
            }
        ],
        "generationConfig": {
            "temperature": 0.2
        }
    }
    res_gemini = requests.post(gemini_url, json=payload, timeout=15)
    if res_gemini.status_code != 200:
        raise RuntimeError(f"Gemini APIエラー: HTTP {res_gemini.status_code} / {res_gemini.text}")
    res_data = res_gemini.json()
    try:
        return res_data["candidates"][0]["content"]["parts"][0]["text"].strip()
    except Exception as e:
        raise RuntimeError(f"レスポンスのパースエラー: {e}")

def sanitize_image(uploaded_file, target_path):
    """
    Pillowを用いてアップロードされた画像を安全に読み込み、
    EXIF回転を物理適用し、標準的なRGB形式のJPEGとして再エンコードして保存する。
    これにより Android/iOS のあらゆるフォルダ依存のパーミッションや
    WebP等の変則的なMIMEタイプによる不具合を100%防止する。
    """
    from PIL import Image, ImageOps
    import io
    
    try:
        # アップロードされたファイルをメモリ上のバイトストリームとして読み込む
        file_bytes = uploaded_file.getvalue()
        # file_uploader のポインタをリセットしておく（後続の処理のため）
        uploaded_file.seek(0)
        
        # Pillowで画像を開く (フォーマットに依存せず安全に開けます)
        img = Image.open(io.BytesIO(file_bytes))
        
        # スマホ撮影写真特有のEXIF回転情報を物理的な画像回転に自動変換・適用
        try:
            img = ImageOps.exif_transpose(img)
        except Exception as e:
            # EXIFが無い画像や、パース失敗時はスキップして安全継続
            pass
            
        # 超巨大画像の縮小（メモリ節約、OOMクラッシュ回避、Gemini送信の高速化）
        MAX_SIZE = 1600
        if max(img.size) > MAX_SIZE:
            img.thumbnail((MAX_SIZE, MAX_SIZE), Image.Resampling.LANCZOS)
            
        # RGBAなどのアルファチャンネル（透明度）がある場合は、JPEG保存のために白色背景と合成してRGBへ変換
        if img.mode in ("RGBA", "LA") or (img.mode == "P" and "transparency" in img.info):
            # 白色背景の新規画像を作成
            background = Image.new("RGB", img.size, (255, 255, 255))
            # アルファチャンネルを取り出してマスクとして利用し合成
            if img.mode == "RGBA":
                background.paste(img, mask=img.split()[3])
            else:
                background.paste(img, mask=img.convert("RGBA").split()[3])
            img = background
        else:
            # その他のモード（CMYKやグレースケール等）も安全にRGBに統一変換
            img = img.convert("RGB")
            
        # 最適な品質（Quality=85）で JPEG として物理保存
        # これにより Android/Chrome のいかなる一時ファイルのロックやパーミッション問題も回避されます
        img.save(target_path, "JPEG", quality=85)
        return True
    except Exception as e:
        # 万が一Pillowでのサニタイズ自体が失敗した場合は、生のバイナリ書き込みにフォールバックして耐障害性を確保
        try:
            uploaded_file.seek(0)
            with open(target_path, "wb") as f:
                f.write(uploaded_file.read())
            uploaded_file.seek(0)
            return True
        except Exception as fallback_err:
            raise RuntimeError(f"画像サニタイズおよび一時保存に完全に失敗しました: {e} (フォールバックエラー: {fallback_err})")
