from sqlalchemy import Column, Integer, String, Date, ForeignKey, TIMESTAMP, text, BigInteger
from sqlalchemy.orm import relationship
from app.database import Base

class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    mobile_no = Column(BigInteger, unique=True, nullable=False)
    dob = Column(Date)
    email = Column(String(255), unique=True, nullable=False)
    alternate_email = Column(String(255), unique=True)
    password = Column(String(255), nullable=False)  # Store only hashed password
    school_college = Column(String(255))
    degree = Column(String(255))
    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))
    gender = Column(String(1))

    feedbacks = relationship("Feedback", back_populates="user")

class Feedback(Base):
    __tablename__ = "feedback"

    feedback_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    feedback_text = Column(String(1000))
    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))

    user = relationship("User", back_populates="feedbacks")
