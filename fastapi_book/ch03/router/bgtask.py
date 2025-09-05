from fastapi import APIRouter, BackgroundTasks

import time

router = APIRouter()


def send_email(email: str, message: str):
    time.sleep(5)  # Simulate a time-consuming email sending process
    print(f"Email sent to {email} with message: {message}")


@router.post("/send-notification/")
async def send_notification(background_tasks: BackgroundTasks):
    """
    Endpoint to send a notification email in the background.
    The email sending process will not block the main request/response cycle.
    """
    background_tasks.add_task(send_email, email="hello@xxx.com", message="This is a background notification email.")
    return {"message": "Notification is being sent in the background."}