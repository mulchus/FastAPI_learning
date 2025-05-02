from typing import Any

from users.schemas import User


def create_user(user: User) -> dict[str, Any]:
    user.name = user.name.strip().title()
    user_dump = user.model_dump()
    return {
        "success": True,
        "data": user_dump,
    }
