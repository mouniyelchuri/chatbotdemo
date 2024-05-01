from dataclasses import dataclass
from typing import Literal
import streamlit as st

import vertexai
from vertexai.preview.language_models import ChatModel
import google.cloud.logging



PROJECT_ID = "hca-tenet-chatbot-poc" # Your Google Cloud Project ID
LOCATION =  "us-central1" # Your Google Cloud Project Region

client = google.cloud.logging.Client(project=PROJECT_ID)
client.setup_logging()

LOG_NAME="hca-chatbot-app-logs"
logger= client.logger(LOG_NAME)

@dataclass
class Message:
    """Class for keeping track of a chat message."""
    origin: Literal["human", "ai"]
    message: str

def load_css():
    with open("static/styles.css", "r") as f:
        css = f"<style>{f.read()}</style>"
        st.markdown(css, unsafe_allow_html=True)

def initialize_session_state():
    if "history" not in st.session_state:
        st.session_state.history = []
    if "conversation" not in st.session_state:
        
        vertexai.init(project=PROJECT_ID, location=LOCATION)

        chat_model = ChatModel.from_pretrained("chat-bison@002")
        st.session_state.conversation = chat_model.start_chat()
        


def response(model, message):
    parameters = {
        "temperature": 0.2,
        "max_output_tokens": 256,
        "top_p": 0.8,
        "top_k": 40
    }
    result = model.send_message(message, **parameters)
    return result.text

        

load_css()
initialize_session_state()

st.title("HCA Demo Chatbot")

chat_placeholder = st.container()

if prompt := st.chat_input("What is up?"):
    llm_response = response(st.session_state.conversation,prompt)
    logger.log(f"Starting chat session...")
    st.session_state.history.append(
        Message("human", prompt)
    )
    st.session_state.history.append(
        Message("ai", llm_response)
    )

with chat_placeholder:
    for chat in st.session_state.history:
        div = f"""
<div class="chat-row 
    {'' if chat.origin == 'ai' else 'row-reverse'}">
    <img class="chat-icon" src="app/static/{
        'ai_icon.png' if chat.origin == 'ai' 
                      else 'user-icon.png'}"
         width=32 height=32>
    <div class="chat-bubble
    {'ai-bubble' if chat.origin == 'ai' else 'human-bubble'}">
        &#8203;{chat.message}
    </div>
</div>
        """
        st.markdown(div, unsafe_allow_html=True)
    
    for _ in range(3):
        st.markdown("")