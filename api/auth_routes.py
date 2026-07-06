from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from database import get_db
import schemas
import auth
import models
from datetime import timedelta
from typing import Optional

router = APIRouter()

@router.post("/register", response_model=schemas.UserResponse)
async def register(
    user_data: schemas.UserCreate,
    db: Session = Depends(get_db)
):
    """Register a new user"""
    # Check if email already exists
    existing_user = auth.get_user_by_email(db, user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )

    # Create new user
    user = auth.create_user(
        db,
        email=user_data.email,
        password=user_data.password,
        full_name=user_data.full_name
    )

    # Create an empty cart for the user
    cart = models.Cart(user_id=user.id)
    db.add(cart)
    db.commit()

    return user

@router.post("/login", response_model=schemas.TokenResponse)
async def login(
    login_data: schemas.LoginRequest,
    db: Session = Depends(get_db)
):
    """Login and get JWT token"""
    # Find user by email
    user = auth.get_user_by_email(db, login_data.email)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    # Verify password
    if not auth.verify_password(login_data.password, user.hashed_password):
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    # Create access token
    access_token = auth.create_access_token(
        data={"sub": str(user.id), "email": user.email}
    )

    return schemas.TokenResponse(access_token=access_token)

def get_current_user_dependency(
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
) -> models.User:
    """Dependency to get the current authenticated user from JWT token"""
    if not authorization:
        raise HTTPException(
            status_code=401,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"}
        )

    # Extract token from "Bearer <token>"
    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication scheme",
            headers={"WWW-Authenticate": "Bearer"}
        )

    token = parts[1]

    try:
        payload = auth.decode_access_token(token)
        user_id = int(payload.get("sub"))
    except Exception as e:
        raise HTTPException(
            status_code=401,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"}
        )

    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=401,
            detail="User not found"
        )

    return user

@router.get("/me", response_model=schemas.UserResponse)
async def get_current_user(
    current_user: models.User = Depends(get_current_user_dependency)
):
    """Get current authenticated user"""
    return current_user
