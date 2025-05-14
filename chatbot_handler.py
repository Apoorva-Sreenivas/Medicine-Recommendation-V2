# chatbot_handler.py
import sqlite3
from llm_response import llama3_2_mem

DB_PATH = 'chatbot.db'

def init_chat_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS chat_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id TEXT,
            message_type TEXT,
            message_content TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def save_message(patient_id, role, content):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO chat_history (patient_id, message_type, message_content) VALUES (?, ?, ?)",
        (patient_id, role, content)
    )
    conn.commit()
    conn.close()

def get_recent_messages(patient_id, limit=5):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT message_type, message_content FROM chat_history WHERE patient_id = ? ORDER BY timestamp DESC LIMIT ?",
        (patient_id, limit)
    )
    messages = cursor.fetchall()
    conn.close()
    return [{"role": role, "content": content} for role, content in reversed(messages)]

def chat_with_llm(patient_id, user_input):
    history = get_recent_messages(patient_id)
    history.append({"role": "user", "content": user_input})
    reply = llama3_2_mem(history)
    save_message(patient_id, "user", user_input)
    save_message(patient_id, "assistant", reply)
    return reply


if __name__ == "__main__":
    init_chat_db()