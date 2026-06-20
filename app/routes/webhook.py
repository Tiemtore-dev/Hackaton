import logging
import uuid
from fastapi import APIRouter, Depends, Query, Response, status, Request
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.config import settings
from app.services.onboarding import handle_whatsapp_message
from app.services.whatsapp import whatsapp_service
from app.models import Match, MatchParticipant
import app.crud as crud

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/webhook", tags=["whatsapp"])

async def handle_match_response(db: AsyncSession, phone_number: str, button_payload: str) -> None:
    """
    Gère la confirmation (Oui/Non) reçue par bouton WhatsApp pour un match.
    """
    parts = button_payload.split(":")
    action = parts[0]  # match_join ou match_decline
    match_id_str = parts[1]
    
    try:
        match_id = uuid.UUID(match_id_str)
    except ValueError:
        logger.error(f"UUID invalide reçu dans le bouton : {match_id_str}")
        return

    # Récupérer l'utilisateur
    user = await crud.get_user_by_phone_number(db, phone_number)
    if not user:
        logger.error(f"Joueur introuvable avec le numéro {phone_number}")
        return

    # Récupérer le match
    match = await crud.get_match(db, match_id)
    if not match:
        await whatsapp_service.send_text_message(
            to=phone_number,
            text="Désolé, cette rencontre n'existe plus ou a été annulée. 😢"
        )
        return
        
    venue = await crud.get_venue(db, match.venue_id)
    venue_name = venue.name if venue else "Terrain inconnu"

    if action == "match_join":
        # Vérifier le nombre actuel de participants confirmés
        result = await db.execute(
            select(func.count(MatchParticipant.user_id)).where(
                MatchParticipant.match_id == match.id,
                MatchParticipant.status == "confirmed"
            )
        )
        confirmed_count = result.scalar() or 0
        
        participant = await crud.get_match_participant(db, match.id, user.id)

        if confirmed_count >= match.max_players:
            # Placer en liste d'attente
            if participant:
                participant.status = "waitlist"
            else:
                await crud.add_match_participant(db, match.id, user.id, "waitlist")
            await db.commit()
            
            await whatsapp_service.send_text_message(
                to=phone_number,
                text=f"Le match de {match.sport} au terrain {venue_name} est complet. Tu es sur *liste d'attente* ! 🟡"
            )
        else:
            # Confirmer la participation
            if participant:
                participant.status = "confirmed"
            else:
                await crud.add_match_participant(db, match.id, user.id, "confirmed")
            await db.commit()
            
            date_str = match.match_time.strftime("%d/%m/%Y à %Hh%M")
            price_text = f"{int(match.price)} FCFA" if match.is_paid else "Gratuit"
            maps_link = f"\n📍 *Lien Maps* : {venue.google_maps_url}" if (venue and venue.google_maps_url) else ""
            
            await whatsapp_service.send_text_message(
                to=phone_number,
                text=(
                    f"C'est confirmé ! Ta place est réservée pour le match de *{match.sport}* le {date_str}.\n"
                    f"🏟️ *Terrain* : {venue_name} ({venue.neighborhood}){maps_link}\n"
                    f"💸 *Tarif* : *{price_text}*\n\n"
                    f"À très vite ! 🟢"
                )
            )
            
            # Notifier le créateur du match
            creator = await crud.get_user(db, match.creator_id)
            if creator and creator.phone_number != phone_number:
                await whatsapp_service.send_text_message(
                    to=creator.phone_number,
                    text=f"🔔 *Wasportly* : {user.prenom} {user.nom} a rejoint ton match de {match.sport} !"
                )
                
    elif action == "match_decline":
        participant = await crud.get_match_participant(db, match.id, user.id)
        if participant:
            participant.status = "declined"
        else:
            await crud.add_match_participant(db, match.id, user.id, "declined")
        await db.commit()
        
        await whatsapp_service.send_text_message(
            to=phone_number,
            text="C'est bien noté, pas de souci ! À une prochaine fois. ⚽"
        )


@router.get("")
async def verify_webhook(
    mode: str = Query(None, alias="hub.mode"),
    verify_token: str = Query(None, alias="hub.verify_token"),
    challenge: str = Query(None, alias="hub.challenge"),
):
    """
    Endpoint for Meta WhatsApp Webhook verification.
    """
    if mode and verify_token:
        if mode == "subscribe" and verify_token == settings.WHATSAPP_VERIFY_TOKEN:
            logger.info("Webhook verified successfully.")
            return Response(content=challenge, media_type="text/plain")
        else:
            logger.warning("Webhook verification failed. Token mismatch.")
            return Response(status_code=status.HTTP_403_FORBIDDEN, content="Verification token mismatch")
    return Response(status_code=status.HTTP_400_BAD_REQUEST, content="Missing parameters")


PROCESSED_MESSAGE_IDS = set()


@router.post("")
async def receive_webhook(request: Request, db: AsyncSession = Depends(get_db)):
    """
    Endpoint that receives messages in real-time from Meta's API.
    """
    try:
        payload = await request.json()
        logger.info(f"Webhook payload received: {payload}")
        
        # Verify if it's a WhatsApp message event
        if not payload.get("object") == "whatsapp_business_account":
            return {"status": "ignored"}

        for entry in payload.get("entry", []):
            for change in entry.get("changes", []):
                value = change.get("value", {})
                messages = value.get("messages", [])
                
                for message in messages:
                    message_id = message.get("id")
                    if message_id:
                        if message_id in PROCESSED_MESSAGE_IDS:
                            logger.info(f"Duplicate message {message_id} ignored.")
                            continue
                        PROCESSED_MESSAGE_IDS.add(message_id)
                        if len(PROCESSED_MESSAGE_IDS) > 2000:
                            PROCESSED_MESSAGE_IDS.pop()

                    sender_phone = message.get("from")
                    message_type = message.get("type")
                    
                    message_body = ""
                    button_payload = None
                    location_data = None
                    
                    if message_type == "text":
                        message_body = message.get("text", {}).get("body", "")
                    elif message_type == "interactive":
                        interactive = message.get("interactive", {})
                        interactive_type = interactive.get("type")
                        if interactive_type == "button_reply":
                            button_reply = interactive.get("button_reply", {})
                            button_payload = button_reply.get("id")
                            message_body = button_reply.get("title", "")
                        elif interactive_type == "list_reply":
                            list_reply = interactive.get("list_reply", {})
                            button_payload = list_reply.get("id")
                            message_body = list_reply.get("title", "")
                    elif message_type == "location":
                        loc = message.get("location", {})
                        location_data = {
                            "latitude": loc.get("latitude"),
                            "longitude": loc.get("longitude"),
                            "name": loc.get("name"),
                            "address": loc.get("address")
                        }
                        message_body = loc.get("name") or loc.get("address") or "Position GPS"
                    
                    # If we have a message from a sender, route it
                    if sender_phone:
                        # Si le bouton concerne la validation d'un match (Phase 2)
                        if button_payload and (button_payload.startswith("match_join:") or button_payload.startswith("match_decline:")):
                            logger.info(f"Processing match response from {sender_phone}: {button_payload}")
                            await handle_match_response(db, sender_phone, button_payload)
                        else:
                            # Sinon, onboarding d'inscription ou création d'événement (Phase 1 & 4)
                            logger.info(f"Processing message from {sender_phone}: {message_body} (Button: {button_payload})")
                            await handle_whatsapp_message(
                                db=db,
                                phone_number=sender_phone,
                                message_body=message_body,
                                button_payload=button_payload,
                                location_data=location_data
                            )
                        
        return {"status": "ok"}
    except Exception as e:
        logger.error(f"Error handling webhook event: {str(e)}")
        return {"status": "error", "message": str(e)}
