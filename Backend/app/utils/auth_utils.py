from functools import wraps
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request
from flask import jsonify
from app.models import User

def role_required(allowed_roles):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            try:
                verify_jwt_in_request()
                current_user_id = get_jwt_identity()
                user = User.query.get(current_user_id)

                if not user:
                    return jsonify({"message": "User not found"}), 404

                if user.role.name not in allowed_roles:
                    return jsonify({"message": "Access denied"}), 403

                return fn(*args, **kwargs)
            except Exception as e:
                return jsonify({"message": f"Unauthorized: {str(e)}"}), 401

        return wrapper
    return decorator
