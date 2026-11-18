# app/api/auth.py
from functools import wraps
from flask import jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt

def role_required(*allowed_roles):
    """Decorator to enforce RBAC on sensitive PII endpoints."""
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            verify_jwt_in_request()
            claims = get_jwt()
            user_role = claims.get("role", "guest")
            if user_role not in allowed_roles:
                return jsonify({"error": "Access denied: Insufficient permissions"}), 403
            return fn(*args, **kwargs)
        return decorator
    return wrapper