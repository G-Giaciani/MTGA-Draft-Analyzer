import requests
import time
import json
import os
from urllib.parse import quote
import config

class ScryfallAPI:
    def __init__(self):
        self.headers = {
            "User-Agent": "MTGCardFetcher/1.0",
            "Accept": "application/json"
        }
    
    def get_cards_by_set(self, set_code):
        cards = []
        for rarity in config.RARITIES:
            rarity_cards = self.get_cards_by_set_and_rarity(set_code, rarity)
            cards.extend(rarity_cards)
        return cards
    
    def get_cards_by_set_and_rarity(self, set_code, rarity):
        cache_file = f"cache_{set_code}_{rarity}.json"
        if os.path.exists(cache_file):
            with open(cache_file, 'r') as f:
                return json.load(f)
                
        query = f"set:{quote(set_code)} rarity:{quote(rarity)}"
        url = f"https://api.scryfall.com/cards/search?q={quote(query)}"
        
        all_cards = []
        
        try:
            while url:
                time.sleep(0.1)
                
                try:
                    response = requests.get(url, headers=self.headers)
                    response.raise_for_status()
                    
                    data = response.json()
                    all_cards.extend([card["name"] for card in data["data"]])
                    
                    url = data.get("next_page")
                    
                except requests.exceptions.RequestException as e:
                    print(f"Request failed: {e}")
                    print(f"URL: {url}")
                    break
                    
        except KeyboardInterrupt:
            print("\nSearch interrupted by user.")
            
        with open(cache_file, 'w') as f:
            json.dump(all_cards, f)
            
        return all_cards