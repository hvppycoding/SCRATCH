import tkinter as tk
from PIL import ImageGrab, ImageEnhance, ImageTk # ImageTk, ImageEnhance 추가
from datetime import datetime
import subprocess
from io import BytesIO
import os

class ScreenCaptureTool:
    def __init__(self):
        self.root = tk.Tk()
        
        # 1. 윈도우 설정
        self.root.attributes('-fullscreen', True)
        self.root.attributes('-topmost', True)
        self.root.config(cursor="cross")

        # 중요: 투명도(alpha) 설정 제거! (RHEL/MATE 호환성 문제 원인)
        # 대신 아래에서 '스크린샷 배경' 방식을 사용합니다.

        # 2. 시작하자마자 전체 화면 캡쳐 (배경으로 쓰기 위함)
        try:
            self.original_image = ImageGrab.grab()
        except Exception as e:
            print(f"초기 화면 캡쳐 실패: {e}")
            self.root.destroy()
            return

        # 3. 배경 이미지를 어둡게 만들기 (사용자에게 캡쳐 모드임을 알림)
        # 밝기를 50%로 줄임
        enhancer = ImageEnhance.Brightness(self.original_image)
        self.dark_image = enhancer.enhance(0.5) 
        
        # Tkinter에서 이미지를 쓰려면 PhotoImage로 변환해야 함
        self.tk_image = ImageTk.PhotoImage(self.dark_image)

        # 4. 캔버스에 어두운 배경 깔기
        self.canvas = tk.Canvas(self.root, cursor="cross", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        # (0,0) 좌표에 이미지 배치
        self.canvas.create_image(0, 0, image=self.tk_image, anchor="nw")

        # 변수 초기화
        self.start_x = None
        self.start_y = None
        self.rect = None

        # 이벤트 바인딩
        self.canvas.bind("<ButtonPress-1>", self.on_button_press)
        self.canvas.bind("<B1-Motion>", self.on_move_press)
        self.canvas.bind("<ButtonRelease-1>", self.on_button_release)
        self.root.bind("<Escape>", lambda e: self.root.destroy())

        self.root.mainloop()

    def on_button_press(self, event):
        self.start_x = event.x
        self.start_y = event.y
        # 빨간색 사각형 그리기
        self.rect = self.canvas.create_rectangle(self.start_x, self.start_y, 1, 1, outline='red', width=2)

    def on_move_press(self, event):
        cur_x, cur_y = (event.x, event.y)
        self.canvas.coords(self.rect, self.start_x, self.start_y, cur_x, cur_y)

    def on_button_release(self, event):
        end_x, end_y = (event.x, event.y)
        
        # 좌표 계산
        x1 = min(self.start_x, end_x)
        y1 = min(self.start_y, end_y)
        x2 = max(self.start_x, end_x)
        y2 = max(self.start_y, end_y)

        # 윈도우 닫기
        self.root.destroy()

        # 유효한 영역이면 저장 프로세스 진행
        if x2 - x1 > 0 and y2 - y1 > 0:
            # 원본 이미지(self.original_image)에서 잘라냄
            # 다시 grab할 필요 없이 아까 찍어둔 원본에서 자르면 됨 (더 빠르고 정확함)
            crop_img = self.original_image.crop((x1, y1, x2, y2))
            self.process_image(crop_img)

    def process_image(self, img):
        # 1. WebP 파일 저장
        filename = datetime.now().strftime("crop_%Y%m%d_%H%M%S.webp")
        img.save(filename, 'WEBP', quality=50, method=6)
        print(f"파일 저장 완료: {filename}")

        # 2. 리눅스 클립보드 전송
        self.send_to_clipboard_linux(img)

    def send_to_clipboard_linux(self, image):
        output = BytesIO()
        image.save(output, format='PNG')
        data = output.getvalue()
        output.close()

        try:
            p = subprocess.Popen(
                ['xclip', '-selection', 'clipboard', '-t', 'image/png', '-i'], 
                stdin=subprocess.PIPE
            )
            p.communicate(input=data)
            print("클립보드 복사 완료!")
        except FileNotFoundError:
            print("오류: xclip이 설치되지 않았습니다.")

if __name__ == "__main__":
    if not os.environ.get('DISPLAY'):
        os.environ['DISPLAY'] = ':0'
    app = ScreenCaptureTool()
