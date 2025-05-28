import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk, GLib
from datetime import datetime
import argparse

# 🧪 테스트용 인자 처리
parser = argparse.ArgumentParser()
parser.add_argument("--test-minute", type=int, default=None, help="강제로 minute 지정")
args = parser.parse_args()
TEST_MINUTE = args.test_minute

class FruitBanner(Gtk.Window):
    def __init__(self):
        super().__init__(title="Fruit Banner")

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

        self.label = Gtk.Label()
        self.label.set_name("fruit-label")
        self.add(self.label)

        self.css_provider = Gtk.CssProvider()
        Gtk.StyleContext.add_provider_for_screen(
            screen,
            self.css_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

        self.set_default_size(200, 40)
        self.current_target = 'left'
        self.is_moving = False

        GLib.idle_add(self.move_to_corner, 'left')
        self.update_fruit()
        if TEST_MINUTE is None:
            GLib.timeout_add_seconds(60, self.update_fruit)
            GLib.timeout_add(200, self.check_mouse_proximity)

    def get_target_position(self, side):
        screen = self.get_screen()
        monitor = screen.get_monitor_geometry(screen.get_primary_monitor())
        win_w, win_h = self.get_size()
        x_center = monitor.x + monitor.width // 2
        y = monitor.y + 5

        if side == 'left':
            x = x_center - monitor.width // 4 - win_w // 2
        else:
            x = x_center + monitor.width // 4 - win_w // 2

        return x, y

    def move_to_corner(self, side):
        x, y = self.get_target_position(side)
        self.move(x, y)
        self.current_target = side
        return False

    def smooth_move_to(self, target_x, target_y, duration_ms=300):
        if self.is_moving:
            return
        self.is_moving = True

        start_x, start_y = self.get_position()
        dx = target_x - start_x
        dy = target_y - start_y
        steps = 20
        interval = duration_ms / steps

        def animate(step=0):
            if step > steps:
                self.move(target_x, target_y)
                self.is_moving = False
                return False
            new_x = int(start_x + dx * step / steps)
            new_y = int(start_y + dy * step / steps)
            self.move(new_x, new_y)
            GLib.timeout_add(int(interval), animate, step + 1)
            return False

        animate()

    def update_fruit(self):
        now = datetime.now()
        minute = TEST_MINUTE if TEST_MINUTE is not None else now.minute

        if 0 <= minute < 30:
            fruit = "🍎 Apple"
            color = "#ff4d4d"
        else:
            fruit = "🍌 Banana"
            color = "#fff166"

        if getattr(self, "current_fruit", None) != fruit:
            self.current_fruit = fruit
            self.blink_then_update(fruit, color)
        return True

    def blink_then_update(self, fruit, color):
        css_blink = f"""
        #fruit-label {{
            background-color: white;
            color: black;
            font-size: 18pt;
            padding: 6px 12px;
            border-radius: 8px;
        }}
        """
        self.label.set_text("")
        self.css_provider.load_from_data(css_blink.encode("utf-8"))

        def apply_fruit():
            self.label.set_text(fruit)
            css_main = f"""
            #fruit-label {{
                background-color: {color};
                color: black;
                font-size: 18pt;
                padding: 6px 12px;
                border-radius: 8px;
                transition: all 300ms ease;
            }}
            """
            self.css_provider.load_from_data(css_main.encode("utf-8"))
            self.shake_window()
            return False

        GLib.timeout_add(200, apply_fruit)

    def shake_window(self):
        if self.is_moving:
            return
        original_x, original_y = self.get_position()
        offsets = [0, 6, -6, 4, -4, 2, -2, 0]
        delay = 30

        def shake_step(i):
            if i >= len(offsets):
                return False
            dx = offsets[i]
            self.move(original_x + dx, original_y)
            GLib.timeout_add(delay, shake_step, i + 1)
            return False

        shake_step(0)

    def check_mouse_proximity(self):
        if self.is_moving:
            return True

        display = Gdk.Display.get_default()
        seat = display.get_default_seat()
        pointer = seat.get_pointer()
        screen, mx, my = pointer.get_position()

        win_x, win_y = self.get_position()
        win_w, win_h = self.get_size()
        margin = 60

        near = (
            win_x - margin < mx < win_x + win_w + margin and
            win_y - margin < my < win_y + win_h + margin
        )

        if near:
            new_target = 'right' if self.current_target == 'left' else 'left'
            x, y = self.get_target_position(new_target)
            self.smooth_move_to(x, y)

        return True

# 실행
win = FruitBanner()
win.connect("destroy", Gtk.main_quit)
win.show_all()
Gtk.main()
