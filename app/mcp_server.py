from mcp.server.fastmcp import FastMCP
from app.database import async_session_local
import app.crud as crud
from app.schemas import UserCreate

mcp = FastMCP("SportMeet MCP Server")

@mcp.tool()
async def get_player(phone_number: str) -> str:
    """
    Récupère le profil et la carte joueur d'un utilisateur à partir de son numéro de téléphone WhatsApp (ex. 2250707070707).
    """
    async with async_session_local() as db:
        user = await crud.get_user_by_phone_number(db, phone_number)
        if not user:
            return f"Aucun joueur trouvé avec le numéro {phone_number}."
        
        status_text = "Inscrit" if user.is_registered else "Inscription en cours"
        return (
            f"👤 Carte Joueur SportMeet :\n"
            f"- Nom complet : {user.prenom} {user.nom}\n"
            f"- Téléphone : {user.phone_number}\n"
            f"- Âge : {user.age} ans\n"
            f"- Taille : {user.taille} cm\n"
            f"- Niveau : {user.niveau}\n"
            f"- Catégorie : {user.categorie}\n"
            f"- Ville/Quartier : {user.quartier}, {user.ville}\n"
            f"- Langue : {user.langue.upper()}\n"
            f"- Statut : {status_text}"
        )

@mcp.tool()
async def list_players() -> str:
    """
    Retourne la liste complète de tous les joueurs de sport inscrits sur la plateforme SportMeet.
    """
    async with async_session_local() as db:
        users = await crud.get_users(db, skip=0, limit=100)
        if not users:
            return "Aucun joueur n'est inscrit pour le moment."
        
        lines = []
        for u in users:
            status_symbol = "🟢" if u.is_registered else "🟡"
            lines.append(f"{status_symbol} {u.prenom} {u.nom} ({u.phone_number}) - {u.niveau} | {u.quartier}, {u.ville}")
        
        return "Liste des joueurs SportMeet :\n" + "\n".join(lines)

@mcp.tool()
async def register_player(
    phone_number: str,
    nom: str,
    prenom: str,
    age: int,
    niveau: str,
    langue: str,
    ville: str,
    quartier: str,
    taille: int,
    categorie: str
) -> str:
    """
    Inscrit directement un nouveau joueur de sport sur SportMeet en remplissant toutes ses coordonnées.
    """
    async with async_session_local() as db:
        existing = await crud.get_user_by_phone_number(db, phone_number)
        if existing:
            return f"Erreur : Le numéro {phone_number} est déjà associé à un joueur ({existing.prenom} {existing.nom})."
        
        user_in = UserCreate(
            phone_number=phone_number,
            nom=nom,
            prenom=prenom,
            age=age,
            niveau=niveau,
            langue=langue or "fr",
            ville=ville,
            quartier=quartier,
            taille=taille,
            categorie=categorie
        )
        
        db_user = await crud.create_user(db, user_in)
        db_user.is_registered = True
        await db.commit()
        await db.refresh(db_user)
        
        return (
            f"🎉 Le joueur {db_user.prenom} {db_user.nom} a été inscrit avec succès !\n"
            f"Sa Carte Joueur unique est maintenant active sur SportMeet."
        )
