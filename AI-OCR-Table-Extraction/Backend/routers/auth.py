from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from typing import Dict

from ..database.database import get_db
from ..utils.auth import AuthService
from ..utils.audit_logger import AuditLogger

router = APIRouter(prefix="/auth", tags=["Authentication"])


class RegisterRequest(BaseModel):
    email: str
    password: str


@router.post("/register")
async def register(
    payload: RegisterRequest,
    db = Depends(get_db)
):
    auth_service = AuthService(db)
    audit_logger = AuditLogger(db)

    try:
        user = await auth_service.create_user(payload.email, payload.password)
        await audit_logger.log_action(
            user_id=str(user.get("_id")),
            action="register",
            resource_type="user",
            resource_id=str(user.get("_id"))
        )
        return {"message": "User created successfully"}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post("/token")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db = Depends(get_db)
):
    auth_service = AuthService(db)
    audit_logger = AuditLogger(db)
    
    user = await auth_service.authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = auth_service.create_access_token(data={"sub": str(user.id)})
    
    await audit_logger.log_action(
        user_id=str(user.id),
        action="login",
        resource_type="user",
        resource_id=str(user.id)
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }

@router.get("/me")
async def get_current_user(
    current_user = Depends(AuthService.get_current_user),
    db = Depends(get_db)
):
    return {
        "email": current_user.email,
        "role": current_user.role,
        "permissions": current_user.permissions
    }