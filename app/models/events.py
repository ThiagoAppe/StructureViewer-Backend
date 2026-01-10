from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey,
    Enum,
    Boolean
)
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base


class Event(Base):
    __tablename__ = "Events"

    id = Column("Id", Integer, primary_key=True)
    event_type = Column("EventType", String(50), nullable=False)
    reference_table = Column("ReferenceTable", String(100))
    reference_id = Column("ReferenceId", Integer)
    created_at = Column("CreatedAt", DateTime, default=datetime.utcnow, nullable=False)
    created_by = Column("CreatedBy", Integer, ForeignKey("Users.Id"))

    user_events = relationship("UserEvent", back_populates="event")


class UserEvent(Base):
    __tablename__ = "UserEvents"

    id = Column("Id", Integer, primary_key=True)
    event_id = Column("EventId", Integer, ForeignKey("Events.Id"), nullable=False)
    user_id = Column("UserId", Integer, ForeignKey("Users.Id"), nullable=False)
    is_read = Column("IsRead", Boolean, default=False, nullable=False)
    read_at = Column("ReadAt", DateTime)

    event = relationship("Event", back_populates="user_events")
    notifications = relationship("Notification", back_populates="user_event")


class Notification(Base):
    __tablename__ = "Notifications"

    id = Column("Id", Integer, primary_key=True)
    user_event_id = Column("UserEventId", Integer, ForeignKey("UserEvents.Id"), nullable=False)
    channel = Column("Channel", Enum("email", "system", "push"), nullable=False)
    sent = Column("Sent", Boolean, default=False, nullable=False)
    sent_at = Column("SentAt", DateTime)

    user_event = relationship("UserEvent", back_populates="notifications")
