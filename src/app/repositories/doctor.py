from src.app.repositories.base import BaseJsonRepository

class DoctorRepository(BaseJsonRepository):
    def __init__(self):
        super().__init__("doctors.json")
        
    def find_by_id(self, doctor_id: str):
        doctors = self.load_all()
        for d in doctors:
            if d.get("id") == doctor_id:
                return d
        return None
