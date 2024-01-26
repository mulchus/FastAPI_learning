"""
Create
Read
Update
Delete
"""

from users.schemas import User


def create_user(user: User) -> dict:
    user.name = user.name.strip().title()
    user = user.model_dump()
    return {
        "success": True,
        "data": user
    }
