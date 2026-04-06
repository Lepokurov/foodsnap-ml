from app.core.security import create_access_token, hash_password, verify_password
from app.schemas.auth import AuthResponse, LoginRequest, RegisterRequest, UserResponse
from app.services.state import UserRecord, store
from app.utils.ids import new_id


class AuthService:
    def register(self, payload: RegisterRequest) -> AuthResponse:
        if payload.email in store.users_by_email:
            raise ValueError("User with this email already exists.")

        user = UserRecord(
            id=new_id("user"),
            email=payload.email,
            full_name=payload.full_name,
            password_hash=hash_password(payload.password),
        )
        store.users_by_id[user.id] = user
        store.users_by_email[user.email] = user

        token = create_access_token(user.id)
        store.tokens[token] = user.id
        return AuthResponse(access_token=token, user=self._to_schema(user))

    def login(self, payload: LoginRequest) -> AuthResponse:
        user = store.users_by_email.get(payload.email)
        if user is None or not verify_password(payload.password, user.password_hash):
            raise ValueError("Invalid email or password.")

        token = create_access_token(user.id)
        store.tokens[token] = user.id
        return AuthResponse(access_token=token, user=self._to_schema(user))

    def get_user_by_token(self, token: str) -> UserRecord | None:
        user_id = store.tokens.get(token)
        if not user_id:
            return None
        return store.users_by_id.get(user_id)

    @staticmethod
    def _to_schema(user: UserRecord) -> UserResponse:
        return UserResponse(id=user.id, email=user.email, full_name=user.full_name)


auth_service = AuthService()

