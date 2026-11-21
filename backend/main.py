from fastapi import FastAPI, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import functions

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# Check email format, e.g. monica@gmail.com
def is_valid_email(email):
    if " " in email:                 
        return False
    if email.count("@") != 1:
        return False

    before_at = email.split("@")[0]  
    after_at = email.split("@")[1]   

    if before_at == "":              
        return False
    if "." not in after_at:         
        return False
    if after_at[0] == ".":       
        return False
    if after_at[len(after_at) - 1] == ".":  
        return False
    return True


# Model 1: Register
class RegisterRequest(BaseModel):
    username: str
    email: str
    password: str


# Model 2: Login
class LoginRequest(BaseModel):
    email: str
    password: str

# A1 - Register
@app.post("/register", status_code=201)
def register_user(data: RegisterRequest):
    if data.username.strip() == "":
        raise HTTPException(status_code=422, detail="Username cannot be empty")
    if data.email.strip() == "":
        raise HTTPException(status_code=422, detail="Email cannot be empty")
    if not is_valid_email(data.email.strip()):
        raise HTTPException(status_code=422, detail="Invalid email format")
    if data.password.strip() == "":
        raise HTTPException(status_code=422, detail="Password cannot be empty")
    result = functions.register_user(username=data.username.strip(), email=data.email.strip().lower(), password=data.password)
    if result is None:
        raise HTTPException(status_code=409, detail="Email already registered")
    return result


# A2 - Login
@app.post("/login")
def login(data: LoginRequest):
    if data.email.strip() == "" or data.password == "":
        raise HTTPException(status_code=422, detail="Email and password are required")
    token = functions.verify_login(email=data.email.strip().lower(), password=data.password)
    if not token:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    return token