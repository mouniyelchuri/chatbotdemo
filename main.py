import streamlit as st
import vertexai
from vertexai.preview.language_models import ChatModel
import google.cloud.logging



PROJECT_ID = "hca-tenet-chatbot-poc" # Your Google Cloud Project ID
LOCATION =  "us-central1" # Your Google Cloud Project Region
vertexai.init(project=PROJECT_ID, location=LOCATION)

client = google.cloud.logging.Client(project=PROJECT_ID)
client.setup_logging()

LOG_NAME = "hca-chatbot-app-logs"
logger = client.logger(LOG_NAME)


@st.cache_resource
def load_models():
    chat_model = ChatModel.from_pretrained("chat-bison@002")
    chat = chat_model.start_chat()
    return chat
    

def response(model, message):
    parameters = {
        "temperature": 0.2,
        "max_output_tokens": 256,
        "top_p": 0.8,
        "top_k": 40
    }
    result = model.send_message(message, **parameters)
    return result.text


st.title("HCA Demo Chatbot")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("How can I help you today?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    

    with st.chat_message("assistant"):
        print("user input is : {}".format(prompt))

        logger.log(f"Starting chat session...")
        model=load_models()
        logger.log(f"Chat Session created")
        response = response(model,prompt)
        if response:
            st.write(response)
    st.session_state.messages.append({"role": "assistant", "content": response})