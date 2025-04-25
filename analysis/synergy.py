import pandas as pd

def calculate_synergy(dataset, cards, synergy_card, min_samples=100):
    results = {}

    synergy_condition = (dataset[f"opening_hand_{synergy_card}"] + dataset[f"drawn_{synergy_card}"]) > 0
    
    for card in cards:
        try:
            card_condition = (dataset[f"opening_hand_{card}"] + dataset[f"drawn_{card}"]) > 0

            card_data = dataset[card_condition]
            if len(card_data) == 0:
                continue

            synergy_data = dataset[card_condition & synergy_condition]
            if len(synergy_data) < min_samples:
                continue
                
            results[card] = {
                'GIH_wr': card_data["won"].mean(),
                'GIH_wr_synergy': synergy_data["won"].mean(),
                'n_GIH_synergy': len(synergy_data)
            }
        except KeyError:
            continue
        
    return pd.DataFrame.from_dict(results, orient='index')