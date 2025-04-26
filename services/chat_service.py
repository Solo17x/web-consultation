from models import db, ChatMessage
from datetime import datetime

class ChatService:
    @staticmethod
    def send_message(sender_id, sender_role, receiver_id, receiver_role, message):
        """Saves a new chat message to the database."""
        chat = ChatMessage(
            sender_id=sender_id,
            sender_role=sender_role,
            receiver_id=receiver_id,
            receiver_role=receiver_role,
            message=message,
            timestamp=datetime.utcnow(),
            is_read=False
        )
        db.session.add(chat)
        db.session.commit()
        return chat

    @staticmethod
    def get_chat_history(user_id, user_role, other_id, other_role):
        """Retrieves chat messages between two users."""
        messages = ChatMessage.query.filter(
            ((ChatMessage.sender_id == user_id) & (ChatMessage.sender_role == user_role) & 
             (ChatMessage.receiver_id == other_id) & (ChatMessage.receiver_role == other_role)) |
            ((ChatMessage.sender_id == other_id) & (ChatMessage.sender_role == other_role) & 
             (ChatMessage.receiver_id == user_id) & (ChatMessage.receiver_role == user_role))
        ).order_by(ChatMessage.timestamp.asc()).all()
        return messages

    @staticmethod
    def mark_messages_as_read(user_id, sender_id):
        """Marks messages from a specific sender as read."""
        unread_messages = ChatMessage.query.filter_by(receiver_id=user_id, sender_id=sender_id, is_read=False).all()
        for msg in unread_messages:
            msg.is_read = True
        db.session.commit()
