import os
import sys
import time
import re
from PIL import Image
from google import genai
from google.genai import types

from data_loader import DataLoader
from recommender import ServiceRecommender
from tools import HospitalTools
from rag_searcher import RAGSearcher

# Khởi tạo dữ liệu và công cụ
loader = DataLoader()
loader.load_data()
recommender = ServiceRecommender(loader.services)
hospital_tools = HospitalTools()
rag_searcher = RAGSearcher(loader.guidelines)

# Định nghĩa Tool Call cho Gemini
def check_room_status(department_name: str) -> str:
    """
    Sử dụng hàm này khi người dùng hỏi về tình trạng, sự đông đúc, thời gian chờ hoặc số lượng bệnh nhân của một phòng khám (khoa) cụ thể.
    Ví dụ: Khoa Nhi, Khoa Nội Tổng Quát, Khoa Da Liễu...
    """
    print(f"\n[System: Đang tự động gọi Tool kiểm tra hệ thống phòng khám cho khoa '{department_name}'...]")
    return hospital_tools.check_room_status(department_name)

def book_appointment(patient_name: str, phone_number: str, service_id: str, appointment_time: str) -> str:
    """
    Sử dụng hàm này để đặt lịch hẹn khám bệnh cho bệnh nhân khi họ cung cấp đầy đủ thông tin:
    - patient_name: Họ tên của bệnh nhân.
    - phone_number: Số điện thoại liên lạc.
    - service_id: Mã dịch vụ y tế bệnh nhân muốn đặt (ví dụ: S001, S002, S003, S004, S005).
    - appointment_time: Thời gian đặt lịch (ví dụ: "10:30 ngày 10/06/2026").
    """
    print(f"\n[System: Đang tự động gọi Tool đặt lịch hẹn cho bệnh nhân '{patient_name}' tại khoa '{service_id}' lúc '{appointment_time}'...]")
    return hospital_tools.book_appointment(patient_name, phone_number, service_id, appointment_time)

def search_web_for_medical_info(query: str) -> str:
    """
    Sử dụng hàm này MỖI KHI người dùng hỏi về:
    - Tin tức y tế, dịch bệnh mới nhất.
    - Các thông tin y khoa, tác dụng phụ của thuốc, phương pháp điều trị mà hệ thống chưa biết.
    Công cụ này sẽ lên mạng tìm kiếm và fact-check từ nguồn uy tín.
    """
    print(f"\n[System: Đang tự động gọi Tool tìm kiếm web (Google Grounding) cho truy vấn: '{query}'...]")
    return hospital_tools.search_web_for_medical_info(query)

def main():
    os.environ["GEMINI_API_KEY"] = "AQ.Ab8RN6L_yScMZRGikw_9fUlx1warPkDnUAxDU5_cZqXPhKaEzw"
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("❌ Lỗi: Chưa thiết lập GEMINI_API_KEY trong biến môi trường.")
        print("Vui lòng chạy lệnh sau trong Terminal trước khi chạy script:")
        print("export GEMINI_API_KEY='chuỗi_api_key_của_bạn'")
        return

    # Khởi tạo Gemini Client (sử dụng SDK mới nhất)
    client = genai.Client()
    
    # System Instruction định hướng hành vi của Agent
    sys_instruct = """Bạn là trợ lý y tế thông minh của bệnh viện. Nhiệm vụ của bạn:
1. Khuyên bệnh nhân nên sử dụng dịch vụ gì dựa trên phần [SYSTEM_INFO] do hệ thống ngầm cung cấp. Hãy trả lời thật tự nhiên.
2. Tra cứu tình trạng phòng khám bằng cách sử dụng công cụ check_room_status khi bệnh nhân thắc mắc về thời gian chờ hoặc sự đông đúc.
3. Khi bệnh nhân đồng ý đặt lịch khám, hãy hỏi đầy đủ thông tin: Họ tên, Số điện thoại và Thời gian hẹn, sau đó gọi công cụ book_appointment.
4. NẾU người dùng hỏi các kiến thức y khoa, thông tin thuốc, hoặc tin tức y tế nói chung, HÃY SỬ DỤNG công cụ search_web_for_medical_info để tìm kiếm và trả lời một cách chính xác dựa trên web result (fact-check).
Trả lời ngắn gọn, lịch sự, ân cần.
"""

    print("\n[System: Đang khởi tạo bộ nhớ đệm (Prompt Caching) cho tài liệu bệnh viện (TTL: 60 phút)...]")
    cache_name = None
    try:
        # Đọc toàn bộ nội dung tài liệu hướng dẫn để đưa vào cache
        with open("hospital_guidelines.txt", "r", encoding="utf-8") as f:
            full_guidelines = f.read()
            
        cache = client.caches.create(
            model="gemini-3.1-flash-lite",
            config=types.CreateCachedContentConfig(
                system_instruction=sys_instruct,
                contents=[f"TÀI LIỆU HƯỚNG DẪN BỆNH VIỆN:\n{full_guidelines}"],
                ttl="3600s" # 60 phút
            )
        )
        cache_name = cache.name
        print(f"[System: Tạo Cache thành công! Tên Cache: {cache_name}]")
    except Exception as e:
        print(f"[System: Cảnh báo - Không thể tạo Cache (có thể do giới hạn API Key Free Tier): {e}]")
        print("[System: Hệ thống sẽ tự động chuyển về chế độ không dùng Cache (Fallback).]")

    if cache_name:
        chat = client.chats.create(
            model="gemini-3.1-flash-lite",
            config=types.GenerateContentConfig(
                cached_content=cache_name,
                tools=[check_room_status, book_appointment, search_web_for_medical_info],
                temperature=0.3
            )
        )
    else:
        chat = client.chats.create(
            model="gemini-3.1-flash-lite",
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

    current_service_id = "S001" # Mặc định là Nội Tổng Quát lúc bắt đầu
    
    while True:
        try:
            user_input = input("👤 Bạn: ")
            if user_input.lower() in ['quit', 'exit']:
                print("🤖 Agent: Cảm ơn bạn đã sử dụng dịch vụ. Chúc bạn nhiều sức khỏe!")
                break
                
            if not user_input.strip():
                continue

            # Phát hiện xem người dùng có truyền đường dẫn ảnh không
            image_path = None
            clean_query = user_input.strip()
            
            # Làm sạch dấu nháy kéo thả từ Finder
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
                print(f"\n[System: Đã phát hiện và nạp ảnh từ đường dẫn: {image_path}]")
                try:
                    img = Image.open(image_path)
                except Exception as e:
                    print(f"❌ Không thể mở hình ảnh: {e}")
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
                    matched_guideline = rag_searcher.search(clean_query)
                    if matched_guideline:
                        vision_instruct += f"\nThông tin hướng dẫn liên quan từ bệnh viện:\n{matched_guideline}"
                
                augmented_prompt = f"[SYSTEM_INFO: {vision_instruct}]\n\nCâu hỏi/Yêu cầu của người dùng: {clean_query if clean_query else 'Hãy phân tích hình ảnh này và đưa ra tư vấn y tế phù hợp.'}"
                message_content = [img, augmented_prompt]
            else:
                # Tìm kiếm thông tin hướng dẫn y tế / nội quy liên quan (RAG)
                matched_guideline = rag_searcher.search(user_input)

                # BƯỚC 1: Dùng Thuật toán Keyword phân tích triệu chứng
                matched_id = recommender.recommend(user_input)
                
                # Khởi tạo danh sách các thông tin bổ trợ hệ thống
                system_info_parts = []
                
                # Cập nhật context chẩn đoán nếu tìm thấy bệnh mới
                if matched_id is not None:
                    current_service_id = matched_id
                    service_details = recommender.get_service_details(current_service_id)
                    system_info_parts.append(f"Thuật toán phát hiện bệnh nhân có triệu chứng. Hãy khuyên họ dùng dịch vụ: {service_details['name']} (Giá: {service_details['price']} VND, Thời gian: {service_details['duration']} phút).")
                else:
                    departments = ", ".join([r['department'] for r in hospital_tools.loader.clinics_rooms])
                    system_info_parts.append(f"Bệnh viện hiện có các khoa: {departments}. Nếu người dùng hỏi thông tin chung, hãy trả lời dựa trên danh sách này. Đừng cố ép họ khám bệnh nếu họ không nêu triệu chứng.")
                
                # Chèn thêm tài liệu hướng dẫn y tế liên quan nếu tìm thấy (RAG)
                if matched_guideline:
                    system_info_parts.append(f"Tài liệu hướng dẫn liên quan tìm thấy từ tài liệu bệnh viện:\n{matched_guideline}\nHãy sử dụng nội dung tài liệu này để giải đáp cho bệnh nhân thật tự nhiên, không nhắc đến từ 'tài liệu hướng dẫn liên quan' hay nguồn trích dẫn.")
                    
                system_info = "\n- ".join(system_info_parts)
                augmented_prompt = f"[SYSTEM_INFO: {system_info}]\n\nNgười dùng nói: {user_input}"
                message_content = augmented_prompt

            # BƯỚC 2: Giao tiếp với Gemini (Gemini có thể gọi Tool ở bước này)
            start_time = time.time()
            response = chat.send_message(message_content)
            
            print("🤖 Agent: ", end="", flush=True)
            for char in (response.text or ""):
                sys.stdout.write(char)
                sys.stdout.flush()
                time.sleep(0.01)
            print("\n")
            
            latency = time.time() - start_time
            print(f"[System Metrics: Thời gian phản hồi: {latency:.2f}s]")
            if response.usage_metadata:
                cached_tokens = getattr(response.usage_metadata, 'cached_content_token_count', 0)
                prompt_tokens = response.usage_metadata.prompt_token_count
                total_tokens = response.usage_metadata.total_token_count
                print(f"[System Metrics: Tiêu thụ Token - Prompt: {prompt_tokens} | Cache: {cached_tokens} | Tổng: {total_tokens}]\n")
            
        except Exception as e:
            print(f"\n❌ Đã xảy ra lỗi: {e}")
            break

if __name__ == "__main__":
    main()
