import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk, GLib

import random

WORDS = ["🍎 Apple", "🍊 Orange", "🍌 Banana", "🍇 Grape", "🍉 Watermelon"]
CORNER_POSITIONS = ["top-left", "top-right", "bottom-left", "bottom-right"]

class TextChanger(Gtk.Window):
    def __init__(self):
        super().__init__(title="Updater")

        self.set_decorated(False)
        self.set_keep_above(True)
        self.set_skip_taskbar_hint(True)
        self.set_skip_pager_hint(True)
        self.set_resizable(False)
        self.set_accept_focus(False)
        self.set_app_paintable(True)

        screen = self.get_screen()
        visual = screen.get_rgba_visual()
        if visual and self.is_composited():
            self.set_visual(visual)

        css = b"""
        * {
            background-color: #ffffff;
            color: #444;
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

        self.label = Gtk.Label(label="")
        self.add(self.label)
        self.set_default_size(150, 30)
        self.update_text()

        self.current_corner = "top-right"
        GLib.idle_add(self.move_to_corner)

        # 30분마다 텍스트 갱신
        GLib.timeout_add_seconds(1800, self.update_text)

        # 마우스 감지 반복 (0.2초 간격)
        GLib.timeout_add(200, self.check_mouse_near)

    def update_text(self):
        new_text = random.choice(WORDS)
        self.label.set_text(new_text)
        return True

    def move_to_corner(self):
        screen = self.get_screen()
        monitor = screen.get_monitor_geometry(screen.get_primary_monitor())
        w, h = self.get_size()
        margin = 10

        corners = {
            "top-left": (monitor.x + margin, monitor.y + margin),
            "top-right": (monitor.x + monitor.width - w - margin, monitor.y + margin),
            "bottom-left": (monitor.x + margin, monitor.y + monitor.height - h - margin),
            "bottom-right": (monitor.x + monitor.width - w - margin, monitor.y + monitor.height - h - margin),
        }

        x, y = corners[self.current_corner]
        self.move(x, y)
        return False

    def check_mouse_near(self):
        display = Gdk.Display.get_default()
        seat = display.get_default_seat()
        pointer = seat.get_pointer()
        screen, mx, my = pointer.get_position()

        win_x, win_y = self.get_position()
        win_w, win_h = self.get_size()

        margin = 50  # 마우스가 이 거리보다 가까우면 튐

        near = (
            win_x - margin < mx < win_x + win_w + margin and
            win_y - margin < my < win_y + win_h + margin
        )

        if near:
            # 다음 코너로 튀기
            available = [c for c in CORNER_POSITIONS if c != self.current_corner]
            self.current_corner = random.choice(available)
            self.move_to_corner()

        return True  # 반복 계속

win = TextChanger()
win.connect("destroy", Gtk.main_quit)
win.show_all()
Gtk.main()
