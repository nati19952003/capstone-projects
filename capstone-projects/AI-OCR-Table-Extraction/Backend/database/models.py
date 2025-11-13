from datetime import datetime
from typing import Dict, Optional, Any, List
from pydantic import BaseModel, Field


class User(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    email: str
    password: str
    role: str = "user"
    permissions: Dict = {}
    created_at: Optional[datetime] = None


class DocumentCreate(BaseModel):
    filename: str
    user_id: Optional[str] = None


class Document(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    filename: str
    status: str = "uploaded"
    user_id: Optional[str] = None
    results: Optional[List[Any]] = None
    created_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error: Optional[str] = None