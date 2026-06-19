import os
import sys
import time
import re
from PIL import Image
from google.genai import types

from src.app.core.config import settings
from src.app.core.logger import setup_logger
from src.app.core.ai_factory import AIFactory

# Nhập các Repository
from src.app.repositories.clinic import ClinicRepository
from src.app.repositories.service import ServiceRepository
from src.app.repositories.appointment import AppointmentRepository
from src.app.repositories.document import DocumentRepository
from src.app.repositories.doctor import DoctorRepository

# Nhập các Service
from src.app.services.facility import FacilityService
from src.app.services.booking import BookingService
from src.app.services.web_search import WebSearchService
from src.app.services.document import DocumentService
from src.app.services.recommender import ServiceRecommender

logger = setup_logger(__name__)

# ----------------- Khởi tạo DI Container -----------------
# 1. Repositories
clinic_repo = ClinicRepository()
service_repo = ServiceRepository()
appointment_repo = AppointmentRepository()
document_repo = DocumentRepository()
doctor_repo = DoctorRepository()

# 2. Services
facility_service = FacilityService(clinic_repo)
booking_service = BookingService(appointment_repo, service_repo)
web_search_service = WebSearchService()
document_service = DocumentService(document_repo)
recommender = ServiceRecommender(service_repo)

# ----------------- Định nghĩa Tool Call cho Gemini -----------------
def check_room_status(department_name: str) -> str:
    """
    Sử dụng hàm này khi người dùng hỏi về tình trạng, sự đông đúc, thời gian chờ hoặc số lượng bệnh nhân của một phòng khám (khoa) cụ thể.
    Ví dụ: Khoa Nhi, Khoa Nội Tổng Quát, Khoa Da Liễu...
    """
    logger.info(f"Đang gọi Tool: kiểm tra phòng khám cho '{department_name}'")
    return facility_service.check_room_status(department_name)

def book_appointment(patient_name: str, phone_number: str, service_id: str, appointment_time: str) -> str:
    """
    Sử dụng hàm này để đặt lịch hẹn khám bệnh cho bệnh nhân khi họ cung cấp đầy đủ thông tin:
    - patient_name: Họ tên của bệnh nhân.
    - phone_number: Số điện thoại liên lạc.
    - service_id: Mã dịch vụ y tế bệnh nhân muốn đặt (ví dụ: S001, S002, S003, S004, S005).
    - appointment_time: Thời gian đặt lịch (ví dụ: "10:30 ngày 10/06/2026").
    """
    logger.info(f"Đang gọi Tool: đặt lịch hẹn cho '{patient_name}' tại '{service_id}' lúc '{appointment_time}'")
    return booking_service.book_appointment(patient_name, phone_number, service_id, appointment_time)

def search_web_for_medical_info(query: str) -> str:
    """
    Sử dụng hàm này MỖI KHI người dùng hỏi về:
    - Tin tức y tế, dịch bệnh mới nhất.
    - Các thông tin y khoa, tác dụng phụ của thuốc, phương pháp điều trị mà hệ thống chưa biết.
    Công cụ này sẽ lên mạng tìm kiếm và fact-check từ nguồn uy tín.
    """
    logger.info(f"Đang gọi Tool: tìm kiếm web (Google Grounding) cho: '{query}'")
    return web_search_service.search_web_for_medical_info(query)

# ----------------- Hàm Main -----------------
def main():
    if not settings.gemini_api_key or settings.gemini_api_key == "your_gemini_api_key_here":
        logger.error("Chưa thiết lập GEMINI_API_KEY hợp lệ trong file .env")
        return

    # Khởi tạo Gemini Client từ AIFactory
    client = AIFactory.get_client()
    chat_model = AIFactory.get_model_name("chat")
    
    sys_instruct = """Bạn là trợ lý y tế thông minh của bệnh viện. Nhiệm vụ của bạn:
1. Khuyên bệnh nhân nên sử dụng dịch vụ gì dựa trên phần [SYSTEM_INFO] do hệ thống ngầm cung cấp. Hãy trả lời thật tự nhiên.
2. Tra cứu tình trạng phòng khám bằng cách sử dụng công cụ check_room_status khi bệnh nhân thắc mắc về thời gian chờ hoặc sự đông đúc.
3. Khi bệnh nhân đồng ý đặt lịch khám, hãy hỏi đầy đủ thông tin: Họ tên, Số điện thoại và Thời gian hẹn, sau đó gọi công cụ book_appointment.
4. NẾU người dùng hỏi các kiến thức y khoa, thông tin thuốc, hoặc tin tức y tế nói chung, HÃY SỬ DỤNG công cụ search_web_for_medical_info để tìm kiếm và trả lời một cách chính xác dựa trên web result (fact-check).
Trả lời ngắn gọn, lịch sự, ân cần.
"""

    logger.info("Đang khởi tạo bộ nhớ đệm (Prompt Caching) cho tài liệu bệnh viện (TTL: 60 phút)...")
    cache_name = None
    try:
        full_guidelines = "\n".join(document_service.guidelines)
        if full_guidelines:
            cache = client.caches.create(
                model=chat_model,
                config=types.CreateCachedContentConfig(
                    system_instruction=sys_instruct,
                    contents=[f"TÀI LIỆU HƯỚNG DẪN BỆNH VIỆN:\n{full_guidelines}"],
                    ttl="3600s" # 60 phút
                )
            )
            cache_name = cache.name
            logger.info(f"Tạo Cache thành công! Tên Cache: {cache_name}")
    except Exception as e:
        logger.warning(f"Không thể tạo Cache (Fallback sang không dùng Cache): {e}")

    if cache_name:
        chat = client.chats.create(
            model=chat_model,
            config=types.GenerateContentConfig(
                cached_content=cache_name,
                tools=[check_room_status, book_appointment, search_web_for_medical_info],
                temperature=0.3
            )
        )
    else:
        chat = client.chats.create(
            model=chat_model,
            config=types.GenerateContentConfig(
                system_instruction=sys_instruct,
                tools=[check_room_status, book_appointment, search_web_for_medical_info],
                temperature=0.3
            )
        )

    print("\n" + "="*60)
    print("🏥 CHÀO MỪNG ĐẾN VỚI HỆ THỐNG AGENT BỆNH VIỆN")
    print("="*60)
    print("🤖 Agent: Chào bạn, tôi là trợ lý ảo của bệnh viện. Tôi có thể giúp gì cho vấn đề sức khỏe của bạn hôm nay?")
    print("(Nhập 'quit' hoặc 'exit' để thoát)\n")

    current_service_id = "S001"
    
    while True:
        try:
            user_input = input("👤 Bạn: ")
            if user_input.lower() in ['quit', 'exit']:
                print("🤖 Agent: Cảm ơn bạn đã sử dụng dịch vụ. Chúc bạn nhiều sức khỏe!")
                break
                
            if not user_input.strip():
                continue

            image_path = None
            clean_query = user_input.strip()
            
            potential_file = clean_query.strip("'\"")
            if os.path.exists(potential_file) and potential_file.lower().endswith(('.png', '.jpg', '.jpeg', '.webp', '.bmp')):
                image_path = potential_file
                clean_query = ""
            else:
                pattern = r'(?:[a-zA-Z]:\\|[/\\])?[\w\-.\\/ ]+\.(?:png|jpg|jpeg|webp|bmp)'
                match = re.search(pattern, clean_query)
                if match:
                    potential_path = match.group(0).strip().strip("'\"")
                    if os.path.exists(potential_path):
                        image_path = potential_path
                        clean_query = clean_query.replace(match.group(0), "").strip()

            if image_path:
                logger.info(f"Đã phát hiện và nạp ảnh từ đường dẫn: {image_path}")
                try:
                    img = Image.open(image_path)
                except Exception as e:
                    logger.error(f"Không thể mở hình ảnh: {e}")
                    continue
                
                vision_instruct = (
                    "Người dùng đã gửi kèm một hình ảnh. Nhiệm vụ của bạn:\n"
                    "1. Nếu đây là đơn thuốc/toa thuốc: Hãy sử dụng khả năng phân tích hình ảnh để đọc nội dung thuốc (OCR), "
                    "trích xuất tên thuốc, liều dùng và hướng dẫn cách sử dụng một cách chi tiết, dễ hiểu.\n"
                    "2. Nếu đây là hình ảnh vết thương hoặc tổn thương ngoài da: Hãy nhận diện sơ bộ tổn thương (mẩn đỏ, ngứa, dị ứng, viêm...) "
                    "và khuyên bệnh nhân đặt lịch khám tại chuyên khoa Da Liễu (S004 - Khám Da Liễu, Giá: 600.000 VND, 30 phút).\n"
                    "3. Luôn đưa ra lời khuyên y tế an toàn, khuyến khích thăm khám bác sĩ trực tiếp."
                )
                
                if clean_query:
                    matched_guideline = document_service.search(clean_query)
                    if matched_guideline:
                        vision_instruct += f"\nThông tin hướng dẫn liên quan từ bệnh viện:\n{matched_guideline}"
                
                augmented_prompt = f"[SYSTEM_INFO: {vision_instruct}]\n\nCâu hỏi/Yêu cầu của người dùng: {clean_query if clean_query else 'Hãy phân tích hình ảnh này và đưa ra tư vấn y tế phù hợp.'}"
                message_content = [img, augmented_prompt]
            else:
                matched_guideline = document_service.search(user_input)
                matched_id = recommender.recommend(user_input)
                
                system_info_parts = []
                
                if matched_id is not None:
                    current_service_id = matched_id
                    service_details = recommender.get_service_details(current_service_id)
                    if service_details:
                        system_info_parts.append(f"Thuật toán phát hiện bệnh nhân có triệu chứng. Hãy khuyên họ dùng dịch vụ: {service_details['name']} (Giá: {service_details['price']} VND, Thời gian: {service_details['duration']} phút).")
                else:
                    clinics = clinic_repo.load_all()
                    departments = ", ".join([r['department'] for r in clinics])
                    system_info_parts.append(f"Bệnh viện hiện có các khoa: {departments}. Nếu người dùng hỏi thông tin chung, hãy trả lời dựa trên danh sách này. Đừng cố ép họ khám bệnh nếu họ không nêu triệu chứng.")
                
                if matched_guideline:
                    system_info_parts.append(f"Tài liệu hướng dẫn liên quan tìm thấy từ tài liệu bệnh viện:\n{matched_guideline}\nHãy sử dụng nội dung tài liệu này để giải đáp cho bệnh nhân thật tự nhiên, không nhắc đến từ 'tài liệu hướng dẫn liên quan' hay nguồn trích dẫn.")
                    
                system_info = "\n- ".join(system_info_parts)
                augmented_prompt = f"[SYSTEM_INFO: {system_info}]\n\nNgười dùng nói: {user_input}"
                message_content = augmented_prompt

            start_time = time.time()
            response = chat.send_message(message_content)
            
            print("🤖 Agent: ", end="", flush=True)
            for char in (response.text or ""):
                sys.stdout.write(char)
                sys.stdout.flush()
                time.sleep(0.01)
            print("\n")
            
            latency = time.time() - start_time
            if settings.debug:
                logger.debug(f"Thời gian phản hồi: {latency:.2f}s")
                if response.usage_metadata:
                    cached_tokens = getattr(response.usage_metadata, 'cached_content_token_count', 0)
                    prompt_tokens = response.usage_metadata.prompt_token_count
                    total_tokens = response.usage_metadata.total_token_count
                    logger.debug(f"Tiêu thụ Token - Prompt: {prompt_tokens} | Cache: {cached_tokens} | Tổng: {total_tokens}")
            
        except Exception as e:
            logger.error(f"Đã xảy ra lỗi: {e}")
            break

if __name__ == "__main__":
    main()
