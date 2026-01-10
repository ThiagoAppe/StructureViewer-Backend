from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from database import get_db
from app.crud.notification import get_notification_by_id
from crud.event import mark_user_event_as_read
from app.validation import auth_required

router = APIRouter(
    prefix="/events",
    tags=["Events"]
)

@router.get("/me")
def get_user_notifications(
    payload=Depends(auth_required),
    only_unread: bool = Query(False),
    db: Session = Depends(get_db)
):
    user_id = payload["user_id"]

    return get_notification_by_id(
        db=db,
        user_id=user_id,
        only_unread=only_unread
    )


@router.post("/{user_event_id}/read")
def mark_as_read(
    user_event_id: int,
    payload=Depends(auth_required),
    db: Session = Depends(get_db)
):
    mark_user_event_as_read(
        db=db,
        user_event_id=user_event_id
    )
    return {"status": "ok"}
