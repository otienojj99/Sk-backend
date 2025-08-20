from pydantic import BaseModel, EmailStr

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    
class UserOut(BaseModel):
    id:int
    name:str
    email:EmailStr
    
    model_config = {
    "from_attributes": True
}
    
    
class LoginRequest(BaseModel):
    email: EmailStr
    password: str
    
class TokenResponse(BaseModel):
    accsess_token: str
    token_type: str
    name: str

