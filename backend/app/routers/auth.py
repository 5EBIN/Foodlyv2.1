"""
Fixed Auth Router
File: backend/app/routers/auth.py
Key fixes:
1. Removed async keywords (for SQLite sync sessions)
2. Proper error handling
3. Clean imports
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.schemas import UserCreate, UserLogin, Token, UserOut
from app.services.auth_service import hash_password, create_access_token, verify_password
from app.models import models
from app.models.database import get_db
from jose import jwt, JWTError
from app.core.config import settings

router = APIRouter(prefix="/auth", tags=["auth"])

# OAuth2 scheme for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user (customer or agent).

    REMOVED async - SQLite uses synchronous sessions
    """
    # Check if username already exists
    existing = db.query(models.User).filter(models.User.username == user_in.username).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken"
        )

    # Create new user
    user = models.User(
        username=user_in.username,
        email=user_in.email if hasattr(user_in, 'email') else None,
        hashed_password=hash_password(user_in.password),
        is_agent=user_in.is_agent
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    # If registering as agent, create agent record
    if user.is_agent:
        agent = models.Agent(
            user_id=user.id,
            active=True,
            current_work_seconds=0.0,
            active_seconds=0.0
        )
        db.add(agent)
        db.commit()

    return user

@router.post("/login", response_model=Token)
def login(user_in: UserLogin, db: Session = Depends(get_db)):
    """
    Login user and return JWT token.

    REMOVED async - SQLite uses synchronous sessions
    """
    # Find user by username
    user = db.query(models.User).filter(models.User.username == user_in.username).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )

    # Verify password
    if not verify_password(user_in.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )

    # Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive"
        )

    # Create access token
    token = create_access_token(subject=user.id)

    return {
        "access_token": token,
        "token_type": "bearer",
        "user_type": "agent" if user.is_agent else "customer"
    }

def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> models.User:
    """
    Dependency to get current authenticated user.
    Use in protected routes: current_user: User = Depends(get_current_user)
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = db.query(models.User).filter(models.User.id == int(user_id)).first()
    if user is None:
        raise credentials_exception
    
    return user

@router.get("/me", response_model=UserOut)
def get_current_user_info(
    current_user: models.User = Depends(get_current_user)
):
    """
    Get current user information.
    Requires authentication.
    """
    return current_user
