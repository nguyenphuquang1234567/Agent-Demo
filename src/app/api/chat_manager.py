import uuid
from typing import Dict, Any
from google.genai import types

from src.app.core.logger import setup_logger
from src.app.core.ai_factory import AIFactory
from src.app.main import (
    check_room_status, 
    book_appointment, 
    search_web_for_medical_info, 
    document_service, 
    recommender,
    service_repo
)

logger = setup_logger(__name__)

SYS_INSTRUCT = """Bạn là trợ lý y tế thông minh của bệnh viện. Nhiệm vụ của bạn:
1. Khuyên bệnh nhân nên sử dụng dịch vụ gì dựa trên phần [SYSTEM_INFO] do hệ thống ngầm cung cấp. Hãy trả lời thật tự nhiên.
2. Tra cứu tình trạng phòng khám bằng cách sử dụng công cụ check_room_status khi bệnh nhân thắc mắc về thời gian chờ hoặc sự đông đúc.
3. Khi bệnh nhân đồng ý đặt lịch khám, hãy hỏi đầy đủ thông tin: Họ tên, Số điện thoại và Thời gian hẹn, sau đó gọi công cụ book_appointment.
4. NẾU người dùng hỏi các kiến thức y khoa, thông tin thuốc, hoặc tin tức y tế nói chung, HÃY SỬ DỤNG công cụ search_web_for_medical_info để tìm kiếm và trả lời một cách chính xác dựa trên web result (fact-check).
Trả lời ngắn gọn, lịch sự, ân cần.
"""

class ChatManager:
    def __init__(self):
        self.sessions: Dict[str, Any] = {}
        self.client = AIFactory.get_client()
        self.chat_model = AIFactory.get_model_name("chat")
        
        # Đọc danh sách khoa khám từ service_repo (lấy từ services.json)
        full_guidelines = "\n".join(document_service.guidelines)
        services = service_repo.load_all()
        services_info = "\n\nDANH SÁCH CÁC KHOA KHÁM VÀ DỊCH VỤ CỦA BỆNH VIỆN:\n"
        for s in services:
            services_info += f"- Tên khoa/dịch vụ: {s['name']} (Mã: {s['service_id']}) - Chi tiết: {s['description']}\n"
            
        self.full_context = f"TÀI LIỆU HƯỚNG DẪN BỆNH VIỆN:\n{full_guidelines}{services_info}"
        
        self.cache_name = None
        try:
            if self.full_context.strip():
                cache = self.client.caches.create(
                    model=self.chat_model,
                    config=types.CreateCachedContentConfig(
                        system_instruction=SYS_INSTRUCT,
                        contents=[self.full_context],
                        ttl="3600s"
                    )
                )
                self.cache_name = cache.name
                logger.info(f"API - Tạo Cache thành công! Tên Cache: {self.cache_name}")
        except Exception as e:
            logger.warning(f"API - Không thể tạo Cache: {e}. Sẽ sử dụng cách chèn động vào System Instruction thay thế.")

    def create_session(self) -> str:
        session_id = str(uuid.uuid4())
        
        if self.cache_name:
            chat = self.client.chats.create(
                model=self.chat_model,
                config=types.GenerateContentConfig(
                    cached_content=self.cache_name,
                    tools=[check_room_status, book_appointment, search_web_for_medical_info],
                    automatic_function_calling={"disable": True},
                    temperature=0.3
                )
            )
        else:
            # Fallback nếu tạo Cache thất bại (ví dụ: hết dung lượng Free Tier)
            # Chúng ta sẽ bơm trực tiếp dữ liệu vào System Instruction cho AI
            dynamic_instruct = f"{SYS_INSTRUCT}\n\n{self.full_context}"
            chat = self.client.chats.create(
                model=self.chat_model,
                config=types.GenerateContentConfig(
                    system_instruction=dynamic_instruct,
                    tools=[check_room_status, book_appointment, search_web_for_medical_info],
                    automatic_function_calling={"disable": True},
                    temperature=0.3
                )
            )
            
        self.sessions[session_id] = chat
        return session_id

    def get_session(self, session_id: str):
        return self.sessions.get(session_id)

chat_manager = ChatManager()
