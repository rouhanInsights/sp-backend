from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User
from app.schemas.schemas import UserCreate 
from app.auth.auth import hash_password, verify_password, create_access_token
from datetime import timedelta
from passlib.context import CryptContext
from sqlalchemy.exc import IntegrityError
import random
import string
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from app.config import settings

router = APIRouter()

@router.post("/signup")
def signup(user_data: UserCreate, db: Session = Depends(get_db)):
    try:
        # Check if email already exists
        existing_user = db.query(User).filter(User.email == user_data.email).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already registered")

        # Hash password before saving
        hashed_password = hash_password(user_data.password)

        # Create new user
        new_user = User(
            name=user_data.name,
            mobile_no=user_data.mobile_no,
            dob=user_data.dob,
            email=user_data.email,
            alternate_email=user_data.alternate_email if user_data.alternate_email else None,  # Allow empty alternate email
            password=hashed_password,
            school_college=user_data.school_college,
            degree=user_data.degree,
            gender=user_data.gender
        )

        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        return {"message": "User created successfully"}
    
    except IntegrityError as e:
        db.rollback()
        if "users_mobile_no_key" in str(e.orig):
            raise HTTPException(status_code=400, detail="Mobile number already exists")
        elif "users_email_key" in str(e.orig):
            raise HTTPException(status_code=400, detail="Email already exists")
        else:
            raise HTTPException(status_code=500, detail="Database error. Please try again.")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")



@router.post("/login")
def login(user_data: dict, db: Session = Depends(get_db)):
    email = user_data.get("email")
    password = user_data.get("password")

    # Find user by email
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=400, detail="Invalid credentials")

    # Verify password
    if not verify_password(password, user.password):
        raise HTTPException(status_code=400, detail="Invalid credentials")

    # Generate JWT Token
    access_token = create_access_token(data={"sub": user.email}, expires_delta=timedelta(hours=1))

    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/logout")
def logout():
    return {"message": "Logout successful. Please delete the token on the client side."}

# Generate a temporary password reset token (in real projects, send an email)
def generate_reset_token():
    return "".join(random.choices(string.ascii_letters + string.digits, k=12))

@router.post("/forgot-password")
def forgot_password(email: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=400, detail="Email not registered.")

    reset_token = generate_reset_token()
    # In a real app, store this token and send via email. For now, just return it.
    return {"message": f"Use this token to reset password: {reset_token}"}

@router.post("/reset-password")
def reset_password(email: str, reset_token: str, new_password: str, db: Session = Depends(get_db)):
    # Normally, you would verify the reset token. For now, allow reset without it.
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=400, detail="Invalid email.")

    user.password = hash_password(new_password)
    db.commit()

    return {"message": "Password reset successful! You can now log in with your new password."}

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise credentials_exception

    return {"user_id": user.user_id, "email": user.email}