from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity
from app import db
from app.models import User, Meeting, Minute
from app.utils.auth_utils import role_required
from app.utils.notify import send_notification  # ✅ Add this
from datetime import datetime

meeting_bp = Blueprint("meeting", __name__)


# ------------------------------------------------
# ✅ Create a new meeting (Secretary or Chair)
# ------------------------------------------------
@meeting_bp.route("/create", methods=["POST"])
@role_required(["Secretary", "Chairperson"])
def create_meeting():
    user = User.query.get(get_jwt_identity())
    data = request.get_json()

    try:
        meeting = Meeting(
            date=datetime.strptime(data["date"], "%Y-%m-%d %H:%M"),
            location=data["location"],
            description=data.get("description", ""),
            created_by=user.id
        )
        db.session.add(meeting)
        db.session.commit()

        # ✅ Notify all members about upcoming meeting
        all_users = User.query.all()
        for u in all_users:
            send_notification(
                user_id=u.id,
                title="Upcoming Meeting",
                message=f"New meeting scheduled on {meeting.date.strftime('%Y-%m-%d %H:%M')} at {meeting.location}."
            )

        return jsonify(message="Meeting created"), 201

    except Exception as e:
        return jsonify(message=str(e)), 500


# ------------------------------------------------
# ✅ View all upcoming meetings
# ------------------------------------------------
@meeting_bp.route("/upcoming", methods=["GET"])
@role_required(["Member", "Chairperson", "Treasurer", "Secretary"])
def view_meetings():
    upcoming = Meeting.query.order_by(Meeting.date.asc()).all()
    return jsonify([
        {
            "id": m.id,
            "date": m.date.strftime("%Y-%m-%d %H:%M"),
            "location": m.location,
            "description": m.description
        } for m in upcoming
    ]), 200


# ------------------------------------------------
# 📝 Secretary adds minutes for a meeting
# ------------------------------------------------
@meeting_bp.route("/<int:meeting_id>/minute", methods=["POST"])
@role_required(["Secretary"])
def add_minutes(meeting_id):
    user = User.query.get(get_jwt_identity())
    data = request.get_json()

    minutes = Minute(
        meeting_id=meeting_id,
        written_by=user.id,
        content=data["content"]
    )
    db.session.add(minutes)
    db.session.commit()

    # ✅ Notify all members that minutes are ready
    all_users = User.query.all()
    for u in all_users:
        send_notification(
            user_id=u.id,
            title="Meeting Minutes Posted",
            message=f"Minutes for meeting #{meeting_id} are now available."
        )

    return jsonify(message="Minutes saved"), 201


# ------------------------------------------------
# 📖 Members & Admins view minutes of a meeting
# ------------------------------------------------
@meeting_bp.route("/<int:meeting_id>/minutes", methods=["GET"])
@role_required(["Member", "Chairperson", "Secretary", "Treasurer"])
def get_minutes(meeting_id):
    minutes = Minute.query.filter_by(meeting_id=meeting_id).all()

    return jsonify([
        {
            "id": m.id,
            "content": m.content,
            "timestamp": m.timestamp.strftime("%Y-%m-%d %H:%M")
        } for m in minutes
    ]), 200
