from typing import List, Union

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi_csrf_protect import CsrfProtect
from sqlmodel import Session, or_, select
from supertokens_python.recipe.session import SessionContainer
from supertokens_python.recipe.session.framework.fastapi import verify_session

from app import models, schemas
from app.database import get_db

from ..auth_check import auth_check


@CsrfProtect.load_config
def get_csrf_config():
    return schemas.CsrfSettings()


router = APIRouter(prefix="/admin/universities", tags=["(Admin) University"])

# helper needed due to how the postgresql dataprovider works for react-admin
def get_university(university_id: int, db: Session):
    university = db.exec(
        select(models.University).where(models.University.id == university_id)
    ).first()
    if university == None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"This university does not exist",
        )
    return university


@router.get(
    "", response_model=Union[List[schemas.UniversityRes], schemas.UniversityRes]
)
@auth_check(roles=["admin"])
def get_universities(
    request: Request,
    response: Response,
    id: str = "-1",
    limit: int = 10,
    offset: int = 0,
    order: str = "id.asc",
    q: str = "",
    db: Session = Depends(get_db),
    session: SessionContainer = Depends(verify_session()),
):
    # Get one university
    if id != "-1":
        return get_university(int(id.split(".")[1]), db)
    order_direction_map = {
        "id": [models.University.id, models.University.id.desc()],
        "name": [models.University.name, models.University.name.desc()],
        "city": [models.University.city, models.University.city.desc()],
        "state": [models.University.state, models.University.state.desc()],
        "conference": [
            models.University.conference,
            models.University.conference.desc(),
        ],
        "division": [models.University.division, models.University.division.desc()],
        "region": [models.University.region, models.University.region.desc()],
        "category": [models.University.category, models.University.category.desc()],
    }

    statement = select(models.University)
    if q != "":
        q = q.split(".")[1]
    order_column, order_direction = order.split(".")
    if q != "":
        statement = statement.where(
            or_(
                models.University.name.contains(q),
                models.University.city.contains(q),
                models.University.state.contains(q),
                models.University.conference.contains(q),
                models.University.division.contains(q),
                models.University.region.contains(q),
                models.University.category.contains(q),
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
    universities = results.all()
    response.headers["Content-Range"] = str(total)
    return universities


@router.post(
    "", status_code=status.HTTP_201_CREATED, response_model=schemas.UniversityRes
)
@auth_check(roles=["admin"])
def create_university(
    request: Request,
    university: schemas.UniversityReq,
    db: Session = Depends(get_db),
    session: SessionContainer = Depends(verify_session()),
    csrf_protect: CsrfProtect = Depends(),
):
    csrf_token = csrf_protect.get_csrf_from_headers(request.headers)
    csrf_protect.validate_csrf(csrf_token, request)
    new_university = models.University(**university.dict())
    db.add(new_university)
    db.commit()
    db.refresh(new_university)
    return new_university


@router.put("", response_model=schemas.UniversityRes)
@auth_check(roles=["admin"])
def update_university(
    request: Request,
    updated_university: schemas.UniversityReq,
    id: str = "-1",
    db: Session = Depends(get_db),
    session: SessionContainer = Depends(verify_session()),
    csrf_protect: CsrfProtect = Depends(),
):
    csrf_token = csrf_protect.get_csrf_from_headers(request.headers)
    csrf_protect.validate_csrf(csrf_token, request)
    if id != "-1":
        university_id = int(id.split(".")[1])
    university = db.exec(
        select(models.University).where(models.University.id == university_id)
    ).first()
    if university == None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"This university does not exist",
        )
    updated_university_data = updated_university.dict(exclude_unset=True)
    for key, value in updated_university_data.items():
        setattr(university, key, value)
    db.add(university)
    db.commit()
    db.refresh(university)
    return university


@router.delete("", status_code=status.HTTP_204_NO_CONTENT)
@auth_check(roles=["admin"])
def delete_university(
    request: Request,
    id: str = "-1",
    db: Session = Depends(get_db),
    session: SessionContainer = Depends(verify_session()),
    csrf_protect: CsrfProtect = Depends(),
):
    csrf_token = csrf_protect.get_csrf_from_headers(request.headers)
    csrf_protect.validate_csrf(csrf_token, request)
    if id != "-1" and "eq" in id:
        university_ids = [int(id.split(".")[1])]
    elif "in" in id:  # delete many
        start = id.index("(") + 1
        university_ids = [int(id) for id in id[start:-1].split(",")]
    for university_id in university_ids:
        university = db.exec(
            select(models.University).where(models.University.id == university_id)
        ).first()
        if university == None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"University with id: {university_id} does not exist",
            )
        db.delete(university)
        db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
