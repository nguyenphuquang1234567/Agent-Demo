from typing import Dict, Any
from src.app.repositories.base import BaseJsonRepository
from src.app.core.logger import setup_logger

logger = setup_logger(__name__)

class AppointmentRepository(BaseJsonRepository):
    def __init__(self):
        super().__init__("appointments.json")
        
    def add(self, appointment: Dict[str, Any]) -> bool:
        """Thêm một lịch hẹn mới vào file."""
        appointments = self.load_all()
        appointments.append(appointment)
        success = self.save_all(appointments)
        if success:
            logger.info(f"Đã lưu lịch hẹn cho {appointment.get('patient_name')} thành công.")
        return success
