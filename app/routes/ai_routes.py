from fastapi import APIRouter, File, UploadFile, HTTPException, Depends, Path
from sqlalchemy.orm import Session
import requests
import os
import uuid
from app.config import settings
from app.database import get_db
from app.models import SpeechConversion, SysFeedback
from app.routes.auth_routes import get_current_user

router = APIRouter()

# ✅ POST /ai/pipeline — process audio through Colab AI and save result
@router.post("/pipeline")
async def process_ai_pipeline(
    audio: UploadFile = File(...),
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user)
):
    print(user["user_id"])
    try:
        colab_url = f"{settings.COLAB_AI_URL}/pipeline"

        # ✅ Send audio to Colab AI
        response = requests.post(
            colab_url,
            files={"audio": (audio.filename, await audio.read(), audio.content_type)},
        )

        if response.status_code != 200:
            raise HTTPException(status_code=500, detail="AI server error")

        result = response.json()
        feedback = result.get("ai_feedback", {})

        # print("🧠 Feedback Score from Colab:", feedback)

        # ✅ Save raw transcription as .txt file
        raw_text = result["raw_transcription"]
        raw_filename = f"raw_{uuid.uuid4().hex}.txt"
        raw_path = os.path.join("static", "audio", raw_filename)
        os.makedirs(os.path.dirname(raw_path), exist_ok=True)
        with open(raw_path, "w", encoding="utf-8") as f:
            f.write(raw_text)

        # ✅ Save into SpeechConversion table
        conversion = SpeechConversion(
            user_id=user["user_id"],
            input_audio_path=result["input_audio_url"],
            input_text_path=f"/{raw_path.replace(os.sep, '/')}",
            output_text_enhanced=result["enhanced_text"],
            output_text_enriched=result["enriched_text"],
            output_audio_path_enhanced=result["enhanced_audio_url"],
            output_audio_path_enriched=result["enriched_audio_url"],
        )

        db.add(conversion)
        db.commit()
        db.refresh(conversion)

        # ✅ Save into SysFeedback table
        if feedback:
            sys_feedback = SysFeedback(
                user_id=user["user_id"],
                clarity_score=feedback["clarity"],
                fluency_score=feedback["fluency"],
                correctness_score=feedback["correctness"],
                ai_suggestion=feedback["suggestion"]
            )
            db.add(sys_feedback)
            db.commit()

        return {
            "message": "Conversion successful",
            "conversion_id": conversion.conversion_id,
            "data": {
                **result,
                "feedback_score": feedback
            }
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process: {str(e)}")


# ✅ GET /ai/sessions — fetch all session metadata for sidebar
@router.get("/sessions")
def get_user_sessions(
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user)
):
    sessions = db.query(SpeechConversion)\
        .filter(SpeechConversion.user_id == user["user_id"])\
        .order_by(SpeechConversion.created_at.desc())\
        .all()

    return [
        {
            "id": session.conversion_id,
            "created_at": session.created_at,
            "enhanced_text": session.output_text_enhanced[:100],
        }
        for session in sessions
    ]


# ✅ GET /ai/session/{id} — load session details
@router.get("/session/{session_id}")
def get_session_by_id(
    session_id: int = Path(...),
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user)
):
    conversion = db.query(SpeechConversion).filter(
        SpeechConversion.conversion_id == session_id,
        SpeechConversion.user_id == user["user_id"]
    ).first()

    if not conversion:
        raise HTTPException(status_code=404, detail="Session not found.")

    raw_text = ""
    if conversion.input_text_path:
        try:
            full_path = os.path.join(os.getcwd(), conversion.input_text_path.strip("/\\"))
            with open(full_path, "r", encoding="utf-8") as f:
                raw_text = f.read()
        except FileNotFoundError:
            raw_text = "[Transcript file missing]"

    return {
        "conversion_id": conversion.conversion_id,
        "created_at": conversion.created_at,
        "raw_transcription": raw_text,
        "enhanced_text": conversion.output_text_enhanced,
        "enriched_text": conversion.output_text_enriched,
        "input_audio_url": conversion.input_audio_path,
        "enhanced_audio_url": conversion.output_audio_path_enhanced,
        "enriched_audio_url": conversion.output_audio_path_enriched,
    }
