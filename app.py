import streamlit as st

from rag_core import get_query_engine, ask_question
from chat_history import load_chat_history, clear_chat_history


st.set_page_config(
    page_title="LlamaIndex Qdrant RAG",
    page_icon="🧠",
    layout="wide",
)

st.title("🧠 LlamaIndex + Qdrant RAG Chatbot")

st.write(
    "Add documents inside the `data/` folder, run `python ingest.py`, then ask questions here."
)


@st.cache_resource
def load_query_engine():
    return get_query_engine()


try:
    query_engine = load_query_engine()
except Exception as e:
    st.error(f"Failed to load query engine: {e}")
    st.stop()


if "messages" not in st.session_state:
    st.session_state.messages = load_chat_history()


if st.sidebar.button("Clear Chat History"):
    clear_chat_history()
    st.session_state.messages = []
    st.rerun()


for message in st.session_state.messages:
    role = message.get("role", "assistant")
    content = message.get("content", "")

    with st.chat_message(role):
        st.write(content)

        sources = message.get("sources", [])
        if role == "assistant" and sources:
            with st.expander("Sources"):
                for i, source in enumerate(sources, start=1):
                    st.markdown(f"**Source {i}**")
                    st.write(f"File: {source.get('file', 'unknown')}")
                    st.write(f"Page: {source.get('page', 'N/A')}")
                    st.write(f"Score: {source.get('score', 'N/A')}")
                    st.write(source.get("text", ""))
                    st.divider()


user_question = st.chat_input("Ask a question from your documents...")

if user_question:
    st.session_state.messages.append(
        {
            "role": "user",
            "content": user_question,
        }
    )

    with st.chat_message("user"):
        st.write(user_question)

    with st.chat_message("assistant"):
        with st.spinner("Searching Qdrant and generating answer..."):
            try:
                answer, sources = ask_question(
                    question=user_question,
                    query_engine=query_engine,
                    save_history=True,
                )

                st.write(answer)

                if sources:
                    with st.expander("Sources"):
                        for i, source in enumerate(sources, start=1):
                            st.markdown(f"**Source {i}**")
                            st.write(f"File: {source.get('file', 'unknown')}")
                            st.write(f"Page: {source.get('page', 'N/A')}")
                            st.write(f"Score: {source.get('score', 'N/A')}")
                            st.write(source.get("text", ""))
                            st.divider()

                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": answer,
                        "sources": sources,
                    }
                )

            except Exception as e:
                error_message = f"Something went wrong: {e}"
                st.error(error_message)

                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": error_message,
                        "sources": [],
                    }
                )