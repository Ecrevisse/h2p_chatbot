from langchain.chat_models import ChatOpenAI
from langchain.agents.agent_toolkits import create_conversational_retrieval_agent
from langchain.agents.agent_toolkits import create_retriever_tool
from dotenv import load_dotenv
import streamlit as st
import os
import pinecone
import time
from langchain.vectorstores import Pinecone
from PIL import Image

from langchain.schema.messages import SystemMessage
from langchain.embeddings.openai import OpenAIEmbeddings

import firebase

load_dotenv()
openai_api_key = os.environ["OPENAI_API_KEY"]
pinecone_api_key = os.environ["PINECONE_API_KEY"]

questions = [
    "Compared to the alkaline water electrolysis system or other existing system, what would be the advantage for H2Power's technology in terms of cost effectiveness & efficiency ? Or any issues ?",
    "We think that a transformation of aluminum into powder is very unique and innovative, is this technology something only H2 Power could do ?",
    "Is your technology patented for the whole process of the transformation, or just partially ?",
    "How versatile is H2Power's technology across different industries and scales, and what impact could its widespread adoption have on the environment and economy?",
]


@st.cache_resource
def rag_tool_openai():
    text_field = "text"
    index_name = "h2p"

    pinecone.init(api_key=pinecone_api_key, environment="gcp-starter")

    index = pinecone.Index(index_name)
    while not pinecone.describe_index(index_name).status["ready"]:
        time.sleep(1)

    embed = OpenAIEmbeddings(openai_api_key=openai_api_key)

    vectorstore = Pinecone(index, embed.embed_query, text_field)

    retriever = vectorstore.as_retriever()

    tool = create_retriever_tool(
        retriever,
        "search_in_document",
        "Searches and returns documents.",
    )
    tools = [tool]

    llm = ChatOpenAI(
        temperature=0,
        model="gpt-4",  # "gpt-3.5-turbo",  # "gpt-4-1106-preview",
        openai_api_key=openai_api_key,
    )

    context = """
    You are an expert in the hydrogen sector.

    Your role is to help peoples to find relevant information about hydrogen, and to answer their questions.
    You work for H2Power, a company that provides hydrogen solutions for the energy transition.
    The company is specialysed in creating hydrogen from aluminium.

    You can search any relevant information in the documents. Do not create informations you don't know, always refer to the documents.
    Never give the source in the answer, this is for readability reasons.
    """
    sys_message = SystemMessage(content=context)

    agent_executor = create_conversational_retrieval_agent(
        llm, tools, system_message=sys_message, verbose=True
    )

    return agent_executor


st.set_page_config(page_title="H2Power - Assistant")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

if "conv_id" not in st.session_state:
    firebase.initialize_firebase()
    st.session_state["conv_id"] = firebase.start_conversation()


st.markdown(
    """
<style>.element-container:has(#button-after) + div button {
    height: 150px;
    padding-top: 10px !important;
    padding-bottom: 10px !important;
 }</style>""",
    unsafe_allow_html=True,
)

st.image(Image.open("static/H2P-logo---transparent-2023.png"))
st.title("H2Power - Assistant")

if "agent" not in st.session_state:
    st.session_state.agent = rag_tool_openai()

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

st.markdown('<span id="button-after"></span>', unsafe_allow_html=True)
if "agent" in st.session_state and "start" not in st.session_state:
    cols = st.columns(int(len(questions) / 2))
    for i, question in enumerate(questions):
        if cols[int(i / 2)].button(question):
            st.session_state.start = True
            with st.chat_message("user"):
                st.markdown(question)
            st.session_state.messages.append({"role": "user", "content": question})
            firebase.add_message(st.session_state["conv_id"], "user", question)
            response = st.session_state.agent({"input": question})["output"]
            with st.chat_message("assistant"):
                st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})
            firebase.add_message(st.session_state["conv_id"], "assistant", response)
            st.rerun()

response = ""
# React to user input
if "agent" in st.session_state:
    if prompt := st.chat_input("Another question ?"):
        st.session_state.start = True
        # Display user message in chat message container
        with st.chat_message("user"):
            st.markdown(prompt)
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        firebase.add_message(st.session_state["conv_id"], "user", prompt)
        response = st.session_state.agent({"input": prompt})["output"]

# Display assistant response in chat message container
if "agent" in st.session_state:
    with st.chat_message("assistant"):
        st.markdown(response)

# Add assistant response to chat history
if response:
    st.session_state.messages.append({"role": "assistant", "content": response})
    firebase.add_message(st.session_state["conv_id"], "assistant", response)
