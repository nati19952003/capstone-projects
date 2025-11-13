from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import Security, HTTPException, Depends
from passlib.context import CryptContext
from jose import jwt, JWTError
from datetime import datetime, timedelta
from typing import Dict, Any
import os
from bson import ObjectId
from ..database.database import get_db

SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY or SECRET_KEY == "your-secret-key-change-this-in-production":
    raise ValueError(
        "SECRET_KEY must be set in environment variables and changed from default. "
        "Please update your .env file with a secure secret key."
    )

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()


class AuthService:
    def __init__(self, db: Any):
        # db is expected to be a Motor database instance (request.app.mongodb)
        self.db = db

    async def create_user(self, email: str, password: str, role: str = "user") -> Dict:
        """Create a new user with hashed password. Returns the user document."""
        existing = await self.db.users.find_one({"email": email})
        if existing:
            raise HTTPException(status_code=400, detail="User already exists")

        hashed = pwd_context.hash(password)
        user = {
            "email": email,
            "password": hashed,
            "role": role,
            "permissions": {"upload": True, "process": True},
            "created_at": datetime.utcnow()
        }
        result = await self.db.users.insert_one(user)
        user["_id"] = str(result.inserted_id)
        return user

    async def authenticate_user(self, email: str, password: str):
        user = await self.db.users.find_one({"email": email})
        if not user:
            return None
        if not pwd_context.verify(password, user.get("password", "")):
            return None
        # normalize id to string
        user["_id"] = str(user.get("_id"))
        return user

    def create_access_token(self, data: Dict) -> str:
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt

    @staticmethod
    async def get_current_user(credentials: HTTPAuthorizationCredentials = Security(security), db=Depends(get_db)) -> Dict:
        """FastAPI dependency to return the current user document from the token."""
        token = credentials.credentials
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            user_id = payload.get("sub")
            if not user_id:
                raise HTTPException(status_code=401, detail="Invalid token payload")
            # lookup user
            user = await db.users.find_one({"_id": ObjectId(user_id)})
            if not user:
                raise HTTPException(status_code=401, detail="User not found")
            # normalize id
            user["_id"] = str(user["_id"])
            return user
        except JWTError:
            raise HTTPException(status_code=401, detail="Invalid authentication credentials")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)
