from fastapi import APIRouter, HTTPException, status

from app.schemas.auth import AuthResponse, LoginRequest, RegisterRequest
from app.services.auth import auth_service


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
def register(payload: RegisterRequest) -> AuthResponse:
    try:
        return auth_service.register(payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.post("/login", response_model=AuthResponse)
def login(payload: LoginRequest) -> AuthResponse:
    try:
        return auth_service.login(payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from exc

