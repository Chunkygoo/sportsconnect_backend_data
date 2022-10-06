from datetime import date, datetime
from typing import List, Optional
from unicodedata import category

from pydantic import BaseModel

from app.config import settings
from app.models import University


# Auth
class UserCreate(BaseModel):
    id: str
    email: str


class UserLogin(BaseModel):
    username: str
    password: str


# Base
class UserBase(BaseModel):
    public: Optional[bool] = False

    class Config:
        orm_mode = True


class ExperienceBase(BaseModel):
    class Config:
        orm_mode = True


class EducationBase(BaseModel):
    class Config:
        orm_mode = True


class UniversityBase(BaseModel):
    class Config:
        orm_mode = True


# Req
class UserReq(UserBase):
    name: Optional[str] = ""
    email: Optional[str] = ""
    wechatId: Optional[str] = ""
    preferred_name: Optional[str] = ""
    bio: Optional[str] = ""
    gender: Optional[str] = ""
    contact_number: Optional[str] = ""
    current_address: Optional[str] = ""
    permanent_address: Optional[str] = ""
    birthday: Optional[date] = None


class ExperienceReq(ExperienceBase):
    description: str
    active: bool
    start_date: date
    end_date: Optional[date] = None


class EducationReq(EducationBase):
    description: str
    active: bool
    start_date: date
    end_date: Optional[date] = None


class UniversityReq(UniversityBase):
    name: str
    city: str
    state: str
    conference: str
    division: str
    region: str
    category: str


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str


class TokenData(BaseModel):
    id: Optional[str] = None


class EmailRequest(BaseModel):
    name: str
    email: str
    message: str


class EmailVerify(BaseModel):
    email: str


# Res
class ExperienceRes(ExperienceBase):
    id: int
    description: str
    active: bool
    start_date: date
    end_date: Optional[date] = None


class EducationRes(EducationBase):
    id: int
    description: str
    active: bool
    start_date: date
    end_date: Optional[date] = None


class ProfilePhotoRes(BaseModel):
    id: int
    photo_name: str
    photo_url: str
    is_deleted: bool


class UniversityRes(UniversityBase):
    id: int
    name: str
    city: str
    state: str
    conference: str
    division: str
    region: str
    category: str
    interested: Optional[bool] = None


class UniversityResWithLink(UniversityRes):
    link: str


class UserRes(UserBase):
    id: str
    name: Optional[str] = ""
    email: Optional[str] = ""
    wechatId: Optional[str] = ""
    preferred_name: Optional[str] = ""
    bio: Optional[str] = ""
    gender: Optional[str] = ""
    contact_number: Optional[str] = ""
    current_address: Optional[str] = ""
    permanent_address: Optional[str] = ""
    birthday: Optional[date] = None
    experiences: List[ExperienceRes] = []
    educations: List[EducationRes] = []
    profile_photo: List[ProfilePhotoRes] = []
    unis: List[UniversityRes] = []


class UserMe(UserRes):
    role: Optional[str] = "user"


class UserAdmin(UserBase):
    id: Optional[int]
    username: Optional[str] = ""
    email: Optional[str] = ""
    name: Optional[str] = ""
    wechatId: Optional[str] = ""
    gender: Optional[str] = ""
    contact_number: Optional[str] = ""
    current_address: Optional[str] = ""
    birthday: Optional[date] = None
    role: Optional[str] = "user"


class UserAdminReq(UserBase):
    email: Optional[str] = ""
    name: Optional[str] = ""
    wechatId: Optional[str] = ""
    gender: Optional[str] = ""
    contact_number: Optional[str] = ""
    current_address: Optional[str] = ""
    birthday: Optional[date] = None
    role: Optional[str] = "user"


class SignUpRes(UserBase):
    name: Optional[str] = ""
    email: Optional[str] = ""
    wechatId: Optional[str] = ""
    preferred_name: Optional[str] = ""
    bio: Optional[str] = ""
    gender: Optional[str] = ""
    contact_number: Optional[str] = ""
    current_address: Optional[str] = ""
    permanent_address: Optional[str] = ""
    birthday: Optional[date] = None
    experiences: List[ExperienceRes] = []
    educations: List[EducationRes] = []
    x_csrf_token: str = ""
    x_csrf_refresh_token: str = ""


class CsrfSettings(BaseModel):
    secret_key: str = settings.csrf_secret_key
    cookie_samesite: str = settings.csrf_cookie_samesite
    httponly: bool = settings.csrf_httponly
    cookie_secure: bool = settings.csrf_cookie_secure
