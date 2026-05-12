from supabase import create_client
from config import Config
import json

client = create_client(Config.SUPABASE_URL, Config.SUPABASE_ANON_KEY)

def save_message(session_id: str, role: str, content: str):
    """Save a single chat message to Supabase."""
    client.table("conversations").insert({
        "session_id": session_id,
        "role": role,
        "content": content
    }).execute()

def load_history(session_id: str, limit: int = 20):
    """Load last N messages for a session."""
    result = client.table("conversations") \
        .select("role, content") \
        .eq("session_id", session_id) \
        .order("created_at", desc=False) \
        .limit(limit) \
        .execute()
    return result.data or []

def save_task(session_id: str, task_input: str, steps: list, output: str, status: str):
    """Persist agent task execution record."""
    client.table("agent_tasks").insert({
        "session_id": session_id,
        "task_input": task_input,
        "agent_steps": json.dumps(steps),
        "final_output": output,
        "status": status
    }).execute()

def load_tasks(session_id: str, limit: int = 10):
    """Load recent agent tasks for a session."""
    result = client.table("agent_tasks") \
        .select("*") \
        .eq("session_id", session_id) \
        .order("created_at", desc=True) \
        .limit(limit) \
        .execute()
    return result.data or []

def save_decision(session_id: str, question: str, reasoning: str,
                  recommendation: str, confidence: float):
    """Log a decision intelligence entry."""
    client.table("decisions").insert({
        "session_id": session_id,
        "question": question,
        "reasoning": reasoning,
        "recommendation": recommendation,
        "confidence": confidence
    }).execute()

def load_decisions(session_id: str):
    result = client.table("decisions") \
        .select("*") \
        .eq("session_id", session_id) \
        .order("created_at", desc=True) \
        .execute()
    return result.data or []
import uuid as uuid_lib

def create_new_chat(session_id: str, title: str = "New Chat") -> str:
    """Create a new named chat session and return its chat_id."""
    chat_id = str(uuid_lib.uuid4())[:8]
    client.table("conversations").insert({
        "session_id": session_id,
        "role": "system",
        "content": f"__CHAT_TITLE__:{title}",
        "chat_id": chat_id
    }).execute()
    return chat_id

def load_chats(session_id: str) -> list:
    """Load all distinct chat sessions for a user."""
    result = client.table("conversations") \
        .select("chat_id, content, created_at") \
        .eq("session_id", session_id) \
        .eq("role", "system") \
        .order("created_at", desc=True) \
        .execute()
    chats = []
    for row in (result.data or []):
        title = row["content"].replace("__CHAT_TITLE__:", "")
        chats.append({
            "chat_id": row["chat_id"],
            "title": title,
            "created_at": row["created_at"]
        })
    return chats

def load_chat_messages(chat_id: str) -> list:
    """Load all messages for a specific chat_id."""
    result = client.table("conversations") \
        .select("role, content, created_at") \
        .eq("chat_id", chat_id) \
        .neq("role", "system") \
        .order("created_at", desc=False) \
        .execute()
    return result.data or []

def delete_chat(chat_id: str):
    """Delete all messages for a chat_id."""
    client.table("conversations") \
        .delete() \
        .eq("chat_id", chat_id) \
        .execute()

def save_message_to_chat(session_id: str, chat_id: str, role: str, content: str):
    """Save a message linked to a specific chat_id."""
    client.table("conversations").insert({
        "session_id": session_id,
        "chat_id": chat_id,
        "role": role,
        "content": content
    }).execute()
