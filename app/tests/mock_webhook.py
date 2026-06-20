import asyncio
import sys
import os

# Add root folder to python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from fastapi import status
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.database import engine, Base
from sqlalchemy import text

def generate_whatsapp_payload(sender: str, message_body: str = "", button_id: str | None = None) -> dict:
    """
    Helper function to generate Meta WhatsApp Webhook payload format.
    """
    message_type = "text" if not button_id else "interactive"
    
    msg_obj = {
        "from": sender,
        "id": "wamid.mock_id_1234567890",
        "timestamp": "1665099300",
        "type": message_type,
    }
    
    if message_type == "text":
        msg_obj["text"] = {"body": message_body}
    else:
        msg_obj["interactive"] = {
            "type": "button_reply",
            "button_reply": {
                "id": button_id,
                "title": message_body
            }
        }

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
                            "messages": [msg_obj]
                        }
                    }
                ]
            }
        ]
    }

async def run_onboarding_test():
    # 1. Clean and reset database tables before test
    print("🧹 Cleaning and recreating database tables for clean state...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    print("✅ Database tables initialized.")

    sender = "2250707070707"
    
    steps = [
        # (Message input, expected reply debug keyword, button_id payload)
        ("Salut", "prénom", None),
        ("Fahim", "nom", None),
        ("Tiemtore", "âge", None),
        ("25", "niveau", None),
        ("Intermédiaire", "langue", "level_intermediaire"),
        ("Français", "ville", "lang_fr"),
        ("Abidjan", "quartier", None),
        ("Cocody", "taille", None),
        ("182", "catégorie", None),
        ("Senior", "Félicitations", "cat_senior"),
    ]

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        print("\n🚀 Starting Onboarding Simulation for WhatsApp user:", sender)
        
        for idx, (msg, expected_kw, btn_id) in enumerate(steps, 1):
            print(f"\n--- Étape {idx}: Envoi de '{msg}' (payload button: {btn_id}) ---")
            payload = generate_whatsapp_payload(sender, msg, btn_id)
            
            response = await ac.post("/webhook", json=payload)
            assert response.status_code == 200, f"Webhook POST failed with {response.status_code}"
            print(f"Response: {response.json()}")

        print("\n🔍 Checking if user is successfully registered via REST API...")
        get_response = await ac.get(f"/users/{sender}")
        assert get_response.status_code == 200, "REST API user lookup failed"
        
        user_data = get_response.json()
        print("\n🏆 User Registration Verification:")
        for key, val in user_data.items():
            print(f"  🔹 {key}: {val}")
        
        assert user_data["nom"] == "Tiemtore"
        assert user_data["prenom"] == "Fahim"
        assert user_data["age"] == 25
        assert user_data["niveau"] == "Intermédiaire"
        assert user_data["langue"] == "fr"
        assert user_data["ville"] == "Abidjan"
        assert user_data["quartier"] == "Cocody"
        assert user_data["taille"] == 182
        assert user_data["categorie"] == "Senior"
        assert user_data["is_registered"] is True
        print("\n🎉 ALL TESTS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    asyncio.run(run_onboarding_test())
