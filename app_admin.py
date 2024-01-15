import streamlit as st
import firebase
import time
from datetime import datetime

st.set_page_config(page_title="H2Power - Admin Portal")

firebase.initialize_firebase()
conversations = firebase.get_all_conversations()
conversations = {
    k: v
    for k, v in sorted(conversations.items(), key=lambda item: -item[1]["timestamp"])
}
conv_ids = list(conversations.keys()) if conversations else []

conv_names = list(range(len(conv_ids)))
conv_dropdown_ids = [i for i in range(len(conv_ids))]
for i, conv_id in enumerate(conv_ids):
    conv = conversations[conv_id]
    dt_object = datetime.fromtimestamp(conv["timestamp"])
    conv["timestamp"] = dt_object.strftime("%d/%m/%Y %H:%M:%S")
    conv_names[i] = f"{conv['timestamp']}"

# Sidebar for filtering
# add button to clear cache
if st.sidebar.button("Refresh"):
    st.cache_data.clear()
    st.rerun()
selected_conversation = st.sidebar.selectbox(
    "Select a conversation", conv_dropdown_ids, format_func=lambda x: conv_names[x]
)

if not conversations:
    st.title("No conversations yet")
else:
    conv = conversations[conv_ids[selected_conversation]]

    st.title(f"Chat History from {conv['timestamp']}")
    if "messages" not in conv:
        st.write("No messages yet")
    else:
        for chat in conv["messages"].values():
            st.markdown(f"**{chat['sender']}:** {chat['message']}")
