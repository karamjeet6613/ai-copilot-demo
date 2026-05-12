from langchain.agents import AgentExecutor, create_react_agent
from langchain.prompts import PromptTemplate
from config import get_llm
from app.tools.search_tool import search_tool
from app.tools.calculator_tool import calculator_tool
from app.tools.db_tool import db_tool
from app.memory.supabase_memory import save_message, load_history

# Custom ReAct prompt tuned for Gemini's output style
REACT_PROMPT = PromptTemplate.from_template("""You are Astra, an AI decision-intelligence copilot.

You have access to these tools:
{tools}

Use this EXACT format:

Question: the input question you must answer
Thought: think about what to do
Action: the action to take, must be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
Thought: I now know the final answer from the observation above
Final Answer: the complete answer

CRITICAL RULES:
- After ONE search observation, immediately write "Thought: I now know the final answer" then "Final Answer:"
- NEVER search the same query twice
- NEVER use "None" as an action
- If observation contains relevant info, use it immediately for Final Answer
- Keep Final Answer concise and direct

Begin!

Question: {input}
Thought: {agent_scratchpad}""")

COPILOT_SYSTEM = """You are Astra AI Copilot — an AI decision-intelligence assistant.
1. Use WebSearch for any real-time or factual questions
2. Use Calculator for any math
3. Use DatabaseQuery to fetch stored session data
4. Always explain your reasoning
5. End every response with a clear Recommendation or Summary
"""

def run_copilot(session_id: str, user_input: str) -> dict:
    history = load_history(session_id, limit=10)
    history_text = "\n".join(
        f"{m['role'].upper()}: {m['content']}" for m in history
    )

    full_input = f"{COPILOT_SYSTEM}\n\nPrevious conversation:\n{history_text}\n\nCurrent question: {user_input}"

    tools = [search_tool, calculator_tool, db_tool]

    agent = create_react_agent(
        llm=get_llm("primary"),
        tools=tools,
        prompt=REACT_PROMPT
    )

    executor = AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True,
        max_iterations=3,
        handle_parsing_errors=True,
        return_intermediate_steps=True,
        early_stopping_method="force"
    )

    try:
        result = executor.invoke({"input": full_input})
        output = result.get("output", "No response generated.")
        steps = result.get("intermediate_steps", [])
        save_message(session_id, "user", user_input)
        save_message(session_id, "assistant", output)
        return {"output": output, "steps": steps, "error": None}
    except Exception as e:
        return {
            "output": f"I encountered an error: {str(e)}. Please try rephrasing your question.",
            "steps": [],
            "error": str(e)
        }
