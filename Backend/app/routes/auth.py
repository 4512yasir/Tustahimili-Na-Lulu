from flask import Blueprint, request, jsonify
from app import db, bcrypt
from app.models import User, Role, Person
from flask_jwt_extended import create_access_token
from sqlalchemy.exc import IntegrityError

auth_bp = Blueprint('auth', __name__)

# ---------------------------------------
# ✅ Register a new user
# ---------------------------------------
@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    if not data:
        return jsonify(message="No data provided"), 400

    try:
        # Check for duplicate email
        if User.query.filter_by(email=data["email"]).first():
            return jsonify(message="Email already registered"), 409

        # Create associated person
        person = Person(full_name=data["full_name"], phone=data["phone"])
        db.session.add(person)
        db.session.flush()  # Get person.id before commit

        # Hash password
        hashed_pw = bcrypt.generate_password_hash(data["password"]).decode("utf-8")

        # Get role object
        role = Role.query.filter(Role.name.ilike(data["role"])).first()
        if not role:
            return jsonify(message="Invalid role"), 400

        # Create user
        user = User(
            email=data["email"],
            password_hash=hashed_pw,
            role_id=role.id,
            person_id=person.id
        )
        db.session.add(user)
        db.session.commit()

        return jsonify(message="User registered successfully"), 201

    except KeyError as e:
        return jsonify(message=f"Missing field: {e.args[0]}"), 400
    except IntegrityError:
        db.session.rollback()
        return jsonify(message="Registration failed — likely duplicate info"), 400
    except Exception as e:
        return jsonify(message=str(e)), 500


# ---------------------------------------
# 🔐 Login a user and issue JWT token
# ---------------------------------------
@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    if not data or not data.get("email") or not data.get("password"):
        return jsonify(message="Email and password required"), 400

    user = User.query.filter_by(email=data["email"]).first()

    if user and bcrypt.check_password_hash(user.password_hash, data["password"]):
        token = create_access_token(identity=user.id)
        return jsonify(token=token, role=user.role.name), 200

    return jsonify(message="Invalid credentials"), 401
