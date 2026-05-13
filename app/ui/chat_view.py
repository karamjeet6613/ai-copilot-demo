import streamlit as st
from app.agents.copilot_agent import run_copilot
from app.memory.supabase_memory import (
    create_new_chat, load_chats, load_chat_messages,
    delete_chat, save_message_to_chat
)

def render_chat(session_id: str):

    # ── Sidebar: chat history panel ──────────────────────────────────────
    with st.sidebar:
        st.markdown("**Chats**")

        if st.button("＋ New Chat", use_container_width=True, type="primary"):
            chat_id = create_new_chat(session_id, title="New Chat")
            st.session_state.active_chat_id = chat_id
            st.session_state.messages = []
            st.rerun()

        # Load all chats for this session from Supabase
        chats = load_chats(session_id)

        if not chats:
            st.caption("No chats yet. Start one above.")
        else:
            for chat in chats:
                col1, col2 = st.columns([4, 1])
                is_active = st.session_state.get("active_chat_id") == chat["chat_id"]

                with col1:
                    label = f"**{chat['title']}**" if is_active else chat["title"]
                    if st.button(
                        label,
                        key=f"chat_{chat['chat_id']}",
                        use_container_width=True
                    ):
                        st.session_state.active_chat_id = chat["chat_id"]
                        # Load messages from Supabase into session state
                        msgs = load_chat_messages(chat["chat_id"])
                        st.session_state.messages = msgs
                        st.rerun()

                with col2:
                    if st.button(
                        "🗑",
                        key=f"del_{chat['chat_id']}",
                        help="Delete this chat"
                    ):
                        delete_chat(chat["chat_id"])
                        if st.session_state.get("active_chat_id") == chat["chat_id"]:
                            st.session_state.active_chat_id = None
                            st.session_state.messages = []
                        st.rerun()

    # ── Main area ────────────────────────────────────────────────────────
    st.subheader("🌟 Astra AI Copilot")
    st.caption("Ask anything — Astra reasons, searches, and recommends.")

    mode = "balanced"

    # Auto-create a chat if none is active
    if not st.session_state.get("active_chat_id"):
        chat_id = create_new_chat(session_id, title="Chat 1")
        st.session_state.active_chat_id = chat_id
        st.session_state.messages = []

    active_chat_id = st.session_state.active_chat_id

    # Load from Supabase if messages not in session state
    # This fixes the refresh bug — messages survive page reloads
    if "messages" not in st.session_state or not st.session_state.messages:
        if active_chat_id:
            st.session_state.messages = load_chat_messages(active_chat_id)

    # Render existing messages
    for msg in st.session_state.get("messages", []):
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Chat input
    if user_input := st.chat_input("Ask Astra anything..."):

        # Auto-title the chat from first message
        chats = load_chats(session_id)
        current = next(
            (c for c in chats if c["chat_id"] == active_chat_id), None
        )
        if current and current["title"] in ("New Chat", "Chat 1"):
            short_title = user_input[:40] + ("..." if len(user_input) > 40 else "")
            from app.memory.supabase_memory import client
            client.table("conversations") \
                .update({"content": f"__CHAT_TITLE__:{short_title}"}) \
                .eq("chat_id", active_chat_id) \
                .eq("role", "system") \
                .execute()

        # Show and save user message
        with st.chat_message("user"):
            st.markdown(user_input)
        save_message_to_chat(session_id, active_chat_id, "user", user_input)
        st.session_state.messages.append({"role": "user", "content": user_input})

        # Run agent and show response
        with st.chat_message("assistant"):
            with st.spinner("Astra is thinking..."):
                result = run_copilot(session_id, user_input, mode=mode)

            output = result["output"]
            steps = result["steps"]

            st.markdown(output)

            if steps:
                with st.expander(f"🔍 Astra's reasoning — {len(steps)} step(s)"):
                    for i, step in enumerate(steps, 1):
                        action = step[0]
                        obs = step[1]
                        tool_name = getattr(action, "tool", "Thought")
                        tool_input = getattr(action, "tool_input", "")
                        st.markdown(f"**Step {i}: {tool_name}**")
                        if tool_input:
                            st.code(str(tool_input), language="text")
                        st.caption(f"Result: {str(obs)[:400]}")

        save_message_to_chat(session_id, active_chat_id, "assistant", output)
        st.session_state.messages.append({"role": "assistant", "content": output})
