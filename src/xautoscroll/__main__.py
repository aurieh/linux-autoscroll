import importlib.resources
import sys

from PyQt5.QtWidgets import QApplication

from xautoscroll import AutoScroll


def main(argv=None):
    app = QApplication(argv or sys.argv)
    app.setQuitOnLastWindowClosed(False)
    icon_rpath = importlib.resources.files("xautoscroll").joinpath("icon.svg")
    with importlib.resources.as_file(icon_rpath) as icon_path:
        autoscroll = AutoScroll(str(icon_path))
        autoscroll.start()
        return app.exec()


if __name__ == "__main__":
    sys.exit(main())
