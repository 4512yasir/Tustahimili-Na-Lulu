from flask import Blueprint, jsonify
from flask_jwt_extended import get_jwt_identity
from app.models import Contribution, Loan, RentPayment, User, Person
from app.utils.auth_utils import role_required
from app import db
from sqlalchemy import func

report_bp = Blueprint("report", __name__)


# ------------------------------------------------
# ✅ 1. Summary report (Admin roles)
# ------------------------------------------------
@report_bp.route("/summary", methods=["GET"])
@role_required(["Chairperson", "Treasurer", "Secretary"])
def summary_report():
    total_contributions = db.session.query(func.sum(Contribution.amount)).scalar() or 0
    total_loans = db.session.query(func.sum(Loan.amount)).filter(Loan.status == "approved").scalar() or 0
    total_rent = db.session.query(func.sum(Rent.amount)).scalar() or 0

    total_members = db.session.query(Person).count()

    return jsonify({
        "total_contributions": total_contributions,
        "total_loans_issued": total_loans,
        "total_rent_collected": total_rent,
        "total_members": total_members
    })


# ------------------------------------------------
# ✅ 2. Individual member financial report
# ------------------------------------------------
@report_bp.route("/member/<int:person_id>", methods=["GET"])
@role_required(["Chairperson", "Treasurer", "Secretary", "Member"])
def member_report(person_id):
    person = Person.query.get(person_id)
    if not person:
        return jsonify(message="Member not found"), 404

    contributions = db.session.query(func.sum(Contribution.amount)).filter_by(person_id=person_id).scalar() or 0
    loans_taken = db.session.query(func.sum(Loan.amount)).filter_by(person_id=person_id).scalar() or 0
    loans_paid = db.session.query(func.sum(Loan.repayment_amount)).filter_by(person_id=person_id).scalar() or 0

    return jsonify({
        "member_name": person.full_name,
        "phone": person.phone,
        "contributions": contributions,
        "loans_taken": loans_taken,
        "loans_repaid": loans_paid
    })


# ------------------------------------------------
# ✅ 3. Income breakdown (Admin)
# ------------------------------------------------
@report_bp.route("/income", methods=["GET"])
@role_required(["Chairperson", "Treasurer"])
def income_report():
    total_contributions = db.session.query(func.sum(Contribution.amount)).scalar() or 0
    total_interest = db.session.query(func.sum(Loan.interest)).scalar() or 0
    total_rent = db.session.query(func.sum(Rent.amount)).scalar() or 0

    return jsonify({
        "contributions": total_contributions,
        "loan_interest": total_interest,
        "rent_income": total_rent,
        "total_income": total_contributions + total_interest + total_rent
    })
