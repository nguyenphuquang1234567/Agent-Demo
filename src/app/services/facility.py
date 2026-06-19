import json
from src.app.repositories.clinic import ClinicRepository

class FacilityService:
    def __init__(self, clinic_repo: ClinicRepository):
        self.clinic_repo = clinic_repo
        
    def check_room_status(self, department_name: str) -> str:
        def clean_text(text):
            return text.lower().replace("khoa", "").replace("phòng", "").replace("khám", "").strip()

        dept_query = clean_text(department_name)
        clinics = self.clinic_repo.load_all()
        
        room = next((r for r in clinics if clean_text(r['department']) in dept_query or dept_query in clean_text(r['department'])), None)
        
        if not room:
            return json.dumps({"error": f"Không tìm thấy phòng khám cho khoa: {department_name}"}, ensure_ascii=False)
            
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
