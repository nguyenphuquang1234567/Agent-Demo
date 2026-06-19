import json
import os
from typing import List, Dict, Any, Optional
from src.app.core.config import settings
from src.app.core.logger import setup_logger

logger = setup_logger(__name__)

class BaseJsonRepository:
    """
    Lớp cơ sở cung cấp các phương thức CRUD cơ bản với file JSON.
    """
    def __init__(self, filename: str):
        self.file_path = os.path.join(settings.data_dir, filename)

    def load_all(self) -> List[Dict[str, Any]]:
        """Đọc toàn bộ dữ liệu từ file JSON."""
        if not os.path.exists(self.file_path):
            logger.warning(f"File không tồn tại: {self.file_path}")
            return []
            
        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            logger.error(f"Lỗi phân tích JSON từ {self.file_path}: {e}")
            return []
        except Exception as e:
            logger.error(f"Lỗi đọc file {self.file_path}: {e}")
            return []

    def save_all(self, data: List[Dict[str, Any]]) -> bool:
        """Lưu toàn bộ dữ liệu vào file JSON (ghi đè)."""
        try:
            # Tạo thư mục nếu chưa tồn tại
            os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
            with open(self.file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            return True
        except Exception as e:
            logger.error(f"Lỗi ghi file {self.file_path}: {e}")
            return False
