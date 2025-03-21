from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User
from app.auth.auth import decode_access_token
from fastapi.security import OAuth2PasswordBearer

router = APIRouter()

# Define OAuth2 scheme to read JWT token from request headers
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

@router.get("/me")
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    # Decode the JWT token
    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(status_code=401, detail="Invalid token or expired")

    # Get user email from token
    user_email = payload.get("sub")
    if user_email is None:
        raise HTTPException(status_code=401, detail="Invalid token payload")

    # Retrieve user from database
    user = db.query(User).filter(User.email == user_email).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    # Return user details (without password)
    return {
        "name": user.name,
        "email": user.email,
        "mobile_no": user.mobile_no,
        "dob": user.dob,
        "school_college": user.school_college,
        "degree": user.degree,
        "gender": user.gender
    }
