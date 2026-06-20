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
    url_or_coords = request.url_or_coords.strip()
    lat, lng = None, None
    
    # 1. Vérifier si ce sont des coordonnées brutes (ex: 5.3434, -4.0123)
    coord_match = re.match(r"^\s*(-?\d+\.\d+)\s*,\s*(-?\d+\.\d+)\s*$", url_or_coords)
    if coord_match:
        try:
            lat = float(coord_match.group(1))
            lng = float(coord_match.group(2))
        except ValueError:
            pass
    else:
        # C'est un lien. Si c'est un lien raccourci Google Maps, suivre la redirection
        url = url_or_coords
        if "maps.app.goo.gl" in url or "goo.gl/maps" in url:
            try:
                async with httpx.AsyncClient(follow_redirects=True) as client:
                    res = await client.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10.0)
                    url = str(res.url)
            except Exception as e:
                logger.error(f"Error expanding short URL: {e}")
        
        # Tenter d'extraire les coordonnées depuis l'URL
        # Pattern 1: @lat,lng
        m1 = re.search(r"@(-?\d+\.\d+),(-?\d+\.\d+)", url)
        if m1:
            try:
                lat = float(m1.group(1))
                lng = float(m1.group(2))
            except ValueError:
                pass
        else:
            # Pattern 2: !3dlat!4dlng
            m2 = re.search(r"!3d(-?\d+\.\d+)!4d(-?\d+\.\d+)", url)
            if m2:
                try:
                    lat = float(m2.group(1))
                    lng = float(m2.group(2))
                except ValueError:
                    pass
            else:
                # Pattern 3: q=lat,lng
                m3 = re.search(r"[?&]q=(-?\d+\.\d+),(-?\d+\.\d+)", url)
                if m3:
                    try:
                        lat = float(m3.group(1))
                        lng = float(m3.group(2))
                    except ValueError:
                        pass
                        
    if lat is None or lng is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Impossible d'extraire des coordonnées de la localisation saisie."
        )
        
    # 2. Reverse Geocoding avec Nominatim (OpenStreetMap)
    geocoding_url = f"https://nominatim.openstreetmap.org/reverse?lat={lat}&lon={lng}&format=json&accept-language=fr"
    headers = {"User-Agent": "SportMeetApp/1.0 (contact@sportmeet.com)"}
    
    try:
        async with httpx.AsyncClient() as client:
            res = await client.get(geocoding_url, headers=headers, timeout=10.0)
            if res.status_code == 200:
                data = res.json()
                addr = data.get("address", {})
                
                # Extraire ville, quartier, route
                city = addr.get("city") or addr.get("town") or addr.get("village") or addr.get("county") or "Abidjan"
                neighborhood = addr.get("neighbourhood") or addr.get("suburb") or addr.get("quarter") or addr.get("city_district") or "Cocody"
                road = addr.get("road") or addr.get("amenity") or addr.get("building") or addr.get("suburb") or ""
                
                # Nom du lieu
                name = data.get("display_name", "").split(",")[0]
                if name.replace(".", "").replace("-", "").isdigit():
                    name = ""
                    
                return {
                    "name": name,
                    "address": road,
                    "city": city,
                    "neighborhood": neighborhood,
                    "latitude": lat,
                    "longitude": lng
                }
            else:
                raise HTTPException(
                    status_code=status.HTTP_502_BAD_GATEWAY,
                    detail="Le service de géocodage externe a retourné une erreur."
                )
    except httpx.HTTPError as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Erreur de communication avec le service de géocodage : {str(e)}"
        )


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
