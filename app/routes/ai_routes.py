from fastapi import APIRouter, File, UploadFile, HTTPException
import requests
from app.config import settings

router = APIRouter()

@router.post("/pipeline")
async def process_ai_pipeline(audio: UploadFile = File(...)):
    try:
        colab_url = f"{settings.COLAB_AI_URL}/pipeline"
        
        # Send the audio file to Colab AI server
        response = requests.post(
            colab_url,
            files={"audio": (audio.filename, await audio.read(), audio.content_type)},
        )

        if response.status_code != 200:
            raise HTTPException(status_code=500, detail="AI server error")

        return response.json()

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process: {str(e)}")
