from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models.user import User


class UserRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def get_by_email(self, email: str) -> User | None:
        return self._session.scalar(select(User).where(User.email == email))

    def get_by_id(self, user_id: str) -> User | None:
        return self._session.get(User, user_id)

    def create(self, *, id: str, email: str, full_name: str, password_hash: str) -> User:
        user = User(
            id=id,
            email=email,
            full_name=full_name,
            password_hash=password_hash,
        )
        self._session.add(user)
        self._session.flush()
        return user
