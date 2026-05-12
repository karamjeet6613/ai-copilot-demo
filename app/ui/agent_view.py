import streamlit as st
from app.agents.task_agent import run_task_agent
from app.memory.supabase_memory import load_tasks

def render_agent_dashboard(session_id: str):
    st.subheader("Astra - Agent Execution Layer — Autonomous Tasks")
    st.caption("Define a multi-step task. The agent will plan, execute, and report back.")

    with st.form("task_form"):
        task = st.text_area(
            "Task description",
            placeholder="e.g. Research the top 3 Python web frameworks, compare their GitHub stars and latest versions, then recommend the best one for a startup.",
            height=100
        )
        submitted = st.form_submit_button("Run Agent Task")

    if submitted and task:
        with st.spinner("Agent is executing... this may take 30-60 seconds."):
            result = run_task_agent(session_id, task)

        st.success(f"Task completed in {result['elapsed']}s — Status: {result['status']}")

        st.markdown("### Final Output")
        st.markdown(result["output"])

        if result["steps"]:
            st.markdown("### Execution Steps")
            for i, step in enumerate(result["steps"], 1):
                with st.expander(f"Step {i} — Tool: {step.get('tool', 'N/A')}"):
                    st.write("**Input:**", step.get("input", ""))
                    st.write("**Output:**", step.get("output", ""))

    # Show task history
    st.markdown("---")
    st.markdown("### Past Tasks (this session)")
    tasks = load_tasks(session_id, limit=5)
    if tasks:
        for t in tasks:
            status_emoji = {"done": "✅", "failed": "❌", "running": "⏳"}.get(t.get("status", ""), "⏳")
            with st.expander(f"{status_emoji} {t['task_input'][:60]}..."):
                st.write(t.get("final_output", "No output yet"))
    else:
        st.info("No tasks yet. Run your first agent task above.")
