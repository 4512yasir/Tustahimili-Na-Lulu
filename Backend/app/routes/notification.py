from flask import Blueprint, jsonify
from flask_jwt_extended import get_jwt_identity
from app.models import Notification
from app.utils.auth_utils import role_required

notify_bp = Blueprint("notify", __name__)

# -----------------------------------------
# 🔔 Get my notifications (any role)
# -----------------------------------------
@notify_bp.route("/", methods=["GET"])
@role_required(["Member", "Chairperson", "Treasurer", "Secretary", "RentManager"])
def get_my_notifications():
    user_id = get_jwt_identity()
    notifications = Notification.query.filter_by(user_id=user_id)\
                                      .order_by(Notification.created_at.desc()).all()

    return jsonify([
        {
            "id": n.id,
            "title": n.title,
            "message": n.message,
            "date": n.created_at.strftime("%Y-%m-%d %H:%M"),
            "is_read": n.is_read
        } for n in notifications
    ]), 200
