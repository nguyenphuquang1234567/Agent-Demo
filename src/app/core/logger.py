import logging
from src.app.core.config import settings

def setup_logger(name: str) -> logging.Logger:
    """
    Thiết lập logger cơ bản cho toàn bộ ứng dụng dựa trên cấu hình trong Settings.
    """
    logger = logging.getLogger(name)
    
    # Nếu logger chưa có handler nào thì mới thêm vào để tránh bị ghi log trùng (duplicate logs)
    if not logger.handlers:
        level = getattr(logging, settings.log_level.upper(), logging.INFO)
        logger.setLevel(level)
        
        # Tạo console handler
        ch = logging.StreamHandler()
        ch.setLevel(level)
        
        # Định dạng log
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        ch.setFormatter(formatter)
        
        # Gắn handler vào logger
        logger.addHandler(ch)
        
    return logger
