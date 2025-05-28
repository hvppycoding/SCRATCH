import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk, GLib

import random

WORDS = ["🍎 Apple", "🍊 Orange", "🍌 Banana", "🍇 Grape", "🍉 Watermelon"]

class TextChanger(Gtk.Window):
    def __init__(self):
        super().__init__(title="Updater")

        # 창 옵션
        self.set_decorated(False)                # 창 테두리 제거
        self.set_keep_above(True)                # 항상 위
        self.set_skip_taskbar_hint(True)         # 작업표시줄 숨김
        self.set_resizable(False)
        self.set_accept_focus(False)

        # 투명도 설정
        self.set_app_paintable(True)
        screen = self.get_screen()
        visual = screen.get_rgba_visual()
        if visual and self.is_composited():
            self.set_visual(visual)

        # 스타일: 배경 반투명 흰색, 글자는 진한 회색
        css = b"""
        * {
            background-color: rgba(255, 255, 255, 0.5);
            color: #222;
            font-size: 16pt;
            padding: 4px;
        }
        """
        style_provider = Gtk.CssProvider()
        style_provider.load_from_data(css)
        Gtk.StyleContext.add_provider_for_screen(
            screen,
            style_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

        # 텍스트 라벨 추가
        self.label = Gtk.Label(label="")
        self.add(self.label)

        self.set_default_size(150, 30)
        self.set_position(Gtk.WindowPosition.MOUSE)  # 초기 위치 설정용

        self.update_text()
        GLib.timeout_add_seconds(1800, self.update_text)  # 30분마다 실행

        # 창이 뜬 후 위치를 우상단으로 이동
        GLib.idle_add(self.move_to_top_right)

        # 마우스 이동 방지용: 버튼 이벤트 캡처
        self.connect("button-press-event", self.disable_mouse_drag)
        self.connect("motion-notify-event", self.disable_mouse_drag)
        self.set_events(Gdk.EventMask.BUTTON_PRESS_MASK | Gdk.EventMask.POINTER_MOTION_MASK)

    def update_text(self):
        new_text = random.choice(WORDS)
        self.label.set_text(new_text)
        print(f"Updated: {new_text}")
        return True

    def move_to_top_right(self):
        screen = self.get_screen()
        monitor = screen.get_monitor_geometry(screen.get_primary_monitor())
        window_width, window_height = self.get_size()
        margin = 10
        x = monitor.x + monitor.width - window_width - margin
        y = monitor.y + margin
        self.move(x, y)

    def disable_mouse_drag(self, widget, event):
        return True  # 이벤트 무시

win = TextChanger()
win.connect("destroy", Gtk.main_quit)
win.show_all()
Gtk.main()
