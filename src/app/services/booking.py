import json
from src.app.repositories.appointment import AppointmentRepository
from src.app.repositories.service import ServiceRepository

class BookingService:
    def __init__(self, appointment_repo: AppointmentRepository, service_repo: ServiceRepository):
        self.appointment_repo = appointment_repo
        self.service_repo = service_repo
        
    def book_appointment(self, patient_name: str, phone_number: str, service_id: str, appointment_time: str) -> str:
        matched_service = None
        clean_input = service_id.strip()
        services = self.service_repo.load_all()
        
        for s in services:
            if s['service_id'].lower() == clean_input.lower():
                matched_service = s
                break
                
        if not matched_service:
            for s in services:
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
        
        success = self.appointment_repo.add(appointment_data)
        
        if success:
            return json.dumps({
                "status": "success",
                "message": f"Đặt lịch thành công cho bệnh nhân {patient_name} tại chuyên khoa {service_name} ({final_service_id}) vào lúc {appointment_time}."
            }, ensure_ascii=False)
        else:
            return json.dumps({
                "status": "error",
                "message": "Lỗi khi lưu lịch hẹn."
            }, ensure_ascii=False)
