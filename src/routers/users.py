from pprint import pprint
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks

from beanie.operators import Set, Push

from fastapi.responses import JSONResponse

from src.models import User, CreateUserRequest, VerifiedUser
from src.utils.security import get_password_hash

from pydantic import EmailStr

router = APIRouter(tags=["Users"], prefix="/api/v1")


async def add_permissions_and_fields_to_verified_user(user_id: EmailStr):
    user = await User.find_one(
        User.email == user_id
    )  # * Add the verified permission to the user
    user.permissions.append("verified")
    await user.save()

    user = await User.find_one(User.email == user_id)  # * Get updated user

    # * Delete user
    await User.find_one(User.email == user_id).delete()

    # * Create a verified user
    await VerifiedUser.insert(VerifiedUser(**user.model_dump(by_alias=True)))


@router.post("/users")
async def create_user(request: CreateUserRequest):

    user = request.model_dump(by_alias=True, exclude={"verify_password"})
    user.update(
        {"permissions": ["me"], "password": get_password_hash(user.get("password"))}
    )
    new_user: User = await User.insert(User(**user))
    return JSONResponse(
        status_code=status.HTTP_201_CREATED, content=new_user.model_dump(by_alias=True)
    )


@router.post("/users/{user_id}")
async def get_user(user_id: EmailStr):
    user = await User.find_one(User.email == user_id, with_children=True)
    if not user:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"message": "User not found"},
        )
    return JSONResponse(
        status_code=status.HTTP_200_OK, content=user.model_dump(by_alias=True)
    )


@router.post("/users/verify/{user_id}")
async def verify_user(user_id: EmailStr, background_tasks: BackgroundTasks):
    user = await User.find_one(User.email == user_id)

    if not user:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"message": "User not found"},
        )
    user.verified = True
    save_response: User = await user.save()
    background_tasks.add_task(add_permissions_and_fields_to_verified_user, user_id)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Account verified",
            "detail": save_response.model_dump(by_alias=True),
        },
    )
