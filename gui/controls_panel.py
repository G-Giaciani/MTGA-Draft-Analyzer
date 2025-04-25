import tkinter as tk
from tkinter import ttk, filedialog
import threading
import time
import random

from data.loader import DataLoader
from api.scryfall import ScryfallAPI
from analysis.synergy import calculate_synergy

class ControlsPanel:
    def __init__(self, parent, state):
        self.parent = parent
        self.state = state
        self.status_var = None
        
        self.panel = ttk.LabelFrame(parent, text="Controls")
        self.panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=False, padx=5, pady=5)
        
        self.data_loader = DataLoader()
        self.api = ScryfallAPI()
        
        self.create_dataset_frame()
        self.create_set_frame()
        self.create_synergy_frame()
        # self.create_cards_frame()
    
    def create_dataset_frame(self):
        dataset_frame = ttk.LabelFrame(self.panel, text="Dataset")
        dataset_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(dataset_frame, text="Load CSV File", command=self.load_csv).pack(fill=tk.X, padx=5, pady=5)
        
        self.chunk_size_var = tk.StringVar(value="1000")
        ttk.Label(dataset_frame, text="Chunk Size:").pack(anchor=tk.W, padx=5)
        ttk.Entry(dataset_frame, textvariable=self.chunk_size_var).pack(fill=tk.X, padx=5, pady=2)
        
        self.max_chunks_var = tk.StringVar(value="200")
        ttk.Label(dataset_frame, text="Max Chunks:").pack(anchor=tk.W, padx=5)
        ttk.Entry(dataset_frame, textvariable=self.max_chunks_var).pack(fill=tk.X, padx=5, pady=2)
        
        self.dataset_status = ttk.Label(dataset_frame, text="Status: No dataset loaded")
        self.dataset_status.pack(fill=tk.X, padx=5, pady=5)
    
    def create_set_frame(self):
        set_frame = ttk.LabelFrame(self.panel, text="Card Set")
        set_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.set_var = tk.StringVar(value=self.state["set_codes"][0])
        ttk.Label(set_frame, text="Set Code:").pack(anchor=tk.W, padx=5)
        ttk.Combobox(set_frame, textvariable=self.set_var, values=self.state["set_codes"]).pack(fill=tk.X, padx=5, pady=2)
        
        ttk.Button(set_frame, text="Load Cards", command=self.load_cards).pack(fill=tk.X, padx=5, pady=5)
    
    def create_synergy_frame(self):
        synergy_frame = ttk.LabelFrame(self.panel, text="Synergy Analysis")
        synergy_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(synergy_frame, text="Synergy Card:").pack(anchor=tk.W, padx=5)
        self.synergy_combo = ttk.Combobox(synergy_frame, state="readonly")
        self.synergy_combo.pack(fill=tk.X, padx=5, pady=2)
        
        ttk.Label(synergy_frame, text="Min Sample Size:").pack(anchor=tk.W, padx=5)
        self.min_samples_var = tk.StringVar(value=str(self.state["min_samples"]))
        ttk.Entry(synergy_frame, textvariable=self.min_samples_var).pack(fill=tk.X, padx=5, pady=2)
        
        ttk.Button(synergy_frame, text="Calculate Synergy", command=self.calculate_synergy).pack(fill=tk.X, padx=5, pady=5)
    
    # def create_cards_frame(self):
    #     cards_frame = ttk.LabelFrame(self.panel, text="Selected Cards")
    #     cards_frame.pack(fill=tk.X, padx=5, pady=5)
        
    #     ttk.Button(cards_frame, text="Add Random Cards", command=self.add_random_cards).pack(fill=tk.X, padx=5, pady=5)
        
    #     self.cards_listbox = tk.Listbox(cards_frame, height=10)
    #     self.cards_listbox.pack(fill=tk.X, padx=5, pady=5)
        
    #     ttk.Button(cards_frame, text="Clear Selected", command=self.clear_selected).pack(fill=tk.X, padx=5, pady=5)
    
    def update_status(self, message):
        if self.status_var:
            self.status_var.set(message)
    
    def load_csv(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
        if not file_path:
            return
            
        self.update_status("Loading CSV file...")
        
        def load_data():
            try:
                start_time = time.time()
                
                chunk_size = int(self.chunk_size_var.get())
                max_chunks = int(self.max_chunks_var.get())
                
                self.state["dataset"] = self.data_loader.load_csv(file_path, chunk_size, max_chunks)
                
                end_time = time.time()
                loading_time = end_time - start_time
                
                self.panel.after(0, lambda: self.update_after_csv_load(loading_time))
            except Exception as e:
                self.panel.after(0, lambda: self.update_status(f"Error loading CSV: {str(e)}"))
        
        threading.Thread(target=load_data, daemon=True).start()
    
    def update_after_csv_load(self, loading_time):
        if self.state["dataset"] is not None:
            self.dataset_status.config(text=f"Status: Loaded {len(self.state['dataset'])} rows in {loading_time:.2f} seconds")
            self.update_status("CSV file loaded successfully")
            
            card_columns = [col.replace("opening_hand_", "") for col in self.state["dataset"].columns if col.startswith("opening_hand_")]
            self.synergy_combo['values'] = sorted(card_columns)
            if card_columns:
                self.synergy_combo.current(0)
        else:
            self.update_status("Failed to load CSV file")
    
    def load_cards(self):
        set_code = self.set_var.get()
        
        self.update_status(f"Loading cards for set {set_code}...")
        
        def fetch_cards():
            try:
                cards = self.api.get_cards_by_set(set_code)
                    
                self.state["cards_dict"][set_code] = cards
                
                self.panel.after(0, lambda: self.update_after_cards_load(set_code, len(cards)))
            except Exception as e:
                self.panel.after(0, lambda: self.update_status(f"Error loading cards: {str(e)}"))
        
        threading.Thread(target=fetch_cards, daemon=True).start()
    
    def update_after_cards_load(self, set_code, card_count):
        self.update_status(f"Loaded {card_count} cards for set {set_code}")
        
        if set_code in self.state["cards_dict"] and self.state["cards_dict"][set_code]:
            self.synergy_combo['values'] = sorted(self.state["cards_dict"][set_code])
            self.synergy_combo.current(0)
    
    def calculate_synergy(self):
        if self.state["dataset"] is None:
            self.update_status("Error: No dataset loaded")
            return
            
        self.state["synergy_card"] = self.synergy_combo.get()
        if not self.state["synergy_card"]:
            self.update_status("Error: No synergy card selected")
            return
            
        try:
            self.state["min_samples"] = int(self.min_samples_var.get())
        except ValueError:
            self.update_status("Error: Invalid minimum sample size")
            return
            
        set_code = self.set_var.get()
        if set_code not in self.state["cards_dict"] or not self.state["cards_dict"][set_code]:
            self.update_status(f"Error: No cards loaded for set {set_code}")
            return
            
        cards = self.state["cards_dict"][set_code]
        
        self.update_status(f"Calculating synergy with {self.state['synergy_card']}...")
        
        def calculate():
            try:
                start_time = time.time()
                
                self.state["plot_dataframe"] = calculate_synergy(
                    self.state["dataset"], 
                    cards, 
                    self.state["synergy_card"], 
                    self.state["min_samples"]
                )
                
                end_time = time.time()
                calc_time = end_time - start_time
                
                self.panel.event_generate("<<SynergyCalculated>>", when="tail", data=str(calc_time))
                self.panel.after(0, lambda: self.update_status(f"Synergy calculated in {calc_time:.2f} seconds"))
            except Exception as e:
                self.panel.after(0, lambda: self.update_status(f"Error calculating synergy: {str(e)}"))
        
        threading.Thread(target=calculate, daemon=True).start()
    
    # def add_random_cards(self):
    #     if self.state["plot_dataframe"] is None or self.state["plot_dataframe"].empty:
    #         self.update_status("Error: Calculate synergy first")
    #         return
            
    #     self.clear_selected()
        
    #     card_indices = self.state["plot_dataframe"].index.tolist()
    #     num_to_select = min(15, len(card_indices))
        
    #     if num_to_select == 0:
    #         self.update_status("No cards available to select")
    #         return
            
    #     selected_indices = random.sample(card_indices, num_to_select)
        
    #     for card in selected_indices:
    #         self.state["selected_cards"].append(card)
    #         self.cards_listbox.insert(tk.END, card)
        
    #     self.panel.event_generate("<<SelectedCardsChanged>>")
    #     self.update_status(f"Added {num_to_select} random cards")
    
    # def clear_selected(self):
    #     self.state["selected_cards"] = []
    #     self.cards_listbox.delete(0, tk.END)
        
    #     self.panel.event_generate("<<SelectedCardsChanged>>")
    #     self.update_status("Cleared selected cards")