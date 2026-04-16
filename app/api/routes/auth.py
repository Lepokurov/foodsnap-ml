from fastapi import APIRouter, Depends, HTTPException, status

from app.api.deps.services import get_auth_service
from app.schemas.auth import AuthResponse, LoginRequest, RegisterRequest
from app.services.auth import AuthService


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
def register(
    payload: RegisterRequest,
    auth: AuthService = Depends(get_auth_service),
) -> AuthResponse:
    try:
        return auth.register(payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.post("/login", response_model=AuthResponse)
def login(
    payload: LoginRequest,
    auth: AuthService = Depends(get_auth_service),
) -> AuthResponse:
    try:
        return auth.login(payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from exc
