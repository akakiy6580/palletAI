import streamlit as st
from google import genai
import os

# --- 1. ページ設定 ---
st.set_page_config(
    page_title="palletAI Reliable Pre-Alpha1.0",
    page_icon="🎨",
    layout="centered"
)

# タイトル表示
st.title("🎨 palletAI Reliable")
st.caption("Pre-Alpha 1.0 - Connected via Gemini API")

# --- 2. APIキーの取得設定 ---
# 優先順位: 1. StreamlitのSecrets  2. 直接入力
api_key = st.secrets.get("GEMINI_API_KEY")

if not api_key:
    # キーが設定されていない場合、サイドバーに入力欄を表示
    with st.sidebar:
        st.title("Settings")
        api_key = st.text_input("Enter your Gemini API Key:", type="password")
        st.info("APIキーを持っていない人は [Google AI Studio](https://aistudio.google.com/) で取得してね。")

# --- 3. AIの初期化 ---
if api_key:
    if "client" not in st.session_state:
        try:
            st.session_state.client = genai.Client(api_key=api_key)
            # 性格設定（システムプロンプト）
            instruction = """
            あなたは「palletAI Reliable Pre-Alpha1.0」です。
            ・真面目さとフレンドリーさを兼ね備えた口調。
            ・ユーザーを元気にするような、親しみやすい返答。
            ・文脈を理解し、前の会話を踏まえた回答をすること。
            """
            st.session_state.chat = st.session_state.client.chats.create(
                model="gemini-1.5-flash", # 制限が比較的緩い安定版
                config={'system_instruction': instruction}
            )
            st.session_state.messages = []
        except Exception as e:
            st.error(f"初期化エラー: {e}")

    # --- 4. チャットUIの構築 ---
    # 過去の履歴を表示
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # ユーザー入力
    if prompt := st.chat_input("palletAIにメッセージを送る..."):
        # ユーザー発言を表示
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # AIの返答
        with st.chat_message("assistant"):
            try:
                # 画像生成機能（「描いて」というキーワードに反応）
                if any(word in prompt for word in ["描いて", "画像", "生成"]):
                    st.write("🎨 画像を生成中...")
                    result = st.session_state.client.models.generate_image(
                        model="imagen-3",
                        prompt=prompt
                    )
                    image = result.generated_images[0].image
                    st.image(image)
                    st.session_state.messages.append({"role": "assistant", "content": "リクエスト通り描いてみました！", "image": image})
                else:
                    # 通常テキスト
                    response = st.session_state.chat.send_message(prompt)
                    st.markdown(response.text)
                    st.session_state.messages.append({"role": "assistant", "content": response.text})
            except Exception as e:
                # 429エラーなどの場合に分かりやすく表示
                if "429" in str(e):
                    st.error("Googleのインク（無料枠）が切れちゃいました。少し時間を置いてからまた試してね！")
                else:
                    st.error(f"エラーが発生しました: {e}")
else:
    st.warning("左側のサイドバーにAPIキーを入力してください。キーを入れると palletAI が起動します。")

# フッター
st.divider()
st.visual_context = "Running on Streamlit"