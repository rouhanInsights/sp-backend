from fastapi import FastAPI
from app.database import engine
from app.models import Base
from app.routes import auth_routes, user_routes, feedback_routes  # Future routes
from fastapi.middleware.cors import CORSMiddleware
from app.routes import ai_routes
from fastapi.staticfiles import StaticFiles
import os
app = FastAPI()

app.mount("/static", StaticFiles(directory=os.path.join(os.getcwd(), "static")), name="static")

Base.metadata.create_all(bind=engine)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for testing
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(auth_routes.router, prefix="/auth", tags=["Authentication"])
app.include_router(user_routes.router, prefix="/users", tags=["Users"]) 
app.include_router(feedback_routes.router, prefix="/feedback", tags=["Feedback"]) 
app.include_router(ai_routes.router, prefix="/ai", tags=["AI Pipeline"])

@app.get("/")
def home():
    print("successfully backend running!")
    return {"message": "Speech Fix Backend is Running"}
