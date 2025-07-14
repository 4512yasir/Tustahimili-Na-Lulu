from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity
from app import db
from app.models import Property, RentPayment, User
from app.utils.auth_utils import role_required
from datetime import datetime

rent_bp = Blueprint("rent", __name__)

# ----------------------
# Property Management
# ----------------------
@rent_bp.route("/property", methods=["POST"])
@role_required(["Chairperson", "Rent Manager"])
def add_property():
    data = request.get_json()
    property = Property(
        name=data["name"],
        location=data.get("location"),
        monthly_rent=data["monthly_rent"],
        is_occupied=data.get("is_occupied", True),
        tenant_name=data.get("tenant_name"),
        tenant_phone=data.get("tenant_phone"),
    )
    db.session.add(property)
    db.session.commit()
    return jsonify(message="Property added successfully"), 201


@rent_bp.route("/properties", methods=["GET"])
@role_required(["Chairperson", "Rent Manager"])
def get_properties():
    properties = Property.query.all()
    return jsonify([
        {
            "id": p.id,
            "name": p.name,
            "location": p.location,
            "monthly_rent": p.monthly_rent,
            "is_occupied": p.is_occupied,
            "tenant_name": p.tenant_name,
            "tenant_phone": p.tenant_phone
        } for p in properties
    ]), 200

# ----------------------
# Rent Payment
# ----------------------
@rent_bp.route("/payment", methods=["POST"])
@role_required(["Chairperson", "Rent Manager"])
def record_payment():
    data = request.get_json()
    payment = RentPayment(
        property_id=data["property_id"],
        amount=data["amount"],
        payment_date=datetime.strptime(data["payment_date"], "%Y-%m-%d"),
        payment_method=data.get("payment_method", "M-Pesa"),
        receipt_code=data.get("receipt_code"),
        notes=data.get("notes")
    )
    db.session.add(payment)
    db.session.commit()
    return jsonify(message="Rent payment recorded"), 201


@rent_bp.route("/payments", methods=["GET"])
@role_required(["Chairperson", "Rent Manager"])
def view_all_payments():
    payments = RentPayment.query.order_by(RentPayment.payment_date.desc()).all()
    return jsonify([
        {
            "id": p.id,
            "property": p.property.name,
            "amount": p.amount,
            "payment_date": p.payment_date.strftime("%Y-%m-%d"),
            "payment_method": p.payment_method,
            "receipt_code": p.receipt_code,
            "notes": p.notes
        } for p in payments
    ]), 200
