from src.app.repositories.base import BaseJsonRepository

class ClinicRepository(BaseJsonRepository):
    def __init__(self):
        super().__init__("clinics_rooms.json")
        
    def find_by_id(self, clinic_id: str):
        clinics = self.load_all()
        for c in clinics:
            if c.get("id") == clinic_id:
                return c
        return None
