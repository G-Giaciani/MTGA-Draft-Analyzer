import tkinter as tk
from gui.app import MTGSynergyApp

def main():
    root = tk.Tk()
    app = MTGSynergyApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()