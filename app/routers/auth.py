from fastapi import APIRouter, Depends, Response, status
from fastapi_csrf_protect import CsrfProtect
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db


@CsrfProtect.load_config
def get_csrf_config():
    return schemas.CsrfSettings()


router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.get("/csrf_token")
def set_csrf_cookie_and_get_csrf_token(
    response: Response, csrf_protect: CsrfProtect = Depends()
):
    csrf_token = csrf_protect.set_csrf_cookie(
        response
    )  # modify the library to return the value self.generate_csrf(self._secret_key)
    return {"csrf_token": csrf_token}


@router.post(
    "/postsignup", status_code=status.HTTP_201_CREATED, response_model=schemas.SignUpRes
)
async def create_user(
    user: schemas.UserPostSignUp,
    db: Session = Depends(get_db),
):
    new_user = models.User(**user.dict())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user
