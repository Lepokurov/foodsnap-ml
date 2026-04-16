from app.core.security import (
    create_access_token,
    hash_password,
    parse_access_token,
    verify_password,
)
from app.db.models.user import User
from app.db.repositories.users import UserRepository
from app.schemas.auth import AuthResponse, LoginRequest, RegisterRequest, UserResponse
from app.utils.ids import new_id


class AuthService:
    def __init__(self, users: UserRepository) -> None:
        self._users = users

    def register(self, payload: RegisterRequest) -> AuthResponse:
        if self._users.get_by_email(payload.email) is not None:
            raise ValueError("User with this email already exists.")

        user = self._users.create(
            id=new_id("user"),
            email=payload.email,
            full_name=payload.full_name,
            password_hash=hash_password(payload.password),
        )

        token = create_access_token(user.id)
        return AuthResponse(access_token=token, user=self._to_schema(user))

    def login(self, payload: LoginRequest) -> AuthResponse:
        user = self._users.get_by_email(payload.email)
        if user is None or not verify_password(payload.password, user.password_hash):
            raise ValueError("Invalid email or password.")

        token = create_access_token(user.id)
        return AuthResponse(access_token=token, user=self._to_schema(user))

    def get_user_by_token(self, token: str) -> User | None:
        user_id = parse_access_token(token)
        if user_id is None:
            return None
        return self._users.get_by_id(user_id)

    @staticmethod
    def _to_schema(user: User) -> UserResponse:
        return UserResponse(id=user.id, email=user.email, full_name=user.full_name)
