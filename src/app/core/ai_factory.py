from google import genai
from src.app.core.config import settings

class AIFactory:
    """
    Factory Pattern dùng để khởi tạo AI Client và quyết định model theo chiến lược tác vụ (Strategy Pattern).
    """
    @staticmethod
    def get_client() -> genai.Client:
        return genai.Client(api_key=settings.gemini_api_key)
        
    @staticmethod
    def get_model_name(task_type: str) -> str:
        """
        Trả về tên model phù hợp với loại tác vụ.
        """
        # Các tác vụ phức tạp dùng bản Flash
        if task_type in ["search", "vision", "batch"]:
            return "gemini-2.5-flash"
        # Mặc định dùng bản Flash Lite cho tốc độ nhanh, tiết kiệm
        return "gemini-3.1-flash-lite"
