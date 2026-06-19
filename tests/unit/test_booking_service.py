import pytest
import json
from src.app.services.booking import BookingService

class FakeServiceRepository:
    """Mock repository để không đọc file services.json thật"""
    def load_all(self):
        return [
            {
                "service_id": "S004",
                "name": "Khám Da Liễu",
                "price": 600000,
                "duration": 30
            }
        ]

class FakeAppointmentRepository:
    """Mock repository để lưu trên memory, không ghi ra file appointments.json thật"""
    def __init__(self):
        self.appointments = []
        
    def add(self, appointment):
        self.appointments.append(appointment)
        return True

def test_book_appointment_success():
    fake_service_repo = FakeServiceRepository()
    fake_appointment_repo = FakeAppointmentRepository()
    service = BookingService(fake_appointment_repo, fake_service_repo)
    
    # Thực hiện đặt lịch với thông tin giả định
    result_str = service.book_appointment(
        patient_name="Trần Thị B", 
        phone_number="0901234567", 
        service_id="S004", 
        appointment_time="10:30 ngày mai"
    )
    result = json.loads(result_str)
    
    # Kiểm tra kết quả phản hồi
    assert result["status"] == "success"
    assert "Trần Thị B" in result["message"]
    
    # Đảm bảo logic Repository Mock đã hoạt động và lưu dữ liệu vào biến
    assert len(fake_appointment_repo.appointments) == 1
    assert fake_appointment_repo.appointments[0]["service_name"] == "Khám Da Liễu"
    assert fake_appointment_repo.appointments[0]["service_id"] == "S004"
