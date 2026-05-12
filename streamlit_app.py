import streamlit as st
import uuid
from app.ui.chat_view import render_chat
from app.ui.agent_view import render_agent_dashboard
from app.ui.decision_view import render_decision_board

st.set_page_config(
    page_title="Astra AI Copilot",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    [data-testid="stSidebar"] { min-width: 260px; }
    .stChatMessage { border-radius: 12px; margin-bottom: 8px; }
    div[data-testid="stSidebarNav"] { display: none; }
    .powered-bar {
        font-size: 0.72rem;
        color: #888;
        padding: 6px 0 12px 0;
        letter-spacing: 0.03em;
    }
</style>
""", unsafe_allow_html=True)

# Session management
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())[:8]

session_id = st.session_state.session_id

# Sidebar
with st.sidebar:
    view = st.radio(
        "Navigate",
        ["Copilot Chat", "Agent Executor", "Decision Board"],
        label_visibility="collapsed"
    )
    st.divider()

# Powered by bar — shown at top of main area subtly
st.markdown("""
<div class="powered-bar">
✦ Gemini 1.5 Flash &nbsp;·&nbsp; Groq Llama 3 &nbsp;·&nbsp; LangChain ReAct &nbsp;·&nbsp; Supabase &nbsp;·&nbsp; Tavily Search
</div>
""", unsafe_allow_html=True)

# Route to selected view
if "Copilot Chat" in view:
    render_chat(session_id)
elif "Agent Executor" in view:
    render_agent_dashboard(session_id)
elif "Decision Board" in view:
    render_decision_board(session_id)