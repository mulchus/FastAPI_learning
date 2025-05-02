from time import sleep
from typing import Annotated

from fastapi import APIRouter, BackgroundTasks
from pydantic import EmailStr, Field


router = APIRouter()

MessageStr = Annotated[str, Field(min_length=5, max_length=10)]


# Функция для отправки уведомлений
def send_notification(email: EmailStr, message: MessageStr) -> None:
    sleep(5)  # Симуляция долгой операции
    print(f"Sent email to {email}: {message}")


# Маршрут для отправки уведомлений
@router.post("/send_notification/")
async def send_email(
    background_tasks: BackgroundTasks,
    email: EmailStr,
    message: MessageStr,
) -> dict[str, str]:
    background_tasks.add_task(send_notification, email, message)
    return {"message": "Notification is being sent in the background"}
