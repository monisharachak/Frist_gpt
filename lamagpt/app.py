import streamlit as st
import requests
import json
import time

# Page config and title
st.set_page_config(page_title="Chat with LLaMA 3.2", layout="centered")
st.title("💬 Chat with LLaMA 3.2")

# Hide slider value bubbles
st.markdown("""
    <style>
    .stSlider div[data-baseweb="slider"] > div > div:nth-child(2) {
        display: none;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize toggle state for sidebar
if "show_sidebar" not in st.session_state:
    st.session_state.show_sidebar = True

# Sidebar toggle button
with st.container():
    col1, col2 = st.columns([0.9, 0.1])
    with col2:
        if st.button("🔧" if not st.session_state.show_sidebar else "❌"):
            st.session_state.show_sidebar = not st.session_state.show_sidebar

# Sidebar content
if st.session_state.show_sidebar:
    with st.sidebar:
        st.header("⚙️ Settings")
        model = st.selectbox("Model", ["llama3.2:1b", "llama3", "llama2"])
        temperature = st.slider("Temperature", 0.0, 1.5, 0.7)
        top_p = st.slider("Top-p", 0.0, 1.0, 0.95)
        if st.button("🧹 Clear Chat"):
            st.session_state.messages = []
else:
    # Defaults when sidebar is hidden
    model = "llama3.2:1b"
    temperature = 0.7
    top_p = 0.95

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display previous messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        emoji = "👤" if msg["role"] == "user" else "🤖"
        st.markdown(f"{emoji} {msg['content']}")

# Input area
prompt = st.chat_input("Ask anything to LLaMA...")

if prompt:
    st.chat_message("user").markdown(f"👤 {prompt}")
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Send request to Ollama
    url = "http://127.0.0.1:11434/api/chat"
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": "You are an AI assistant."},
            {"role": "user", "content": prompt}
        ],
        "stream": True,
        "options": {
            "temperature": temperature,
            "top_p": top_p
        }
    }

    # Stream and display response
    response_box = st.chat_message("assistant").empty()
    full_response = ""
    try:
        with requests.post(url, json=payload, stream=True) as response:
            for line in response.iter_lines():
                if line:
                    data = json.loads(line.decode("utf-8"))
                    if 'message' in data and 'content' in data['message']:
                        token = data['message']['content']
                        full_response += token
                        response_box.markdown(f"🤖 {full_response}▌")
        response_box.markdown(f"🤖 {full_response}")
        st.session_state.messages.append({"role": "assistant", "content": full_response})
    except Exception as e:
        response_box.markdown(f"⚠️ Error: {e}")
