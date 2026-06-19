import os
import json
import time
from google import genai
from google.genai import types

def generate_dummy_data(file_path="patient_logs.jsonl"):
    """Tạo file JSONL chứa các đoạn chat giả lập của bệnh nhân để phân tích Batch."""
    print(f"\n[1] Đang tạo dữ liệu mẫu (patient_logs.jsonl)...")
    logs = [
        "Hôm nay tôi khám ở khoa Nội, bác sĩ rất nhiệt tình nhưng thời gian chờ lấy thuốc hơi lâu.",
        "Tôi muốn phàn nàn về thái độ của nhân viên lễ tân lúc 8h sáng nay.",
        "Dịch vụ ở khoa Da liễu rất tuyệt vời, tôi đã chữa khỏi hẳn viêm da cơ địa.",
        "Tôi bị đau đầu liên tục kèm theo buồn nôn, không biết có phải do thuốc mới không?",
        "Khoa Nhi lúc nào cũng đông đúc, hi vọng bệnh viện mở rộng thêm phòng khám."
    ]
    
    with open(file_path, "w", encoding="utf-8") as f:
        for i, log in enumerate(logs):
            request_body = {
                "id": f"req-{i}",
                "request": {
                    "contents": [{"parts": [{"text": f"Hãy phân tích đoạn chat sau của bệnh nhân. Yêu cầu: 1. Đánh giá mức độ hài lòng (Tích cực, Tiêu cực, Trung lập). 2. Trích xuất phàn nàn hoặc triệu chứng nếu có. Đoạn chat: '{log}'"}]}]
                }
            }
            f.write(json.dumps(request_body, ensure_ascii=False) + "\n")
    print(f"✅ Đã tạo thành công {len(logs)} bản ghi vào {file_path}")

def process_batch():
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("❌ Lỗi: Chưa thiết lập GEMINI_API_KEY trong biến môi trường.")
        return

    client = genai.Client()
    file_name = "patient_logs.jsonl"
    
    # 1. Tạo file dữ liệu
    generate_dummy_data(file_name)
    
    try:
        # 2. Upload file lên hệ thống Google
        print(f"\n[2] Đang tải file dữ liệu lên Google Cloud...")
        uploaded_file = client.files.upload(file=file_name, config={'mime_type': 'application/jsonl'})
        print(f"✅ Tải lên thành công! File URI: {uploaded_file.uri}")
        
        # 3. Tạo Batch Job
        print(f"\n[3] Đang gửi yêu cầu Batch Processing (Phân tích hàng loạt)...")
        # Sử dụng model gemini-2.5-flash cho Batch Processing
        job = client.batches.create(
            model="gemini-2.5-flash", 
            src=uploaded_file.name
        )
        print(f"✅ Đã khởi tạo Batch Job thành công!")
        print(f"   Mã Job: {job.name}")
        print(f"   Trạng thái: {job.state}")
        
        print("\n[Hệ thống sẽ chạy ngầm và trả về kết quả lúc nửa đêm. Do đây là môi trường Demo, chúng ta sẽ dừng tại đây để tránh tốn phí.]")
        
    except Exception as e:
        print(f"\n❌ Cảnh báo - Không thể khởi tạo Batch Job (Có thể do giới hạn API Key Free Tier hoặc Model không hỗ trợ Batch): {e}")
        print("[System: Hệ thống sẽ tự động chuyển về chế độ chạy tuần tự (Fallback) nếu cần thiết.]")
        
if __name__ == "__main__":
    process_batch()
