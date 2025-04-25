import pandas as pd
import time

class DataLoader:
    def __init__(self):
        pass
        
    def load_csv(self, file_path, chunk_size=1000, max_chunks=200):
        chunk_iterator = pd.read_csv(file_path, chunksize=chunk_size)
        
        chunks = []
        for i, chunk in enumerate(chunk_iterator):
            if i >= max_chunks:
                break
            chunks.append(chunk)
        
        return pd.concat(chunks)