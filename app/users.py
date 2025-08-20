import os
from dotenv import load_dotenv
from sqlalchemy.orm import Session
from . import models, schemas, auth
from .models import User
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from .database import SessionLocal
from .database import get_db


def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = auth.hash_password(user.password)
    db_user = models.User(
        name = user.name,
        email = user.email,
        hashed_password = hashed_password,
        is_social=False
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def authenticate_user(db: Session, email: str, password: str):
   
    user = db.query(User).filter(User.email == email).first()
    print(f"Authenticating user: {user}")
    if not user:
        return None
    if user.is_social:
        raise HTTPException(
            status_code=400,
            detail="Use Google sign-in for this account"
        )
    if not auth.verify_password(password, user.hashed_password):
        print("Password verification failed")
        return None
    return user

load_dotenv()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
     credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
     
     try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
     except JWTError:
          raise credentials_exception

     user = db.query(User).filter(User.email == email).first()
     if user is None:
         raise credentials_exception
     return user