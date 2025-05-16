from pydantic import BaseModel, EmailStr, Field, validator
from datetime import datetime

class UserCreate(BaseModel):
    name: str
    mobile_no: int
    dob: str
    email: EmailStr
    alternate_email: EmailStr | None = None 
    password: str = Field(..., min_length=8) 
    confirm_password: str
    school_college: str
    degree: str
    gender: str

    @validator("confirm_password")
    def passwords_match(cls, confirm_password, values):
        if "password" in values and confirm_password != values["password"]:
            raise ValueError("Passwords do not match")
        return confirm_password

class SysFeedbackOut(BaseModel):
    clarity_score: float
    fluency_score: float
    correctness_score: float
    ai_suggestion: str
    created_at: datetime

    model_config = {
        "from_attributes": True
    }
