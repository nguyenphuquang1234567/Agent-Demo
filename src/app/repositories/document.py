import os
from typing import List
from src.app.core.config import settings
from src.app.core.logger import setup_logger

logger = setup_logger(__name__)

class DocumentRepository:
    def __init__(self, filename: str = "hospital_guidelines.txt"):
        self.file_path = os.path.join(settings.data_dir, filename)
        
    def load_guidelines(self) -> List[str]:
        """Đọc và phân tách các đoạn văn từ file text."""
        if not os.path.exists(self.file_path):
            logger.warning(f"File tài liệu không tồn tại: {self.file_path}")
            return []
            
        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                content = f.read()
                return [p.strip() for p in content.split("\n\n") if p.strip()]
        except Exception as e:
            logger.error(f"Lỗi đọc file {self.file_path}: {e}")
            return []
