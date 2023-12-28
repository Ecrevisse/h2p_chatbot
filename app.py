from langchain.chat_models import ChatOpenAI
from langchain.agents.agent_toolkits import create_conversational_retrieval_agent
from langchain.agents.agent_toolkits import create_retriever_tool
from dotenv import load_dotenv
import streamlit as st
import os
import pinecone
from langchain.vectorstores import Pinecone

from langchain.schema.messages import SystemMessage
from langchain.embeddings.openai import OpenAIEmbeddings

load_dotenv()
api_key = os.environ["OPENAI_API_KEY"]

questions = [
    "Quels sont les modules ou compétences clés couverts dans la formation LinkedIn Recruiter spécifique au secteur bancaire ?",
    "Comment la formation peut-elle m'aider à améliorer ma stratégie de marque employeur sur LinkedIn pour attirer des talents dans le secteur bancaire ?",
    "Quelles sont les meilleures pratiques enseignées dans la formation pour rédiger des offres d'emploi et des messages d'approche qui se démarquent dans le secteur bancaire ?",
    "Y a-t-il des études de cas ou des retours d'expérience intégrés dans la formation qui illustrent l'application réussie des techniques de recrutement sur LinkedIn dans le secteur bancaire ?",
]


def rag_tool_openai():
    text_field = "text"
    index_name = "h2p"

    index = pinecone.Index(index_name)

    embed = OpenAIEmbeddings(openai_api_key=api_key)

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
        model="gpt-4-1106-preview",
        openai_api_key=api_key,
    )

    context = """
    You are an expert in the hydrogen sector.

    Your role is to help peoples to find relevant information about hydrogen, and to answer their questions.
    You work for H2Power, a company that provides hydrogen solutions for the energy transition.
    The company is specialysed in creating hydrogen from aluminium.

    You can search any relevant information in the documents.
    """
    sys_message = SystemMessage(content=context)

    agent_executor = create_conversational_retrieval_agent(
        llm, tools, system_message=sys_message, verbose=True
    )

    return agent_executor


# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

st.set_page_config(page_title="Assistant pour le recrutement sur LinkedIn")

st.markdown(
    """
<style>.element-container:has(#button-after) + div button {
    height: 150px;
    padding-top: 10px !important;
    padding-bottom: 10px !important;
    backgroundColor: #573666;
    textColor: #ffffff;
 }</style>""",
    unsafe_allow_html=True,
)

img_col0, img_col1 = st.columns(2)
# img_col0.image(Image.open("static/TOMORROW_MORNING_TRANSPARENT-PhotoRoom.png"))
# img_col1.image(Image.open("static/groupe-bpce-logos-idCHAGU1zo.png"))
st.title("Assistant pour le recrutement sur LinkedIn")

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
            response = st.session_state.agent({"input": question})["output"]
            with st.chat_message("assistant"):
                st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})
            st.rerun()

response = ""
# React to user input
if "agent" in st.session_state:
    if prompt := st.chat_input("Encore une question ?"):
        # Display user message in chat message container
        with st.chat_message("user"):
            st.markdown(prompt)
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        response = st.session_state.agent({"input": prompt})["output"]

# Display assistant response in chat message container
if "agent" in st.session_state:
    with st.chat_message("assistant"):
        st.markdown(response)

# Add assistant response to chat history
if response:
    st.session_state.messages.append({"role": "assistant", "content": response})
