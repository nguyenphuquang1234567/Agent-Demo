from fastapi import FastAPI, HTTPException, Form, UploadFile, File
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional
import os
import io
from PIL import Image

from google.genai import types
from src.app.api.chat_manager import chat_manager, recommender
from src.app.main import check_room_status, book_appointment, search_web_for_medical_info

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
        def stream_generator():
            try:
                current_response = chat.send_message_stream(message_content) # type: ignore
                
                while True:
                    function_call_detected = None
                    for chunk in current_response:
                        if chunk.text:
                            yield chunk.text
                        if getattr(chunk, 'function_calls', None):
                            function_call_detected = chunk.function_calls[0]
                    
                    if function_call_detected:
                        # Thực thi Tool thủ công
                        tool_name = function_call_detected.name
                        args = function_call_detected.args
                        
                        try:
                            if tool_name == "check_room_status":
                                result = check_room_status(**args)
                            elif tool_name == "book_appointment":
                                result = book_appointment(**args)
                            elif tool_name == "search_web_for_medical_info":
                                result = search_web_for_medical_info(**args)
                            else:
                                result = f"Tool {tool_name} không tồn tại."
                        except Exception as e:
                            result = f"Lỗi khi chạy tool {tool_name}: {str(e)}"
                            
                        # Gửi kết quả lại cho AI tiếp tục stream
                        current_response = chat.send_message_stream(
                            types.Part.from_function_response(
                                name=tool_name, 
                                response={"result": result}
                            )
                        )
                    else:
                        break # Kết thúc nếu không còn gọi hàm
            except Exception as e:
                yield f"\n\n**Lỗi Stream:** {str(e)}"
                
        return StreamingResponse(stream_generator(), media_type="text/plain")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi khi gửi qua Gemini: {str(e)}")

# Mount static files
os.makedirs("src/app/static", exist_ok=True)
app.mount("/", StaticFiles(directory="src/app/static", html=True), name="static")
