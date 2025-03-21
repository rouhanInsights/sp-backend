from pydantic import BaseModel, EmailStr, Field, validator

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
