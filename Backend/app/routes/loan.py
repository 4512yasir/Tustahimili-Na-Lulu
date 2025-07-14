from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity
from datetime import datetime
from app import db
from app.models import User, Loan, Person
from app.utils.auth_utils import role_required
from app.utils.notify import send_notification  # ✅ Notification function

loan_bp = Blueprint("loan", __name__)


# -------------------------------------------
# 📌 Member requests a loan
# -------------------------------------------
@loan_bp.route("/request", methods=["POST"])
@role_required(["Member", "Chairperson"])
def request_loan():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    data = request.get_json()
    loan = Loan(
        amount=data["amount"],
        purpose=data.get("purpose"),
        due_date=datetime.strptime(data["due_date"], "%Y-%m-%d"),
        person_id=user.person_id,
    )

    db.session.add(loan)
    db.session.commit()
    return jsonify(message="Loan request submitted"), 201


# -------------------------------------------
# 📌 Admins view all loan requests
# -------------------------------------------
@loan_bp.route("/all", methods=["GET"])
@role_required(["Chairperson", "Treasurer"])
def view_all_loans():
    loans = Loan.query.order_by(Loan.request_date.desc()).all()
    results = []
    for loan in loans:
        results.append({
            "id": loan.id,
            "member": loan.person.full_name,
            "amount": loan.amount,
            "purpose": loan.purpose,
            "status": loan.status,
            "due_date": loan.due_date.strftime("%Y-%m-%d"),
        })
    return jsonify(loans=results), 200


# -------------------------------------------
# ✅ Admin approves loan — sends notification
# -------------------------------------------
@loan_bp.route("/approve/<int:loan_id>", methods=["POST"])
@role_required(["Chairperson", "Treasurer"])
def approve_loan(loan_id):
    approver_id = get_jwt_identity()
    approver = User.query.get(approver_id)
    loan = Loan.query.get(loan_id)

    if not loan:
        return jsonify(message="Loan not found"), 404

    # ❌ Prevent approving your own loan
    if approver.person_id == loan.person_id:
        return jsonify(message="Cannot approve your own loan"), 403

    loan.status = "approved"
    loan.approved = True
    loan.approved_by = approver_id
    db.session.commit()

    # ✅ Send notification to the member
    send_notification(
        user_id=loan.person.user.id,
        title="Loan Approved",
        message=f"Your loan of KES {loan.amount} has been approved!"
    )

    return jsonify(message="Loan approved"), 200


# -------------------------------------------
# ❌ Admin rejects loan — sends notification
# -------------------------------------------
@loan_bp.route("/reject/<int:loan_id>", methods=["POST"])
@role_required(["Chairperson", "Treasurer"])
def reject_loan(loan_id):
    approver_id = get_jwt_identity()
    approver = User.query.get(approver_id)
    loan = Loan.query.get(loan_id)

    if not loan:
        return jsonify(message="Loan not found"), 404

    if approver.person_id == loan.person_id:
        return jsonify(message="Cannot reject your own loan"), 403

    loan.status = "rejected"
    loan.approved = False
    db.session.commit()

    # ✅ Notify user
    send_notification(
        user_id=loan.person.user.id,
        title="Loan Rejected",
        message=f"Your loan request of KES {loan.amount} was rejected."
    )

    return jsonify(message="Loan rejected"), 200
