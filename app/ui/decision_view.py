import streamlit as st
from config import get_llm
from langchain_core.messages import HumanMessage, SystemMessage
from app.memory.supabase_memory import save_decision, load_decisions
import json, re

DECISION_PROMPT = """You are a structured decision intelligence engine.
Given a question or decision, respond ONLY with valid JSON in this exact format:
{
  "reasoning": "Step-by-step analysis of the situation",
  "options": ["Option A description", "Option B description", "Option C description"],
  "recommendation": "Your top recommendation with clear justification",
  "confidence": 0.85,
  "risks": ["Risk 1", "Risk 2"],
  "next_steps": ["Step 1", "Step 2", "Step 3"]
}
Do not include any text outside the JSON."""

def render_decision_board(session_id: str):
    st.subheader("Decision Intelligence Board")
    st.caption("Powered by Groq (speed layer) — get structured decision analysis in seconds.")

    question = st.text_input(
        "Decision question",
        placeholder="Should we launch product X in Q3 or wait until Q4?"
    )

    col1, col2 = st.columns([1, 3])
    with col1:
        run = st.button("Analyse Decision", type="primary")

    if run and question:
        llm = get_llm("speed")  # Use Groq for fast structured output

        with st.spinner("Analysing..."):
            messages = [
                SystemMessage(content=DECISION_PROMPT),
                HumanMessage(content=f"Decision question: {question}")
            ]
            response = llm.invoke(messages)
            raw = response.content.strip()

        # Parse JSON safely
        try:
            # Strip markdown fences if present
            clean = re.sub(r"```json|```", "", raw).strip()
            data = json.loads(clean)
        except json.JSONDecodeError:
            st.error("Could not parse structured response. Raw output:")
            st.code(raw)
            return

        # Persist
        save_decision(
            session_id, question,
            data.get("reasoning", ""),
            data.get("recommendation", ""),
            data.get("confidence", 0.0)
        )

        # Display
        conf = data.get("confidence", 0)
        st.metric("Confidence", f"{int(conf * 100)}%")

        st.markdown("#### Reasoning")
        st.info(data.get("reasoning", "N/A"))

        st.markdown("#### Options Considered")
        for opt in data.get("options", []):
            st.markdown(f"- {opt}")

        st.markdown("#### Recommendation")
        st.success(data.get("recommendation", "N/A"))

        col_r, col_n = st.columns(2)
        with col_r:
            st.markdown("**Risks**")
            for r in data.get("risks", []):
                st.warning(r)
        with col_n:
            st.markdown("**Next Steps**")
            for s in data.get("next_steps", []):
                st.markdown(f"→ {s}")

    # History
    st.markdown("---")
    st.markdown("### Decision History (this session)")
    decisions = load_decisions(session_id)
    if decisions:
        for d in decisions:
            with st.expander(d["question"][:70]):
                st.markdown(f"**Recommendation:** {d.get('recommendation', 'N/A')}")
                st.markdown(f"**Confidence:** {int((d.get('confidence', 0)) * 100)}%")
    else:
        st.info("No decisions analysed yet.")
