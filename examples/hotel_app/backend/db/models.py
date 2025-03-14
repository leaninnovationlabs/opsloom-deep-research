import uuid
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import declarative_base
import datetime

Base = declarative_base()

class Room(Base):
    __tablename__ = 'rooms'

    room_id = Column(Integer, primary_key=True, autoincrement=True)
    room_type = Column(String(50), nullable=False)
    rate = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)


class Guest(Base):
    __tablename__ = 'guests'

    # For SQLite, we'll store UUID as string
    guest_id = Column(
        String(36), 
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )
    full_name = Column(String(100), nullable=False)
    email = Column(String, nullable=False)  # No CITEXT in SQLite
    phone = Column(String(20), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)


class Reservation(Base):
    __tablename__ = 'reservations'

    reservation_id = Column(Integer, primary_key=True, autoincrement=True)
    
    guest_id = Column(
        String(36),
        ForeignKey('guests.guest_id'),
        nullable=False
    )
    
    room_id = Column(Integer, ForeignKey('rooms.room_id'), nullable=False)
    check_in = Column(DateTime, nullable=False)
    check_out = Column(DateTime, nullable=False)
    status = Column(String(20), nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)


class Service(Base):
    __tablename__ = 'services'
    
    service_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    price = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)


class ServiceOrders(Base):
    __tablename__ = 'service_orders'
    
    order_id = Column(Integer, primary_key=True, autoincrement=True)
    reservation_id = Column(Integer, ForeignKey('reservations.reservation_id'), nullable=False)
    service_id = Column(Integer, ForeignKey('services.service_id'), nullable=False)
    quantity = Column(Integer, nullable=False, default=1)
    status = Column(String(20), nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)


class Session(Base):
    __tablename__ = 'sessions'
    
    session_id = Column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )
    
    guest_id = Column(
        String(36),
        ForeignKey('guests.guest_id'),
        nullable=False
    )
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)


class MessagePair(Base):
    __tablename__ = 'messages'

    message_id = Column(Integer, primary_key=True, autoincrement=True)
    
    session_id = Column(
        String(36),
        ForeignKey('sessions.session_id'),
        nullable=False
    )

    guest_id = Column(
        String(36),
        ForeignKey('guests.guest_id'),
        nullable=False
    )

    user_message = Column(Text, nullable=False)
    ai_message = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)