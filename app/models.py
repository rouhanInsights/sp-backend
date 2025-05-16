from sqlalchemy import Column, Integer, String, Date, ForeignKey, TIMESTAMP, BigInteger, Text, DateTime, text, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    mobile_no = Column(BigInteger, unique=True, nullable=False)
    dob = Column(Date)
    email = Column(String(255), unique=True, nullable=False)
    alternate_email = Column(String(255), unique=True)
    password = Column(String(255), nullable=False)  
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

class SpeechConversion(Base):
    __tablename__ = "speech_conversions"

    conversion_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)

    input_audio_path = Column(String(255), nullable=False)
    input_text_path = Column(String(255), nullable=False)

    output_text_enhanced = Column(Text, nullable=False)
    output_text_enriched = Column(Text, nullable=False)

    output_audio_path_enhanced = Column(String(255), nullable=False)
    output_audio_path_enriched = Column(String(255), nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

class SysFeedback(Base):
    __tablename__ = "sys_feedback"

    feedback_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)

    clarity_score = Column(Float, nullable=False)
    fluency_score = Column(Float, nullable=False)
    correctness_score = Column(Float, nullable=False)
    ai_suggestion = Column(Text, nullable=False)

    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))

    user = relationship("User", backref="sys_feedbacks")
