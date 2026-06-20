import logging
import uuid
import re
from datetime import datetime, timedelta
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.whatsapp import whatsapp_service
from app.config import settings
import app.crud as crud
from app.schemas import UserCreate, VenueCreate
from app.models import Venue, Match, MatchParticipant
from app.services.matching import run_matchmaking_for_match
from app.services.geocoding import parse_location

logger = logging.getLogger(__name__)

# Helpers
def parse_hour_helper(text_lower: str) -> tuple[int, int]:
    hour = 18
    minute = 0
    # Pattern 1: 19h30 or 19h
    m_hour = re.search(r"(\d{1,2})h(\d{2})?", text_lower)
    if m_hour:
        try:
            hour = int(m_hour.group(1))
            if m_hour.group(2):
                minute = int(m_hour.group(2))
            return hour, minute
        except ValueError:
            pass
    # Pattern 2: 19:30
    m_colon = re.search(r"(\d{1,2}):(\d{2})", text_lower)
    if m_colon:
        try:
            return int(m_colon.group(1)), int(m_colon.group(2))
        except ValueError:
            pass
    # Pattern 3: simple number like "à 19"
    m_simple = re.search(r"(?:à|@|a)?\s*(\d{1,2})\s*(?:heures?|hrs?)?", text_lower)
    if m_simple:
        try:
            val = int(m_simple.group(1))
            if 0 <= val <= 23:
                return val, 0
        except ValueError:
            pass
    return hour, minute


def parse_date_input(text: str) -> datetime:
    text = text.strip()
    text_lower = text.lower()
    
    # Check DD/MM/YYYY HH:MM
    m1 = re.search(r"(\d{1,2})/(\d{1,2})/(\d{4})\s+(\d{1,2})h?(\d{2})?", text)
    if m1:
        day, month, year, hour, minute = m1.groups()
        minute = minute or "00"
        try:
            return datetime(int(year), int(month), int(day), int(hour), int(minute))
        except ValueError:
            pass
            
    # Check DD/MM HH:MM or DD/MM à HHhMM
    m2 = re.search(r"(\d{1,2})/(\d{1,2})\s*(?:à|@|a)?\s*(\d{1,2})h?(\d{2})?", text, re.IGNORECASE)
    if m2:
        day, month, hour, minute = m2.groups()
        minute = minute or "00"
        year = datetime.now().year
        try:
            dt = datetime(year, int(month), int(day), int(hour), int(minute))
            if dt < datetime.now():
                dt = dt.replace(year=year+1)
            return dt
        except ValueError:
            pass

    # Check for "demain"
    if "demain" in text_lower:
        now = datetime.now()
        target_date = now + timedelta(days=1)
        hour, minute = parse_hour_helper(text_lower)
        return target_date.replace(hour=hour, minute=minute, second=0, microsecond=0)

    # Check for "ce soir" or "aujourd'hui"
    if "ce soir" in text_lower or "aujourd" in text_lower:
        now = datetime.now()
        hour, minute = parse_hour_helper(text_lower)
        return now.replace(hour=hour, minute=minute, second=0, microsecond=0)

    # Check for weekday name (lundi, mardi, etc.)
    weekdays = {
        "lundi": 0,
        "mardi": 1,
        "mercredi": 2,
        "jeudi": 3,
        "vendredi": 4,
        "samedi": 5,
        "dimanche": 6
    }
    
    day_num = None
    for name, num in weekdays.items():
        if name in text_lower:
            day_num = num
            break
            
    if day_num is not None:
        now = datetime.now()
        days_ahead = day_num - now.weekday()
        if days_ahead <= 0:
            days_ahead += 7
        target_date = now + timedelta(days=days_ahead)
        hour, minute = parse_hour_helper(text_lower)
        return target_date.replace(hour=hour, minute=minute, second=0, microsecond=0)

    # Fallback: tomorrow at 18:00
    return datetime.now().replace(hour=18, minute=0, second=0, microsecond=0) + timedelta(days=1)


def parse_neighborhood(address: str, default_neighborhood: str) -> str:
    neighborhoods = ["Koumassi", "Cocody", "Marcory", "Treichville", "Yopougon", "Plateau", "Adjamé", "Abobo", "Port-Bouët", "Bingerville"]
    address_lower = address.lower() if address else ""
    for n in neighborhoods:
        if n.lower() in address_lower:
            return n
    return default_neighborhood


def generate_time_slots(now: datetime) -> list[dict]:
    slots = []
    
    # 1. Today's slots
    if now.hour < 17:
        t1 = now.replace(hour=18, minute=0, second=0, microsecond=0)
        slots.append({
            "id": f"date_slot:{t1.isoformat()}",
            "title": "Ce soir à 18:00 🌅",
            "description": t1.strftime("%d/%m/%Y à 18h00")
        })
    if now.hour < 19:
        t2 = now.replace(hour=20, minute=0, second=0, microsecond=0)
        slots.append({
            "id": f"date_slot:{t2.isoformat()}",
            "title": "Ce soir à 20:00 🌃",
            "description": t2.strftime("%d/%m/%Y à 20h00")
        })
        
    # 2. Tomorrow's slots
    tomorrow = now + timedelta(days=1)
    t3 = tomorrow.replace(hour=18, minute=0, second=0, microsecond=0)
    slots.append({
        "id": f"date_slot:{t3.isoformat()}",
        "title": "Demain à 18:00 🌅",
        "description": t3.strftime("%d/%m/%Y à 18h00")
    })
    t4 = tomorrow.replace(hour=20, minute=0, second=0, microsecond=0)
    slots.append({
        "id": f"date_slot:{t4.isoformat()}",
        "title": "Demain à 20:00 🌃",
        "description": t4.strftime("%d/%m/%Y à 20h00")
    })
    
    # 3. Next Saturday
    days_to_sat = (5 - now.weekday()) % 7
    if days_to_sat == 0 and now.hour >= 16:
        days_to_sat = 7
    sat = now + timedelta(days=days_to_sat)
    
    sat_10 = sat.replace(hour=10, minute=0, second=0, microsecond=0)
    slots.append({
        "id": f"date_slot:{sat_10.isoformat()}",
        "title": f"Samedi à 10:00 ☀️",
        "description": sat_10.strftime("%d/%m/%Y à 10h00")
    })
    
    sat_17 = sat.replace(hour=17, minute=0, second=0, microsecond=0)
    slots.append({
        "id": f"date_slot:{sat_17.isoformat()}",
        "title": f"Samedi à 17:00 🌆",
        "description": sat_17.strftime("%d/%m/%Y à 17h00")
    })

    # 4. Next Sunday
    days_to_sun = (6 - now.weekday()) % 7
    if days_to_sun == 0 and now.hour >= 16:
        days_to_sun = 7
    sun = now + timedelta(days=days_to_sun)
    
    sun_16 = sun.replace(hour=16, minute=0, second=0, microsecond=0)
    slots.append({
        "id": f"date_slot:{sun_16.isoformat()}",
        "title": f"Dimanche à 16:00 🌆",
        "description": sun_16.strftime("%d/%m/%Y à 16h00")
    })
    
    # 5. Manual option
    slots.append({
        "id": "date_slot_manual",
        "title": "Saisir manuellement ✍️",
        "description": "Saisir une date et heure personnalisées"
    })
    
    return slots


async def send_match_confirmation_prompt(db: AsyncSession, phone_number: str, temp_data: dict) -> None:
    sport = temp_data.get("sport")
    dt_parsed = datetime.fromisoformat(temp_data.get("match_time"))
    date_str = dt_parsed.strftime("%d/%m/%Y à %Hh%M")
    venue_name = temp_data.get("venue_name")
    max_players = temp_data.get("max_players")
    is_paid = temp_data.get("is_paid", False)
    price = temp_data.get("price", 0.0)
    
    price_text = f"Payant ({int(price)} FCFA) 💸" if is_paid else "Gratuit 🟢"
    
    confirm_text = (
        f"⚽ *Résumé du Match à Créer :*\n\n"
        f"- Sport : *{sport}*\n"
        f"- Date : *{date_str}*\n"
        f"- Terrain : *{venue_name}*\n"
        f"- Joueurs max : *{max_players}*\n"
        f"- Tarif : *{price_text}*\n\n"
        f"Souhaitez-vous valider et envoyer les invitations WhatsApp ?"
    )
    await whatsapp_service.send_interactive_buttons(
        to=phone_number,
        text=confirm_text,
        buttons=[
            {"id": "match_confirm_yes", "title": "Confirmer"},
            {"id": "match_confirm_cancel", "title": "Annuler"}
        ]
    )


async def handle_whatsapp_message(
    db: AsyncSession,
    phone_number: str,
    message_body: str,
    button_payload: str | None = None,
    location_data: dict | None = None
) -> None:
    # 1. Get user profile
    user = await crud.get_user_by_phone_number(db, phone_number)
    
    # 2. Get registration or creation state
    state = await crud.get_registration_state(db, phone_number)
    
    # Clean input
    input_text = (button_payload or message_body or "").strip()
    
    # CASE A: User is already registered
    if user and user.is_registered:
        # If there is no active creation/registration state
        if not state:
            # Check if user typed an option or clicked a menu button
            if input_text == "1" or input_text.lower() == "organiser" or input_text == "menu_organise":
                # Start Match Creation state machine!
                temp_data = {}
                await crud.create_or_update_registration_state(db, phone_number, "CREATE_MATCH_SPORT", temp_data)
                await whatsapp_service.send_interactive_list(
                    to=phone_number,
                    text="⚽ *Organiser un match* 🏀\n\nQuel sport souhaitez-vous organiser ?",
                    button_label="Choisir le sport",
                    sections=[
                        {
                            "title": "Sports",
                            "rows": [
                                {"id": "sport_football", "title": "Football ⚽"},
                                {"id": "sport_basketball", "title": "Basketball 🏀"},
                                {"id": "sport_tennis", "title": "Tennis 🎾"},
                                {"id": "sport_boxe", "title": "Boxe 🥊"}
                            ]
                        }
                    ]
                )
                return
                
            elif input_text == "2" or input_text.lower() == "matchs" or input_text == "menu_matchs":
                # List user's active matches (created or joined)
                stmt = (
                    select(MatchParticipant)
                    .where(MatchParticipant.user_id == user.id)
                )
                result = await db.execute(stmt)
                participations = result.scalars().all()
                
                if not participations:
                    await whatsapp_service.send_text_message(
                        to=phone_number,
                        text="Vous n'avez aucun match programmé pour le moment. 📅\nTapez *1* pour en organiser un !"
                    )
                    return
                
                lines = ["📅 *Vos matchs programmés :*"]
                for part in participations:
                    match_details = await crud.get_match(db, part.match_id)
                    if match_details:
                        date_str = match_details.match_time.strftime("%d/%m à %Hh%M")
                        venue_name = match_details.venue.name if match_details.venue else "Terrain inconnu"
                        status_emoji = "🟢" if part.status == "confirmed" else "🟡" if part.status == "waitlist" else "🔵"
                        price_text = f"{int(match_details.price)} FCFA" if match_details.is_paid else "Gratuit"
                        lines.append(
                            f"- {status_emoji} *{match_details.sport}* le {date_str} ({price_text})\n"
                            f"  📍 {venue_name} ({part.status})"
                        )
                
                await whatsapp_service.send_text_message(to=phone_number, text="\n".join(lines))
                return
                
            elif input_text == "3" or input_text.lower() == "carte" or input_text == "menu_carte":
                # Display player card details
                card_text = (
                    f"💳 *Votre Carte Joueur Wasportly* :\n\n"
                    f"👤 Nom complet : {user.prenom} {user.nom}\n"
                    f"🎂 Âge : {user.age} ans\n"
                    f"📏 Taille : {user.taille} cm\n"
                    f"📊 Niveau : {user.niveau}\n"
                    f"🏆 Catégorie : {user.categorie}\n"
                    f"⚽ Sport préféré : {user.sport_prefere}\n"
                    f"📍 Localisation : {user.quartier}, {user.ville}\n"
                    f"🔗 Visualiser sur le Web : {settings.FRONTEND_URL}/?phone={user.phone_number}"
                )
                await whatsapp_service.send_text_message(to=phone_number, text=card_text)
                return
                
            else:
                # Send Main Menu
                menu_text = (
                    f"Salut {user.prenom} ! Bienvenue sur le menu principal Wasportly. 🏆\n\n"
                    "Que souhaitez-vous faire ?\n"
                    "1️⃣ *Organiser un match* ⚽\n"
                    "2️⃣ *Voir mes matchs programmés* 📅\n"
                    "3️⃣ *Voir ma carte joueur* 💳\n\n"
                    "Répondez par le numéro de l'option (1, 2, 3) !"
                )
                await whatsapp_service.send_interactive_buttons(
                    to=phone_number,
                    text=menu_text,
                    buttons=[
                        {"id": "menu_organise", "title": "Organiser match"},
                        {"id": "menu_matchs", "title": "Mes Matchs"},
                        {"id": "menu_carte", "title": "Ma Carte"}
                    ]
                )
                return

        # If they do have a state and it starts with CREATE_MATCH_
        current_step = state.current_step
        temp_data = dict(state.temp_data)
        
        if current_step == "CREATE_MATCH_SPORT":
            if not input_text:
                await whatsapp_service.send_text_message(to=phone_number, text="S'il vous plaît, entrez le sport :")
                return
            sport_map = {
                "sport_football": "Football",
                "sport_basketball": "Basketball",
                "sport_tennis": "Tennis",
                "sport_boxe": "Boxe",
            }
            sport = sport_map.get(input_text.lower(), input_text.capitalize())
            temp_data["sport"] = sport
            await crud.create_or_update_registration_state(db, phone_number, "CREATE_MATCH_DATE", temp_data)
            
            slots = generate_time_slots(datetime.now())
            await whatsapp_service.send_interactive_list(
                to=phone_number,
                text="Quand aura lieu le match ? 📅\n\nSélectionnez une option de date/heure ci-dessous ou choisissez de saisir une heure personnalisée.",
                button_label="Choisir la date",
                sections=[
                    {
                        "title": "Options proposées",
                        "rows": slots
                    }
                ]
            )
            return
            
        elif current_step == "CREATE_MATCH_DATE":
            if not input_text:
                await whatsapp_service.send_text_message(to=phone_number, text="S'il vous plaît, sélectionnez une date ou écrivez-la :")
                return
            
            if input_text == "date_slot_manual":
                await whatsapp_service.send_text_message(
                    to=phone_number,
                    text="Veuillez saisir le jour et l'heure manuellement (ex: 22/06 à 18h, ou Samedi à 17:00) : ✍️"
                )
                temp_data["waiting_for_manual_date"] = True
                await crud.create_or_update_registration_state(db, phone_number, "CREATE_MATCH_DATE", temp_data)
                return
            
            if input_text.startswith("date_slot:"):
                iso_str = input_text.split(":", 1)[1]
                parsed_dt = datetime.fromisoformat(iso_str)
                temp_data["match_time"] = parsed_dt.isoformat()
                temp_data["match_time_text"] = parsed_dt.strftime("%d/%m à %Hh%M")
            else:
                parsed_dt = parse_date_input(input_text)
                temp_data["match_time"] = parsed_dt.isoformat()
                temp_data["match_time_text"] = input_text
                
            temp_data.pop("waiting_for_manual_date", None)
            await crud.create_or_update_registration_state(db, phone_number, "CREATE_MATCH_LOCATION", temp_data)
            await whatsapp_service.send_text_message(
                to=phone_number,
                text=(
                    "Où se déroulera le match ? 📍\n\n"
                    "👉 Option A: Partagez la position GPS/localisation via WhatsApp (Bouton + > Localisation).\n"
                    "👉 Option B: Entrez simplement le nom du terrain (ex: Agora Koumassi) ou un lien Google Maps."
                )
            )
            return
            
        elif current_step == "CREATE_MATCH_LOCATION":
            # Handle GPS upload
            if location_data:
                lat = location_data.get("latitude")
                lon = location_data.get("longitude")
                name = location_data.get("name") or "Position Partagée"
                addr = location_data.get("address") or f"Coords: {lat}, {lon}"
                city = "Abidjan"
                neigh = parse_neighborhood(addr, user.quartier or "Cocody")
                
                # Create Venue
                venue_in = VenueCreate(
                    name=name,
                    address=addr,
                    city=city,
                    neighborhood=neigh,
                    latitude=lat,
                    longitude=lon
                )
                venue = await crud.create_venue(db, venue_in)
                temp_data["venue_id"] = str(venue.id)
                temp_data["venue_name"] = f"{venue.name} ({venue.neighborhood})"
                
                await whatsapp_service.send_text_message(
                    to=phone_number,
                    text=f"📍 Localisation GPS reçue et terrain enregistré : *{venue.name}* ({venue.neighborhood}) !"
                )
            else:
                # Handle text name input
                if not input_text:
                    await whatsapp_service.send_text_message(to=phone_number, text="Entrez le nom du terrain ou partagez la position GPS :")
                    return
                
                # Check if it's a Google Maps link or coordinates string
                is_url_or_coords = "http" in input_text or re.match(r"^\s*(-?\d+\.\d+)\s*,\s*(-?\d+\.\d+)\s*$", input_text)
                parsed = None
                if is_url_or_coords:
                    parsed = await parse_location(input_text)
                
                if parsed:
                    # Create a new venue from parsed maps link
                    venue_in = VenueCreate(
                        name=parsed["name"],
                        address=parsed["address"],
                        city=parsed["city"],
                        neighborhood=parsed["neighborhood"],
                        latitude=parsed["latitude"],
                        longitude=parsed["longitude"],
                        google_maps_url=parsed["google_maps_url"]
                    )
                    venue = await crud.create_venue(db, venue_in)
                    temp_data["venue_id"] = str(venue.id)
                    temp_data["venue_name"] = f"{venue.name} ({venue.neighborhood})"
                    await whatsapp_service.send_text_message(
                        to=phone_number,
                        text=f"📍 Lien Google Maps ou coordonnées GPS analysés ! Terrain enregistré : *{venue.name}* ({venue.neighborhood}, {venue.city}) !"
                    )
                else:
                    # Look up existing venue matching text
                    stmt = select(Venue).where(Venue.name.ilike(input_text))
                    res = await db.execute(stmt)
                    existing_venue = res.scalars().first()
                    
                    if existing_venue:
                        temp_data["venue_id"] = str(existing_venue.id)
                        temp_data["venue_name"] = existing_venue.name
                    else:
                        # Create new Venue based on typed text
                        venue_in = VenueCreate(
                            name=input_text,
                            address=input_text,
                            city=user.ville or "Abidjan",
                            neighborhood=user.quartier or "Cocody"
                        )
                        venue = await crud.create_venue(db, venue_in)
                        temp_data["venue_id"] = str(venue.id)
                        temp_data["venue_name"] = venue.name
            
            await crud.create_or_update_registration_state(db, phone_number, "CREATE_MATCH_PLAYERS", temp_data)
            await whatsapp_service.send_text_message(
                to=phone_number,
                text="Combien de joueurs maximum pour cette partie ? (ex: 10, 5) :"
            )
            return
            
        elif current_step == "CREATE_MATCH_PLAYERS":
            try:
                max_players = int(input_text)
                if max_players < 2 or max_players > 100:
                    raise ValueError()
            except ValueError:
                await whatsapp_service.send_text_message(to=phone_number, text="Veuillez entrer un nombre de joueurs valide (entre 2 et 100) :")
                return
                
            temp_data["max_players"] = max_players
            await crud.create_or_update_registration_state(db, phone_number, "CREATE_MATCH_PAYMENT_TYPE", temp_data)
            await whatsapp_service.send_interactive_buttons(
                to=phone_number,
                text="Est-ce que ce match est gratuit ou payant ? 💸",
                buttons=[
                    {"id": "pay_free", "title": "Gratuit"},
                    {"id": "pay_paid", "title": "Payant"}
                ]
            )
            return

        elif current_step == "CREATE_MATCH_PAYMENT_TYPE":
            val = input_text.lower()
            if val in ["pay_free", "gratuit", "free"]:
                temp_data["is_paid"] = False
                temp_data["price"] = 0.0
                await crud.create_or_update_registration_state(db, phone_number, "CREATE_MATCH_CONFIRM", temp_data)
                await send_match_confirmation_prompt(db, phone_number, temp_data)
                return
            elif val in ["pay_paid", "payant", "paid"]:
                temp_data["is_paid"] = True
                await crud.create_or_update_registration_state(db, phone_number, "CREATE_MATCH_PRICE", temp_data)
                await whatsapp_service.send_text_message(
                    to=phone_number,
                    text="Quel est le prix/tarif par joueur pour ce match (en FCFA, ex: 1500) ? 💸"
                )
                return
            else:
                await whatsapp_service.send_interactive_buttons(
                    to=phone_number,
                    text="Veuillez choisir une option en utilisant les boutons ou en écrivant 'Gratuit' ou 'Payant' :",
                    buttons=[
                        {"id": "pay_free", "title": "Gratuit"},
                        {"id": "pay_paid", "title": "Payant"}
                    ]
                )
                return

        elif current_step == "CREATE_MATCH_PRICE":
            if not input_text:
                await whatsapp_service.send_text_message(
                    to=phone_number,
                    text="Veuillez entrer le prix par joueur (ex: 1500) :"
                )
                return
            cleaned = "".join(c for c in input_text if c.isdigit())
            try:
                price = float(cleaned)
                if price < 0:
                    raise ValueError()
            except ValueError:
                await whatsapp_service.send_text_message(
                    to=phone_number,
                    text="Veuillez saisir un tarif valide (un nombre supérieur ou égal à 0, ex: 1500) :"
                )
                return
            temp_data["price"] = price
            await crud.create_or_update_registration_state(db, phone_number, "CREATE_MATCH_CONFIRM", temp_data)
            await send_match_confirmation_prompt(db, phone_number, temp_data)
            return
            
        elif current_step == "CREATE_MATCH_CONFIRM":
            if input_text.lower() in ["confirmer", "oui", "match_confirm_yes"]:
                # 1. Create match in db
                sport = temp_data.get("sport")
                dt = datetime.fromisoformat(temp_data.get("match_time"))
                vid = uuid.UUID(temp_data.get("venue_id"))
                max_p = temp_data.get("max_players")
                
                db_match = Match(
                    creator_id=user.id,
                    sport=sport,
                    match_time=dt,
                    venue_id=vid,
                    max_players=max_p,
                    status="pending",
                    is_paid=temp_data.get("is_paid", False),
                    price=temp_data.get("price", 0.0)
                )
                db.add(db_match)
                await db.commit()
                await db.refresh(db_match)
                
                # 2. Join creator as confirmed
                await crud.add_match_participant(db, db_match.id, user.id, "confirmed")
                
                # 3. Trigger matchmaking invitations
                invited_count = await run_matchmaking_for_match(db, db_match.id)
                
                # 4. Clean up registration state
                await crud.delete_registration_state(db, phone_number)
                
                success_text = (
                    f"🎉 *Match créé avec succès !*\n\n"
                    f"Nous avons identifié et invité *{invited_count}* joueur(s) dans le quartier de {temp_data.get('venue_name')}. Vous recevrez une alerte dès qu'ils confirmeront !"
                )
                await whatsapp_service.send_text_message(to=phone_number, text=success_text)
                return
            else:
                # Cancel creation
                await crud.delete_registration_state(db, phone_number)
                await whatsapp_service.send_text_message(to=phone_number, text="Création annulée. Retour au menu principal. Vous pouvez retaper '1' à tout moment.")
                return

    # CASE B: User is not registered yet (Signup flow)
    if not state:
        # User is starting onboarding
        temp_data = {}
        await crud.create_or_update_registration_state(db, phone_number, "ASK_PRENOM", temp_data)
        
        welcome_text = (
            "⚽ *Bienvenue sur Wasportly !* 🏀\n\n"
            "Je suis votre assistant Wasportly. Je vais vous aider à créer votre *Carte Joueur* en quelques instants pour vous mettre en relation avec d'autres sportifs près de chez vous.\n\n"
            "Commençons dès maintenant ! Quel est votre *prénom* ? 😊"
        )
        await whatsapp_service.send_text_message(to=phone_number, text=welcome_text)
        return

    # User is in the middle of onboarding
    current_step = state.current_step
    temp_data = dict(state.temp_data)

    if current_step == "ASK_PRENOM":
        if not input_text:
            await whatsapp_service.send_text_message(to=phone_number, text="S'il vous plaît, entrez votre prénom :")
            return
        temp_data["prenom"] = input_text
        await crud.create_or_update_registration_state(db, phone_number, "ASK_NOM", temp_data)
        await whatsapp_service.send_text_message(to=phone_number, text="Enchanté ! Quel est votre *nom* de famille ?")
        return

    elif current_step == "ASK_NOM":
        if not input_text:
            await whatsapp_service.send_text_message(to=phone_number, text="S'il vous plaît, entrez votre nom :")
            return
        temp_data["nom"] = input_text
        await crud.create_or_update_registration_state(db, phone_number, "ASK_AGE", temp_data)
        await whatsapp_service.send_text_message(to=phone_number, text="Quel est votre *âge* (ex. 25) ?")
        return

    elif current_step == "ASK_AGE":
        try:
            age = int(input_text)
            if age <= 0 or age > 120:
                raise ValueError()
        except ValueError:
            await whatsapp_service.send_text_message(
                to=phone_number,
                text="Veuillez entrer un âge valide sous forme de nombre (ex: 22) :"
            )
            return
        
        temp_data["age"] = age
        await crud.create_or_update_registration_state(db, phone_number, "ASK_NIVEAU", temp_data)
        
        await whatsapp_service.send_interactive_buttons(
            to=phone_number,
            text="Quel est votre niveau de pratique sportive global ?",
            buttons=[
                {"id": "level_debutant", "title": "Débutant"},
                {"id": "level_intermediaire", "title": "Intermédiaire"},
                {"id": "level_avance", "title": "Avancé"}
            ]
        )
        return

    elif current_step == "ASK_NIVEAU":
        level_map = {
            "level_debutant": "Débutant",
            "level_intermediaire": "Intermédiaire",
            "level_avance": "Avancé",
            "débutant": "Débutant",
            "intermédiaire": "Intermédiaire",
            "avancé": "Avancé"
        }
        
        level = level_map.get(input_text.lower(), input_text)
        temp_data["niveau"] = level
        await crud.create_or_update_registration_state(db, phone_number, "ASK_LANGUE", temp_data)
        
        await whatsapp_service.send_interactive_list(
            to=phone_number,
            text="Quelle est votre langue préférée ? 🌐",
            button_label="Choisir la langue",
            sections=[
                {
                    "title": "Langues",
                    "rows": [
                        {"id": "lang_darija", "title": "Darija 🇲🇦"},
                        {"id": "lang_darija_en", "title": "Darija + Anglais 🇲🇦🇬🇧"},
                        {"id": "lang_fr_en", "title": "Français + Anglais 🇫🇷🇬🇧"},
                        {"id": "lang_darija_fr", "title": "Darija + Français 🇲🇦🇫🇷"},
                        {"id": "lang_all", "title": "Les 3 (Darija+Fr+En) 🇲🇦🇫🇷🇬🇧"}
                    ]
                }
            ]
        )
        return

    elif current_step == "ASK_LANGUE":
        lang_map = {
            "lang_darija": "Darija",
            "lang_darija_en": "Darija + Anglais",
            "lang_fr_en": "Français + Anglais",
            "lang_darija_fr": "Darija + Français",
            "lang_all": "Darija + Français + Anglais",
            "darija": "Darija",
            "darija+anglais": "Darija + Anglais",
            "darija + anglais": "Darija + Anglais",
            "français+anglais": "Français + Anglais",
            "français + anglais": "Français + Anglais",
            "darija+français": "Darija + Français",
            "darija + français": "Darija + Français",
            "les 3": "Darija + Français + Anglais",
            "les trois": "Darija + Français + Anglais",
            "toutes": "Darija + Français + Anglais",
        }
        
        lang = lang_map.get(input_text.lower(), input_text)
        temp_data["langue"] = lang
        await crud.create_or_update_registration_state(db, phone_number, "ASK_VILLE", temp_data)
        await whatsapp_service.send_text_message(
            to=phone_number, 
            text="Dans quelle *ville* résidez-vous (ex: Abidjan, Bouaké) ?"
        )
        return

    elif current_step == "ASK_VILLE":
        if not input_text:
            await whatsapp_service.send_text_message(to=phone_number, text="S'il vous plaît, entrez votre ville :")
            return
        temp_data["ville"] = input_text
        await crud.create_or_update_registration_state(db, phone_number, "ASK_QUARTIER", temp_data)
        await whatsapp_service.send_text_message(
            to=phone_number, 
            text="Quel est votre *quartier* de résidence (ex: Cocody, Marcory) ?"
        )
        return

    elif current_step == "ASK_QUARTIER":
        if not input_text:
            await whatsapp_service.send_text_message(to=phone_number, text="S'il vous plaît, entrez votre quartier :")
            return
        temp_data["quartier"] = input_text
        await crud.create_or_update_registration_state(db, phone_number, "ASK_TAILLE", temp_data)
        await whatsapp_service.send_text_message(
            to=phone_number, 
            text="Quelle est votre *taille* en centimètres (ex. 180) ?"
        )
        return

    elif current_step == "ASK_TAILLE":
        try:
            taille = int(input_text)
            if taille < 50 or taille > 280:
                raise ValueError()
        except ValueError:
            await whatsapp_service.send_text_message(
                to=phone_number,
                text="Veuillez entrer une taille valide en centimètres sous forme de nombre entier (ex: 175) :"
            )
            return
        
        temp_data["taille"] = taille
        await crud.create_or_update_registration_state(db, phone_number, "ASK_CATEGORIE", temp_data)
        
        await whatsapp_service.send_interactive_buttons(
            to=phone_number,
            text="Dans quelle catégorie vous situez-vous principalement ?",
            buttons=[
                {"id": "cat_senior", "title": "Senior"},
                {"id": "cat_loisir", "title": "Loisir"},
                {"id": "cat_competition", "title": "Compétition"}
            ]
        )
        return

    elif current_step == "ASK_CATEGORIE":
        cat_map = {
            "cat_senior": "Senior",
            "cat_loisir": "Loisir",
            "cat_competition": "Compétition",
            "senior": "Senior",
            "loisir": "Loisir",
            "compétition": "Compétition"
        }
        
        category = cat_map.get(input_text.lower(), input_text)
        temp_data["categorie"] = category
        await crud.create_or_update_registration_state(db, phone_number, "ASK_SPORT", temp_data)
        
        await whatsapp_service.send_interactive_list(
            to=phone_number,
            text="Quel est votre *sport préféré* ? 🏆",
            button_label="Choisir le sport",
            sections=[
                {
                    "title": "Sports",
                    "rows": [
                        {"id": "sport_football", "title": "Football ⚽"},
                        {"id": "sport_basketball", "title": "Basketball 🏀"},
                        {"id": "sport_tennis", "title": "Tennis 🎾"},
                        {"id": "sport_boxe", "title": "Boxe 🥊"}
                    ]
                }
            ]
        )
        return

    elif current_step == "ASK_SPORT":
        if not input_text:
            await whatsapp_service.send_text_message(to=phone_number, text="S'il vous plaît, entrez votre sport préféré :")
            return
        sport_map = {
            "sport_football": "Football",
            "sport_basketball": "Basketball",
            "sport_tennis": "Tennis",
            "sport_boxe": "Boxe",
        }
        sport = sport_map.get(input_text.lower(), input_text.capitalize())
        temp_data["sport_prefere"] = sport

        # Complete Registration!
        user_in = UserCreate(
            phone_number=phone_number,
            nom=temp_data.get("nom"),
            prenom=temp_data.get("prenom"),
            age=temp_data.get("age"),
            niveau=temp_data.get("niveau"),
            langue=temp_data.get("langue", "fr"),
            ville=temp_data.get("ville"),
            quartier=temp_data.get("quartier"),
            taille=temp_data.get("taille"),
            categorie=temp_data.get("categorie"),
            sport_prefere=temp_data.get("sport_prefere"),
        )
        
        db_user = await crud.create_user(db, user_in)
        db_user.is_registered = True
        await db.commit()
        
        await crud.delete_registration_state(db, phone_number)
        
        success_message = (
            "🎉 Félicitations ! Votre inscription sur Wasportly est terminée !\n\n"
            "Voici le récapitulatif de votre Carte Joueur 💳 :\n"
            f"👤 *Nom complet* : {db_user.prenom} {db_user.nom}\n"
            f"🎂 *Âge* : {db_user.age} ans\n"
            f"📏 *Taille* : {db_user.taille} cm\n"
            f"📊 *Niveau* : {db_user.niveau}\n"
            f"🏆 *Catégorie* : {db_user.categorie}\n"
            f"⚽ *Sport préféré* : {db_user.sport_prefere}\n"
            f"📍 *Localisation* : {db_user.quartier}, {db_user.ville}\n"
            f"🌐 *Langue* : {db_user.langue.upper()}\n\n"
            "Votre profil est maintenant actif ! Tapez *menu* ou n'importe quel message pour voir le menu des fonctionnalités. 🚀"
        )
        await whatsapp_service.send_text_message(to=phone_number, text=success_message)
        return
