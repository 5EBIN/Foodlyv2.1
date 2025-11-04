from datetime import datetime, timedelta
from jose import jwt
from passlib.context import CryptContext
from app.core.config import settings

pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_ctx.hash(password)

def verify_password(plain, hashed) -> bool:
    return pwd_ctx.verify(plain, hashed)

def create_access_token(subject: str | int, expires_delta: timedelta | None = None) -> str:
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded = jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
    return encoded

def decode_token(token: str):
    payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
    return payload
