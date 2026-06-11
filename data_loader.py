import json
import os

class DataLoader:
    def __init__(self, data_dir: str = "."):
        self.data_dir = data_dir
        self.clinics_rooms = []
        self.doctors = []
        self.services = []
        self.guidelines = []

    def load_data(self):
        """Loads data from JSON files into memory."""
        self.clinics_rooms = self._load_json("clinics_rooms.json")
        self.doctors = self._load_json("doctors.json")
        self.services = self._load_json("services.json")
        
        # Nạp tri thức RAG từ hospital_guidelines.txt
        guidelines_path = os.path.join(self.data_dir, "hospital_guidelines.txt")
        self.guidelines = []
        if os.path.exists(guidelines_path):
            with open(guidelines_path, "r", encoding="utf-8") as f:
                content = f.read()
                self.guidelines = [p.strip() for p in content.split("\n\n") if p.strip()]
                
        print("✅ Đã nạp thành công dữ liệu:")
        print(f"   - {len(self.clinics_rooms)} phòng khám")
        print(f"   - {len(self.doctors)} bác sĩ")
        print(f"   - {len(self.services)} dịch vụ")
        print(f"   - {len(self.guidelines)} tài liệu hướng dẫn (RAG)")

    def _load_json(self, filename: str):
        file_path = os.path.join(self.data_dir, filename)
        if not os.path.exists(file_path):
            print(f"⚠️ Không tìm thấy file: {file_path}")
            return []
        with open(file_path, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError as e:
                print(f"❌ Lỗi đọc file {filename}: {e}")
                return []

# Đoạn code dưới đây dùng để test nhanh việc đọc file
if __name__ == "__main__":
    loader = DataLoader()
    loader.load_data()
    print("\nVí dụ dữ liệu Dịch vụ đầu tiên:")
    if loader.services:
        print(json.dumps(loader.services[0], indent=2, ensure_ascii=False))
