import json
from datetime import datetime

import streamlit as st
import ollama

st.set_page_config(page_title="My Local LLM Chat", layout="wide")


# Initialize Session State

if "history" not in st.session_state:
    st.session_state.history = []  # current chat
if "conversations" not in st.session_state:
    st.session_state.conversations = []  # saved chats
if "current_title" not in st.session_state:
    st.session_state.current_title = "Untitled"


# Sidebar

with st.sidebar:
    st.header("Conversations")

    choice = st.selectbox(
        "Open",
        ["New conversation"] + [c["title"] for c in st.session_state.conversations],
    )

    if choice != "New conversation":
        for c in st.session_state.conversations:
            if c["title"] == choice:
                st.session_state.history = c["history"].copy()
                st.session_state.current_title = c["title"]
                st.success(f'Loaded "{c["title"]}"')
                break

    st.text_input("Conversation title", key="current_title")

    if st.button("Save conversation"):
        title = st.session_state.current_title or f"Conv {len(st.session_state.conversations) + 1}"
        st.session_state.conversations.append({
            "title": title,
            "history": st.session_state.history.copy(),
            "saved_at": datetime.utcnow().isoformat() + "Z"
        })
        st.success(f'Saved "{title}"')

    if st.button("Reset all saved"):
        st.session_state.conversations = []
        st.success("All saved conversations removed")

    if st.session_state.history:
        st.download_button(
            "Download current conversation (JSON)",
            data=json.dumps(st.session_state.history, indent=2),
            file_name=f"{st.session_state.current_title}.json",
            mime="application/json",
        )


# Main Chat Area

st.title("My Local LLM Chat")

col1, col2 = st.columns([3, 1])

with col1:

    # Chat input form (auto clears on rerun)
    with st.form(key="chat_form"):
        user_input = st.text_input(
            "Ask me something:",
            placeholder="Type your question and press Enter or click Send",
        )
        submit = st.form_submit_button("Send")

        if submit and user_input.strip():

            try:
                with st.spinner("Thinking..."):
                    response = ollama.chat(
                        model="tinyllama",
                        messages=[{"role": "user", "content": user_input}]
                    )
                bot_reply = response.get("message", {}).get("content", "<no response>")

            except Exception as e:
                bot_reply = f"Error: {e}"

            # Save messages
            st.session_state.history.append({
                "user": user_input,
                "bot": bot_reply,
                "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })

            st.rerun()  # <-- NEW Streamlit function (fully supported)

    # Chat clear/reset
    c1, c2 = st.columns(2)
    if c1.button("Clear chat"):
        st.session_state.history = []
        st.rerun()

    if c2.button("Reset (clear everything)"):
        st.session_state.history = []
        st.session_state.conversations = []
        st.session_state.current_title = "Untitled"
        st.rerun()

with col2:
    st.markdown("### Info")
    st.write("• Press Enter to send.")
    st.write("• Save conversations from sidebar.")
    st.write("• Download chats as JSON.")


# Chat Display

for msg in st.session_state.history:
    st.markdown("---")
    st.write(f"**You** ({msg['time']}):")
    st.info(msg["user"], icon="🧑")
    st.write(f"**Bot** ({msg['time']}):")
    st.success(msg["bot"], icon="🤖")
