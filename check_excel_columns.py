#!/usr/bin/env python
import pandas as pd

try:
    df = pd.read_excel('SALES USER LIST.xlsx')
    print("Excel file columns:")
    for i, col in enumerate(df.columns):
        print(f"{i+1}. {col}")
    
    print(f"\nFirst few rows:")
    print(df.head())
    
except Exception as e:
    print(f"Error: {e}")