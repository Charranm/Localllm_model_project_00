import streamlit as st
from agent import ask, SYSTEM

st.title("Chat with your data")

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": SYSTEM}]
    st.session_state.display = []

for role, text in st.session_state.display:
    st.chat_message(role).write(text)

if prompt := st.chat_input("Ask a question about the shop data"):
    st.chat_message("user").write(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.spinner("Thinking..."):
        answer, sqls = ask(st.session_state.messages)
    with st.chat_message("assistant"):
        for s in sqls:
            st.code(s, language="sql")
        st.write(answer)
    st.session_state.display += [("user", prompt), ("assistant", answer)]