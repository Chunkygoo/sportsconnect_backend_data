from datetime import date, datetime
from typing import List, Optional

from sqlmodel import Field, Relationship, SQLModel


# Represents the interest of player(s) in uni(s)
class UserUniLink(SQLModel, table=True):
    user_id: str = Field(foreign_key="user.id", primary_key=True, nullable=False)
    uni_id: Optional[int] = Field(
        foreign_key="university.id", primary_key=True, nullable=False
    )


class User(SQLModel, table=True):
    email: str = Field(default="", max_length=50, nullable=True)
    id: str = Field(default=None, primary_key=True, nullable=False, max_length=50)
    name: str = Field(default="", max_length=50, nullable=True)
    wechatId: str = Field(default="", max_length=50, nullable=True)
    preferred_name: str = Field(default="", max_length=50, nullable=True)
    bio: str = Field(default="", max_length=1000, nullable=True)
    gender: str = Field(default="", max_length=50, nullable=True)
    contact_number: str = Field(default="", max_length=50, nullable=True)
    current_address: str = Field(default="", max_length=300, nullable=True)
    permanent_address: str = Field(default="", max_length=300, nullable=True)
    birthday: date = Field(nullable=True)
    created_at: datetime = Field(default=datetime.utcnow(), nullable=False)
    experiences: Optional[List["Experience"]] = Relationship(
        back_populates="owner",
        sa_relationship_kwargs={"cascade": "all,delete,delete-orphan"},
    )
    educations: Optional[List["Education"]] = Relationship(
        back_populates="owner",
        sa_relationship_kwargs={"cascade": "all,delete,delete-orphan"},
    )
    profile_photo: Optional["ProfilePhoto"] = Relationship(
        back_populates="owner",
        sa_relationship_kwargs={"cascade": "all,delete,delete-orphan"},
    )
    unis: Optional[List["University"]] = Relationship(
        back_populates="interested_users", link_model=UserUniLink
    )
    public: bool = Field(default=False, nullable=False)
    role: str = Field(default="user", nullable=False)


class Experience(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True, nullable=False)
    description: str = Field(nullable=False, max_length=100)
    owner_id: str = Field(nullable=False, foreign_key="user.id")
    created_at: datetime = Field(default=datetime.utcnow(), nullable=False)
    active: bool = Field(default=False, nullable=True)
    start_date: date = Field(nullable=False)
    end_date: date = Field(nullable=True)
    owner: User = Relationship(back_populates="experiences")


class Education(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True, nullable=False)
    description: str = Field(nullable=False, max_length=100)
    owner_id: str = Field(nullable=False, foreign_key="user.id")
    created_at: datetime = Field(default=datetime.utcnow(), nullable=False)
    active: bool = Field(default=False, nullable=True)
    start_date: date = Field(nullable=False)
    end_date: date = Field(nullable=True)
    owner: User = Relationship(back_populates="educations")


class University(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True, nullable=False)
    name: str = Field(nullable=False, max_length=100)
    city: str = Field(nullable=False, max_length=100)
    state: str = Field(nullable=False, max_length=100)
    conference: str = Field(nullable=False, max_length=100)
    division: str = Field(nullable=False, max_length=100)
    category: str = Field(nullable=False, max_length=100)
    region: str = Field(nullable=False, max_length=100)
    created_at: datetime = Field(default=datetime.utcnow(), nullable=False)
    interested_users: Optional[List["User"]] = Relationship(
        back_populates="unis", link_model=UserUniLink
    )


class ProfilePhoto(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True, nullable=False)
    photo_name: str = Field(nullable=False)
    photo_url: str = Field(nullable=False)
    is_deleted: bool = Field(default=False, nullable=True)
    owner_id: str = Field(nullable=False, foreign_key="user.id")
    owner: User = Relationship(back_populates="profile_photo")


class UniversityLink(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True, nullable=False)
    name: str = Field(nullable=False, max_length=100)
    link: str = Field(nullable=False, max_length=100)
