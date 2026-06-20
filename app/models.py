import uuid
from datetime import datetime
from sqlalchemy import String, Integer, Boolean, DateTime, JSON, func, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base

class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    phone_number: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    nom: Mapped[str | None] = mapped_column(String(100), nullable=True)
    prenom: Mapped[str | None] = mapped_column(String(100), nullable=True)
    age: Mapped[int | None] = mapped_column(Integer, nullable=True)
    niveau: Mapped[str | None] = mapped_column(String(50), nullable=True)
    langue: Mapped[str] = mapped_column(String(10), default="fr", nullable=False)
    ville: Mapped[str | None] = mapped_column(String(100), nullable=True)
    quartier: Mapped[str | None] = mapped_column(String(100), nullable=True)
    taille: Mapped[int | None] = mapped_column(Integer, nullable=True)
    categorie: Mapped[str | None] = mapped_column(String(100), nullable=True)
    sport_prefere: Mapped[str | None] = mapped_column(String(100), nullable=True)
    hashed_password: Mapped[str | None] = mapped_column(String(255), nullable=True)
    is_registered: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)

    # Relationships
    matches_created = relationship("Match", back_populates="creator")
    match_participations = relationship("MatchParticipant", back_populates="user")


class RegistrationState(Base):
    __tablename__ = "registration_states"

    phone_number: Mapped[str] = mapped_column(String(50), primary_key=True)
    current_step: Mapped[str] = mapped_column(String(100), default="WELCOME", nullable=False)
    # temp_data stores progressive inputs: { "prenom": "Fahim", "nom": "Tiemtore", etc. }
    temp_data: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False
    )


class Venue(Base):
    __tablename__ = "venues"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    address: Mapped[str] = mapped_column(String(300), nullable=False)
    city: Mapped[str] = mapped_column(String(100), nullable=False)
    neighborhood: Mapped[str] = mapped_column(String(100), nullable=False)
    latitude: Mapped[float | None] = mapped_column(nullable=True)
    longitude: Mapped[float | None] = mapped_column(nullable=True)

    # Relationships
    matches = relationship("Match", back_populates="venue")


class Match(Base):
    __tablename__ = "matches"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    creator_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    sport: Mapped[str] = mapped_column(String(100), nullable=False)
    match_time: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    venue_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("venues.id", ondelete="CASCADE"), nullable=False)
    max_players: Mapped[int] = mapped_column(Integer, default=10, nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="pending", nullable=False) # pending, completed, cancelled
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)

    # Relationships
    creator = relationship("User", back_populates="matches_created")
    venue = relationship("Venue", back_populates="matches")
    participants = relationship("MatchParticipant", back_populates="match", cascade="all, delete-orphan")


class MatchParticipant(Base):
    __tablename__ = "match_participants"

    match_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("matches.id", ondelete="CASCADE"), primary_key=True)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    status: Mapped[str] = mapped_column(String(50), default="invited", nullable=False) # invited, confirmed, declined, waitlist
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # Relationships
    match = relationship("Match", back_populates="participants")
    user = relationship("User", back_populates="match_participations")
