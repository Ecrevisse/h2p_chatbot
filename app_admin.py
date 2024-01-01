import streamlit as st
import firebase
import time
from datetime import datetime

st.set_page_config(page_title="H2Power - Admin Portal")

firebase.initialize_firebase()
conversations = firebase.get_all_conversations()
conv_ids = list(conversations.keys())

conv_names = {}
for conv_id in conv_ids:
    conv = conversations[conv_id]
    dt_object = datetime.fromtimestamp(conv["timestamp"])
    conv["timestamp"] = dt_object.strftime("%d/%m/%Y %H:%M:%S")
    conv_names[conv_id] = f"{conv['timestamp']} - {conv_id}"

# Sidebar for filtering
# add button to clear cache
if st.sidebar.button("Refresh"):
    st.cache_data.clear()
    st.rerun()
selected_conversation = st.sidebar.selectbox(
    "Select a conversation", conv_ids, format_func=lambda x: conv_names[x]
)

conv = conversations[selected_conversation]

st.title(f"Chat History from {conv['timestamp']}")
if "messages" not in conv:
    st.write("No messages yet")
else:
    for chat in conv["messages"].values():
        st.markdown(f"**{chat['sender']}:** {chat['message']}")
