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


# Check user authentication (every user can only use their own data)
def check_user(token):
    user_id = functions.verify_token(token=token, token_type="access")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid or expired access token")
    if not functions.user_exists(user_id):
        raise HTTPException(status_code=401, detail="User not found")
    return user_id


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


# Model 3: Submit Feedback
class FeedbackCreate(BaseModel):
    subject: str
    message: str
    rating: int


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


# A3 - Refresh access token
@app.post("/refresh")
def refresh(refresh_token: str = Header(None)):
    user_id = functions.verify_token(token=refresh_token, token_type="refresh")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")
    return {"access_token": functions.create_token(user_id=user_id, token_type="access")}


# E1 - Get my feedback
@app.get("/feedback")
def get_feedback(token: str = Header(None)):
    user_id = check_user(token)
    return functions.get_feedback(user_id)


# E2 - Submit feedback
@app.post("/feedback", status_code=201)
def add_feedback(data: FeedbackCreate, token: str = Header(None)):
    user_id = check_user(token)  # user_id comes from the token, never from the request body
    if data.subject.strip() == "":
        raise HTTPException(status_code=422, detail="Subject cannot be empty")
    if data.message.strip() == "":
        raise HTTPException(status_code=422, detail="Message cannot be empty")
    if data.rating < 1 or data.rating > 5:
        raise HTTPException(status_code=422, detail="Rating must be between 1 and 5")
    return functions.add_feedback(user_id=user_id, subject=data.subject.strip(), message=data.message.strip(), rating=data.rating)
