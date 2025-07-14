from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity
from app import db
from app.models import User, Person, Role
from app.utils.auth_utils import role_required

user_bp = Blueprint("user", __name__)

# ----------------------------------------------
# ✅ 1. Get own profile
# ----------------------------------------------
@user_bp.route("/me", methods=["GET"])
def get_my_profile():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    return jsonify({
        "id": user.id,
        "email": user.email,
        "role": user.role.name,
        "name": user.person.full_name,
        "phone": user.person.phone,
    }), 200


# ----------------------------------------------
# ✅ 2. Update own profile
# ----------------------------------------------
@user_bp.route("/me", methods=["PUT"])
def update_my_profile():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    data = request.get_json()

    user.person.full_name = data.get("full_name", user.person.full_name)
    user.person.phone = data.get("phone", user.person.phone)
    db.session.commit()

    return jsonify(message="Profile updated"), 200


# ----------------------------------------------
# ✅ 3. List all users (Admin roles)
# ----------------------------------------------
@user_bp.route("/all", methods=["GET"])
@role_required(["Chairperson", "Secretary", "Treasurer"])
def list_users():
    users = User.query.all()
    return jsonify([
        {
            "id": u.id,
            "email": u.email,
            "name": u.person.full_name,
            "phone": u.person.phone,
            "role": u.role.name
        } for u in users
    ]), 200


# ----------------------------------------------
# ✅ 4. Change user role (optional, restricted)
# ----------------------------------------------
@user_bp.route("/<int:user_id>/role", methods=["PUT"])
@role_required(["Chairperson"])
def change_user_role(user_id):
    user = User.query.get(user_id)
    data = request.get_json()

    new_role = Role.query.filter_by(name=data["role"]).first()
    if not new_role:
        return jsonify(message="Role not found"), 404

    user.role_id = new_role.id
    db.session.commit()

    return jsonify(message=f"User role updated to {new_role.name}"), 200
