import json
from data_loader import DataLoader
import re

class ServiceRecommender:
    def __init__(self, services):
        self.services = services
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
        # Loại bỏ dấu câu cơ bản để dễ match từ
        symptoms = re.sub(r'[^\w\s]', '', symptoms)
        words = symptoms.split()
        
        scores = {service['service_id']: 0 for service in self.services}
        
        # Chấm điểm dựa trên Keyword Matching
        for service_id, keywords in self.keyword_map.items():
            for kw in keywords:
                # Dùng regex để tìm chính xác từ (tránh lỗi 'nhi' nằm trong 'nhiều')
                if re.search(rf'\b{kw}\b', symptoms):
                    # Trọng số đặc biệt cho Khoa Nhi (để tránh nhầm với sốt của người lớn)
                    if service_id == "S003":
                        scores[service_id] += 2
                    else:
                        scores[service_id] += 1
                    
        # Tìm service có điểm cao nhất
        best_match_id = max(scores, key=scores.get)
        
        # Nếu không có điểm nào > 0, trả về None để giữ ngữ cảnh cũ
        if scores[best_match_id] == 0:
            return None
            
        return best_match_id

    def get_service_details(self, service_id: str):
        for s in self.services:
            if s['service_id'] == service_id:
                return s
        return None

if __name__ == "__main__":
    loader = DataLoader()
    loader.load_data()
    
    recommender = ServiceRecommender(loader.services)
    
    # Test cases
    test_cases = [
        "Tôi hay bị nhói ngực trái và cảm thấy khó thở về đêm",
        "Con tôi 3 tuổi bị sốt cao từ hôm qua",
        "Mặt tôi tự nhiên nổi nhiều mẩn đỏ và rất ngứa",
        "Tôi muốn đi kiểm tra sức khỏe định kỳ",
        "Dạo này tôi hay bị ho có đờm và sổ mũi kéo dài"
    ]
    
    print("\n--- KẾT QUẢ TEST THUẬT TOÁN TƯ VẤN ---")
    for case in test_cases:
        matched_id = recommender.recommend(case)
        details = recommender.get_service_details(matched_id)
        print(f"Triệu chứng: '{case}'")
        print(f"-> Gợi ý: {details['name']} ({details['price']} VND)\n")
