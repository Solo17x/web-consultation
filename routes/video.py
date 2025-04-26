from flask import Blueprint, request, jsonify
from models import db, VideoCall
from services.video_call_service import VideoCallService

video_bp = Blueprint("video", __name__)

@video_bp.route("/initiate_call", methods=["POST"])
def initiate_call():
    """Handles the initiation of a video call request."""
    data = request.get_json()
    caller_id = data.get("caller_id")
    caller_role = data.get("caller_role")
    receiver_id = data.get("receiver_id")
    receiver_role = data.get("receiver_role")

    if not all([caller_id, caller_role, receiver_id, receiver_role]):
        return jsonify({"error": "Missing required fields"}), 400

    call = VideoCallService.initiate_call(caller_id, caller_role, receiver_id, receiver_role)
    return jsonify({"message": "Call initiated", "call_id": call.id}), 200

@video_bp.route("/accept_call/<int:call_id>", methods=["POST"])
def accept_call(call_id):
    """Accepts a video call."""
    call = VideoCallService.accept_call(call_id)
    if not call:
        return jsonify({"error": "Call not found or already accepted"}), 404
    return jsonify({"message": "Call accepted", "call_id": call.id}), 200

@video_bp.route("/reject_call/<int:call_id>", methods=["POST"])
def reject_call(call_id):
    """Rejects a video call."""
    call = VideoCallService.reject_call(call_id)
    if not call:
        return jsonify({"error": "Call not found or already rejected"}), 404
    return jsonify({"message": "Call rejected", "call_id": call.id}), 200

@video_bp.route("/end_call/<int:call_id>", methods=["POST"])
def end_call(call_id):
    """Ends an ongoing video call."""
    call = VideoCallService.end_call(call_id)
    if not call:
        return jsonify({"error": "Call not found or not active"}), 404
    return jsonify({"message": "Call ended", "call_id": call.id}), 200
