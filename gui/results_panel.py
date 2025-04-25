import tkinter as tk
from tkinter import ttk, scrolledtext
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import mplcursors

class ResultsPanel:
    def __init__(self, parent, state):
        self.parent = parent
        self.state = state
        self.status_var = None
        self.scatter_point_to_card = {}
        
        self.panel = ttk.LabelFrame(parent, text="Results")
        self.panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.create_widgets()
        self.parent.bind("<<SelectedCardsChanged>>", self.update_plot)
        
    def create_widgets(self):
        self.results_text = scrolledtext.ScrolledText(self.panel, height=10)
        self.results_text.pack(fill=tk.X, padx=5, pady=5)
        
        self.plot_frame = ttk.Frame(self.panel)
        self.plot_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    def update_status(self, message):
        if self.status_var:
            self.status_var.set(message)
    
    def update_results(self, event=None):
        
        self.results_text.delete(1.0, tk.END)
        self.results_text.insert(tk.END, f"Synergy Card: {self.state['synergy_card']}\n")
        self.results_text.insert(tk.END, f"Cards analyzed: {len(self.state['plot_dataframe']) if self.state['plot_dataframe'] is not None else 0}\n")
        
        self.create_plot()
    
    def create_plot(self):
        if self.state["plot_dataframe"] is None or self.state["plot_dataframe"].empty:
            self.update_status("No data to plot")
            return
            
        for widget in self.plot_frame.winfo_children():
            widget.destroy()
            
        fig = plt.Figure(figsize=(8, 6), dpi=100)
        ax = fig.add_subplot(111)
        
        min_wr = min(self.state["plot_dataframe"]['GIH_wr'].min(), self.state["plot_dataframe"]['GIH_wr_synergy'].min())
        max_wr = max(self.state["plot_dataframe"]['GIH_wr'].max(), self.state["plot_dataframe"]['GIH_wr_synergy'].max())
        ax.plot([min_wr, max_wr], [min_wr, max_wr], 'k--', alpha=0.3, label='Same Win Rate')
        
        self.scatter_point_to_card = {}
        
        x_data = self.state["plot_dataframe"]['GIH_wr']
        y_data = self.state["plot_dataframe"]['GIH_wr_synergy']
        sizes = np.sqrt(self.state["plot_dataframe"]['n_GIH_synergy']) * 2
        colors = self.state["plot_dataframe"]['GIH_wr_synergy'] - self.state["plot_dataframe"]['GIH_wr']
        
        scatter = ax.scatter(x_data, y_data, s=sizes, alpha=0.7, c=colors, cmap='coolwarm')
        
        for i, card_name in enumerate(self.state["plot_dataframe"].index):
            self.scatter_point_to_card[i] = card_name
        
        for card in self.state["selected_cards"]:
                
                wr_general = self.state["plot_dataframe"].loc[card, 'GIH_wr']
                wr_synergy = self.state["plot_dataframe"].loc[card, 'GIH_wr_synergy']
                diff = wr_synergy - wr_general
                num_games = self.state["plot_dataframe"].loc[card, 'n_GIH_synergy']
                
                self.results_text.insert(tk.END, f"\n{card}:\n")
                self.results_text.insert(tk.END, f"  Winrate: {wr_general:.2%}\n")
                self.results_text.insert(tk.END, f"  Winrate with {self.state['synergy_card']}: {wr_synergy:.2%}\n")
                self.results_text.insert(tk.END, f"  Difference: {diff:+.2%}\n")
                self.results_text.insert(tk.END, f"  Samples: {num_games}\n")
        
        ax.set_title(f'Card performance with and without "{self.state["synergy_card"]}"', fontsize=14)
        ax.set_xlabel('Original Win Rate (GIH_wr)', fontsize=12)
        ax.set_ylabel(f'Win Rate with {self.state["synergy_card"]} (GIH_wr_synergy)', fontsize=12)
        
        cbar = fig.colorbar(scatter, ax=ax)
        cbar.set_label('Difference in Win Rate (Synergy - Original)')
        
        ax.grid(True, alpha=0.3)
        
        sizes = [min(self.state["plot_dataframe"]['n_GIH_synergy']), 
                 self.state["plot_dataframe"]['n_GIH_synergy'].median(), 
                 max(self.state["plot_dataframe"]['n_GIH_synergy'])]
        labels = [f'n={int(s)}' for s in sizes]
        
        legend_elements = []
        for i, size in enumerate(sizes):
            legend_elements.append(plt.Line2D([0], [0], marker='o', color='w', 
                                   markerfacecolor='gray', markersize=np.sqrt(size)*0.2,
                                   label=labels[i]))
        
        ax.legend(handles=legend_elements, title='Sample Size', loc='lower right')
        
        canvas = FigureCanvasTkAgg(fig, master=self.plot_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        mplcursor_obj = mplcursors.cursor(scatter, hover=True)
        
        @mplcursor_obj.connect("add")
        def on_add(sel):
            try:
                point_idx = sel.index
                
                card_name = self.state["plot_dataframe"].index[point_idx]
                
                wr = self.state["plot_dataframe"].loc[card_name, 'GIH_wr']
                wr_synergy = self.state["plot_dataframe"].loc[card_name, 'GIH_wr_synergy']
                diff = wr_synergy - wr
                samples = self.state["plot_dataframe"].loc[card_name, 'n_GIH_synergy']
                
                text = f"{card_name}\nWR: {wr:.2%}\nWR w/ {self.state['synergy_card']}: {wr_synergy:.2%}\nDiff: {diff:+.2%}\nSamples: {samples}"
                sel.annotation.set_text(text)
                sel.annotation.get_bbox_patch().set(fc="white", alpha=0.8)
            except Exception as e:
                sel.annotation.set_text(f"Point {sel.index}")
    
    def update_plot(self, event=None):
        if self.state["plot_dataframe"] is not None and not self.state["plot_dataframe"].empty:
            self.create_plot()