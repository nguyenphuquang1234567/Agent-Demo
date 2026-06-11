import re

class RAGSearcher:
    def __init__(self, guidelines):
        self.guidelines = guidelines
        # Tập từ dừng tiếng Việt phổ biến để lọc từ khóa
        self.stop_words = {
            "và", "hoặc", "của", "cho", "để", "bị", "tôi", "bạn", "này", "khi", 
            "có", "là", "nếu", "muốn", "như", "thế", "nào", "gì", "cần", "ta", 
            "tao", "ở", "tại", "đâu", "nào", "mấy", "bao", "nhiêu", "làm", "sao",
            "cách", "hướng", "dẫn", "quy", "định", "trình", "bản"
        }
        
    def clean_text(self, text: str) -> list[str]:
        text = text.lower()
        # Thay thế các ký tự đặc biệt bằng dấu cách
        text = re.sub(r'[^\w\s]', ' ', text)
        words = text.split()
        return [w for w in words if w not in self.stop_words]
        
    def search(self, query: str, threshold: float = 0.3) -> str:
        """
        Tìm kiếm phân đoạn tài liệu y tế / quy định liên quan nhất tới câu hỏi.
        Nếu không có phân đoạn nào có điểm trùng khớp >= threshold, trả về chuỗi rỗng.
        """
        query_keywords = self.clean_text(query)
        if not query_keywords:
            return ""
            
        best_score = 0
        best_paragraph = ""
        
        for paragraph in self.guidelines:
            # Lấy tập hợp từ khóa của đoạn văn bản
            para_keywords = set(self.clean_text(paragraph))
            if not para_keywords:
                continue
                
            # Đếm số từ khóa của câu hỏi khớp trong đoạn văn bản
            match_count = sum(1 for kw in query_keywords if kw in para_keywords)
            
            # Điểm số là tỷ lệ từ khóa của truy vấn được tìm thấy trong đoạn văn
            score = match_count / len(query_keywords)
            
            if score > best_score:
                best_score = score
                best_paragraph = paragraph
                
        if best_score >= threshold:
            return best_paragraph
        return ""
