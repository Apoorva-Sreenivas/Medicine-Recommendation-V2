import sqlite3

conn = sqlite3.connect("chat.db")
cursor = conn.cursor()



# Insert a message
# cursor.execute("INSERT INTO chat_messages (session_id, sender, message) VALUES (?, ?, ?)",
#                ("session124", "patient", "I feel fine now."))

# conn.commit()

# Fetch and print messages
cursor.execute("SELECT sender, message FROM chat_messages WHERE session_id = ?", ("session1241",))
for row in cursor.fetchall():
    print(row)

conn.close()
