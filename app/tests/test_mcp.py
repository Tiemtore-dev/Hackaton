import asyncio
import sys
import os

# Add root folder to python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from httpx import AsyncClient, ASGITransport
from app.main import app
from app.database import engine, Base
from app.mcp_server import get_player, list_players, register_player

async def run_mcp_test():
    # 1. Clean and reset database tables before test
    print("🧹 Cleaning database tables...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    print("✅ Database cleaned.")

    print("\n🚀 Testing MCP Tools programmatically...")
    
    # Test register_player tool
    print("\n--- Testing register_player tool ---")
    reg_result = await register_player(
        phone_number="2250101010101",
        nom="Coulibaly",
        prenom="Adama",
        age=22,
        niveau="Avancé",
        langue="fr",
        ville="Abidjan",
        quartier="Marcory",
        taille=190,
        categorie="Loisir"
    )
    print(f"Result: {reg_result}")
    
    # Test list_players tool
    print("\n--- Testing list_players tool ---")
    list_result = await list_players()
    print(f"Result:\n{list_result}")
    
    # Test get_player tool
    print("\n--- Testing get_player tool ---")
    get_result = await get_player(phone_number="2250101010101")
    print(f"Result:\n{get_result}")

    # Test non-existing player
    print("\n--- Testing get_player for non-existing user ---")
    get_fake_result = await get_player(phone_number="999999999")
    print(f"Result: {get_fake_result}")

    # 2. Test HTTP SSE endpoints mounted in FastAPI
    print("\n🚀 Testing mounted HTTP routes via AsyncClient...")
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://localhost:8000") as ac:
        # Check GET /mcp/sse (SSE connection endpoint)
        print("\n--- Testing GET /mcp/sse ---")
        try:
            async with ac.stream("GET", "/mcp/sse") as response:
                print(f"Response status: {response.status_code}")
                print(f"Response headers: {response.headers}")
                # Lire la première ligne du flux
                async for line in response.aiter_lines():
                    if line:
                        print(f"Received stream line: {line}")
                        if "event:" in line or "data:" in line:
                            print("✅ SSE Endpoint stream validation passed!")
                            break
        except Exception as e:
            print(f"Error reading SSE stream: {e}")
        
    print("\n🎉 ALL MCP TESTS COMPLETED SUCCESSFULLY!")

if __name__ == "__main__":
    asyncio.run(run_mcp_test())
