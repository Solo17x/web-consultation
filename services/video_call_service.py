from models import db, VideoCall
from datetime import datetime

class VideoCallService:
    @staticmethod
    def initiate_call(caller_id, caller_role, receiver_id, receiver_role):
        """Creates a new video call request."""
        call = VideoCall(
            caller_id=caller_id,
            caller_role=caller_role,
            receiver_id=receiver_id,
            receiver_role=receiver_role,
            status="Pending"
        )
        db.session.add(call)
        db.session.commit()
        return call

    @staticmethod
    def accept_call(call_id):
        """Marks a call as accepted and starts the session."""
        call = VideoCall.query.get(call_id)
        if call and call.status == "Pending":
            call.status = "Accepted"
            call.start_time = datetime.utcnow()
            db.session.commit()
            return call
        return None

    @staticmethod
    def reject_call(call_id):
        """Marks a call as rejected."""
        call = VideoCall.query.get(call_id)
        if call and call.status == "Pending":
            call.status = "Rejected"
            db.session.commit()
            return call
        return None

    @staticmethod
    def end_call(call_id):
        """Ends a call and records the end time."""
        call = VideoCall.query.get(call_id)
        if call and call.status == "Accepted":
            call.status = "Ended"
            call.end_time = datetime.utcnow()
            db.session.commit()
            return call
        return None
