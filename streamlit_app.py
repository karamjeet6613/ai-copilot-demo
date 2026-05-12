import streamlit as st
import uuid
from app.ui.chat_view import render_chat
from app.ui.agent_view import render_agent_dashboard
from app.ui.decision_view import render_decision_board

st.set_page_config(
    page_title="AI Copilot + Agent System",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Session management — generate unique session ID per browser tab
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())[:8]

session_id = st.session_state.session_id

# Sidebar
with st.sidebar:
    st.title("AI Copilot System")
    st.caption(f"Session: `{session_id}`")
    st.divider()

    view = st.radio(
        "Select Module",
        ["Copilot Chat", "Agent Executor", "Decision Board"],
        captions=["Gemini-powered Q&A", "Autonomous task agent", "Groq speed analysis"]
    )

    st.divider()
    st.markdown("**Stack**")
    st.markdown("- 🧠 Gemini 1.5 Flash")
    st.markdown("- ⚡ Groq Llama 3")
    st.markdown("- 🔗 LangChain ReAct")
    st.markdown("- 🗄 Supabase")
    st.markdown("- 🖥 Streamlit")

    if st.button("Clear Session Memory"):
        st.session_state.messages = []
        st.success("Session cleared.")

# Main content
if view == "Copilot Chat":
    render_chat(session_id)
elif view == "Agent Executor":
    render_agent_dashboard(session_id)
elif view == "Decision Board":
    render_decision_board(session_id)
