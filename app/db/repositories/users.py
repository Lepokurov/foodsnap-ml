from sqlalchemy import select

from app.db.models.user import User
from app.db.session import get_db_session


class UserRepository:
    def get_by_email(self, email: str) -> User | None:
        with get_db_session() as session:
            return session.scalar(select(User).where(User.email == email))

    def get_by_id(self, user_id: str) -> User | None:
        with get_db_session() as session:
            return session.get(User, user_id)

    def create(self, *, id: str, email: str, full_name: str, password_hash: str) -> User:
        user = User(
            id=id,
            email=email,
            full_name=full_name,
            password_hash=password_hash,
        )
        with get_db_session() as session:
            session.add(user)
        return user
