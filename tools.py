import math
import json
from data_loader import DataLoader

class HospitalTools:
    def __init__(self):
        self.loader = DataLoader()
        self.loader.load_data()
        
    def check_room_status(self, department_name: str) -> str:
        """
        Tool call function: Lấy thông tin phòng khám và dùng M/M/c để tính thời gian chờ
        """
        # Chuẩn hóa chuỗi: bỏ các từ "khoa", "phòng", "khám" để tìm kiếm chính xác hơn
        def clean_text(text):
            return text.lower().replace("khoa", "").replace("phòng", "").replace("khám", "").strip()

        dept_query = clean_text(department_name)
        room = next((r for r in self.loader.clinics_rooms if clean_text(r['department']) in dept_query or dept_query in clean_text(r['department'])), None)
        
        if not room:
            return json.dumps({"error": f"Không tìm thấy phòng khám cho khoa: {department_name}"}, ensure_ascii=False)
            
        # Đóng gói dữ liệu trả về cho Gemini trực tiếp từ file JSON
        result = {
            "department": room['department'],
            "doctor_on_duty": room['doctor'],
            "status": room['status'],
            "current_patients_waiting": room['current_patients'],
            "capacity": room['capacity'],
            "estimated_wait_minutes": room['estimated_wait_minutes'],
            "message": "Sử dụng thông số này để tư vấn cho bệnh nhân."
        }
        
        return json.dumps(result, indent=2, ensure_ascii=False)

    def book_appointment(self, patient_name: str, phone_number: str, service_id: str, appointment_time: str) -> str:
        """
        Sử dụng hàm này để đặt lịch hẹn khám bệnh cho bệnh nhân khi họ cung cấp đầy đủ thông tin:
        - patient_name: Họ tên của bệnh nhân.
        - phone_number: Số điện thoại liên lạc.
        - service_id: Mã dịch vụ y tế bệnh nhân muốn đặt (ví dụ: S001, S002, S003, S004, S005).
        - appointment_time: Thời gian đặt lịch (ví dụ: "10:30 ngày 10/06/2026").
        """
        import os
        
        # Chuẩn hóa service_id và lấy tên dịch vụ tương ứng
        matched_service = None
        clean_input = service_id.strip()
        
        # 1. Tìm theo mã dịch vụ (service_id)
        for s in self.loader.services:
            if s['service_id'].lower() == clean_input.lower():
                matched_service = s
                break
                
        # 2. Nếu không tìm thấy, thử tìm theo tên khoa/dịch vụ
        if not matched_service:
            for s in self.loader.services:
                if clean_input.lower() in s['name'].lower() or s['name'].lower() in clean_input.lower():
                    matched_service = s
                    break
                    
        if matched_service:
            final_service_id = matched_service['service_id']
            service_name = matched_service['name']
        else:
            final_service_id = service_id
            service_name = service_id
            
        appointment_data = {
            "patient_name": patient_name,
            "phone_number": phone_number,
            "service_id": final_service_id,
            "service_name": service_name,
            "appointment_time": appointment_time
        }
        
        appointments_file = "appointments.json"
        appointments = []
        if os.path.exists(appointments_file):
            try:
                with open(appointments_file, "r", encoding="utf-8") as f:
                    appointments = json.load(f)
            except Exception:
                appointments = []
                
        appointments.append(appointment_data)
        
        try:
            with open(appointments_file, "w", encoding="utf-8") as f:
                json.dump(appointments, f, indent=2, ensure_ascii=False)
            return json.dumps({
                "status": "success",
                "message": f"Đặt lịch thành công cho bệnh nhân {patient_name} tại chuyên khoa {service_name} ({final_service_id}) vào lúc {appointment_time}."
            }, ensure_ascii=False)
        except Exception as e:
            return json.dumps({
                "status": "error",
                "message": f"Lỗi khi lưu lịch hẹn: {str(e)}"
            }, ensure_ascii=False)

    def search_web_for_medical_info(self, query: str) -> str:
        """
        Thực hiện tra cứu web (Google Search Grounding) để fact-check và tìm kiếm các thông tin y khoa mới nhất.
        """
        import os
        from google import genai
        from google.genai import types

        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            return json.dumps({"error": "Chưa thiết lập GEMINI_API_KEY để tìm kiếm web."}, ensure_ascii=False)

        client = genai.Client()
        try:
            # Dùng Gemini 2.5 Flash kèm tính năng Search Grounding để tra cứu web
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=f"Tra cứu thông tin y khoa hoặc y tế sau trên web và trả lời ngắn gọn, fact-check kỹ từ các nguồn uy tín: {query}",
                config=types.GenerateContentConfig(
                    tools=[{"google_search": {}}],
                    temperature=0.1
                )
            )
            return json.dumps({
                "status": "success",
                "query": query,
                "web_result": response.text
            }, ensure_ascii=False)
        except Exception as e:
            return json.dumps({
                "status": "error",
                "message": f"Lỗi khi tìm kiếm web: {str(e)}"
            }, ensure_ascii=False)

if __name__ == "__main__":
    tools = HospitalTools()
    print("--- TEST TOOL CALL: CHECK_ROOM_STATUS (ĐỌC TRỰC TIẾP TỪ JSON) ---")
    
    # Test Khoa Nhi (Đang có 10 bệnh nhân theo JSON)
    print("\nTra cứu: 'Nhi Khoa'")
    print(tools.check_room_status("Nhi Khoa"))
    
    # Test Da Liễu (Đang có 1 bệnh nhân theo JSON)
    print("\nTra cứu: 'Da Liễu'")
    print(tools.check_room_status("Da Liễu"))
