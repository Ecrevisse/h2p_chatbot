import firebase_admin
from firebase_admin import credentials, initialize_app, get_app, storage, db
import time
import streamlit as st
from uuid import uuid4


@st.cache_resource
def initialize_firebase():
    if not firebase_admin._apps:
        cred = credentials.Certificate(
            "./h2power-6c703-firebase-adminsdk-ri939-4fbfff0f30.json"
        )
        print("Initializing firebase")
        return initialize_app(
            cred,
            {"databaseURL": "https://h2power-6c703-default-rtdb.firebaseio.com"},
        )


@st.cache_resource
def start_conversation():
    conv_id = str(uuid4())
    conversations = db.reference("conversations")
    conversations.update({conv_id: {"messages": {}, "timestamp": time.time()}})
    return conv_id


def add_message(conv_id, sender, message):
    conversations = db.reference("conversations")
    message_id = "m0"
    messages = conversations.child(conv_id).child("messages").get()
    last_id = -1
    if messages:
        for key in messages.keys():
            if int(key[1:]) > last_id:
                last_id = int(key[1:])
    message_id = f"m{last_id + 1}"

    conversations.update({f"{conv_id}/messages/{message_id}/sender": sender})
    conversations.update({f"{conv_id}/messages/{message_id}/message": message})
