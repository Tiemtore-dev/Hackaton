import asyncio
import sys
import os
from datetime import datetime

# Ajouter le répertoire racine au PATH Python
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from httpx import AsyncClient, ASGITransport
from app.main import app
from app.database import engine, Base, async_session_local
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
                            "contacts": [{"profile": {"name": "Test User"}, "wa_id": sender}],
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

async def run_onboarding_signup_test():
    print("🧹 Nettoyage de la base de données...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    print("✅ Base de données nettoyée.")

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://localhost:8000") as ac:
        sender = "212782913924"
        
        # 1. Start onboarding
        print("\n💬 1. User sends 'Hello'...")
        resp = await ac.post("/webhook", json=generate_text_payload(sender, "Hello"))
        assert resp.status_code == 200
        
        # 2. Prenom
        print("💬 2. User sends Prenom 'Fahim'...")
        resp = await ac.post("/webhook", json=generate_text_payload(sender, "Fahim"))
        assert resp.status_code == 200

        # 3. Nom
        print("💬 3. User sends Nom 'Tiemtore'...")
        resp = await ac.post("/webhook", json=generate_text_payload(sender, "Tiemtore"))
        assert resp.status_code == 200

        # 4. Age
        print("💬 4. User sends Age '25'...")
        resp = await ac.post("/webhook", json=generate_text_payload(sender, "25"))
        assert resp.status_code == 200

        # 5. Niveau
        print("💬 5. User sends Niveau 'Avancé'...")
        resp = await ac.post("/webhook", json=generate_text_payload(sender, "Avancé"))
        assert resp.status_code == 200

        # 6. Langue
        print("💬 6. User sends Langue 'Darija'...")
        resp = await ac.post("/webhook", json=generate_text_payload(sender, "darija"))
        assert resp.status_code == 200

        # 7. Ville
        print("💬 7. User sends Ville 'Abidjan'...")
        resp = await ac.post("/webhook", json=generate_text_payload(sender, "Abidjan"))
        assert resp.status_code == 200

        # 8. Quartier
        print("💬 8. User sends Quartier 'Cocody'...")
        resp = await ac.post("/webhook", json=generate_text_payload(sender, "Cocody"))
        assert resp.status_code == 200

        # 9. Taille
        print("💬 9. User sends Taille '180'...")
        resp = await ac.post("/webhook", json=generate_text_payload(sender, "180"))
        assert resp.status_code == 200

        # 10. Categorie
        print("💬 10. User sends Categorie 'Loisir'...")
        resp = await ac.post("/webhook", json=generate_text_payload(sender, "Loisir"))
        assert resp.status_code == 200

        # 11. Sport
        print("💬 11. User sends Sport 'Football'...")
        resp = await ac.post("/webhook", json=generate_text_payload(sender, "Football"))
        assert resp.status_code == 200

        # 12. Password (Too short validation test)
        print("💬 12. User sends Password '123' (should be too short)...")
        resp = await ac.post("/webhook", json=generate_text_payload(sender, "123"))
        assert resp.status_code == 200

        # 13. Password (Valid password)
        print("💬 13. User sends Password 'mypassword123'...")
        resp = await ac.post("/webhook", json=generate_text_payload(sender, "mypassword123"))
        assert resp.status_code == 200

        # Verify registration in DB
        print("\n🔍 Vérification des données créées en base...")
        async with async_session_local() as db:
            user = await crud.get_user_by_phone_number(db, sender)
            assert user is not None, "L'utilisateur devrait être créé en base de données"
            assert user.prenom == "Fahim"
            assert user.nom == "Tiemtore"
            assert user.age == 25
            assert user.niveau == "Avancé"
            assert user.langue == "Darija"
            assert user.ville == "Abidjan"
            assert user.quartier == "Cocody"
            assert user.taille == 180
            assert user.categorie == "Loisir"
            assert user.sport_prefere == "Football"
            assert user.hashed_password is not None, "Le mot de passe devrait être hashé"
            assert crud.verify_password("mypassword123", user.hashed_password) is True, "Le mot de passe devrait être correct"
            print("🎉 L'utilisateur a été créé avec succès, avec le mot de passe hashé !")

if __name__ == "__main__":
    asyncio.run(run_onboarding_signup_test())
