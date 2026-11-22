from sqlalchemy import Integer, String, Column, create_engine, DateTime, ForeignKey
from sqlalchemy.orm import Session, declarative_base
from datetime import datetime, timedelta, timezone

import jwt
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

ph = PasswordHasher()

# Database file is kept in /app/data, the folder mounted from EC2 (/opt/feedback/data)
DB_URL = "sqlite:////app/data/feedback.db"
engine = create_engine(DB_URL)
Base = declarative_base()

ACCESS_TOKEN_EXPIRY = 15  # mins
REFRESH_TOKEN_EXPIRY = 7 * 24 * 60  # mins
SECRET_KEY = "SECRET123"
ALGORITHM = "HS256"


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String)
    email = Column(String)
    hashed_password = Column(String)
    created_at = Column(DateTime, default=datetime.now)


class Feedback(Base):
    __tablename__ = "feedback"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    subject = Column(String)
    message = Column(String)
    rating = Column(Integer)
    created_at = Column(DateTime, default=datetime.now)


Base.metadata.create_all(engine)


#Users 

def register_user(username, email, password):
    session = Session(engine)
    if session.query(User).filter_by(email=email).first() is not None:
        session.close()
        return None
    user = User(username=username, email=email, hashed_password=ph.hash(password))
    session.add(user)
    session.commit()  # commit first so user.id is set
    response = {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "created_at": user.created_at.strftime("%d-%m-%Y %H:%M:%S")
    }
    session.close()
    return response


# Authentication 

def verify_login(email, password):
    session = Session(engine)
    user = session.query(User).filter_by(email=email).first()
    session.close()
    if user is None:
        return False
    try:
        ph.verify(user.hashed_password, password)
    except VerifyMismatchError:
        return False
    return {
        "access_token": create_token(user_id=user.id, token_type="access"),
        "refresh_token": create_token(user_id=user.id, token_type="refresh"),
        "username": user.username
    }


def create_token(user_id, token_type):
    time = ACCESS_TOKEN_EXPIRY
    if token_type == "refresh":
        time = REFRESH_TOKEN_EXPIRY
    payload = {
        "user_id": user_id,
        "token_type": token_type,
        "exp": datetime.now(timezone.utc) + timedelta(minutes=time)
    }
    return jwt.encode(payload, key=SECRET_KEY, algorithm=ALGORITHM)


def verify_token(token, token_type):
    if token is None:
        return False
    try:
        payload = jwt.decode(jwt=token, key=SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.PyJWTError:
        return False
    if payload["token_type"] == token_type:
        return payload["user_id"]
    return False


def user_exists(user_id):
    session = Session(engine)
    user = session.get(User, user_id)
    session.close()
    return user is not None


#Feedback 

def get_feedback(user_id):
    session = Session(engine)
    feedbacks = session.query(Feedback).filter(Feedback.user_id == user_id).order_by(Feedback.id.desc()).all()
    response = []
    for feedback in feedbacks:
        temp_feedback = {
            "id": feedback.id,
            "subject": feedback.subject,
            "message": feedback.message,
            "rating": feedback.rating,
            "created_at": feedback.created_at.strftime("%d-%m-%Y %H:%M:%S")
        }
        response.append(temp_feedback)
    session.close()
    return response


def add_feedback(user_id, subject, message, rating):
    session = Session(engine)
    feedback = Feedback(user_id=user_id, subject=subject, message=message, rating=rating)
    session.add(feedback)
    session.commit()  # commit first so feedback.id is set
    response = {
        "id": feedback.id,
        "subject": feedback.subject,
        "message": feedback.message,
        "rating": feedback.rating,
        "created_at": feedback.created_at.strftime("%d-%m-%Y %H:%M:%S")
    }
    session.close()
    return response
