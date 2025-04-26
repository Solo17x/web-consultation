from flask import flash
from models import db, Doctor, Patient, Message, VideoCall
from models import Message, Doctor, Patient
from datetime import datetime

def get_conversation_history(sender_id, recipient_id, sender_type, recipient_type):
    """Fetch the conversation history between sender and recipient"""
    try:
        conversation = Message.query.filter(
            ((Message.sender_id == sender_id) & (Message.recipient_id == recipient_id) & 
             (Message.sender_type == sender_type) & (Message.recipient_type == recipient_type)) |
            ((Message.sender_id == recipient_id) & (Message.recipient_id == sender_id) & 
             (Message.sender_type == recipient_type) & (Message.recipient_type == sender_type))
        ).order_by(Message.timestamp).all()

        formatted_conversation = []
        for msg in conversation:
            sender = (
                Doctor.query.get(msg.sender_id).full_name
                if msg.sender_type == "doctor"
                else Patient.query.get(msg.sender_id).full_name
            )

            formatted_conversation.append({
                "sender": sender.upper(),
                "content": msg.content,
                "timestamp": msg.timestamp.strftime("%Y-%m-%d %H:%M:%S")  # Convert to readable format
            })

        return formatted_conversation
    except Exception as e:
        print(f"Error fetching conversation history: {e}")
        return []
    

def send_message(sender_id, recipient_id, content, sender_type, recipient_type):
    """Send a new message from the sender to the recipient"""
    try:
        sender = Doctor.query.get(sender_id) if sender_type == 'doctor' else Patient.query.get(sender_id)
        recipient = Doctor.query.get(recipient_id) if recipient_type == 'doctor' else Patient.query.get(recipient_id)

        if not sender or not recipient:
            flash("Invalid sender or recipient.", "error")
            return

        # Create message using correct __init__ method
        message = Message(sender=sender, recipient=recipient, content=content)

        db.session.add(message)
        db.session.commit()
        flash("Message sent successfully!", "success")
    except Exception as e:
        print(f"Error sending message: {e}")
        db.session.rollback()
        flash("An error occurred. Please try again.", "error")
