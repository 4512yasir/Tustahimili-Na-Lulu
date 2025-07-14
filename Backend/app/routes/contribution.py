from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity
from app import db
from app.models import Contribution, User
from app.utils.auth_utils import role_required
from app.utils.notify import send_notification  # ✅ Import this
from datetime import datetime

contrib_bp = Blueprint("contrib", __name__)


# -------------------------------------------
# ✅ Member submits contribution
# -------------------------------------------
@contrib_bp.route("/submit", methods=["POST"])
@role_required(["Member", "Chairperson"])
def submit_contribution():
    user = User.query.get(get_jwt_identity())
    data = request.get_json()

    contribution = Contribution(
        amount=data["amount"],
        date=datetime.strptime(data["date"], "%Y-%m-%d"),
        payment_method=data.get("payment_method", "M-Pesa"),
        receipt_code=data.get("receipt_code", ""),
        person_id=user.person_id,
    )
    db.session.add(contribution)
    db.session.commit()

    # ✅ Notify the user
    send_notification(
        user_id=user.id,
        title="Contribution Received",
        message=f"We received your contribution of KES {contribution.amount} on {contribution.date.strftime('%Y-%m-%d')}."
    )

    return jsonify(message="Contribution recorded successfully"), 201


# -------------------------------------------
# ✅ Member views their contributions
# -------------------------------------------
@contrib_bp.route("/my", methods=["GET"])
@role_required(["Member", "Chairperson"])
def view_my_contributions():
    user = User.query.get(get_jwt_identity())
    records = Contribution.query.filter_by(person_id=user.person_id).all()

    return jsonify([
        {
            "id": c.id,
            "amount": c.amount,
            "date": c.date.strftime("%Y-%m-%d"),
            "payment_method": c.payment_method,
            "receipt_code": c.receipt_code
        } for c in records
    ]), 200


# -------------------------------------------
# ✅ Admins view all contributions
# -------------------------------------------
@contrib_bp.route("/all", methods=["GET"])
@role_required(["Chairperson", "Treasurer"])
def view_all_contributions():
    records = Contribution.query.order_by(Contribution.date.desc()).all()
    return jsonify([
        {
            "member": c.person.full_name,
            "amount": c.amount,
            "date": c.date.strftime("%Y-%m-%d"),
            "payment_method": c.payment_method,
            "receipt_code": c.receipt_code
        } for c in records
    ]), 200
