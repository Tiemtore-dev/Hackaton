import hashlib
import secrets
import uuid
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import User, RegistrationState, Venue, Match, MatchParticipant
from app.schemas import UserCreate, UserUpdate, VenueCreate, MatchCreate, UserRegister, UserLogin

# --- Password Hashing Utilities ---

def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    key = hashlib.pbkdf2_hmac(
        'sha256',
        password.encode('utf-8'),
        salt.encode('utf-8'),
        100000
    )
    return f"{salt}${key.hex()}"

def verify_password(plain_password: str, hashed_password: str | None) -> bool:
    if not hashed_password:
        return False
    try:
        salt, key_hex = hashed_password.split("$")
        key = hashlib.pbkdf2_hmac(
            'sha256',
            plain_password.encode('utf-8'),
            salt.encode('utf-8'),
            100000
        )
        return key.hex() == key_hex
    except Exception:
        return False

# --- User CRUD ---

async def get_user(db: AsyncSession, user_id: uuid.UUID) -> User | None:
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalars().first()


async def get_user_by_phone_number(db: AsyncSession, phone_number: str) -> User | None:
    result = await db.execute(select(User).where(User.phone_number == phone_number))
    return result.scalars().first()


async def get_users(db: AsyncSession, skip: int = 0, limit: int = 100) -> list[User]:
    result = await db.execute(select(User).offset(skip).limit(limit))
    return list(result.scalars().all())


async def create_user(db: AsyncSession, user: UserCreate) -> User:
    hashed_pwd = hash_password(user.password) if user.password else None
    db_user = User(
        phone_number=user.phone_number,
        nom=user.nom,
        prenom=user.prenom,
        age=user.age,
        niveau=user.niveau,
        langue=user.langue,
        ville=user.ville,
        quartier=user.quartier,
        taille=user.taille,
        categorie=user.categorie,
        sport_prefere=user.sport_prefere,
        hashed_password=hashed_pwd,
        is_registered=False,
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user


async def update_user(db: AsyncSession, db_user: User, user_update: UserUpdate) -> User:
    update_data = user_update.model_dump(exclude_unset=True)
    if "password" in update_data:
        password = update_data.pop("password")
        if password:
            update_data["hashed_password"] = hash_password(password)
    for key, value in update_data.items():
        setattr(db_user, key, value)
    await db.commit()
    await db.refresh(db_user)
    return db_user


async def authenticate_user(db: AsyncSession, credentials: UserLogin) -> User | None:
    user = await get_user_by_phone_number(db, credentials.phone_number)
    if not user:
        return None
    if verify_password(credentials.password, user.hashed_password):
        return user
    return None


async def register_web_user(db: AsyncSession, user_reg: UserRegister) -> User:
    db_user = await get_user_by_phone_number(db, user_reg.phone_number)
    hashed_pwd = hash_password(user_reg.password)
    
    if db_user:
        # User already exists (e.g. created via WhatsApp), update details & set password
        db_user.nom = user_reg.nom if user_reg.nom is not None else db_user.nom
        db_user.prenom = user_reg.prenom if user_reg.prenom is not None else db_user.prenom
        db_user.age = user_reg.age if user_reg.age is not None else db_user.age
        db_user.niveau = user_reg.niveau if user_reg.niveau is not None else db_user.niveau
        db_user.ville = user_reg.ville if user_reg.ville is not None else db_user.ville
        db_user.quartier = user_reg.quartier if user_reg.quartier is not None else db_user.quartier
        db_user.taille = user_reg.taille if user_reg.taille is not None else db_user.taille
        db_user.categorie = user_reg.categorie if user_reg.categorie is not None else db_user.categorie
        db_user.sport_prefere = user_reg.sport_prefere if user_reg.sport_prefere is not None else db_user.sport_prefere
        db_user.hashed_password = hashed_pwd
        db_user.is_registered = True
    else:
        db_user = User(
            phone_number=user_reg.phone_number,
            nom=user_reg.nom,
            prenom=user_reg.prenom,
            age=user_reg.age,
            niveau=user_reg.niveau,
            ville=user_reg.ville,
            quartier=user_reg.quartier,
            taille=user_reg.taille,
            categorie=user_reg.categorie,
            sport_prefere=user_reg.sport_prefere,
            hashed_password=hashed_pwd,
            is_registered=True,
        )
        db.add(db_user)
        
    await db.commit()
    await db.refresh(db_user)
    return db_user


async def delete_user(db: AsyncSession, user_id: uuid.UUID) -> bool:
    db_user = await get_user(db, user_id)
    if db_user:
        await db.delete(db_user)
        await db.commit()
        return True
    return False


# --- Registration State CRUD ---

async def get_registration_state(db: AsyncSession, phone_number: str) -> RegistrationState | None:
    result = await db.execute(
        select(RegistrationState).where(RegistrationState.phone_number == phone_number)
    )
    return result.scalars().first()


async def create_or_update_registration_state(
    db: AsyncSession, phone_number: str, current_step: str, temp_data: dict
) -> RegistrationState:
    db_state = await get_registration_state(db, phone_number)
    if db_state:
        db_state.current_step = current_step
        db_state.temp_data = temp_data
    else:
        db_state = RegistrationState(
            phone_number=phone_number,
            current_step=current_step,
            temp_data=temp_data,
        )
        db.add(db_state)
    await db.commit()
    await db.refresh(db_state)
    return db_state


async def delete_registration_state(db: AsyncSession, phone_number: str) -> bool:
    db_state = await get_registration_state(db, phone_number)
    if db_state:
        await db.delete(db_state)
        await db.commit()
        return True
    return False


# --- Venue CRUD ---

async def create_venue(db: AsyncSession, venue: VenueCreate) -> Venue:
    db_venue = Venue(
        name=venue.name,
        address=venue.address,
        city=venue.city,
        neighborhood=venue.neighborhood,
        latitude=venue.latitude,
        longitude=venue.longitude,
        google_maps_url=venue.google_maps_url,
    )
    db.add(db_venue)
    await db.commit()
    await db.refresh(db_venue)
    return db_venue


async def get_venue(db: AsyncSession, venue_id: uuid.UUID) -> Venue | None:
    result = await db.execute(select(Venue).where(Venue.id == venue_id))
    return result.scalars().first()


async def get_venues(db: AsyncSession, skip: int = 0, limit: int = 100) -> list[Venue]:
    result = await db.execute(select(Venue).offset(skip).limit(limit))
    return list(result.scalars().all())


# --- Match CRUD ---

async def create_match(db: AsyncSession, match: MatchCreate) -> Match:
    db_match = Match(
        creator_id=match.creator_id,
        sport=match.sport,
        match_time=match.match_time,
        venue_id=match.venue_id,
        max_players=match.max_players,
        status="pending",
        is_paid=match.is_paid,
        price=match.price,
    )
    db.add(db_match)
    await db.commit()
    await db.refresh(db_match)
    return db_match


async def get_match(db: AsyncSession, match_id: uuid.UUID) -> Match | None:
    result = await db.execute(
        select(Match)
        .options(selectinload(Match.venue))
        .where(Match.id == match_id)
    )
    return result.scalars().first()



async def get_matches(db: AsyncSession, skip: int = 0, limit: int = 100) -> list[Match]:
    result = await db.execute(
        select(Match)
        .options(selectinload(Match.venue))
        .offset(skip)
        .limit(limit)
    )
    return list(result.scalars().all())


# --- Match Participant CRUD ---

async def add_match_participant(
    db: AsyncSession, match_id: uuid.UUID, user_id: uuid.UUID, status: str
) -> MatchParticipant:
    db_participant = MatchParticipant(
        match_id=match_id,
        user_id=user_id,
        status=status,
    )
    db.add(db_participant)
    await db.commit()
    await db.refresh(db_participant)
    return db_participant


async def get_match_participant(
    db: AsyncSession, match_id: uuid.UUID, user_id: uuid.UUID
) -> MatchParticipant | None:
    result = await db.execute(
        select(MatchParticipant).where(
            MatchParticipant.match_id == match_id,
            MatchParticipant.user_id == user_id
        )
    )
    return result.scalars().first()


async def update_match_participant_status(
    db: AsyncSession, match_id: uuid.UUID, user_id: uuid.UUID, status: str
) -> MatchParticipant | None:
    db_participant = await get_match_participant(db, match_id, user_id)
    if db_participant:
        db_participant.status = status
        await db.commit()
        await db.refresh(db_participant)
    return db_participant


async def get_players_for_matching(
    db: AsyncSession, sport: str, city: str, neighborhood: str
) -> list[User]:
    """
    Recherche les joueurs éligibles pour le matching :
    - Inscrits
    - Pratiquant le sport en question
    - Dans la même ville et le même quartier
    """
    result = await db.execute(
        select(User).where(
            User.is_registered == True,
            User.sport_prefere.ilike(sport),
            User.ville.ilike(city),
            User.quartier.ilike(neighborhood)
        )
    )
    return list(result.scalars().all())

