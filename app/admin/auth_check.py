from functools import wraps

from fastapi.responses import JSONResponse
from sqlmodel import select

from app import models


def auth_check(roles):
    def decorator_auth(func):
        @wraps(func)
        def wrapper_auth(*args, **kwargs):
            session = kwargs["session"]
            db = kwargs["db"]
            current_user = db.exec(
                select(models.User).where(models.User.id == session.get_user_id())
            ).first()
            user_role = current_user.role
            if user_role in roles:
                return func(*args, **kwargs)
            return JSONResponse(status_code=403, content={"detail": "Unauthorized"})

        return wrapper_auth

    return decorator_auth
