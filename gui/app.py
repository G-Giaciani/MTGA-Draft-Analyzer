import tkinter as tk
from tkinter import ttk
import os

from gui.controls_panel import ControlsPanel
from gui.results_panel import ResultsPanel
import config

icon_path = os.path.join(os.path.dirname(__file__), '..', 'favicon.ico')

class MTGSynergyApp:
    def __init__(self, root):
        self.root = root
        self.root.title("MTG Synergy Analyzer")
        self.root.iconbitmap(icon_path)
        self.root.geometry(f"{config.WINDOW_WIDTH}x{config.WINDOW_HEIGHT}")
        self.root.configure(bg="#f0f0f0")
        
        self.state = {
            "dataset": None,
            "set_codes": config.DEFAULT_SET_CODES.copy(),
            "cards_dict": {},
            "synergy_card": None,
            "min_samples": config.DEFAULT_MIN_SAMPLES,
            "plot_dataframe": None,
            "selected_cards": []
        }
        
        self.create_widgets()
        
    def create_widgets(self):
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.controls_panel = ControlsPanel(main_frame, self.state)
        self.results_panel = ResultsPanel(main_frame, self.state)
        
        self.status_var = tk.StringVar(value="Ready")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.controls_panel.status_var = self.status_var
        self.results_panel.status_var = self.status_var
        
        self.root.bind("<<SynergyCalculated>>", self.results_panel.update_results)