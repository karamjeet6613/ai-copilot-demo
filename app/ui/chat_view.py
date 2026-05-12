import streamlit as st
from app.agents.copilot_agent import run_copilot

def render_chat(session_id: str):
    st.subheader("AI Copilot — Decision Intelligence")
    st.caption("Ask anything. The copilot will reason, search, calculate, and recommend.")

    # Display message history from session state
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Input
    if user_input := st.chat_input("Ask a question or describe a decision you need help with..."):
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                result = run_copilot(session_id, user_input)

            output = result["output"]
            steps  = result["steps"]

            st.markdown(output)

            # Show reasoning steps in an expander
            if steps:
                with st.expander(f"Agent reasoning — {len(steps)} step(s)"):
                    for i, step in enumerate(steps, 1):
                        action = step[0]
                        obs    = step[1]
                        st.markdown(f"**Step {i}: {getattr(action, 'tool', 'Thought')}**")
                        st.code(str(getattr(action, 'tool_input', '')), language="text")
                        st.info(f"Result: {str(obs)[:400]}")

        st.session_state.messages.append({"role": "assistant", "content": output})
