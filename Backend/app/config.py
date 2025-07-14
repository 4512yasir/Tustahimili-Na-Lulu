import os

class Config:
    # Secret keys (for production override with .env)
    SECRET_KEY = os.environ.get("SECRET_KEY", "super-secret-key")
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "jwt-secret")

    # Database config
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", "sqlite:///tustahimili.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Optional: JWT token expiration (e.g., 2 days)
    JWT_ACCESS_TOKEN_EXPIRES = 172800  # seconds

    # Optional: Frontend CORS control
    CORS_HEADERS = "Content-Type"
