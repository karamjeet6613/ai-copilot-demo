from langchain.agents import AgentExecutor, create_react_agent
from langchain.prompts import PromptTemplate
from config import get_llm
from app.tools.search_tool import search_tool
from app.tools.calculator_tool import calculator_tool
from app.tools.db_tool import db_tool
from app.memory.supabase_memory import save_message, load_history

REACT_PROMPT = PromptTemplate.from_template("""You are Astra, an AI decision-intelligence copilot.

You have access to these tools:
{tools}

Use this EXACT format:

Question: the input question you must answer
Thought: think about what to do
Action: the action to take, must be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
Thought: I now know the final answer
Final Answer: the complete answer

CRITICAL RULES:
- After getting search results, IMMEDIATELY write "Thought: I now know the final answer" then "Final Answer:"
- NEVER search more than once per sub-question
- NEVER use "None" as an action — always use WebSearch, Calculator or DatabaseQuery
- Extract the answer directly from the Observation
- Final Answer must be a complete, direct response

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
def run_copilot(session_id: str, user_input: str, mode: str = "balanced") -> dict:
    import time
    
    history = load_history(session_id, limit=10)
    history_text = "\n".join(
        f"{m['role'].upper()}: {m['content']}" for m in history
    )

    full_input = f"{COPILOT_SYSTEM}\n\nPrevious conversation:\n{history_text}\n\nCurrent question: {user_input}"

    tools = [search_tool, calculator_tool, db_tool]

    agent = create_react_agent(
        llm=get_llm(mode),
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

    start_time = time.time()

    try:
        result = executor.invoke({"input": full_input})
        output = result.get("output", "No response generated.")
        steps = result.get("intermediate_steps", [])

        latency = round(time.time() - start_time, 2)

        # Exact token counting using tiktoken
        import tiktoken
        try:
            enc = tiktoken.get_encoding("cl100k_base")
            input_tokens  = len(enc.encode(full_input))
            output_tokens = len(enc.encode(output))
            total_tokens  = input_tokens + output_tokens
        except Exception:
            input_tokens  = int(len(full_input.split()) * 1.3)
            output_tokens = int(len(output.split()) * 1.3)
            total_tokens  = input_tokens + output_tokens

        # Cost calculation (Groq pricing)
        input_cost  = (input_tokens / 1_000_000) * 0.07
        output_cost = (output_tokens / 1_000_000) * 0.30
        total_cost  = round(input_cost + output_cost, 6)

        # Confidence approximation
        iterations_used = len(steps)
        max_iter = 3
        temp = 0.1 if mode == "agent" else 0.4
        confidence = round(
            max(0.5, 1 - (iterations_used / max_iter) * temp), 2
        )

        # Tools used
        tools_used = list(set(
            getattr(step[0], "tool", "Thought")
            for step in steps
            if getattr(step[0], "tool", None)
        ))

        # Success check
        success = "Agent stopped" not in output and output != "No response generated."

        metrics = {
            "latency": latency,
            "input_tokens": int(input_tokens),
            "output_tokens": int(output_tokens),
            "total_tokens": total_tokens,
            "total_cost": total_cost,
            "confidence": confidence,
            "iterations_used": iterations_used,
            "tools_used": tools_used,
            "model": "llama-3.3-70b-versatile",
            "mode": mode,
            "success": success
        }

        save_message(session_id, "user", user_input)
        save_message(session_id, "assistant", output)

        return {
            "output": output,
            "steps": steps,
            "error": None,
            "metrics": metrics
        }

    except Exception as e:
        latency = round(time.time() - start_time, 2)
        return {
            "output": f"I encountered an error: {str(e)}. Please try rephrasing.",
            "steps": [],
            "error": str(e),
            "metrics": {
                "latency": latency,
                "input_tokens": 0,
                "output_tokens": 0,
                "total_tokens": 0,
                "total_cost": 0,
                "confidence": 0,
                "iterations_used": 0,
                "tools_used": [],
                "model": "llama-3.3-70b-versatile",
                "mode": mode,
                "success": False
            }
        }