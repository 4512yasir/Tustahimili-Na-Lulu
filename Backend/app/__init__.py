from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from .config import Config

db = SQLAlchemy()
bcrypt = Bcrypt()
jwt = JWTManager()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Init extensions
    db.init_app(app)
    bcrypt.init_app(app)
    jwt.init_app(app)
    CORS(app)

    # Register Blueprints
    from app.routes.auth import auth_bp
    from app.routes.loan import loan_bp 
    from app.routes.contribution import contrib_bp
    from app.routes.meeting import meeting_bp
    from app.routes.notification import notify_bp
    from app.routes.report import report_bp
    from app.routes.user import user_bp
    from app.routes.maintances import maintenance_bp

    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(loan_bp, url_prefix="/api/loan")
    app.register_blueprint(contrib_bp, url_prefix="/api/contribution")
    app.register_blueprint(meeting_bp, url_prefix="/api/meeting")
    app.register_blueprint(notify_bp, url_prefix="/api/notifications")
    app.register_blueprint(report_bp, url_prefix="/api/report")
    app.register_blueprint(user_bp, url_prefix="/api/user")
    app.register_blueprint(maintenance_bp, url_prefix="/api/maintenance") 


    # Optional: Global error handler
    @app.errorhandler(404)
    def not_found(e):
        return jsonify(message="Not found"), 404

    return app
