from sqlalchemy.orm import Session
from models.events import Notification


def create_notification(
    db: Session,
    user_event_id: int,
    channel: str
) -> Notification:
    notification = Notification(
        user_event_id=user_event_id,
        channel=channel
    )
    db.add(notification)
    db.flush()
    return notification


def get_notification_by_id(
    db: Session,
    notification_id: int
) -> Notification | None:
    return (
        db.query(Notification)
        .filter(Notification.id == notification_id)
        .first()
    )


def get_notifications_by_user_event(
    db: Session,
    user_event_id: int
) -> list[Notification]:
    return (
        db.query(Notification)
        .filter(Notification.user_event_id == user_event_id)
        .order_by(Notification.id.desc())
        .all()
    )


def delete_notification(
    db: Session,
    notification_id: int
) -> bool:
    notification = (
        db.query(Notification)
        .filter(Notification.id == notification_id)
        .first()
    )

    if not notification:
        return False

    db.delete(notification)
    db.commit()
    return True
