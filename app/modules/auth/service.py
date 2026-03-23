from sqlalchemy.orm import Session
from typing import Optional, List
from app.core.security import get_password_hash, verify_password
from app.modules.auth.models import User
from app.modules.auth.schemas import UserCreate, UserUpdate


# -------------------------
# Get User
# -------------------------

def get_user(db: Session, user_id: int) -> Optional[User]:
    return db.query(User).filter(User.id == user_id).first()


def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(User).offset(skip).limit(limit).all()


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    return db.query(User).filter(User.email == email).first()


def get_user_by_username(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()


# -------------------------
# Create User
# -------------------------

def create_user(db: Session, user_create: UserCreate):
    db_obj = User(
        username=user_create.username,
        email=user_create.email,
        hashed_password=get_password_hash(user_create.password),
        full_name=user_create.full_name,
    )
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


# -------------------------
# Update User
# -------------------------

def update_user(db: Session, db_obj: User, user_update: UserUpdate):
    update_data = user_update.dict(exclude_unset=True)

    if "password" in update_data:
        update_data["hashed_password"] = get_password_hash(update_data.pop("password"))

    for field, value in update_data.items():
        setattr(db_obj, field, value)

    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


# -------------------------
# Delete User
# -------------------------

def delete_user(db: Session, user_id: int):
    obj = db.query(User).filter(User.id == user_id).first()
    if obj:
        db.delete(obj)
        db.commit()
    return obj


# -------------------------
# Authenticate User
# -------------------------

def authenticate_user(db: Session, username: str, password: str):
    user = get_user_by_username(db, username=username)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user