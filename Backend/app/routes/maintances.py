from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity
from app.models import MaintenanceRequest, Property
from app.utils.auth_utils import role_required
from app import db
from datetime import datetime

maintenance_bp = Blueprint("maintenance", __name__)

@maintenance_bp.route("/report", methods=["POST"])
@role_required(["Chairperson", "Rent Manager"])
def report_issue():
    data = request.get_json()
    issue = MaintenanceRequest(
        property_id=data["property_id"],
        issue_description=data["issue_description"]
    )
    db.session.add(issue)
    db.session.commit()
    return jsonify(message="Maintenance request submitted"), 201


@maintenance_bp.route("/", methods=["GET"])
@role_required(["Chairperson", "Rent Manager"])
def list_requests():
    requests = MaintenanceRequest.query.order_by(MaintenanceRequest.reported_date.desc()).all()
    return jsonify([
        {
            "id": r.id,
            "property": r.property.name,
            "description": r.issue_description,
            "status": r.status,
            "reported_date": r.reported_date.strftime("%Y-%m-%d"),
            "resolved_date": r.resolved_date.strftime("%Y-%m-%d") if r.resolved_date else None,
            "resolution_notes": r.resolution_notes
        } for r in requests
    ]), 200


@maintenance_bp.route("/resolve/<int:req_id>", methods=["POST"])
@role_required(["Chairperson", "Rent Manager"])
def resolve_request(req_id):
    data = request.get_json()
    request_obj = MaintenanceRequest.query.get(req_id)
    if not request_obj:
        return jsonify(message="Request not found"), 404

    request_obj.status = "Resolved"
    request_obj.resolved_date = datetime.utcnow()
    request_obj.resolution_notes = data.get("resolution_notes", "")
    db.session.commit()
    return jsonify(message="Request marked as resolved"), 200
