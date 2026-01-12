import streamlit as st
from google import genai

# --- 1. ページ設定 ---
st.set_page_config(
    page_title="palletAI Reliable Pre-Alpha1.0",
    page_icon="🎨",
    layout="centered"
)

# タイトル
st.title("🎨 palletAI Reliable")
st.caption("Pre-Alpha 1.0 - Stable Edition")

# --- 2. APIキーの設定 (Secretsから取得) ---
# Streamlit Cloudの Advanced settings > Secrets に書いたキーを自動で読み込みます
api_key = st.secrets.get("GEMINI_API_KEY")

# もしSecretsに未設定ならサイドバーで入力させる（バックアップ機能）
if not api_key:
    with st.sidebar:
        st.title("Settings")
        api_key = st.text_input("Enter Gemini API Key:", type="password")

# --- 3. AIの初期化 ---
if api_key:
    if "client" not in st.session_state:
        try:
            # 最新のライブラリ形式でクライアント作成
            st.session_state.client = genai.Client(api_key=api_key)
            st.session_state.messages = []
        except Exception as e:
            st.error(f"初期化エラー: {e}")

    # 過去の履歴を表示（画像も含めて再現）
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if "image" in message:
                st.image(message["image"])

    # --- 4. チャット・画像生成ロジック ---
    if prompt := st.chat_input("何か話しかけてみて！"):
        # ユーザーの発言を保存・表示
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            try:
                # 「画像」や「描いて」が含まれる場合は画像生成（Imagen 3）
                if any(word in prompt for word in ["描いて", "画像", "生成", "image"]):
                    st.write("🎨 画像を生成中...")
                    result = st.session_state.client.models.generate_image(
                        model="imagen-3",
                        prompt=prompt
                    )
                    generated_image = result.generated_images[0].image
                    st.image(generated_image)
                    
                    # 履歴に保存
                    st.session_state.messages.append({
                        "role": "assistant", 
                        "content": "描いてみました！", 
                        "image": generated_image
                    })
                else:
                    # 通常のチャットは「確実」に動く latest を使用
                    response = st.session_state.client.models.generate_content(
                        model="gemini-flash-latest",
                        contents=prompt,
                        config={'system_instruction': "あなたはpalletAI Reliableです。真面目さと親しみやすさを持ち合わせたAIとして振る舞ってください。"}
                    )
                    st.markdown(response.text)
                    st.session_state.messages.append({"role": "assistant", "content": response.text})
            
            except Exception as e:
                # エラーハンドリング
                if "429" in str(e):
                    st.error("Googleの無料枠（インク）が切れました。1分ほど待って再試行してください。")
                else:
                    st.error(f"エラーが発生しました: {e}")
else:
    # APIキーがない時の案内
    st.warning("⚠️ サイドバー、またはStreamlit CloudのSecretsにAPIキーを設定してください。")

# フッター
st.divider()
st.caption("Developed by bluetree")
