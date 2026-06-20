from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field


class UserBase(BaseModel):
    nom: str | None = None
    prenom: str | None = None
    age: int | None = None
    niveau: str | None = None
    langue: str = "fr"
    ville: str | None = None
    quartier: str | None = None
    taille: int | None = None
    categorie: str | None = None
    sport_prefere: str | None = None


class UserCreate(UserBase):
    phone_number: str
    password: str | None = None


class UserUpdate(UserBase):
    is_registered: bool | None = None
    password: str | None = None


class UserLogin(BaseModel):
    phone_number: str
    password: str


class UserRegister(UserBase):
    phone_number: str
    password: str


class UserResponse(UserBase):
    id: UUID
    phone_number: str
    is_registered: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# --- Venue Schemas ---
class VenueBase(BaseModel):
    name: str
    address: str
    city: str
    neighborhood: str
    latitude: float | None = None
    longitude: float | None = None
    google_maps_url: str | None = None


class VenueCreate(VenueBase):
    pass


class VenueResponse(VenueBase):
    id: UUID

    model_config = ConfigDict(from_attributes=True)


# --- Match Schemas ---
class MatchBase(BaseModel):
    sport: str
    match_time: datetime
    venue_id: UUID
    max_players: int = 10
    is_paid: bool = False
    price: float | None = None


class MatchCreate(MatchBase):
    creator_id: UUID


class MatchResponse(MatchBase):
    id: UUID
    creator_id: UUID
    status: str
    created_at: datetime
    venue: VenueResponse | None = None

    model_config = ConfigDict(from_attributes=True)


# --- Match Participant Schemas ---
class MatchParticipantResponse(BaseModel):
    match_id: UUID
    user_id: UUID
    status: str
    updated_at: datetime
    user: UserResponse | None = None

    model_config = ConfigDict(from_attributes=True)


# Pydantic models for WhatsApp Webhook parsing
class MessageText(BaseModel):
    body: str


class MessageButton(BaseModel):
    payload: str
    text: str


class WebhookMessage(BaseModel):
    from_field: str = Field(alias="from")
    id: str
    timestamp: str
    type: str
    text: MessageText | None = None
    button: MessageButton | None = None


class ContactProfile(BaseModel):
    name: str | None = None


class WebhookContact(BaseModel):
    profile: ContactProfile | None = None
    wa_id: str


class WebhookValue(BaseModel):
    messaging_product: str
    metadata: dict | None = None
    contacts: list[WebhookContact] | None = None
    messages: list[WebhookMessage] | None = None


class WebhookChange(BaseModel):
    value: WebhookValue
    field: str


class WebhookEntry(BaseModel):
    id: str
    changes: list[WebhookChange]


class WebhookPayload(BaseModel):
    object: str
    entry: list[WebhookEntry]


class LocationParseRequest(BaseModel):
    url_or_coords: str
