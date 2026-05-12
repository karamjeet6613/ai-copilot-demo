from langchain_classic.agents import AgentExecutor, create_react_agent
from langchain_classic.prompts import PromptTemplate
from config import get_llm
from app.tools.search_tool import search_tool
from app.tools.calculator_tool import calculator_tool
from app.tools.db_tool import db_tool
from app.memory.supabase_memory import save_message, load_history

COPILOT_SYSTEM = """You are an AI decision copilot. 
IMPORTANT: For general knowledge questions, answer directly without using tools.
Only use tools for: current prices, live data, math calculations, or database queries.
Be concise. End with a brief Recommendation."""

REACT_PROMPT = PromptTemplate.from_template("""Answer the following questions as best you can. You have access to the following tools:

{tools}

Use the following format EXACTLY:

Question: the input question you must answer
Thought: you should always think about what to do
Action: the tool to use, must be exactly one of [{tool_names}]
Action Input: the input to the tool
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

Begin!

Question: {input}
Thought: Let me think about whether I need a tool or can answer directly.
{agent_scratchpad}""")

def build_copilot(session_id: str):
    llm = get_llm("primary")
    tools = [search_tool, calculator_tool, db_tool]

    agent = create_react_agent(llm=llm, tools=tools, prompt=REACT_PROMPT)

    executor = AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True,
        max_iterations=10,
        handle_parsing_errors=True,
        return_intermediate_steps=True
    )
    return executor

def run_copilot(session_id: str, user_input: str) -> dict:
    """Run the copilot and return response + steps."""
    history = load_history(session_id, limit=3)
    history_text = "\n".join(f"{m['role'].upper()}: {m['content']}" for m in history)

    full_input = f"""Previous conversation:
{history_text}

Current question: {user_input}

{COPILOT_SYSTEM}"""

    executor = build_copilot(session_id)

    try:
        result = executor.invoke({"input": full_input})
        output = result.get("output", "")
        steps  = result.get("intermediate_steps", [])

        # If agent stopped early, extract best result from steps
        if not output and steps:
            last_step = steps[-1]
            output = f"Best result found:\n{last_step[1]}"
        elif not output:
            output = "No response generated."

        save_message(session_id, "user", user_input)
        save_message(session_id, "assistant", output)

        return {"output": output, "steps": steps, "error": None}
    except Exception as e:
        return {"output": f"Agent error: {str(e)}", "steps": [], "error": str(e)}
