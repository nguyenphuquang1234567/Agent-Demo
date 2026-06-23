from fastapi import FastAPI, HTTPException, Form, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional
import os
import io
from PIL import Image

from src.app.api.chat_manager import chat_manager, recommender

app = FastAPI(title="Hospital Agent API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class StartSessionResponse(BaseModel):
    session_id: str
    message: str

@app.post("/api/chat/start", response_model=StartSessionResponse)
async def start_chat():
    session_id = chat_manager.create_session()
    return StartSessionResponse(
        session_id=session_id,
        message="Chào bạn, tôi là trợ lý y tế của bệnh viện. Tôi có thể giúp gì cho vấn đề sức khỏe của bạn hôm nay?"
    )

@app.post("/api/chat/message")
async def send_message(
    session_id: str = Form(...),
    message: str = Form(...),
    file: Optional[UploadFile] = File(None)
):
    chat = chat_manager.get_session(session_id)
    if not chat:
        raise HTTPException(status_code=404, detail="Session không tồn tại hoặc đã hết hạn")
        
    message_content = message
    
    if file:
        try:
            contents = await file.read()
            img = Image.open(io.BytesIO(contents))
            # Gemin API support list format for multimodal
            message_content = [img, message]
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Lỗi định dạng ảnh: {str(e)}")
    
    # Recommender: Augment prompt with system info
    recommended_service_id = recommender.recommend(message)
    augmented_prompt = f"[SYSTEM_INFO: Current Context - Patient might need service_id '{recommended_service_id}']\n{message}"
    
    if isinstance(message_content, list):
        message_content[1] = augmented_prompt
    else:
        message_content = augmented_prompt
        
    try:
        response = chat.send_message(message_content) # type: ignore
        return {"response": response.text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi khi gửi qua Gemini: {str(e)}")

# Mount static files
os.makedirs("src/app/static", exist_ok=True)
app.mount("/", StaticFiles(directory="src/app/static", html=True), name="static")
