import streamlit as st
import time
from openai import OpenAI

# OpenAI istemcisi için ön yükleme
@st.cache_resource
def initialize_openai_client(api_key, assistant_id):
    client = OpenAI(api_key=api_key)
    assistant = client.beta.assistants.retrieve(assistant_id)
    thread = client.beta.threads.create()
    return client, assistant, thread

def wait_for_completion(run, client, thread):
    while run.status in ["queued", "in_progress"]:
        run = client.beta.threads.runs.retrieve(
            thread_id=thread.id,
            run_id=run.id,
        )
        time.sleep(0.5)
    return run

def get_assistant_response(client, thread, assistant_id, user_input):
    message = client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=user_input,
    )
    run = client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=assistant_id,
    )
    run = wait_for_completion(run, client, thread)
    messages = client.beta.threads.messages.list(
        thread_id=thread.id, order="asc", after=message.id
    )
    return messages.data[0].content[0].text.value

# Streamlit UI Başlangıcı
st.set_page_config(page_title="Sakarya Chatbot", layout="centered")

# Sayfa Başlığı ve Alt Bilgi
st.title("REHBERSERDIVAN")
st.markdown("### Sakarya hakkında sorularınızı sorun. 😊")

# Sol tarafta görsel gösterimi
st.sidebar.image("app.jpeg", use_container_width=True)

# OpenAI API Bağlantısı
api_key = st.secrets["openai_apikey"]
assistant_id = st.secrets["assistant_id"]
client, assistant, thread = initialize_openai_client(api_key, assistant_id)

# Mesaj geçmişi için session state kontrolü
if "messages" not in st.session_state:
    st.session_state.messages = []

def submit_query():
    user_input = st.session_state.query
    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        st.session_state.query = ""
        assistant_response = get_assistant_response(client, thread, assistant_id, user_input)
        st.session_state.messages.append({"role": "assistant", "content": assistant_response})

# Kullanıcı girişi için metin kutusu
st.text_input("Bir soru sorun:", key="query", on_change=submit_query)

# Mesajları görselleştirme
st.markdown("---")
for message in st.session_state.messages:
    if message["role"] == "user":
        st.markdown(
            f"""
            <div style='background-color:#1a0e2e; padding:10px; border-radius:5px; margin-bottom:10px; color:white;'>
                <b>👤 Siz:</b> {message['content']}
            </div>
            """, unsafe_allow_html=True)
    elif message["role"] == "assistant":
        st.markdown(
            f"""
            <div style='background-color:#5f00f7; padding:10px; border-radius:5px; margin-bottom:10px; color:white;'>
                <b>🤖 Asistan:</b> {message['content']}
            </div>
            """, unsafe_allow_html=True)

# Alt bilgi
st.markdown("---")
st.markdown("<p style='text-align: center;'>Made with ❤️ in Sakarya</p>", unsafe_allow_html=True)
