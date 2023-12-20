import base64
import io
import os
import threading
import tkinter as tk

import cv2
import pystray
import win32api
import win32con
import win32gui
from PIL import Image, ImageTk
from pystray import MenuItem, Menu


class Window:

    def __init__(self):
        self.window = tk.Tk()
        self.window.geometry("320x200")

        self.canvas = tk.Canvas(self.window, width=320, height=180)
        self.canvas.place(x=0, y=0)

        self.label_str = tk.StringVar()
        label = tk.Label(self.window, textvariable=self.label_str)
        label.place(x=0, y=180)

        self.top_label_str = tk.StringVar()
        top_label = tk.Label(self.window, textvariable=self.top_label_str)
        top_label.place(x=100, y=180)

        self.capture = None
        self.delay = 15
        self.show = True
        # 修改壁纸样式
        reg_key = win32api.RegOpenKeyEx(win32con.HKEY_CURRENT_USER, "Control Panel\\Desktop", 0, win32con.KEY_SET_VALUE)
        win32api.RegSetValueEx(reg_key, "WallpaperStyle", 0, win32con.REG_SZ, "2")
        win32api.RegSetValueEx(reg_key, "TileWallpaper", 0, win32con.REG_SZ, "0")

    def quit_window(self, icon: pystray.Icon):
        icon.stop()
        self.window.destroy()
        self.show = False

    def show_window(self):
        self.window.deiconify()
        self.show = True

    def on_exit(self):
        self.window.withdraw()

    def set_topmost(self):
        topmost = self.window.attributes("-topmost")
        if topmost:
            self.window.attributes("-topmost", False)
            self.top_label_str.set("")
        else:
            self.show_window()
            self.window.attributes("-topmost", True)
            self.top_label_str.set("已置顶")

    def init_capture(self):
        try:
            self.label_str.set("摄像头加载中")
            self.capture = cv2.VideoCapture(0)
            self.capture.set(3, 1920)
            self.capture.set(4, 1080)
            self.update_canvas()
            self.label_str.set("摄像头加载完成")
        except:
            self.label_str.set("摄像头加载失败")

    def update_canvas(self):
        ret, frame = self.capture.read()
        if ret:
            file_path = os.getcwd() + "/1.png"
            cv2.imwrite(file_path, frame)
            # 设置壁纸
            win32gui.SystemParametersInfo(win32con.SPI_SETDESKWALLPAPER, file_path, win32con.SPIF_SENDWININICHANGE)
            if self.show:
                img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(img)
                img = ImageTk.PhotoImage(img.resize((320, 180)))
                self.canvas.imgtk = img
                self.canvas.create_image(0, 0, anchor=tk.NW, image=img)
        # 重复更新画布
        self.window.after(self.delay, self.update_canvas)

    def start(self):
        # 菜单
        menu = (
            MenuItem('显示', self.show_window, default=True),
            Menu.SEPARATOR,
            MenuItem('置顶', self.set_topmost),
            Menu.SEPARATOR,
            MenuItem('退出', self.quit_window))
        image_bytes = base64.b64decode(
            "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")
        image_data = io.BytesIO(image_bytes)
        image = Image.open(image_data)
        icon = pystray.Icon("icon", image, "图标名称", menu)
        threading.Thread(target=icon.run, daemon=True).start()
        threading.Thread(target=self.init_capture, daemon=True).start()

        # 重新定义点击关闭按钮的处理
        self.window.protocol('WM_DELETE_WINDOW', self.on_exit)
        self.window.title('摄像壁纸')
        self.window.mainloop()


if __name__ == '__main__':
    window = Window()
    window.start()
