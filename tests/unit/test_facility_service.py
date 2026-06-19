import pytest
from src.app.services.facility import FacilityService

class FakeClinicRepository:
    """Mock repository để không đọc file json thật khi test"""
    def load_all(self):
        return [
            {
                "id": "C001",
                "department": "Khoa Da Liễu",
                "doctor": "BS. Nguyễn Văn A",
                "status": "Đang hoạt động",
                "current_patients": 2,
                "capacity": 10,
                "estimated_wait_minutes": 15
            }
        ]

def test_check_room_status_found():
    fake_repo = FakeClinicRepository()
    service = FacilityService(fake_repo)
    
    result = service.check_room_status("Khoa Da Liễu")
    
    assert "BS. Nguyễn Văn A" in result
    assert "Đang hoạt động" in result
    assert "15" in result

def test_check_room_status_not_found():
    fake_repo = FakeClinicRepository()
    service = FacilityService(fake_repo)
    
    result = service.check_room_status("Khoa Tim Mạch")
    
    assert "error" in result
    assert "Không tìm thấy" in result
