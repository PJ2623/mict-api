from src.models import User, VerifiedUser

from pydantic import EmailStr


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
