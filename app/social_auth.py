from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel
from firebase_admin import auth as firebase_auth
from sqlalchemy.orm import Session
from .database import get_db
from .models import User
from .token import create_access_token # Already implemented

router = APIRouter()

class GoogleToken(BaseModel):
    id_token: str
    
@router.post("/google-login")
def google_login(token: GoogleToken, db: Session = Depends(get_db)):
    try:
        decode_token = firebase_auth.verify_id_token(token.id_token)
        email = decode_token.get("email")
        uid = decode_token.get("uid")
        name = decode_token.get("name", "Unknown User")

        if not email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email not found in token"
            )

        # Check if user exists
        user = db.query(User).filter(User.email == email).first()

        if not user:
            # Create user if doesn't exist
            user = User(email=email, name=name, hashed_password="", is_social=True)
            db.add(user)
            db.commit()
            db.refresh(user)

        # ✅ Always generate and return token
        access_token = create_access_token(data={"sub": user.email})

        return {
            "access_token": access_token,
            "token_type": "bearer"
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Google token verification failed: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )
