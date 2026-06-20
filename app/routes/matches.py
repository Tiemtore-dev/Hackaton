import re
import httpx
import uuid
import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas import VenueCreate, VenueResponse, MatchCreate, MatchResponse, MatchParticipantResponse, LocationParseRequest
from app.models import MatchParticipant
import app.crud as crud
from app.services.matching import run_matchmaking_for_match
from app.services.geocoding import parse_location

logger = logging.getLogger(__name__)

router = APIRouter(tags=["matches"])


# --- Venue Routes ---

@router.post("/venues", response_model=VenueResponse, status_code=status.HTTP_201_CREATED)
async def create_venue(venue: VenueCreate, db: AsyncSession = Depends(get_db)):
    """
    Créer un terrain de sport (ex. Agora Koumassi, City Sport Cocody).
    """
    return await crud.create_venue(db, venue)


@router.get("/venues", response_model=list[VenueResponse])
async def list_venues(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    """
    Lister tous les terrains de sport enregistrés.
    """
    return await crud.get_venues(db, skip, limit)


@router.post("/venues/parse-location")
async def parse_location_endpoint(request: LocationParseRequest):
    """
    Analyser une localisation (coordonnées ou lien Google Maps), extraire les coordonnées
    et faire du reverse-geocoding (Nominatim) pour obtenir la ville, quartier et adresse.
    """
    parsed = await parse_location(request.url_or_coords)
    if not parsed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Impossible d'extraire des coordonnées de la localisation saisie."
        )
    return parsed


# --- Match Routes ---

@router.get("/matches", response_model=list[MatchResponse])
async def list_matches(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    """
    Lister tous les matchs programmés.
    """
    return await crud.get_matches(db, skip, limit)


@router.post("/matches", response_model=MatchResponse, status_code=status.HTTP_201_CREATED)
async def create_match(match: MatchCreate, db: AsyncSession = Depends(get_db)):
    """
    Créer une rencontre sportive, inscrire automatiquement le créateur
    et lancer le matchmaking pour inviter les joueurs correspondants via WhatsApp.
    """
    # Vérifier que le créateur existe
    creator = await crud.get_user(db, match.creator_id)
    if not creator:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Créateur du match introuvable"
        )
        
    # Vérifier que le terrain existe
    venue = await crud.get_venue(db, match.venue_id)
    if not venue:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Terrain de sport introuvable"
        )

    # 1. Créer le match en base
    db_match = await crud.create_match(db, match)
    
    # 2. Inscrire automatiquement le créateur comme participant confirmé
    await crud.add_match_participant(db, db_match.id, db_match.creator_id, "confirmed")
    
    # 3. Lancer le matchmaking (synchrone/bloquant pour la validation simplifiée du MVP)
    invited_count = await run_matchmaking_for_match(db, db_match.id)
    
    logger_msg = f"Match créé avec ID {db_match.id}. {invited_count} invitations WhatsApp envoyées."
    logger.info(logger_msg)
    
    # Re-charger le match
    match_with_relations = await crud.get_match(db, db_match.id)
    return match_with_relations


@router.get("/matches/{match_id}", response_model=MatchResponse)
async def get_match_details(match_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    """
    Obtenir les détails d'un match par son UUID.
    """
    db_match = await crud.get_match(db, match_id)
    if not db_match:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Match introuvable"
        )
    return db_match


@router.get("/matches/{match_id}/participants", response_model=list[MatchParticipantResponse])
async def list_match_participants(match_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    """
    Lister l'ensemble des participants d'un match avec leur statut (invited, confirmed, declined, waitlist).
    """
    # Vérifier que le match existe
    db_match = await crud.get_match(db, match_id)
    if not db_match:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Match introuvable"
        )
        
    result = await db.execute(
        select(MatchParticipant)
        .options(selectinload(MatchParticipant.user))
        .where(MatchParticipant.match_id == match_id)
    )
    return list(result.scalars().all())
