from typing import List

from fastapi import (APIRouter, Depends, HTTPException, Request, Response,
                     status)
from fastapi_csrf_protect import CsrfProtect
from sqlmodel import Session, select
from supertokens_python.recipe.session import SessionContainer
from supertokens_python.recipe.session.framework.fastapi import verify_session

from .. import models, schemas
from ..database import get_db


@CsrfProtect.load_config
def get_csrf_config():
    return schemas.CsrfSettings()


router = APIRouter(prefix="/educations", tags=["Education"])


@router.get("", response_model=List[schemas.EducationRes])
def get_educations(
    db: Session = Depends(get_db), session: SessionContainer = Depends(verify_session())
):
    statement = select(models.Education).where(
        models.Education.owner_id == session.get_user_id()
    )
    results = db.exec(statement)
    educations = results.all()
    return educations


@router.post("", status_code=status.HTTP_201_CREATED)
def create_education(
    request: Request,
    education: schemas.EducationReq,
    csrf_protect: CsrfProtect = Depends(),
    session: SessionContainer = Depends(verify_session()),
    db: Session = Depends(get_db),
):
    csrf_token = csrf_protect.get_csrf_from_headers(request.headers)
    csrf_protect.validate_csrf(csrf_token, request)

    statement = select(models.Education).where(
        models.Education.owner_id == session.get_user_id()
    )
    results = db.exec(statement)
    educations = results.all()
    if len(educations) >= 5:
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail="You can only have a maximum of 5 education items",
        )
    current_user = db.exec(
        select(models.User).where(models.User.id == session.get_user_id())
    ).first()
    new_education = models.Education(owner_id=session.get_user_id(), **education.dict())
    new_education.owner = current_user
    db.add(new_education)
    db.commit()
    db.refresh(new_education)
    return new_education


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_education(
    request: Request,
    id: int,
    db: Session = Depends(get_db),
    session: SessionContainer = Depends(verify_session()),
    csrf_protect: CsrfProtect = Depends(),
):
    csrf_token = csrf_protect.get_csrf_from_headers(request.headers)
    csrf_protect.validate_csrf(csrf_token, request)

    statement = select(models.Education).where(models.Education.id == id)
    results = db.exec(statement)
    education = results.first()
    if education == None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"education with id: {id} does not exist",
        )
    if education.owner_id != session.get_user_id():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to perform requested action",
        )
    db.delete(education)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.put("/{id}")
def update_education(
    request: Request,
    id: int,
    updated_education: schemas.EducationReq,
    db: Session = Depends(get_db),
    session: SessionContainer = Depends(verify_session()),
    csrf_protect: CsrfProtect = Depends(),
):
    csrf_token = csrf_protect.get_csrf_from_headers(request.headers)
    csrf_protect.validate_csrf(csrf_token, request)

    statement = select(models.Education).where(models.Education.id == id)
    results = db.exec(statement)
    education = results.first()
    if education == None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"education with id: {id} does not exist",
        )
    if education.owner_id != session.get_user_id():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to perform requested action",
        )
    updated_education_data = updated_education.dict(exclude_unset=True)
    for key, value in updated_education_data.items():
        setattr(education, key, value)
    db.add(education)
    db.commit()
    db.refresh(education)
    return education


@router.get("/user/{user_id}", response_model=List[schemas.ExperienceRes])
def get_educations_for_user(user_id: str, db: Session = Depends(get_db)):
    statement = (
        select(models.User)
        .where(models.User.id == user_id)
        .where(models.User.public == True)
    )
    results = db.exec(statement)
    user = results.first()
    if user == None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"The user does not exist"
        )
    return user.educations
