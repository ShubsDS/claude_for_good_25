# auth.py

import hashlib
from passlib.context import CryptContext
import jwt
from datetime import datetime, timedelta

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

SECRET_KEY = "SUPER_SECRET_KEY"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60


def hash_password(password: str) -> str:
    # Convert to bytes
    print("--- inside hash_password() ---")
    print("password =", password)
    print("bytes =", len(password.encode('utf-8')))
    pwd_bytes = password.encode("utf-8")

    # If password >72 bytes, hash with SHA256 first
    if len(pwd_bytes) > 72:
        password = hashlib.sha256(pwd_bytes).hexdigest()

    return pwd_context.hash(password)


def verify_password(password: str, hashed: str) -> bool:
    # Same logic on verification
    pwd_bytes = password.encode("utf-8")

    if len(pwd_bytes) > 72:
        password = hashlib.sha256(pwd_bytes).hexdigest()

    return pwd_context.verify(password, hashed)

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode["exp"] = expire
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
