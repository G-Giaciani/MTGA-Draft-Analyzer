import pandas as pd

class DataProcessor:
    def __init__(self, dataset):
        self.dataset = dataset
    
    def filter_by_set(self, set_code):
        return self.dataset[self.dataset['expansion'] == set_code]
    
    def get_card_columns(self):
        return [col.replace("opening_hand_", "") for col in self.dataset.columns if col.startswith("opening_hand_")]