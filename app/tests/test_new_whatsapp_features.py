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

async def run_new_whatsapp_features_test():
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
        quartier="Zone\xa04",
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
        
        # Test A: Test the parse-location API endpoint directly
        print("\n🧪 Test de l'endpoint API parse-location...")
        parse_resp = await ac.post("/venues/parse-location", json={"url_or_coords": "5.3056, -3.9876"})
        assert parse_resp.status_code == 200
        parsed_data = parse_resp.json()
        print(f"  Resultat parse-location: {parsed_data}")
        assert parsed_data["city"] == "Abidjan"
        assert parsed_data["neighborhood"] in ["Marcory", "Zone 4", "Zone\xa04"]

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

        # Étape 4 : L'utilisateur envoie un lien Google Maps (simulé par coordonnées textuelles pour éviter les requêtes réseau lentes)
        # Mais notre parseur gère les coordonnées sous forme de texte brut 5.3056, -3.9876
        print("💬 Fahim envoie des coordonnées GPS brutes (5.3056, -3.9876)...")
        resp = await ac.post("/webhook", json=generate_text_payload(sender, "5.3056, -3.9876"))
        assert resp.status_code == 200

        # Étape 5 : L'utilisateur envoie la capacité maximale "4"
        print("💬 Fahim envoie '4' (max joueurs)...")
        resp = await ac.post("/webhook", json=generate_text_payload(sender, "4"))
        assert resp.status_code == 200

        # Étape 6 : L'utilisateur choisit 'Payant'
        print("💬 Fahim choisit 'Payant'...")
        resp = await ac.post("/webhook", json=generate_text_payload(sender, "payant"))
        assert resp.status_code == 200

        # Étape 7 : L'utilisateur envoie le tarif '2500'
        print("💬 Fahim envoie le tarif '2500'...")
        resp = await ac.post("/webhook", json=generate_text_payload(sender, "2500 FCFA"))
        assert resp.status_code == 200

        # Étape 8 : L'utilisateur confirme la création du match
        print("💬 Fahim confirme la création du match...")
        resp = await ac.post("/webhook", json=generate_text_payload(sender, "oui"))
        assert resp.status_code == 200
        print(f"Réponse webhook: {resp.json()}")

        # 2. Vérifications en base de données
        print("\n🔍 Vérification des données créées en base...")
        async with async_session_local() as db:
            # Vérifier que le terrain a été créé via parseur
            venues = await crud.get_venues(db)
            assert len(venues) == 1, "Un terrain GPS aurait dû être créé"
            venue = venues[0]
            print(f"  🏟️ Terrain créé : {venue.name} ({venue.neighborhood}, {venue.city})")
            assert venue.city == "Abidjan"
            assert venue.neighborhood in ["Marcory", "Zone 4", "Zone\xa04"]

            # Vérifier le match payant
            matches = await crud.get_matches(db)
            assert len(matches) == 1, "Un match de Tennis aurait dû être créé"
            match = matches[0]
            print(f"  ⚽ Match créé : ID {match.id} | Sport: {match.sport} | Max: {match.max_players}")
            print(f"  💸 Tarification : payant={match.is_paid} | prix={match.price} FCFA")
            assert match.sport == "Tennis"
            assert match.max_players == 4
            assert match.is_paid == True
            assert match.price == 2500.0

            # Vérifier les invitations
            participants = await db.execute(
                crud.select(crud.MatchParticipant).where(crud.MatchParticipant.match_id == match.id)
            )
            participants = list(participants.scalars().all())
            print(f"  👥 Participants ({len(participants)}) :")
            for p in participants:
                print(f"    User: {p.user_id} | Statut: {p.status}")
            assert len(participants) == 2

    print("\n🎉 TOUS LES TESTS DE GEOLOCALISATION ET DE TARIFICATION ONT RÉUSSI !")

if __name__ == "__main__":
    asyncio.run(run_new_whatsapp_features_test())
