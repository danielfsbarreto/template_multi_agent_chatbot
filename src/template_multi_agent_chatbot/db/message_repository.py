from template_multi_agent_chatbot.db.connection import get_connection
from template_multi_agent_chatbot.types import Message


class MessageRepository:
    def find_by_conversation(self, conversation_id: str) -> list[Message]:
        conn = get_connection()
        rows = conn.execute(
            "SELECT role, content FROM messages WHERE conversation_id = ? ORDER BY id ASC",
            (conversation_id,),
        ).fetchall()
        conn.close()
        return [Message(role=r["role"], content=r["content"]) for r in rows]

    def add(self, conversation_id: str, message: Message) -> None:
        conn = get_connection()
        conn.execute(
            "INSERT INTO messages (conversation_id, role, content) VALUES (?, ?, ?)",
            (conversation_id, message.role, message.content),
        )
        conn.commit()
        conn.close()
