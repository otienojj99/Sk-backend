from fastapi import FastAPI, Depends, HTTPException, status
import firebase_admin
from firebase_admin import credentials
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware
from .social_auth import router as auth_router
from .models import Base
from .database import engine
from . import models, schemas, users, database
from .schemas import LoginRequest, TokenResponse
from .users import authenticate_user, get_current_user
from .token import create_access_token

Base.metadata.create_all(bind=engine)
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://1f43d9776b5d.ngrok-free.app"],  # for testing — lock down in production!
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
 
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/register", response_model=schemas.UserOut)
def  register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    return users.create_user(db, user)

@app.post("/login", response_model=TokenResponse)
def login(data: LoginRequest, db: Session = Depends(get_db)):
    user = authenticate_user(db, data.email, data.password)
    if not user:
        raise HTTPException(
             status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
        
    access_token = create_access_token(data={"sub": user.email})
    
    return {
        "accsess_token": access_token,
        "token_type": "bearer",
        "name": user.name
    }
    
@app.get("/me", response_model=schemas.UserOut)
def get_me(current_user: models.User = Depends(get_current_user)):
     return current_user
 
 
cred = credentials.Certificate("C:/Users/user/OneDrive/Desktop/skinlytics/backend/serviceFile/skinlytics-85cec-firebase-adminsdk-fbsvc-897ed8b128.json")
firebase_admin.initialize_app(cred)

app.include_router(auth_router)