import requests

BASE_URL = "http://127.0.0.1:5000"

# 📢 CHAT FUNCTIONALITY
def send_chat_message(sender_id, sender_role, receiver_id, receiver_role, message):
    """Send a chat message to the server."""
    url = f"{BASE_URL}/chat/send_message"
    data = {
        "sender_id": sender_id,
        "sender_role": sender_role,
        "receiver_id": receiver_id,
        "receiver_role": receiver_role,
        "message": message
    }
    response = requests.post(url, json=data)
    
    if response.status_code == 200:
        print("💬 Message sent successfully!")
        print(response.json())
    else:
        print("❌ Message sending failed:", response.text)

def get_chat_history(user_id, user_role, other_id, other_role):
    """Retrieve chat history between two users."""
    url = f"{BASE_URL}/chat/get_chat_history"
    params = {
        "user_id": user_id,
        "user_role": user_role,
        "other_id": other_id,
        "other_role": other_role
    }
    response = requests.get(url, params=params)
    
    if response.status_code == 200:
        print("📜 Chat History:")
        for msg in response.json():
            print(f"{msg['timestamp']} - {msg['sender_role']} {msg['sender_id']} -> {msg['message']}")
    else:
        print("❌ Failed to retrieve chat history:", response.text)


# 📞 VIDEO CALL FUNCTIONALITY
def initiate_video_call(caller_id, caller_role, receiver_id, receiver_role):
    """Initiate a video call request."""
    url = f"{BASE_URL}/video/initiate_call"
    data = {
        "caller_id": caller_id,
        "caller_role": caller_role,
        "receiver_id": receiver_id,
        "receiver_role": receiver_role
    }
    response = requests.post(url, json=data)

    if response.status_code == 200:
        print("📞 Video call initiated successfully!")
        print(response.json())
    else:
        print("❌ Video call initiation failed:", response.text)


# Example Usage
print("\n🔹 Sending a chat message...")
send_chat_message(1, "Doctor", 2, "Patient", "Hello! How are you?")

print("\n🔹 Retrieving chat history...")
get_chat_history(1, "Doctor", 2, "Patient")

print("\n🔹 Initiating a video call...")
initiate_video_call(1, "Doctor", 2, "Patient")
