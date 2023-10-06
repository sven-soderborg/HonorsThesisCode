import os
import re
import numpy as np
import pandas as pd
import urllib.request, json
from dateutil.parser import parse


def get_raw_data() -> pd.DataFrame:
    """
    Get raw json data from DSIRE API if not already on local machine.
    Otherwise, open the raw json from local machine.
    Return data as a pandas dataframe
    """
    if not os.path.isfile("Data/DSIRE/raw_dsire_data_off.json"):
        with urllib.request.urlopen("http://programs.dsireusa.org/api/v1/getprograms/json") as url:
            data = json.load(url)

        # Save raw json just in case you need to use it later
        with open("Data/DSIRE/raw_dsire_data_off.json", "w") as f:
            json.dump(data, f)
    else:
        with open("Data/DSIRE/raw_dsire_data_off.json", "r") as f:
            data = json.load(f)

    data = data["data"]
    return pd.DataFrame(data)


def drop_superfluous_cols(data: pd.DataFrame) -> pd.DataFrame:
    """
    Drop columns that are not needed for analysis
    """
    cols_to_drop = ['LastUpdate', 'WebsiteUrl', 'Administrator', 'FundingSource', 'Code',
                    'Budget', 'Counties', 'Cities', 'ZipCodes', 'Contacts', 'Utilities',
                    'ProgramParameters', 'Details', 'Summary', 'FromSir', 'EndDate']
    return df.drop(cols_to_drop, axis=1)


def extract_years_from_string(s):
    """Extract all 4-digit years from a string."""
    return [int(match) for match in re.findall(r'\b\d{4}\b', s)]


def extract_earliest_year_from_string(s):
    """Extract the earliest 4-digit year from a string, ensuring it's within a reasonable range."""
    years = extract_years_from_string(s)
    
    # Filter years to ensure they are within a reasonable range
    current_year = 2023  # As per the current simulation date
    years = [year for year in years if 1900 <= year <= current_year]
    
    return min(years) if years else None

def find_earliest_enacted_date(data: pd.DataFrame) -> pd.DataFrame:
    """
    Find the earliest enacted date for each program and add it to the dataframe.
    For some this may be the StartDate field, for others it will come from the list
    of dictionaries in th Authorities field. 
    """
    # Find earliest date from Authorities field
    data['Authorities'] = data['Authorities'].astype(str)
    data['EarliestAuthorityDate'] = data['Authorities'].apply(extract_earliest_year_from_string)

    # Change StartDate to just the year and convert to float (can't use int yet because of NaNs )
    data['StartDate'] = data['StartDate'].replace('', np.nan)
    data['StartDate'] = data['StartDate'].str[-4:].astype(float)

    # Find the earliest enacted date
    data['EarliestEnactedYear'] = data[['StartDate', 'EarliestAuthorityDate']].min(axis=1).fillna(0).astype(int)

    # Drop superfluous columns
    data.drop(['StartDate', 'Authorities', 'EarliestAuthorityDate'], axis=1, inplace=True)
    return data


def break_out_categories(data: pd.DataFrame) -> pd.DataFrame:
    """
    Break out the Applicable Technology and Applicable Sectors 
    categories into their own columns with binary values.
    """
    for item in ['Sectors', 'Technologies']:
        # Extract unique `item` categories from list of dictionaries
        unique_cats = set()
        for cats in data[item]:
            for cat in cats:
                if item == 'Sectors':
                    unique_cats.add(f"Sector_{cat['id']}")
                else:
                    unique_cats.add(f"Tech_{cat['categoryId']}")

        # Create new columns for each unique `item` category
        for cat in unique_cats:
            data[cat] = 0

        # Populate new columns with binary values
        for i in range(len(data)):
            for cat in data[item][i]:
                if item == 'Sectors':
                    data.loc[i, f"Sector_{cat['id']}"] = 1
                else:
                    data.loc[i, f"Tech_{cat['categoryId']}"] = 1

    # Drop original `item` columns
    data = data.drop(['Sectors', 'Technologies'], axis=1)

    return data


def change_to_state_abbreviations(data: pd.DataFrame) -> pd.DataFrame:
    """
    The State column has the whole state name, but I want two letter abbreviations.
    """
    # Get state abbreviations and merge datasets
    abbrevs = pd.read_csv("Data/state_abbreviations.csv", usecols=['State', 'abbrev'])
    data = pd.merge(data, abbrevs, on='State', how='left', validate='m:1')
    data = data.drop(['State'], axis=1)
    data = data.rename(columns={'abbrev': 'State'})

    # Move the state column to position 1 for readability
    col = data.pop("State")
    data.insert(1, col.name, col)

    return data


if __name__ == '__main__':
    df = get_raw_data()
    df = drop_superfluous_cols(df)
    df = find_earliest_enacted_date(df)
    df = break_out_categories(df)
    df = change_to_state_abbreviations(df)
    df.to_csv("Data/DSIRE/clean_dsire_data_off.csv", index=False)
