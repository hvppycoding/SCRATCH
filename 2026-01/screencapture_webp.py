import tkinter as tk
from PIL import ImageGrab
from datetime import datetime
import subprocess  # 리눅스 명령어 실행용
from io import BytesIO
import os

class ScreenCaptureTool:
    def __init__(self):
        self.root = tk.Tk()
        
        # 리눅스(MATE) 호환 전체화면 설정
        self.root.attributes('-fullscreen', True)
        self.root.attributes('-topmost', True)
        
        # 투명도 설정 (컴포지터가 켜져 있어야 작동함. 안 되면 검은 화면이 뜰 수 있음)
        try:
            self.root.attributes('-alpha', 0.3)
        except tk.TclError:
            print("경고: 투명도 설정 실패 (컴포지터 미지원 가능성)")

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
        self.root.withdraw()

        x1 = min(self.start_x, end_x)
        y1 = min(self.start_y, end_y)
        x2 = max(self.start_x, end_x)
        y2 = max(self.start_y, end_y)

        if x2 - x1 > 0 and y2 - y1 > 0:
            self.process_image(x1, y1, x2, y2)
        
        self.root.destroy()

    def process_image(self, x1, y1, x2, y2):
        # 1. 캡쳐 (Linux X11 환경에서는 xdisplay 매개변수가 필요할 수 있으나 보통 자동 감지됨)
        try:
            img = ImageGrab.grab(bbox=(x1, y1, x2, y2))
        except Exception as e:
            print(f"캡쳐 실패 (X11 설정 확인 필요): {e}")
            return

        # 2. WebP 파일 저장
        filename = datetime.now().strftime("crop_%Y%m%d_%H%M%S.webp")
        img.save(filename, 'WEBP', quality=50, method=6)
        print(f"파일 저장 완료: {filename}")

        # 3. 리눅스 클립보드 전송 (xclip 사용)
        self.send_to_clipboard_linux(img)

    def send_to_clipboard_linux(self, image):
        # 이미지를 메모리 버퍼에 PNG로 저장 (xclip은 PNG를 선호함)
        output = BytesIO()
        image.save(output, format='PNG')
        data = output.getvalue()
        output.close()

        try:
            # xclip 프로세스를 실행하여 클립보드에 데이터 밀어넣기
            # -selection clipboard: Ctrl+V용 클립보드 지정
            # -t image/png: MIME 타입 지정
            p = subprocess.Popen(
                ['xclip', '-selection', 'clipboard', '-t', 'image/png', '-i'], 
                stdin=subprocess.PIPE
            )
            p.communicate(input=data)
            print("클립보드 복사 완료! (xclip)")
        except FileNotFoundError:
            print("오류: 'xclip' 명령어를 찾을 수 없습니다. 'sudo dnf install xclip'을 실행해주세요.")

if __name__ == "__main__":
    # Display 환경변수가 없는 경우 대비 (SSH 터미널 실행 등)
    if not os.environ.get('DISPLAY'):
        os.environ['DISPLAY'] = ':0'
        
    app = ScreenCaptureTool()
