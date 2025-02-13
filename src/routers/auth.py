import os
from datetime import timedelta

from fastapi import APIRouter, status, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm

from typing import Annotated

from dotenv import load_dotenv

from src.utils.security import authenticate_user, create_access_token
from src.models import FakeLogin, User, VerifiedUser

load_dotenv()


router = APIRouter(tags=["Auth"])


@router.post("/login")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
):
    user = await authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(
        minutes=int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))
    )
    access_token = create_access_token(
        data={"sub": user.email, "scopes": user.permissions},
        expires_delta=access_token_expires,
    )

    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/fake-login")
async def fake_login_for_access_token(request: FakeLogin):
    user = await User.find_one(User.email == request.email, with_children=True)

    try:
        verified_user = VerifiedUser(**user.model_dump())
        for post in verified_user.posts:
            post.update(
                {
                    "image": f"http://localhost:8000/api/v1/posts/{verified_user.email}/{post["title"]}/image"
                }
            )
        return verified_user.model_dump(exclude={"password", "permissions"})
    except Exception as e:    
        return user.model_dump(exclude={"password", "permissions"})
