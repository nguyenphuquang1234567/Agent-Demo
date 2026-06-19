import json
from google.genai import types
from src.app.core.ai_factory import AIFactory
from src.app.core.logger import setup_logger

logger = setup_logger(__name__)

class WebSearchService:
    def __init__(self):
        self.client = AIFactory.get_client()
        self.model_name = AIFactory.get_model_name("search")
        
    def search_web_for_medical_info(self, query: str) -> str:
        try:
            logger.info(f"Đang tìm kiếm thông tin trên Web với model: {self.model_name}")
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=f"Tra cứu thông tin y khoa hoặc y tế sau trên web và trả lời ngắn gọn, fact-check kỹ từ các nguồn uy tín: {query}",
                config=types.GenerateContentConfig(
                    tools=[{"google_search": {}}],
                    temperature=0.1
                )
            )
            return json.dumps({
                "status": "success",
                "query": query,
                "web_result": response.text
            }, ensure_ascii=False)
        except Exception as e:
            logger.error(f"WebSearchService Error: {e}")
            return json.dumps({
                "status": "error",
                "message": f"Lỗi khi tìm kiếm web: {str(e)}"
            }, ensure_ascii=False)
