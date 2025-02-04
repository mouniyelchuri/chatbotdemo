import streamlit as st
import vertexai
from vertexai.preview.language_models import ChatModel
import google.cloud.logging

from google import genai
from google.genai import types
client = genai.Client(
  vertexai=True, project="YOUR_PROJECT_ID", location="YOUR_LOCATION",
)
chat = client.chats.create(model="gemini-1.0-pro-002")

PROJECT_ID = "hca-tenet-chatbot-poc" # Your Google Cloud Project ID
LOCATION =  "us-central1" # Your Google Cloud Project Region
vertexai.init(project=PROJECT_ID, location=LOCATION)

client = google.cloud.logging.Client(project=PROJECT_ID)
client.setup_logging()

LOG_NAME="hca-chatbot-app-logs"
logger= client.logger(LOG_NAME)

@st.cache_resource
def load_models():
    client = genai.Client(
    vertexai=True, project="hca-tenet-chatbot-poc", location="us-central1",
    )
    chat = client.chats.create(model="gemini-1.0-pro-002")
    return chat


def load_css():
    with open("static/styles.css", "r") as f:
        css = f"<style>{f.read()}</style>"
        st.markdown(css, unsafe_allow_html=True)
    

def response(model, message):
    parameters = {
        "temperature": 0.2,
        "max_output_tokens": 256,
        "top_p": 0.8,
        "top_k": 40
    }
    #result = model.send_message(message, **parameters)
    result = model.send_message(message)
    return result.text


load_css()
st.title("HCA Chatbot")

if "messages" not in st.session_state:
    st.session_state.messages = []

for chat in st.session_state.messages:

    div = f"""
<div class="chat-row 
    {'' if chat["role"] == 'ai' else 'row-reverse'}">
    <img class="chat-icon" src="app/static/{
        'ai_icon.png' if chat["role"] == 'ai' 
                      else 'user_icon.png'}"
         width=32 height=32>
    <div class="chat-bubble
    {'ai-bubble' if chat["role"] == 'ai' else 'human-bubble'}">
        &#8203;{chat["content"]}
    </div>
</div>
        """
    st.markdown(div, unsafe_allow_html=True)

if prompt := st.chat_input("Enter your question here"):
    logger.log(f"Starting chat session...")
    st.session_state.messages.append({"role": "user", "content": prompt})
    
        #st.markdown(prompt)
    user_div= f"""
        <div class="chat-row row-reverse">
    <img class="chat-icon" src="app/static/user_icon.png" width=32 height=32 >
    <div class="chat-bubble human-bubble">&#8203;{prompt}
    </div> 
    </div>  
        """
    st.markdown(user_div, unsafe_allow_html=True)
    
    model=load_models()
    logger.log(f"Invoking model with {prompt}")
    response = response(model,prompt)
    
    if response:
        ai_div= f"""
            <div class="chat-row">
        <img class="chat-icon" src="app/static/ai_icon.png" width=32 height=32 >
        <div class="chat-bubble ai-bubble">&#8203;{response}
        </div> 
        </div>  
        """
        st.markdown(ai_div, unsafe_allow_html=True)
            
        st.session_state.messages.append({"role": "ai", "content": response})
