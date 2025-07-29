from sqlalchemy.orm import Session
from shallowfind.models.user import User


class UserService:
    def __init__(self, db: Session):
        self.db = db

    def get_user_by_id(self, user_id: str):
        """Retrieve user by ID."""
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise Exception(f"User with ID {user_id} not found.")
        return user
