import time
import jwt
from fastapi import HTTPException
from pydantic import BaseModel
from sqlmodel import Session, select
from .database import engine
from .models import User
from .auth import hash_password
from .auth import verify_password

import secrets
JWT_SECRET = secrets.token_hex(16)
JWT_ALGORITHM = "HS256"

print(JWT_SECRET)

def sign(email):
    payload = {
        "email": email,
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

    return token

def decode(token):
    try:
        decoded_token = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return decoded_token
        
    except:
        raise HTTPException(status_code=401, detail="Invalid token")

class SignUpSchema(BaseModel):
    name: str
    email: str
    password: str

class SignInSchema(BaseModel):
    email: str
    password: str

userlist = []

def signup(name, email, password):
    print("RAW PASSWORD:", password, "LEN:", len(password))
    with Session(engine) as session:
        existing = session.exec(select(User).where(User.email == email)).first()
        if existing:
            raise HTTPException(status_code=400, detail="Email already registered")

        hashed = hash_password(password)

        user = User(
            name=name,
            email=email,
            hashed_password=hashed
        )

        session.add(user)
        session.commit()
        session.refresh(user)

        return sign(user.email)

from .auth import verify_password

def signin(email, password):
    with Session(engine) as session:
        user = session.exec(select(User).where(User.email == email)).first()

        if not user:
            raise HTTPException(status_code=400, detail="Email not registered")

        if not verify_password(password, user.hashed_password):
            raise HTTPException(status_code=400, detail="Incorrect password")

        return sign(user.email)
