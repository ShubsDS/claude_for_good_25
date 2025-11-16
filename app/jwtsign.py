import time
import jwt
import os
from fastapi import HTTPException
from pydantic import BaseModel
from sqlmodel import Session, select
from .database import engine
from .models import User
from .auth import hash_password, verify_password
import secrets

# ----------------------
# JWT CONFIG
# ----------------------
JWT_SECRET = os.getenv("JWT_SECRET", secrets.token_hex(16))
JWT_ALGORITHM = "HS256"

# ----------------------
# SCHEMAS
# ----------------------
class SignUpSchema(BaseModel):
    name: str
    email: str
    password: str

class SignInSchema(BaseModel):
    email: str
    password: str

# ----------------------
# JWT FUNCTIONS
# ----------------------
def sign(email: str):
    payload = {"email": email}
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return token

def decode(token: str):
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except:
        raise HTTPException(status_code=401, detail="Invalid token")

# ----------------------
# SIGNUP (DB VERSION)
# ----------------------
def signup(data: SignUpSchema):
    with Session(engine) as session:

        # check if user exists
        existing = session.exec(
            select(User).where(User.email == data.email)
        ).first()

        if existing:
            raise HTTPException(status_code=400, detail="Email already registered")

        # hash password
        hashed = hash_password(data.password)

        # create user
        user = User(
            name=data.name,
            email=data.email,
            hashed_password=hashed,
        )

        session.add(user)
        session.commit()
        session.refresh(user)

        # return JWT
        return {"token": sign(user.email)}

# ----------------------
# LOGIN
# ----------------------
def signin(data: SignInSchema):
    with Session(engine) as session:
        user = session.exec(
            select(User).where(User.email == data.email)
        ).first()

        if not user:
            raise HTTPException(status_code=400, detail="Invalid email or password")

        if not verify_password(data.password, user.hashed_password):
            raise HTTPException(status_code=400, detail="Invalid email or password")

        return {"token": sign(user.email)}
