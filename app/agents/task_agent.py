from langchain_classic.agents import AgentExecutor, create_react_agent
from langchain_classic import hub
from config import get_llm, Config
from app.tools.search_tool import search_tool
from app.tools.calculator_tool import calculator_tool
from app.tools.db_tool import db_tool
from app.memory.supabase_memory import save_task
import time

TASK_SYSTEM = """You are an autonomous AI agent. When given a task:
1. Break it down into sub-steps
2. Execute each step using available tools
3. Verify each result before proceeding
4. Compile a final structured report

Be methodical. Show all reasoning. If a tool fails, try an alternative approach.
"""

def run_task_agent(session_id: str, task_description: str) -> dict:
    """Execute an autonomous multi-step task."""
    llm = get_llm("primary")
    tools = [search_tool, calculator_tool, db_tool]
    prompt = hub.pull("hwchase17/react")

    agent = create_react_agent(llm=llm, tools=tools, prompt=prompt)
    executor = AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True,
        max_iterations=Config.MAX_ITERATIONS,
        handle_parsing_errors=True,
        return_intermediate_steps=True
    )

    full_task = f"{TASK_SYSTEM}\n\nTask: {task_description}"

    start = time.time()
    try:
        result = executor.invoke({"input": full_task})
        output = result.get("output", "Task incomplete.")
        steps  = result.get("intermediate_steps", [])
        status = "done"
    except Exception as e:
        output = f"Task failed: {str(e)}"
        steps  = []
        status = "failed"

    elapsed = round(time.time() - start, 2)

    # Format steps for storage
    steps_log = [
        {
            "tool": str(step[0].tool) if hasattr(step[0], 'tool') else "unknown",
            "input": str(step[0].tool_input) if hasattr(step[0], 'tool_input') else "",
            "output": str(step[1])[:500]  # truncate long outputs
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
