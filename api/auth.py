from datetime import datetime, timedelta
from passlib.context import CryptContext
import jwt
from config import settings
from sqlalchemy.orm import Session
import models
from pydantic import BaseModel, ValidationError
from typing import Dict, Any

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT Token payload validation
class TokenPayload(BaseModel):
    """Expected JWT payload structure"""
    sub: str  # Must be string per JWT standard
    exp: int
    iat: int
    type: str = "access"

def hash_password(password: str) -> str:
    """Hash a password for storage"""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    """Create a JWT access token with all required claims"""
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.access_token_expire_minutes
        )

    # ✅ Ensure all required claims are set
    to_encode.update({
        "exp": int(expire.timestamp()),
        "iat": int(datetime.utcnow().timestamp()),
        "type": "access"
    })

    encoded_jwt = jwt.encode(
        to_encode,
        settings.secret_key,
        algorithm=settings.jwt_algorithm
    )
    return encoded_jwt

def decode_access_token(token: str) -> dict:
    """Decode and verify a JWT token with claim validation"""
    try:
        # Decode the token
        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=[settings.jwt_algorithm]
        )

        # ✅ Validate required claims exist
        try:
            token_payload = TokenPayload(**payload)
        except ValidationError as e:
            raise ValueError(f"Invalid token claims: {e}")

        # ✅ Validate token type
        if token_payload.type != "access":
            raise ValueError("Invalid token type")

        # Note: PyJWT already validates expiration automatically
        return payload

    except jwt.ExpiredSignatureError:
        raise Exception("Token expired")
    except jwt.InvalidTokenError as e:
        raise Exception(f"Invalid token: {str(e)}")
    except ValueError as e:
        raise Exception(str(e))

def get_user_by_email(db: Session, email: str):
    """Get a user from the database by email"""
    return db.query(models.User).filter(models.User.email == email).first()

def create_user(db: Session, email: str, password: str, full_name: str):
    """Create a new user in the database"""
    hashed_password = hash_password(password)
    db_user = models.User(
        email=email,
        hashed_password=hashed_password,
        full_name=full_name,
        is_admin=False
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user
