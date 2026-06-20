import asyncio
import sys
import os
from datetime import datetime, timedelta

# Add root folder to python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from httpx import AsyncClient, ASGITransport
from app.main import app
from app.database import engine, Base
from app.schemas import UserCreate, VenueCreate
import app.crud as crud

def generate_button_webhook_payload(sender: str, button_id: str, title: str) -> dict:
    """
    Simulates a Meta WhatsApp Webhook payload for interactive button responses.
    """
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
                            "contacts": [
                                {
                                    "profile": {"name": "Test User"},
                                    "wa_id": sender
                                }
                            ],
                            "messages": [
                                {
                                    "from": sender,
                                    "id": "wamid.mock_btn_reply_id_098",
                                    "timestamp": "1665099300",
                                    "type": "interactive",
                                    "interactive": {
                                        "type": "button_reply",
                                        "button_reply": {
                                            "id": button_id,
                                            "title": title
                                        }
                                    }
                                }
                            ]
                        }
                    }
                ]
            }
        ]
    }

async def run_matching_test():
    # 1. Reset database tables
    print("🧹 Cleaning database tables...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    print("✅ Database reset.")

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://localhost:8000") as ac:
        
        # 2. Seed mock players
        print("\n🌱 Seeding mock players...")
        
        # Player 1 (Creator) - Basketball in Koumassi
        p1 = UserCreate(
            phone_number="2250707070707",
            nom="Tiemtore",
            prenom="Fahim",
            age=25,
            niveau="Intermédiaire",
            langue="fr",
            ville="Abidjan",
            quartier="Koumassi",
            taille=182,
            categorie="Senior",
            sport_prefere="Basketball"
        )
        
        # Player 2 (Matching Target) - Basketball in Koumassi
        p2 = UserCreate(
            phone_number="2250101010101",
            nom="Coulibaly",
            prenom="Adama",
            age=22,
            niveau="Intermédiaire",
            langue="fr",
            ville="Abidjan",
            quartier="Koumassi",
            taille=190,
            categorie="Loisir",
            sport_prefere="Basketball"
        )
        
        # Player 3 (Cocody - wrong neighborhood)
        p3 = UserCreate(
            phone_number="2250202020202",
            nom="Soro",
            prenom="Michel",
            age=28,
            niveau="Intermédiaire",
            langue="fr",
            ville="Abidjan",
            quartier="Cocody",
            taille=185,
            categorie="Senior",
            sport_prefere="Basketball"
        )
        
        # Player 4 (Koumassi - wrong sport)
        p4 = UserCreate(
            phone_number="2250303030303",
            nom="Keita",
            prenom="Kader",
            age=24,
            niveau="Intermédiaire",
            langue="fr",
            ville="Abidjan",
            quartier="Koumassi",
            taille=175,
            categorie="Compétition",
            sport_prefere="Football"
        )
        
        # We need a session, let's create users directly via CRUD
        from app.database import async_session_local
        async with async_session_local() as db:
            u1 = await crud.create_user(db, p1)
            u1.is_registered = True
            u2 = await crud.create_user(db, p2)
            u2.is_registered = True
            u3 = await crud.create_user(db, p3)
            u3.is_registered = True
            u4 = await crud.create_user(db, p4)
            u4.is_registered = True
            
            # Seed Venue
            venue_in = VenueCreate(
                name="Agora de Koumassi",
                address="Boulevard du 7 Décembre",
                city="Abidjan",
                neighborhood="Koumassi"
            )
            v1 = await crud.create_venue(db, venue_in)
            await db.commit()
            
            creator_id = u1.id
            venue_id = v1.id
            matching_player_id = u2.id
            matching_player_phone = u2.phone_number
            print(f"✅ Seeding finished. Creator ID: {creator_id}, Venue ID: {venue_id}")

        # 3. Create Match
        print("\n🏀 Creating Basketball Match via POST /matches...")
        match_time = (datetime.now() + timedelta(days=2)).isoformat()
        
        match_payload = {
            "sport": "Basketball",
            "match_time": match_time,
            "venue_id": str(venue_id),
            "max_players": 5,
            "creator_id": str(creator_id)
        }
        
        response = await ac.post("/matches", json=match_payload)
        assert response.status_code == 201, f"Failed to create match: {response.text}"
        match_data = response.json()
        match_id = match_data["id"]
        print(f"✅ Match created. Match ID: {match_id}")

        # 4. Check Match Participants list
        print("\n🔍 Checking initial participants status...")
        part_resp = await ac.get(f"/matches/{match_id}/participants")
        assert part_resp.status_code == 200
        participants = part_resp.json()
        
        print(f"Found {len(participants)} participants:")
        for p in participants:
            print(f"  🔹 User: {p['user_id']} | Status: {p['status']}")
            
        # Creator should be "confirmed", player 2 should be "invited"
        # Others (player 3, player 4) should NOT be here
        p_ids = [p["user_id"] for p in participants]
        assert str(creator_id) in p_ids
        assert str(matching_player_id) in p_ids
        assert len(participants) == 2, "Only creator and the single matching player should be registered"

        # 5. Simulate Matching Player accepting the invitation
        print(f"\n📲 Simulating player Adama (+{matching_player_phone}) clicking 'Rejoindre'...")
        webhook_payload = generate_button_webhook_payload(
            sender=matching_player_phone,
            button_id=f"match_join:{match_id}",
            title="Rejoindre"
        )
        
        web_resp = await ac.post("/webhook", json=webhook_payload)
        assert web_resp.status_code == 200
        print(f"Webhook response: {web_resp.json()}")

        # 6. Verify status updated to 'confirmed'
        print("\n🔍 Checking updated participants status...")
        part_resp2 = await ac.get(f"/matches/{match_id}/participants")
        participants2 = part_resp2.json()
        for p in participants2:
            print(f"  🔹 User: {p['user_id']} | Status: {p['status']}")
            if p["user_id"] == str(matching_player_id):
                assert p["status"] == "confirmed", "Matching player status should be updated to confirmed"

        print("\n🎉 PHASE 2 MATCHMAKING TESTS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    asyncio.run(run_matching_test())
