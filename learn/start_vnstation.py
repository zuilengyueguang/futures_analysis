import platform
from urllib.parse import urlencode

from vnpy.trader.ui import QtGui, create_qapp
from vnstation.ui.login.login_widget import LoginWidget
from vnstation.ui.main.mainwindow import MainWindow
from vnstation.web_engine import VNPY_URL_BASE, init_web_engine_profile


def get_windows_color_bits():
    import ctypes
    BITSPIXEL = 12
    user32 = ctypes.windll.user32
    gdi32 = ctypes.windll.gdi32
    dc = user32.GetDC(None)
    bits = gdi32.GetDeviceCaps(dc, BITSPIXEL)
    user32.ReleaseDC(dc)
    return bits


class Main():

    def exec(self):
        """"""

        # some system(win7 and win server 2008 R2)
        # has a color depth of 16 which doesn't support alpha mode, making QWebEngineView blank.
        # we must set it by ourselves if alpha mode is not supported by OS.
        if platform.system() == "Windows":
            if get_windows_color_bits() == 16:
                surface = QtGui.QSurfaceFormat.defaultFormat()
                surface.setAlphaBufferSize(8)
                QtGui.QSurfaceFormat.setDefaultFormat(surface)

        app = create_qapp("VN Station")
        init_web_engine_profile(app)

        self.main_window = MainWindow()

        login_widget = LoginWidget()
        login_widget.show()
        login_widget.username_password_accepted.connect(
            self.on_username_password_accepted
        )
        login_widget.wechat_accepted.connect(self.on_wechat_accepted)

        return app.exec_()

    def on_username_password_accepted(self, username, password):
        target_url = f"{VNPY_URL_BASE}/portal/"
        params = {
            "username": username,
            "password": password,
            "next": target_url
        }
        url = f"{VNPY_URL_BASE}/login_api/login_and_next?{urlencode(params)}"
        self.main_window.set_url(url)
        self.main_window.show()

    def on_wechat_accepted(self):
        self.main_window.reload()
        self.main_window.show()


def main():
    return Main().exec()


if __name__ == "__main__":
    exit(main())
