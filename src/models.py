"""Contains the Request models for the API"""

import re

from datetime import datetime

from fastapi.responses import JSONResponse
from fastapi import status, HTTPException, Form

from pydantic import BaseModel, Field, EmailStr, model_validator, field_validator

from beanie import Document, Indexed

from typing import Annotated, Union
from typing_extensions import Self


class DOB(BaseModel):
    """Model for Date of Birth"""

    day: str = Field(
        title="Day of the month",
        pattern=r"^\d+$",
        examples=["01"],
        max_length=2,
        min_length=2,
    )
    month: str = Field(
        title="Month of the year",
        pattern=r"^\d+$",
        examples=["01"],
        max_length=2,
        min_length=2,
    )
    year: str = Field(
        title="Year", pattern=r"^\d+$", examples=["1911"], max_length=4, min_length=4
    )

    @model_validator(mode="after")
    def check_if_adult(self) -> Self:
        """Checks if the user is an adult"""
        year = datetime.now().year

        if not (year - int(self.year)) >= 18:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"detail": "User must be 18 years or older"},
            )
        return self


class UserBase(BaseModel):
    """User Base Model"""

    email: EmailStr = Field(
        title="Email address of the user",
        examples=["johndoe@example.com"],
        max_length=100,
    )
    first_name: str = Field(
        title="First name of the user",
        min_length=2,
        max_length=50,
        examples=["John"],
        alias="first_name",
    )
    last_name: str = Field(
        title="Last name of the user",
        min_length=2,
        max_length=50,
        examples=["Doe"],
        alias="last_name",
    )
    phone_number: str = Field(
        title="Phone number of the user",
        pattern=r"^(26481|26485)\d{7}$",
        examples=["264812111111"],
        alias="phone_number",
    )
    employer: Annotated[
        Union[str, None],
        Field(
            title="Employer of the user",
            max_length=100,
            examples=["Ministry of Information and Communication Technology"],
            description="Provide the name of the employer in full, when specified",
            default=None,
        ),
    ]
    position: Annotated[
        Union[str, None],
        Field(
            title="Position of the user",
            max_length=50,
            examples=["Spokesperson"],
            default=None,
        ),
    ]
    password: str = Field(
        title="Password of the user", min_length=8, examples=["Password@123"]
    )
    national_id_number: str = Field(
        title="National ID number of the user",
        min_length=11,
        max_length=11,
        pattern=r"^\d+$",
        examples=["11010100000"],
    )
    dob: DOB = Field(title="Date of birth of the user", alias="dob")


class CreateUserRequest(UserBase):
    """Model for creating a new user"""

    verify_password: Annotated[
        str,
        Field(
            min_length=6,
            max_length=100,
            examples=["Password@123"],
            alias="verify_password",
        ),
    ]

    # * Validate the National ID number
    @model_validator(mode="after")
    def validate_national_email_number(self) -> Self:
        email_number = self.national_id_number
        invalid_email_exception = HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Invalid national ID number",
        )

        if not email_number[:2] == self.dob.year[2:]:
            raise invalid_email_exception
        elif not email_number[2:4] == self.dob.month:
            raise invalid_email_exception
        elif not email_number[4:6] == self.dob.day:
            raise invalid_email_exception

        return self

    # * Validate the password to ensure it has at least one uppercase letter,
    # * one special character, one lowercase letter, and one number
    @field_validator("password")
    @classmethod
    def validate_password(cls, v):
        if not re.search(r"[A-Z]", v):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Password must contain at least one uppercase letter",
            )
        if not re.search(r"[a-z]", v):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Password must contain at least one lowercase letter",
            )
        if not re.search(r"\d", v):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Password must contain at least one number",
            )
        if not re.search(r"[@$!%*?&#]", v):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Password must contain at least one special character",
            )
        return v

    # * Checks if password and verify password fields match
    @model_validator(mode="after")
    def check_password_match(self) -> Self:
        password = self.password
        verify_password = self.verify_password

        if (
            password is not None
            and verify_password is not None
            and password != verify_password
        ):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Passwords do not match",
            )
        return self

    # * Check if first name and last name in password
    @model_validator(mode="after")
    def check_first_name_last_name_in_password(self) -> Self:
        first_name = self.first_name
        last_name = self.last_name
        password = self.password

        if first_name in password:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Password contains first name",
            )
        if last_name in password:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Password contains last name",
            )
        return self


class User(Document, UserBase):
    class Settings:
        name = "users"
        is_root = True

    is_active: bool = Field(default=True, description="User activation status")
    verified: bool = Field(default=False, description="User verification status")
    permissions: list[str] = Field(
        default=["me"], description="User permissions", alias="permissions"
    )


class PollOptions(BaseModel):
    option: str = Field(description="Option for the poll")
    votes: int = Field(description="Number of votes for the option", default=0)


class CreatePoll(BaseModel):
    class Settings:
        name = "polls"

    title: str = Field(description="Title of the poll")
    question: str = Field(description="Question of the poll")
    options: list[PollOptions] = Field(description="Options for the poll")
    duration: int = Field(description="Duration of the poll in seconds")


class CreateAnnouncement(BaseModel):
    class Settings:
        name = "announcements"

    title: str = Field(description="Title of the announcement")
    content: str = Field(description="Content of the announcement")


class Announcements(Document, CreateAnnouncement):
    class Settings:
        name = "announcements"
        is_root = True

    comments: list[str] = Field(description="Comments on the announcement", default=[])
    likes: int = Field(description="Number of likes on the announcement", default=0)
    dislikes: int = Field(
        description="Number of dislikes on the announcement", default=0
    )


class Poll(Document, CreatePoll):
    class Settings:
        name = "polls"

    comments: list[str] = Field(description="Comments on the poll", default=[])


class Comment(BaseModel):
    comment: str = Field(description="Comment on the post")


class Post(Document):
    class Settings:
        name = "posts"

    title: str = Field(description="Title of the post")
    content: str = Field(description="Content of the post")
    image: dict | None = Field(description="Image of the post", default=None)
    comments: list[str] = Field(description="Comments on the post", default=[])
    likes: int = Field(description="Number of likes on the post", default=0)
    dislikes: int = Field(description="Number of dislikes on the post", default=0)


class VerifiedUser(User):
    polls: list = Field(description="Polls created by the user", default=[])
    posts: list = Field(description="Posts created by the user", default=[])
    announcements: list = Field(
        description="Announcements created by the user", default=[]
    )


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None
    scopes: list[str] = []
