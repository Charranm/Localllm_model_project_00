import sqlite3
import ollama
import pandas as pd

DB = "data/shop.db"
MODEL = "gemma4:e4b"   # try "qwen3:8b" later


def get_schema() -> str:
    conn = sqlite3.connect(DB)
    rows = conn.execute("SELECT sql FROM sqlite_master WHERE type='table'").fetchall()
    conn.close()
    return "\n\n".join(r[0] for r in rows)


def run_sql(query: str) -> str:
    """Run a read-only SQLite SELECT query on the shop database and return the rows.

    Args:
        query: A single SQLite SELECT statement.
    """
    q = query.strip().rstrip(";")
    if not q.lower().startswith(("select", "with")) or ";" in q:
        return "Error: only a single SELECT query is allowed."
    try:
        conn = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)  # read-only connection
        df = pd.read_sql_query(q, conn)
        conn.close()
        return df.head(50).to_string(index=False)
    except Exception as e:
        return f"SQL error: {e}"


SYSTEM = f"""You are a data analyst assistant. Answer questions about the database below
by calling the run_sql tool. Use SQLite syntax. If a query returns an error, fix it and try again.
Never invent numbers; base every answer only on tool results.

Schema:
{get_schema()}"""


def ask(messages: list) -> tuple[str, list]:
    """Returns (answer, list_of_sql_queries_used)."""
    sqls = []
    for _ in range(5):  # max 5 tool-call rounds
        resp = ollama.chat(model=MODEL, messages=messages, tools=[run_sql],
                           options={"temperature": 0})
        messages.append(resp.message)
        if not resp.message.tool_calls:
            return resp.message.content, sqls
        for call in resp.message.tool_calls:
            args = call.function.arguments
            if call.function.name == "run_sql":
                sqls.append(args.get("query", ""))
                result = run_sql(**args)
            else:
                result = "Unknown tool."
            messages.append({"role": "tool", "tool_name": call.function.name, "content": result})
    return "I couldn't get a reliable answer after several attempts.", sqls


if __name__ == "__main__":
    history = [{"role": "system", "content": SYSTEM}]
    print("Ask about the shop data (type 'exit' to quit)")
    while True:
        q = input("\nYou: ")
        if q.lower() == "exit":
            break
        history.append({"role": "user", "content": q})
        answer, sqls = ask(history)
        for s in sqls:
            print(f"\n[SQL] {s}")
        print(f"\nAgent: {answer}")