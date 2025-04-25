import pandas as pd
import numpy as np

def calculate_win_rate_difference(df, col1, col2):
    return df[col2] - df[col1]

def get_top_synergies(df, count=10):
    df_sorted = df.sort_values(by=['GIH_wr_synergy'], ascending=False)
    return df_sorted.head(count)

def get_top_differences(df, count=10):
    df_sorted = df.sort_values(by=lambda x: df['GIH_wr_synergy'] - df['GIH_wr'], ascending=False)
    return df_sorted.head(count)