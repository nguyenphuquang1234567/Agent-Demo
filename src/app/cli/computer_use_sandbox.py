import os
import json
import time
from google import genai
from google.genai import types

class ComputerUseSandbox:
    """
    Môi trường Sandbox giả lập an toàn để chặn các thao tác điều khiển thực tế.
    Thay vì click chuột thật, hệ thống sẽ in ra màn hình các hành động của Agent.
    """
    def __init__(self):
        self.screen_resolution = (1920, 1080)
        self.current_app = "Hospital Information System (HIS)"

    def take_screenshot(self) -> str:
        """Giả lập việc chụp ảnh màn hình phần mềm HIS"""
        return f"[Sandbox] Đã chụp ảnh màn hình ({self.screen_resolution[0]}x{self.screen_resolution[1]}). Ứng dụng hiện tại: {self.current_app}"

    def mouse_click(self, x: int, y: int) -> str:
        """Tool cho phép LLM click chuột vào một tọa độ"""
        action = f"[Sandbox] 🖱️ Agent đã di chuyển chuột và CLICK tại tọa độ (X:{x}, Y:{y})."
        print(action)
        return action

    def keyboard_type(self, text: str) -> str:
        """Tool cho phép LLM gõ phím"""
        action = f"[Sandbox] ⌨️ Agent đã gõ văn bản: '{text}'"
        print(action)
        return action

    def press_key(self, key_name: str) -> str:
        """Tool cho phép LLM ấn các phím đặc biệt (Enter, Tab, Esc...)"""
        action = f"[Sandbox] 🔘 Agent đã ấn phím: [{key_name}]"
        print(action)
        return action

def run_computer_use_demo():
    print("\n" + "="*70)
    print("🖥️ THỬ NGHIỆM COMPUTER USE - ĐIỀU KHIỂN PHẦN MỀM HIS (SANDBOX)")
    print("="*70)

    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("❌ Lỗi: Chưa thiết lập GEMINI_API_KEY trong biến môi trường.")
        return

    client = genai.Client()
    sandbox = ComputerUseSandbox()
    
    # Lấy ảnh màn hình giả lập
    print(sandbox.take_screenshot())
    print("\n[Bác sĩ yêu cầu]: 'Hãy mở phần mềm HIS và tra cứu hồ sơ bệnh án của bệnh nhân mã số BN-1002'.")
    print("-" * 50)

    sys_instruct = """Bạn là một Agent có khả năng điều khiển máy tính (Computer Use).
Hiện tại bạn đang ở trong màn hình phần mềm HIS (Hospital Information System) của bệnh viện.
Để tra cứu bệnh án, bạn phải thực hiện ĐÚNG các bước sau:
1. Click chuột vào thanh tìm kiếm ở tọa độ x=300, y=150. (dùng hàm mouse_click)
2. Gõ mã bệnh nhân mà bác sĩ yêu cầu. (dùng hàm keyboard_type)
3. Ấn phím Enter để tìm kiếm. (dùng hàm press_key)

Hãy gọi các công cụ (tools) một cách tuần tự để hoàn thành nhiệm vụ này."""

    # Wrapper functions for Gemini Tools
    def mouse_click(x: int, y: int) -> str:
        return sandbox.mouse_click(x, y)
        
    def keyboard_type(text: str) -> str:
        return sandbox.keyboard_type(text)
        
    def press_key(key_name: str) -> str:
        return sandbox.press_key(key_name)

    chat = client.chats.create(
        model="gemini-2.5-flash", # Dùng 2.5 Flash vì nó hỗ trợ tool calling rất tốt
        config=types.GenerateContentConfig(
            system_instruction=sys_instruct,
            tools=[mouse_click, keyboard_type, press_key],
            temperature=0.1
        )
    )

    print("\n🤖 Agent đang suy nghĩ và chiếm quyền điều khiển máy tính...\n")
    time.sleep(1)
    
    # Kích hoạt Agent
    try:
        response = chat.send_message("Hãy mở hồ sơ bệnh án mã BN-1002.")
        print(f"\n🤖 Agent báo cáo: {response.text}")
        print("\n✅ Thử nghiệm Computer Use thành công! (Tất cả thao tác đều được bảo vệ trong Sandbox)")
    except Exception as e:
        print(f"\n❌ Đã xảy ra lỗi khi gọi AI: {e}")

if __name__ == "__main__":
    run_computer_use_demo()
