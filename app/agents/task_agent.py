from langchain.agents import AgentExecutor, create_react_agent
from langchain.prompts import PromptTemplate
from config import get_llm, Config
from app.tools.search_tool import search_tool
from app.tools.calculator_tool import calculator_tool
from app.tools.db_tool import db_tool
from app.memory.supabase_memory import save_task
import time

REACT_PROMPT = PromptTemplate.from_template("""You are Astra, an autonomous AI task execution agent.

You have access to these tools:
{tools}

Use this EXACT format — never deviate:

Question: the input question you must answer
Thought: think step by step about what to do
Action: the action to take, must be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (repeat Thought/Action/Action Input/Observation as needed)
Thought: I now know the final answer
Final Answer: a detailed structured report of what was found and done

RULES:
- Always write "Action Input:" immediately after "Action:" on a new line
- Never skip Action Input
- Be methodical — verify each result before the next step
- Only use: [{tool_names}]

Begin!

Question: {input}
Thought: {agent_scratchpad}""")

def run_task_agent(session_id: str, task_description: str) -> dict:
    tools = [search_tool, calculator_tool, db_tool]

    agent = create_react_agent(
        llm=get_llm("agent"),
        tools=tools,
        prompt=REACT_PROMPT
    )

    executor = AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True,
        max_iterations=Config.MAX_ITERATIONS,
        handle_parsing_errors=True,
        return_intermediate_steps=True,
        early_stopping_method="generate"
    )

    start = time.time()
    try:
        result = executor.invoke({"input": task_description})
        output = result.get("output", "Task incomplete.")
        steps = result.get("intermediate_steps", [])
        status = "done"
    except Exception as e:
        output = f"Task failed: {str(e)}"
        steps = []
        status = "failed"

    elapsed = round(time.time() - start, 2)

    steps_log = [
        {
            "tool": str(step[0].tool) if hasattr(step[0], "tool") else "Thought",
            "input": str(step[0].tool_input) if hasattr(step[0], "tool_input") else "",
            "output": str(step[1])[:500]
        }
        for step in steps
    ]

    save_task(session_id, task_description, steps_log, output, status)

    return {
        "output": output,
        "steps": steps_log,
        "status": status,
        "elapsed": elapsed
    }
