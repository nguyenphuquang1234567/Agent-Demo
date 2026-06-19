import re
from src.app.repositories.document import DocumentRepository

class DocumentService:
    def __init__(self, doc_repo: DocumentRepository):
        self.doc_repo = doc_repo
        self.guidelines = self.doc_repo.load_guidelines()
        self.stop_words = {
            "và", "hoặc", "của", "cho", "để", "bị", "tôi", "bạn", "này", "khi", 
            "có", "là", "nếu", "muốn", "như", "thế", "nào", "gì", "cần", "ta", 
            "tao", "ở", "tại", "đâu", "nào", "mấy", "bao", "nhiêu", "làm", "sao",
            "cách", "hướng", "dẫn", "quy", "định", "trình", "bản"
        }
        
    def clean_text(self, text: str) -> list[str]:
        text = text.lower()
        text = re.sub(r'[^\w\s]', ' ', text)
        words = text.split()
        return [w for w in words if w not in self.stop_words]
        
    def search(self, query: str, threshold: float = 0.3) -> str:
        query_keywords = self.clean_text(query)
        if not query_keywords or not self.guidelines:
            return ""
            
        best_score = 0
        best_paragraph = ""
        
        for paragraph in self.guidelines:
            para_keywords = set(self.clean_text(paragraph))
            if not para_keywords:
                continue
                
            match_count = sum(1 for kw in query_keywords if kw in para_keywords)
            score = match_count / len(query_keywords)
            
            if score > best_score:
                best_score = score
                best_paragraph = paragraph
                
        if best_score >= threshold:
            return best_paragraph
        return ""
