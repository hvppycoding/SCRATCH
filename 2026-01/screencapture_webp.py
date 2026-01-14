import tkinter as tk
from PIL import ImageGrab
from datetime import datetime
import win32clipboard # 클립보드 제어 모듈
from io import BytesIO

class ScreenCaptureTool:
    def __init__(self):
        self.root = tk.Tk()
        # 반투명 배경 및 전체화면 설정
        self.root.attributes('-alpha', 0.3)
        self.root.attributes('-fullscreen', True)
        self.root.attributes('-topmost', True)
        self.root.config(bg="black", cursor="cross")

        self.start_x = None
        self.start_y = None
        self.rect = None

        self.canvas = tk.Canvas(self.root, cursor="cross", bg="grey11")
        self.canvas.pack(fill="both", expand=True)

        self.canvas.bind("<ButtonPress-1>", self.on_button_press)
        self.canvas.bind("<B1-Motion>", self.on_move_press)
        self.canvas.bind("<ButtonRelease-1>", self.on_button_release)
        self.root.bind("<Escape>", lambda e: self.root.destroy())

        self.root.mainloop()

    def on_button_press(self, event):
        self.start_x = event.x
        self.start_y = event.y
        self.rect = self.canvas.create_rectangle(self.start_x, self.start_y, 1, 1, outline='red', width=2)

    def on_move_press(self, event):
        cur_x, cur_y = (event.x, event.y)
        self.canvas.coords(self.rect, self.start_x, self.start_y, cur_x, cur_y)

    def on_button_release(self, event):
        end_x, end_y = (event.x, event.y)
        self.root.withdraw() # 캡쳐 순간 창 숨기기

        x1 = min(self.start_x, end_x)
        y1 = min(self.start_y, end_y)
        x2 = max(self.start_x, end_x)
        y2 = max(self.start_y, end_y)

        if x2 - x1 > 0 and y2 - y1 > 0:
            self.process_image(x1, y1, x2, y2)
        
        self.root.destroy()

    def process_image(self, x1, y1, x2, y2):
        # 1. 이미지 캡쳐
        img = ImageGrab.grab(bbox=(x1, y1, x2, y2))
        
        # 2. 파일로 저장 (초경량 WebP)
        filename = datetime.now().strftime("crop_%Y%m%d_%H%M%S.webp")
        img.save(filename, 'WEBP', quality=50, method=6)
        print(f"파일 저장 완료: {filename}")

        # 3. 클립보드로 전송
        self.send_to_clipboard(img)
        print("클립보드 복사 완료! (Ctrl+V 가능)")

    def send_to_clipboard(self, image):
        # 이미지를 윈도우 클립보드 포맷(DIB)으로 변환
        output = BytesIO()
        image.convert("RGB").save(output, "BMP")
        data = output.getvalue()[14:] # BMP 헤더 14바이트를 제거해야 DIB 포맷이 됨
        output.close()

        # 클립보드 열기 및 데이터 넣기
        win32clipboard.OpenClipboard()
        win32clipboard.EmptyClipboard()
        win32clipboard.SetClipboardData(win32clipboard.CF_DIB, data)
        win32clipboard.CloseClipboard()

if __name__ == "__main__":
    app = ScreenCaptureTool()
