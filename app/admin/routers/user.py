from typing import List, Union

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi_csrf_protect import CsrfProtect
from fastapi_jwt_auth import AuthJWT
from sqlmodel import Session, or_, select

from app import models, schemas, utils
from app.database import get_db

from ..auth_check import auth_check


@CsrfProtect.load_config
def get_csrf_config():
    return schemas.CsrfSettings()


router = APIRouter(prefix="/admin/users", tags=["(Admin) Users"])

# helper needed due to how the postgresql dataprovider works for react-admin
def get_user(user_id: int, db: Session):
    statement = select(models.User).where(models.User.id == user_id)
    results = db.exec(statement)
    user = results.first()
    if user == None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"The user does not exist"
        )
    return user


@router.get("", response_model=Union[List[schemas.UserAdmin], schemas.UserAdmin])
@auth_check(roles=["admin"])
def get_users(
    request: Request,
    response: Response,
    id: str = "-1",
    limit: int = 10,
    offset: int = 0,
    order: str = "id.asc",
    q: str = "",
    db: Session = Depends(get_db),
    Authorize: AuthJWT = Depends(),
    csrf_protect: CsrfProtect = Depends(),
):
    csrf_token = csrf_protect.get_csrf_from_headers(request.headers)
    csrf_protect.validate_csrf(csrf_token, request)
    Authorize.jwt_required()
    # Get one user
    if id != "-1":
        return get_user(int(id.split(".")[1]), db)
    order_direction_map = {
        "id": [models.User.id, models.User.id.desc()],
        "username": [models.User.id, models.User.id.desc()],
        "email": [models.User.email, models.User.email.desc()],
        "name": [models.User.name, models.User.name.desc()],
        "wechatId": [models.User.wechatId, models.User.wechatId.desc()],
        "gender": [models.User.gender, models.User.gender.desc()],
        "contact_number": [
            models.User.contact_number,
            models.User.contact_number.desc(),
        ],
        "current_address": [
            models.User.current_address,
            models.User.current_address.desc(),
        ],
        "birthday": [models.User.birthday, models.User.birthday.desc()],
        "public": [models.User.public, models.User.public.desc()],
        "role": [models.User.role, models.User.role.desc()],
    }

    statement = select(models.User)
    if q != "":
        q = q.split(".")[1]
    order_column, order_direction = order.split(".")
    if q != "":
        statement = statement.where(
            or_(
                models.User.username.contains(q),
                models.User.email.contains(q),
                models.User.name.contains(q),
                models.User.wechatId.contains(q),
                models.User.gender.contains(q),
                models.User.contact_number.contains(q),
                models.User.current_address.contains(q),
                models.User.role.contains(q),
            )
        )
    total = len(db.exec(statement).all())
    if order_direction == "asc":
        statement = (
            statement.order_by(order_direction_map[order_column][0])
            .offset(offset)
            .limit(limit)
        )
    else:
        statement = (
            statement.order_by(order_direction_map[order_column][1])
            .offset(offset)
            .limit(limit)
        )
    results = db.exec(statement)
    users = results.all()
    response.headers["Content-Range"] = str(total)
    return users


@router.post("", status_code=status.HTTP_201_CREATED, response_model=schemas.UserAdmin)
@auth_check(roles=["admin"])
def create_user(
    request: Request,
    user: schemas.UserCreate,
    db: Session = Depends(get_db),
    Authorize: AuthJWT = Depends(),
    csrf_protect: CsrfProtect = Depends(),
):
    csrf_token = csrf_protect.get_csrf_from_headers(request.headers)
    csrf_protect.validate_csrf(csrf_token, request)
    Authorize.jwt_required()
    hashed_password = utils.hash(user.password)
    user.password = hashed_password
    new_user = models.User(**user.dict())
    users = db.query(models.User).all()
    for user in users:
        if user.username == new_user.username:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Username is used by another user",
            )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@router.put("", response_model=schemas.UserAdmin)
@auth_check(roles=["admin"])
def update_user(
    request: Request,
    updated_user: schemas.UserAdminReq,
    id: str = "-1",
    db: Session = Depends(get_db),
    Authorize: AuthJWT = Depends(),
    csrf_protect: CsrfProtect = Depends(),
):
    csrf_token = csrf_protect.get_csrf_from_headers(request.headers)
    csrf_protect.validate_csrf(csrf_token, request)
    Authorize.jwt_required()
    if id != "-1":
        user_id = int(id.split(".")[1])
    user = db.exec(select(models.User).where(models.User.id == user_id)).first()
    if user == None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"The user does not exist"
        )
    updated_user_data = updated_user.dict(exclude_unset=True)
    for key, value in updated_user_data.items():
        setattr(user, key, value)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.delete("", status_code=status.HTTP_204_NO_CONTENT)
@auth_check(roles=["admin"])
def delete_user(
    request: Request,
    id: str = "-1",
    db: Session = Depends(get_db),
    Authorize: AuthJWT = Depends(),
    csrf_protect: CsrfProtect = Depends(),
):
    csrf_token = csrf_protect.get_csrf_from_headers(request.headers)
    csrf_protect.validate_csrf(csrf_token, request)
    Authorize.jwt_required()
    if id != "-1" and "eq" in id:
        user_ids = [int(id.split(".")[1])]
    elif "in" in id:  # delete many
        start = id.index("(") + 1
        user_ids = [int(id) for id in id[start:-1].split(",")]
    for user_id in user_ids:
        user = db.exec(select(models.User).where(models.User.id == user_id)).first()
        if user == None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with id: {user_id} does not exist",
            )
        db.delete(user)
        db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
