from langchain.tools import Tool
from app.memory.supabase_memory import client

def query_database(query: str) -> str:
    """
    Simple structured query tool. Accepts commands like:
    'tasks:session_id' or 'decisions:session_id'
    """
    try:
        # Strip quotes the agent sometimes adds
        query = query.strip().strip("'\"")
        parts = query.split(":")
        if len(parts) < 2:
            return "Format: 'table_name:session_id' — e.g. 'agent_tasks:abc123'"
        table = parts[0].strip().strip("'\"")
        session_id = parts[1].strip().strip("'\"")

        # Handle 'all' as a wildcard - fetch recent records
        if session_id.lower() == "all":
            result = client.table(table).select("*").limit(5).execute()
        else:
            result = client.table(table).select("*").eq("session_id", session_id).limit(5).execute()

        if not result.data:
            return f"No records found in {table}"
        return "\n".join(str(row) for row in result.data)
    except Exception as e:
        return f"DB query error: {str(e)}"

db_tool = Tool(
    name="DatabaseQuery",
    func=query_database,
    description="Query Supabase database. Input format: table_name:session_id — e.g. conversations:abc123. Use 'all' as session_id to fetch recent records."
)
