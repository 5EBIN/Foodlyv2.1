from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas import UserCreate, Token, UserOut
from app.services.auth_service import hash_password, create_access_token, verify_password
from app.models import models
from app.models.database import get_db

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", response_model=UserOut)
async def register(user_in: UserCreate, db: AsyncSession = Depends(get_db)):
    q = await db.execute(
        models.User.__table__.select().where(models.User.email == user_in.email)
    )
    existing = q.first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    user = models.User(email=user_in.email, hashed_password=hash_password(user_in.password), is_agent=user_in.is_agent)
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user

@router.post("/login", response_model=Token)
async def login(user_in: UserCreate, db: AsyncSession = Depends(get_db)):
    q = await db.execute(models.User.__table__.select().where(models.User.email == user_in.email))
    row = q.first()
    if not row:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    user = row[0]
    if not verify_password(user_in.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token(subject=user.id)
    return {"access_token": token, "token_type": "bearer"}
