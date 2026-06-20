import logging
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
import app.crud as crud
from app.services.whatsapp import whatsapp_service

logger = logging.getLogger(__name__)

async def run_matchmaking_for_match(db: AsyncSession, match_id: uuid.UUID) -> int:
    """
    Algorithme de matching pour trouver des partenaires de jeu.
    Recherche les joueurs pratiquant le même sport dans le même quartier
    et leur envoie une invitation WhatsApp.
    """
    logger.info(f"Démarrage du matchmaking pour le match {match_id}...")
    
    # 1. Charger les détails du match
    match = await crud.get_match(db, match_id)
    if not match:
        logger.error(f"Match {match_id} introuvable.")
        return 0
        
    # Charger le terrain
    venue = await crud.get_venue(db, match.venue_id)
    if not venue:
        logger.error(f"Terrain {match.venue_id} introuvable pour le match {match_id}.")
        return 0

    # 2. Récupérer les joueurs éligibles
    players = await crud.get_players_for_matching(
        db, 
        sport=match.sport, 
        city=venue.city, 
        neighborhood=venue.neighborhood
    )
    
    invited_count = 0
    
    # Date lisible en français
    date_str = match.match_time.strftime("%d/%m/%Y à %Hh%M")
    
    for player in players:
        # Ne pas inviter le créateur
        if player.id == match.creator_id:
            continue
            
        # Vérifier si le joueur est déjà inscrit ou invité à ce match
        existing_participant = await crud.get_match_participant(db, match.id, player.id)
        if existing_participant:
            continue
            
        # 3. Créer l'invitation en base
        await crud.add_match_participant(db, match.id, player.id, "invited")
        
        # 4. Envoyer l'invitation interactive via WhatsApp
        invitation_text = (
            f"⚽ *Opportunité de Match !* 🏀\n\n"
            f"Salut {player.prenom} ! Une partie de *{match.sport}* de niveau *{player.niveau}* s'organise dans ton quartier !\n\n"
            f"📍 *Terrain* : {venue.name} ({venue.neighborhood})\n"
            f"📅 *Date* : {date_str}\n\n"
            f"Il reste des places. Souhaites-tu rejoindre la partie ?"
        )
        
        buttons = [
            {"id": f"match_join:{match.id}", "title": "Rejoindre"},
            {"id": f"match_decline:{match.id}", "title": "Refuser"}
        ]
        
        await whatsapp_service.send_interactive_buttons(
            to=player.phone_number,
            text=invitation_text,
            buttons=buttons
        )
        
        invited_count += 1
        logger.info(f"Invitation envoyée au joueur {player.prenom} {player.nom} ({player.phone_number})")
        
    return invited_count
