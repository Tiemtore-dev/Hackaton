import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas import UserResponse, UserCreate, UserUpdate, UserLogin, UserRegister
import app.crud as crud

router = APIRouter(prefix="/users", tags=["users"])

@router.post("/register", response_model=UserResponse)
async def register_user(user_reg: UserRegister, db: AsyncSession = Depends(get_db)):
    """
    Register a new user on the web platform or complete an existing WhatsApp profile with a password.
    """
    try:
        user = await crud.register_web_user(db, user_reg)
        return user
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Registration failed: {str(e)}"
        )


@router.post("/login", response_model=UserResponse)
async def login_user(credentials: UserLogin, db: AsyncSession = Depends(get_db)):
    """
    Authenticate a user using their phone number and password.
    """
    user = await crud.authenticate_user(db, credentials)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Numéro de téléphone ou mot de passe incorrect."
        )
    return user



@router.get("", response_model=list[UserResponse])
async def list_users(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    """
    Get all registered users.
    """
    users = await crud.get_users(db, skip=skip, limit=limit)
    return users


@router.get("/{phone_number}", response_model=UserResponse)
async def get_user_by_phone(phone_number: str, db: AsyncSession = Depends(get_db)):
    """
    Get user details by WhatsApp phone number.
    """
    user = await crud.get_user_by_phone_number(db, phone_number)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user


@router.put("/{phone_number}", response_model=UserResponse)
async def update_user_profile(
    phone_number: str,
    user_update: UserUpdate,
    db: AsyncSession = Depends(get_db)
):
    """
    Update user profile details by phone number.
    """
    db_user = await crud.get_user_by_phone_number(db, phone_number)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    updated_user = await crud.update_user(db, db_user, user_update)
    return updated_user


@router.delete("/{user_id}")
async def delete_user(user_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    """
    Delete a user by UUID.
    """
    success = await crud.delete_user(db, user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return {"status": "success", "message": "User deleted successfully"}
