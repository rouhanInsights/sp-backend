from fastapi import APIRouter, UploadFile, File
import shutil
import requests

router = APIRouter()

NGROK_COLAB_URL = "https://bdee-34-44-84-201.ngrok-free.app"

@router.post("/posture-analyze")
async def posture_analyze(file: UploadFile = File(...)):
    temp_file_path = f"static/uploads/{file.filename}"
    with open(temp_file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    with open(temp_file_path, "rb") as f:
        response = requests.post(NGROK_COLAB_URL, files={"file": f})

    return response.json()
