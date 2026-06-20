import asyncio
import sys
import os
from datetime import datetime

# Ajouter le répertoire racine au PATH Python
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from httpx import AsyncClient, ASGITransport
from app.main import app
from app.database import engine, Base, async_session_local
from app.schemas import UserCreate
import app.crud as crud

def generate_text_payload(sender: str, text: str) -> dict:
    return {
        "object": "whatsapp_business_account",
        "entry": [
            {
                "id": "mock_waba_id_000",
                "changes": [
                    {
                        "field": "messages",
                        "value": {
                            "messaging_product": "whatsapp",
                            "metadata": {
                                "display_phone_number": "15555555555",
                                "phone_number_id": "mock_phone_id"
                            },
                            "contacts": [{"profile": {"name": "Test"}, "wa_id": sender}],
                            "messages": [
                                {
                                    "from": sender,
                                    "id": f"wamid.mock_txt_{datetime.now().timestamp()}",
                                    "timestamp": "1665099300",
                                    "type": "text",
                                    "text": {"body": text}
                                }
                            ]
                        }
                    }
                ]
            }
        ]
    }

def generate_location_payload(sender: str, latitude: float, longitude: float, name: str, address: str) -> dict:
    return {
        "object": "whatsapp_business_account",
        "entry": [
            {
                "id": "mock_waba_id_000",
                "changes": [
                    {
                        "field": "messages",
                        "value": {
                            "messaging_product": "whatsapp",
                            "metadata": {
                                "display_phone_number": "15555555555",
                                "phone_number_id": "mock_phone_id"
                            },
                            "contacts": [{"profile": {"name": "Test"}, "wa_id": sender}],
                            "messages": [
                                {
                                    "from": sender,
                                    "id": f"wamid.mock_loc_{datetime.now().timestamp()}",
                                    "timestamp": "1665099300",
                                    "type": "location",
                                    "location": {
                                        "latitude": latitude,
                                        "longitude": longitude,
                                        "name": name,
                                        "address": address
                                    }
                                }
                            ]
                        }
                    }
                ]
            }
        ]
    }

async def run_whatsapp_creation_test():
    print("🧹 Nettoyage de la base de données...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    print("✅ Base de données nettoyée.")

    # 1. Seed two players in Marcory playing Tennis
    print("\n🌱 Enregistrement initial des joueurs...")
    p1 = UserCreate(
        phone_number="2250707070707",
        nom="Tiemtore",
        prenom="Fahim",
        age=25,
        niveau="Avancé",
        langue="fr",
        ville="Abidjan",
        quartier="Marcory",
        taille=182,
        categorie="Senior",
        sport_prefere="Tennis"
    )
    p2 = UserCreate(
        phone_number="2250101010101",
        nom="Yapi",
        prenom="Jean",
        age=29,
        niveau="Avancé",
        langue="fr",
        ville="Abidjan",
        quartier="Marcory",
        taille=180,
        categorie="Senior",
        sport_prefere="Tennis"
    )

    async with async_session_local() as db:
        u1 = await crud.create_user(db, p1)
        u1.is_registered = True
        u2 = await crud.create_user(db, p2)
        u2.is_registered = True
        await db.commit()
        print("✅ Joueurs enregistrés (Fahim et Jean).")

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://localhost:8000") as ac:
        sender = "2250707070707"
        
        # Étape 1 : L'utilisateur envoie "1" pour lancer l'organisation
        print("\n💬 Fahim envoie '1' (Organiser un match)...")
        resp = await ac.post("/webhook", json=generate_text_payload(sender, "1"))
        assert resp.status_code == 200

        # Étape 2 : L'utilisateur envoie le sport "Tennis"
        print("💬 Fahim envoie 'Tennis'...")
        resp = await ac.post("/webhook", json=generate_text_payload(sender, "Tennis"))
        assert resp.status_code == 200

        # Étape 3 : L'utilisateur envoie la date "24/06 à 18h"
        print("💬 Fahim envoie la date '24/06 à 18h'...")
        resp = await ac.post("/webhook", json=generate_text_payload(sender, "24/06 à 18h"))
        assert resp.status_code == 200

        # Étape 4 : L'utilisateur partage sa position GPS (Stade de Marcory)
        print("💬 Fahim partage sa position GPS (Stade de Marcory)...")
        resp = await ac.post("/webhook", json=generate_location_payload(
            sender=sender,
            latitude=5.3056,
            longitude=-3.9876,
            name="Stade de Marcory",
            address="Avenue de la Paix, Marcory, Abidjan"
        ))
        assert resp.status_code == 200

        # Étape 5 : L'utilisateur envoie la capacité maximale "4"
        print("💬 Fahim envoie '4' (max joueurs)...")
        resp = await ac.post("/webhook", json=generate_text_payload(sender, "4"))
        assert resp.status_code == 200

        # Étape 6 : L'utilisateur confirme la création du match
        print("💬 Fahim confirme la création du match...")
        resp = await ac.post("/webhook", json=generate_text_payload(sender, "oui"))
        assert resp.status_code == 200
        print(f"Réponse webhook: {resp.json()}")

        # 2. Vérifications en base de données
        print("\n🔍 Vérification des données créées en base...")
        async with async_session_local() as db:
            # Vérifier que le terrain GPS a été créé
            venues = await crud.get_venues(db)
            assert len(venues) == 1, "Un terrain GPS aurait dû être créé"
            venue = venues[0]
            print(f"  🏟️ Terrain créé : {venue.name} ({venue.neighborhood}) | GPS: {venue.latitude}, {venue.longitude}")
            assert venue.name == "Stade de Marcory"
            assert venue.neighborhood == "Marcory"
            assert venue.latitude == 5.3056

            # Vérifier que le match a été créé
            matches = await crud.get_matches(db)
            assert len(matches) == 1, "Un match de Tennis aurait dû être créé"
            match = matches[0]
            print(f"  ⚽ Match créé : ID {match.id} | Sport: {match.sport} | Max: {match.max_players}")
            assert match.sport == "Tennis"
            assert match.max_players == 4

            # Vérifier les invitations
            participants = await db.execute(
                crud.select(crud.MatchParticipant).where(crud.MatchParticipant.match_id == match.id)
            )
            participants = list(participants.scalars().all())
            print(f"  👥 Participants ({len(participants)}) :")
            for p in participants:
                print(f"    🔹 User: {p.user_id} | Statut: {p.status}")
            
            # Devrait y avoir le créateur (confirmed) et le joueur Jean (invited)
            assert len(participants) == 2, "Seuls le créateur et le joueur compatible Marcory-Tennis doivent être inscrits/invités"

    print("\n🎉 TESTS DE CRÉATION DE MATCH ET GÉOLOCALISATION WHATSAPP PASSÉS AVEC SUCCÈS !")

if __name__ == "__main__":
    asyncio.run(run_whatsapp_creation_test())
