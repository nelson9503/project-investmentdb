import tkinter as tk
from tkinter import ttk
from tkinter import font
from pystray import MenuItem as item
import pystray
from PIL import Image
from . import services
import time


class MainUI:

    def __init__(self):
        self.setup_tkui()

    def setup_tkui(self):
        self.ui = tk.Tk()
        self.ui.title("Investment Server")
        self.ui.geometry("500x100")
        self.ui.resizable(0, 0)
        defaultFont = font.nametofont("TkDefaultFont")
        defaultFont.config(size=14)
        frame = ttk.LabelFrame(self.ui, text="Status")
        frame.pack(fill="both")
        self.lbl = ttk.Label(frame, text="Waiting...")
        self.lbl.pack(fill="both")
        self.btn_background = ttk.Button(
            self.ui, text="Run in backgroud", command=self.runInBackground)
        self.btn_background.pack()
        self.ui.after(1000, self.StartServer)
        self.ui.mainloop()

    def setup_tray(self):
        image = Image.open("./icon.png")
        menu = (item("open ui", self.openUI),
                item("close server", self.killApp))
        self.tray = pystray.Icon(
            "Investmentdb Server", image, "Investmentdb", menu)
        self.tray.run()

    def runInBackground(self):
        self.ui.withdraw()
        self.setup_tray()

    def openUI(self):
        self.tray.stop()
        self.ui.deiconify()

    def killApp(self):
        self.tray.stop()
        self.ui.destroy()
    
    def setStatus(self, text: str):
        self.lbl.config(text=text)
        self.ui.update()

    def StartServer(self):
        while True:
            services.startchecking(self)
            services.update_us_symbols(self)
            services.update_price(self)
            for i in range(86400):
                for _ in range(100):
                    self.setStatus("Sleep: next update start in {}s".format(86400-i))
                    time.sleep(0.01)