import asyncio
import sys
import os
from datetime import datetime, timedelta

# Ajouter le répertoire racine au PATH Python
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import engine, Base, async_session_local
from app.schemas import UserCreate, VenueCreate
import app.crud as crud

async def seed_database():
    print("🧹 Nettoyage et réinitialisation de la base de données...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    print("✅ Tables de la base de données recréées.")

    async with async_session_local() as db:
        print("\n🌱 Création des terrains (Venues)...")
        v1_in = VenueCreate(
            name="Agora de Koumassi",
            address="Boulevard du 7 Décembre",
            city="Abidjan",
            neighborhood="Koumassi"
        )
        v2_in = VenueCreate(
            name="City Sport Cocody",
            address="Rue des Jardins",
            city="Abidjan",
            neighborhood="Cocody"
        )
        v3_in = VenueCreate(
            name="Stade de Marcory",
            address="Avenue de la Paix",
            city="Abidjan",
            neighborhood="Marcory"
        )
        
        v1 = await crud.create_venue(db, v1_in)
        v2 = await crud.create_venue(db, v2_in)
        v3 = await crud.create_venue(db, v3_in)
        print(f"✅ Terrains créés : {v1.name}, {v2.name}, {v3.name}")

        print("\n🌱 Création des profils joueurs...")
        # 1. Joueur de Basketball (Koumassi, Avancé)
        u1_in = UserCreate(
            phone_number="2250707070707",
            nom="Tiemtore",
            prenom="Fahim",
            age=25,
            niveau="Avancé",
            langue="fr",
            ville="Abidjan",
            quartier="Koumassi",
            taille=182,
            categorie="Senior",
            sport_prefere="Basketball"
        )
        # 2. Joueur de Basketball (Koumassi, Intermédiaire)
        u2_in = UserCreate(
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
        # 3. Joueur de Football (Cocody, Avancé)
        u3_in = UserCreate(
            phone_number="2250404040404",
            nom="Kone",
            prenom="Marie",
            age=24,
            niveau="Avancé",
            langue="fr",
            ville="Abidjan",
            quartier="Cocody",
            taille=168,
            categorie="Senior",
            sport_prefere="Football"
        )
        # 4. Joueur de Football (Cocody, Intermédiaire)
        u4_in = UserCreate(
            phone_number="2250909090909",
            nom="Kouadio",
            prenom="Luc",
            age=26,
            niveau="Intermédiaire",
            langue="fr",
            ville="Abidjan",
            quartier="Cocody",
            taille=175,
            categorie="Loisir",
            sport_prefere="Football"
        )
        # 5. Joueur de Football (Cocody, Avancé)
        u5_in = UserCreate(
            phone_number="2250808080808",
            nom="Yao",
            prenom="Pierre",
            age=27,
            niveau="Avancé",
            langue="fr",
            ville="Abidjan",
            quartier="Cocody",
            taille=178,
            categorie="Senior",
            sport_prefere="Football"
        )
        # 6. Joueuse de Tennis (Marcory, Débutant)
        u6_in = UserCreate(
            phone_number="2250505050505",
            nom="Diallo",
            prenom="Sarah",
            age=23,
            niveau="Débutant",
            langue="fr",
            ville="Abidjan",
            quartier="Marcory",
            taille=170,
            categorie="Loisir",
            sport_prefere="Tennis"
        )
        # 7. Joueur de Tennis (Marcory, Intermédiaire)
        u7_in = UserCreate(
            phone_number="2250606060606",
            nom="Yapi",
            prenom="Jean",
            age=29,
            niveau="Intermédiaire",
            langue="fr",
            ville="Abidjan",
            quartier="Marcory",
            taille=180,
            categorie="Senior",
            sport_prefere="Tennis"
        )

        users = [u1_in, u2_in, u3_in, u4_in, u5_in, u6_in, u7_in]
        db_users = []
        for u in users:
            u.password = "sportmeet123"
            db_u = await crud.create_user(db, u)
            db_u.is_registered = True
            db_users.append(db_u)
            
        await db.commit()
        print(f"✅ {len(db_users)} joueurs créés et marqués comme inscrits.")

        print("\n🌱 Création des rencontres sportives (Matches)...")
        # Match 1: Basketball à l'Agora de Koumassi (Créé par Fahim u1)
        m1_time = datetime.now() + timedelta(days=2, hours=4)
        m1 = await db.merge(crud.Match(
            creator_id=db_users[0].id,
            sport="Basketball",
            match_time=m1_time,
            venue_id=v1.id,
            max_players=4,
            status="pending"
        ))
        
        # Match 2: Football au City Sport Cocody (Créé par Marie u3)
        m2_time = datetime.now() + timedelta(days=1, hours=2)
        m2 = await db.merge(crud.Match(
            creator_id=db_users[2].id,
            sport="Football",
            match_time=m2_time,
            venue_id=v2.id,
            max_players=10,
            status="pending"
        ))
        
        db.add(m1)
        db.add(m2)
        await db.commit()
        await db.refresh(m1)
        await db.refresh(m2)
        print(f"✅ Matchs créés : {m1.sport} (Koumassi) et {m2.sport} (Cocody)")

        print("\n🌱 Enregistrement des participants...")
        # Match 1: Fahim (créateur, confirmed) et Adama (confirmed)
        await crud.add_match_participant(db, m1.id, db_users[0].id, "confirmed")
        await crud.add_match_participant(db, m1.id, db_users[1].id, "confirmed")

        # Match 2: Marie (créateur, confirmed), Luc (confirmed), Pierre (invited)
        await crud.add_match_participant(db, m2.id, db_users[2].id, "confirmed")
        await crud.add_match_participant(db, m2.id, db_users[3].id, "confirmed")
        await crud.add_match_participant(db, m2.id, db_users[4].id, "invited")
        
        await db.commit()
        print("✅ Participations enregistrées avec succès.")

    print("\n🎉 BASE DE DONNÉES ALIMENTÉE AVEC SUCCÈS !")

if __name__ == "__main__":
    asyncio.run(seed_database())
