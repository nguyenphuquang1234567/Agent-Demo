import re
from src.app.repositories.service import ServiceRepository

class ServiceRecommender:
    def __init__(self, service_repo: ServiceRepository):
        self.service_repo = service_repo
        # Tập từ khóa tĩnh ánh xạ cho từng loại dịch vụ
        self.keyword_map = {
            "S001": ["tổng quát", "sốt", "đau đầu", "chóng mặt", "mệt mỏi", "đau bụng", "người lớn", "khám bệnh"],
            "S002": ["tim", "ngực", "khó thở", "huyết áp", "nhói", "hồi hộp", "đập nhanh"],
            "S003": ["trẻ em", "bé", "nhi", "trẻ nhỏ", "con nít", "trẻ con"],
            "S004": ["da", "mụn", "ngứa", "mẩn đỏ", "dị ứng", "nổi cục", "ghẻ", "nám"],
            "S005": ["tai", "mũi", "họng", "amidan", "ho", "sổ mũi", "viêm", "đờm", "ù tai"]
        }

    def recommend(self, patient_symptoms: str):
        """Phân tích triệu chứng và trả về service_id phù hợp nhất"""
        symptoms = patient_symptoms.lower()
        symptoms = re.sub(r'[^\w\s]', '', symptoms)
        words = symptoms.split()
        
        services = self.service_repo.load_all()
        scores: dict[str, int] = {str(service['service_id']): 0 for service in services}
        
        # Chấm điểm dựa trên Keyword Matching
        for service_id, keywords in self.keyword_map.items():
            for kw in keywords:
                # Nếu từ khóa có nhiều âm tiết (ví dụ "đau đầu")
                if " " in kw:
                    if kw in symptoms:
                        scores[service_id] += 2 # Ưu tiên cụm từ ghép
                else:
                    if kw in words:
                        scores[service_id] += 1
                        
        best_service_id = max(scores, key=lambda k: scores[k])
        
        if scores[best_service_id] > 0:
            return best_service_id
        return None
        
    def get_service_details(self, service_id: str):
        return self.service_repo.find_by_code(service_id)
