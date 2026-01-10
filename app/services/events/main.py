from sqlalchemy.orm import Session
from models.events import Event
from crud.event import (
    create_event,
    create_user_event,
    create_notification
)

def create_event_with_users(
    db: Session,
    event_type: str,
    user_ids: list[int],
    reference_table: str | None = None,
    reference_id: int | None = None,
    created_by: int | None = None,
    notification_channels: list[str] | None = None
) -> Event:
    event = create_event(
        db=db,
        event_type=event_type,
        reference_table=reference_table,
        reference_id=reference_id,
        created_by=created_by
    )

    user_events = []
    for user_id in user_ids:
        user_event = create_user_event(
            db=db,
            event_id=event.id,
            user_id=user_id
        )
        user_events.append(user_event)

    if notification_channels:
        for user_event in user_events:
            for channel in notification_channels:
                create_notification(
                    db=db,
                    user_event_id=user_event.id,
                    channel=channel
                )

    db.commit()
    db.refresh(event)
    return event
