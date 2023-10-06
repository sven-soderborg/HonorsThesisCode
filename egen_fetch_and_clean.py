import os
import pandas as pd
import numpy as np
import requests
import openpyxl


def get_report() -> pd.DataFrame:
    """
    Download the EIA annual generation by state report if it's not
    already on your local machine.
    return it as a dataframe
    """
    if not os.path.isfile("Data/EIA/annual_generation_raw.xlsx"):
        # Get the annual generation by state EIA report
        link = "https://www.eia.gov/electricity/data/state/annual_generation_state.xls"
        response = requests.get(link)

        # Save the excel file
        with open("Data/EIA/annual_generation_raw.xlsx", "wb") as f:
            f.write(response.content)

    return pd.read_excel("Data/EIA/annual_generation_raw.xlsx", skiprows=1) # first row is a note

def rename_vars(df: pd.DataFrame) -> pd.DataFrame:
    """ Make the var names easier to work with """
    # Rename the variables
    df = df.rename(columns={
        "STATE": "state",
        "TYPE OF PRODUCER": "producerType",
        "ENERGY SOURCE": "energySource",
        "YEAR": "year",
        "GENERATION (Megawatthours)": "genMWH" # I know it's MWh but that's so annoying for a var name
    })

    return df

def clean_strings(df: pd.DataFrame) -> pd.DataFrame:
    """ Just setting everything to lowercase and removing lead/trail whitespace """
    for col in df.columns:
        if df[col].dtype == "object":
            df[col] = df[col].str.lower().str.strip()

    return df

def clean_producer_types(df: pd.DataFrame) -> pd.DataFrame:
    """
    The producerType column's values are very wordy, which 
    will make code harder to read. This function will shorten 
    the various names of producer types.
    """
    # New names
    name_map = {'total electric power industry': 'total', 
                'electric generators, electric utilities': 'utilities',
                'electric generators, independent power producers': 'independent',
                'combined heat and power, industrial power': 'industrial_chp',
                'combined heat and power, commercial power': 'commercial_chp',
                'combined heat and power, electric power': 'electric_chp'}
    
    # Replace the names
    df['producerType'] = df['producerType'].replace(name_map)

    return df

def drop_totals(df: pd.DataFrame) -> pd.DataFrame:
    """ 
    Drop the rows that have the total generation for each state. 
    It screws up the groupby operations
    """
    df = df[df['energySource'] != 'total']

    return df

if __name__ == "__main__":
    df = get_report()
    df = rename_vars(df)
    df = clean_strings(df)
    df = clean_producer_types(df)
    df = drop_totals(df)
    old_shape = df.shape
    df.dropna(inplace=True) 
    if df.shape != old_shape:
        print("Dropped some rows with missing values")

    # Save cleaned data
    df.to_csv("Data/EIA/annual_generation_clean.csv", index=False)