from datetime import datetime, timezone
from sqlalchemy.orm import Session
from models.events import Event, UserEvent, Notification


def create_event(
    db: Session,
    event_type: str,
    reference_table: str | None = None,
    reference_id: int | None = None,
    created_by: int | None = None
) -> Event:
    event = Event(
        event_type=event_type,
        reference_table=reference_table,
        reference_id=reference_id,
        created_by=created_by
    )
    db.add(event)
    db.flush()
    return event


def create_user_event(
    db: Session,
    event_id: int,
    user_id: int
) -> UserEvent:
    user_event = UserEvent(
        event_id=event_id,
        user_id=user_id
    )
    db.add(user_event)
    db.flush()
    return user_event


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
    return notification


def mark_user_event_as_read(
    db: Session,
    user_event_id: int
) -> None:
    user_event = db.query(UserEvent).filter(
        UserEvent.id == user_event_id
    ).first()

    if not user_event:
        return

    user_event.is_read = True
    user_event.read_at = datetime.now(timezone.utc)
    db.commit()


def get_user_events(
    db: Session,
    user_id: int,
    only_unread: bool = False
) -> list[UserEvent]:
    query = db.query(UserEvent).filter(
        UserEvent.user_id == user_id
    )

    if only_unread:
        query = query.filter(UserEvent.is_read.is_(False))

    return query.order_by(UserEvent.id.desc()).all()
