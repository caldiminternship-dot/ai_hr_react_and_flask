from passlib.context import CryptContext
from sqlalchemy.orm import Session
from models import User
import streamlit as st

# Switch to pbkdf2_sha256 to avoid bcrypt 72-byte limit and version issues
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def login_user(db: Session, email, password):
    user = db.query(User).filter(User.email == email).first()
    if not user:
        return None
    if not verify_password(password, user.password_hash):
        return None
    return user

def create_user(db: Session, email, password):
    # Check if user exists
    existing_user = db.query(User).filter(User.email == email).first()
    if existing_user:
        return None, "Email already registered"
    
    hashed_password = get_password_hash(password)
    new_user = User(email=email, password_hash=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user, "Success"
