# ==== backend/routers/auth.py ====
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from datetime import datetime, timedelta, timezone
from pydantic import BaseModel, EmailStr
from typing import Optional
import os

from ..database.db_connect import get_db
from ..models.user import User
from ..schemas.auth import Token, TokenData, UserCreate, UserResponse, UserPayload, UserRole
from ..utils.auth_utils import verify_password, get_password_hash
from ..utils.logger import setup_logging

router = APIRouter()
logger = setup_logging()

# --- JWT Configuration ---
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your_super_secret_jwt_key")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 # 24 hours

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """
    Creates a JWT access token.
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user_from_token(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """
    Dependency to get the current user from the JWT token.
    Raises HTTPException if token is invalid or user not found.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        user_role: str = payload.get("role")
        if email is None or user_role is None:
            raise credentials_exception
        token_data = TokenData(email=email, role=user_role)
    except JWTError as e:
        logger.warning(f"JWT decode failed: {str(e)}")
        raise credentials_exception
    
    try:
        user = db.query(User).filter(User.email == token_data.email).first()
    except Exception as db_err:
        logger.error(f"DB error while fetching user for token: {db_err}")
        raise credentials_exception
    if user is None:
        raise credentials_exception
    return UserPayload(email=user.email, role=UserRole(user.role)) # Return UserPayload for consistency

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED,
             summary="Register a new user",
             response_description="The newly registered user's details (excluding password hash).")
async def register_user(
    user_create: UserCreate,
    db: Session = Depends(get_db)
):
    """
    Registers a new user with a specified role.
    By default, new registrations are 'EndUser'.
    Admin roles should be created via seed data or a separate admin endpoint.
    """
    logger.info(f"Attempting to register new user: {user_create.email}")
    db_user = db.query(User).filter(User.email == user_create.email).first()
    if db_user:
        logger.warning(f"Registration failed: User with email {user_create.email} already exists.")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

    # Default new users to EndUser role
    hashed_password = get_password_hash(user_create.password)
    user_role = UserRole.ENDUSER.value # Ensure it's the string value
    
    new_user = User(email=user_create.email, hashed_password=hashed_password, role=user_role)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    logger.info(f"User {new_user.email} registered successfully with role {new_user.role}.")
    return new_user

@router.post("/login", response_model=Token,
             summary="Login and get an access token",
             response_description="JWT access token and token type.")
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    Authenticates a user and returns a JWT access token upon successful login.
    """
    logger.info(f"Login attempt for user: {form_data.username}")
    try:
        user = db.query(User).filter(User.email == form_data.username).first()
    except Exception as db_err:
        logger.error(f"DB error during login for {form_data.username}: {db_err}")
        raise HTTPException(status_code=500, detail="Authentication temporarily unavailable")
    if not user or not verify_password(form_data.password, user.hashed_password):
        logger.warning(f"Login failed for {form_data.username}: Invalid credentials.")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email, "role": user.role},
        expires_delta=access_token_expires,
    )
    return {"access_token": access_token, "token_type": "bearer"}