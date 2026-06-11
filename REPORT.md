# BÁO CÁO DỰ ÁN: HỆ THỐNG TRỢ LÝ Y TẾ AI (HOSPITAL AGENT)

## 1. Tổng quan dự án
Dự án xây dựng một AI Agent thông minh hoạt động trong lĩnh vực y tế, đóng vai trò như một nhân viên tư vấn và lễ tân tại bệnh viện. Hệ thống có khả năng tương tác ngôn ngữ tự nhiên với bệnh nhân, tự động phân tích triệu chứng để đề xuất dịch vụ khám bệnh phù hợp, đồng thời có khả năng tra cứu trạng thái phòng khám theo thời gian thực để cung cấp thông tin về thời gian chờ.

## 2. Công nghệ sử dụng
- **Ngôn ngữ lập trình:** Python 3
- **AI Core:** Google GenAI SDK (Tích hợp mô hình Gemini tiên tiến)
- **Kiến trúc dữ liệu:** Lưu trữ cấu trúc qua hệ thống file JSON (đóng vai trò như Database).

## 3. Các tính năng cốt lõi đã hoàn thiện
Hệ thống hiện tại chạy qua Terminal với 2 luồng xử lý chính:

### 3.1. Thuật toán phân tích triệu chứng (Symptom-to-Service Mapping)
- **Cơ chế:** Hoạt động độc lập bằng Python (không phụ thuộc AI) để đảm bảo tính chính xác về mặt y khoa. Sử dụng kỹ thuật *Keyword Matching* và *Scoring*.
- **Cách thức:** Bệnh nhân nhập câu nói chứa triệu chứng (vd: "ho", "sổ mũi", "nhói ngực"). Hệ thống lọc từ khóa, chấm điểm và trả về mã dịch vụ (Service ID) phù hợp nhất.
- **Dữ liệu mồi (Prompt Injection):** Kết quả của thuật toán được đính kèm ngầm dưới dạng `[SYSTEM_INFO]` để định hướng câu trả lời của LLM.
- **Bộ nhớ ngữ cảnh (Context Memory):** Hệ thống có khả năng lưu trữ trạng thái chẩn đoán hiện tại (Stateful). Nếu bệnh nhân hỏi các câu tiếp theo không chứa từ khóa bệnh lý (VD: "Giá đắt quá", "Ở đó bao nhiêu người?"), thuật toán sẽ giữ nguyên khoa khám bệnh đã chẩn đoán trước đó thay vì reset lại, giúp LLM giao tiếp mượt mà như người thật.
- **Fallback:** Tự động điều hướng về dịch vụ "Khám Nội Tổng Quát" nếu ngay từ đầu câu nói không có triệu chứng rõ ràng.

### 3.2. Tra cứu dữ liệu thời gian thực qua Tool Calling (Function Calling)
- **Cơ chế:** Cung cấp công cụ `check_room_status` cho phép Gemini tự động truy xuất dữ liệu hệ thống.
- **Cách thức:** Khi bệnh nhân hỏi các thông tin mang tính cập nhật (như sự đông đúc, thời gian chờ của một khoa cụ thể), Gemini sẽ chủ động tạm dừng luồng hội thoại, kích hoạt Tool để lấy dữ liệu từ `clinics_rooms.json` (Số lượng bệnh nhân chờ, trạng thái phòng, bác sĩ trực).
- **Trải nghiệm:** JSON dữ liệu thô được Gemini tự động phiên dịch lại thành ngôn ngữ tự nhiên mềm mại để báo cáo cho bệnh nhân.
- **Cải tiến:** Đã tích hợp logic xử lý chuỗi (chuẩn hóa tên khoa) giúp Tool hoạt động chính xác dù Gemini gọi tham số dưới nhiều hình thức (VD: "Khoa Nhi", "Phòng Khám Nhi", "Nhi").

## 4. Cấu trúc dữ liệu
Hệ thống tải dữ liệu bộ nhớ từ 3 nguồn:
- `services.json`: Chứa danh mục các dịch vụ khám bệnh, chi phí, thời gian khám.
- `clinics_rooms.json`: Lưu trạng thái luân chuyển bệnh nhân tại các phòng khám, bao gồm sức chứa và thời gian chờ dự kiến.
- `doctors.json`: Danh sách bác sĩ theo chuyên khoa.


