from src.app.repositories.base import BaseJsonRepository

class ServiceRepository(BaseJsonRepository):
    def __init__(self):
        super().__init__("services.json")
        
    def find_by_code(self, code: str):
        services = self.load_all()
        for s in services:
            if s.get("service_code") == code:
                return s
        return None
