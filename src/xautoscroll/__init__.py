"""Windows-like autoscroll for X."""

from threading import Event, Thread
from time import sleep

from pynput.mouse import Button, Controller, Listener
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtSvg import QSvgWidget

__version__ = "0.1.0"


class AutoScrollIconSvg(QSvgWidget):
    scroll_mode_entered = pyqtSignal()
    scroll_mode_exited = pyqtSignal()

    def __init__(self, path, size):
        super().__init__(path)
        self.size = size
        self.renderer().setAspectRatioMode(Qt.KeepAspectRatio)
        self.resize(self.size, self.size)
        self.setWindowFlags(Qt.WindowStaysOnTopHint |
                            Qt.FramelessWindowHint |
                            Qt.X11BypassWindowManagerHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.scroll_mode_entered.connect(self.show)
        self.scroll_mode_exited.connect(self.close)

    def show(self):
        x = self.pos[0] - self.size // 2
        y = self.pos[1] - self.size // 2
        self.move(x, y)
        super().show()


class AutoScroll:
    # TODO(auri): make these configurable
    button_start = Button.middle
    button_stop = Button.middle
    delay = 5
    dead_area = 30
    icon_size = 30

    def __init__(self, icon_path):
        self.icon = AutoScrollIconSvg(icon_path, self.icon_size)
        self.mouse = Controller()
        self.scroll_mode = Event()
        self.listener = Listener(on_move=self.on_move, on_click=self.on_click)
        self.looper = Thread(target=self.loop)

    def start(self):
        self.listener.start()
        self.looper.start()

    def on_move(self, x, y):
        if self.scroll_mode.is_set():
            delta = self.icon.pos[1] - y
            if abs(delta) <= self.dead_area:
                self.direction = 0
            elif delta > 0:
                self.direction = 1
            elif delta < 0:
                self.direction = -1
            if abs(delta) <= self.dead_area + self.delay * 2:
                self.interval = 0.5
            else:
                self.interval = self.delay / (abs(delta) - self.dead_area)

    def on_click(self, x, y, button, pressed):
        if (
            button == self.button_start
            and pressed and not self.scroll_mode.is_set()
        ):
            self.icon.pos = (x, y)
            self.direction = 0
            self.interval = 0.5
            self.scroll_mode.set()
            self.icon.scroll_mode_entered.emit()
        elif (
            button == self.button_stop
            and pressed and self.scroll_mode.is_set()
        ):
            self.scroll_mode.clear()
            self.icon.scroll_mode_exited.emit()

    def loop(self):
        while True:
            self.scroll_mode.wait()
            sleep(self.interval)
            self.mouse.scroll(0, self.direction)
