from phase_retriever import PhaseRetrieverGUI
import platform
import tkinter as tk
import tkinter.ttk as ttk

if __name__ == "__main__":
    root = tk.Tk()
    style = ttk.Style()
    if platform.system() == "Linux":
        style.theme_use("clam")
    bg = style.lookup("TFrame", "background")
    root["background"] = bg
    gui = PhaseRetrieverGUI(root, bg)
    root.mainloop()
