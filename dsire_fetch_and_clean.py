import os
import re
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

def date_helper(date_str: str):
    """
    Helper function for find_earliest_enacted_date.
    return date_obj.strftime("%Y/%m/%d")
    """
    if date_str is not None:
        date_str = re.sub('[^0-9/]', '', date_str)
        try:
            return parse(date_str)
        except ValueError:
            if "/" in date_str[:4]: # Means there are two mm/dd/yyyy dates in the string
                # Find the index of the first "/" in the string
                first_slash_index = date_str.find('/')

                # Find the index of the second "/" in the string
                second_slash_index = date_str.find('/', first_slash_index + 1)
                return parse(date_str[:second_slash_index + 5])
            elif len(date_str) == 8: # Means there are two yyyy dates in the string
                return parse(date_str[:4])
            elif len(date_str) == 12: # Means there is a yyyy at the start and mm/dd/yyyy at the end
                return parse(date_str[:4])
            else: # Sometimes there's only so much you can do
                return ""
    else:
        return ""
    
def authorities_date_finder(authorities: list) -> str:
    """
    Helper function for find_earliest_enacted_date from the list
    of Authorities.
    Goes through the list of dictionaries in the Authorities field,
    finds all of the dates in the various fields, and returns the earliest one.
    """
    dates = []
    for auth in authorities:
        if auth["enactedDate"] != "":
            dates.append(date_helper(auth["enactedDate"]))
        if auth["enactedDateDisplay"] != "":
            dates.append(date_helper(auth["enactedDateDisplay"]))
        if auth["enactedText"] != "":
            dates.append(date_helper(auth["enactedText"]))
        if auth["effectiveDate"] != "":
            dates.append(date_helper(auth["effectiveDate"]))
        if auth["effectiveDateDisplay"] != "":
            dates.append(date_helper(auth["effectiveDateDisplay"]))
        if auth["effectiveText"] != "":
            dates.append(date_helper(auth["effectiveText"]))
    
    dates = [x for x in dates if x != ""] # Remove empty strings
    if len(dates) == 0:
        return ""
    else:
        dates.sort()
        return dates[0].strftime("%Y/%m/%d")

def find_earliest_enacted_date(data: pd.DataFrame) -> pd.DataFrame:
    """
    Find the earliest enacted date for each program and add it to the dataframe.
    For some this may be the StartDate field, for others it will come from the list
    of dictionaries in th Authorities field. 
    """
    for i in range(len(data)):
        if data.loc[i, 'StartDate'] != "":
            data.loc[i, 'EarliestEnactedDate'] = date_helper(data.loc[i, 'StartDate']).strftime("%Y/%m/%d")
        elif len(data.loc[i, 'Authorities']) > 0:
            data.loc[i, 'EarliestEnactedDate'] = authorities_date_finder(data.loc[i, 'Authorities'])
        else:
            data.loc[i, 'EarliestEnactedDate'] = ""

    data.drop(['StartDate', 'Authorities'], axis=1, inplace=True)
    return data

def break_out_categories(data: pd.DataFrame) -> pd.DataFrame:
    """
    Break out the Applicable Technology and Applicable Sectors 
    categories into their own columns with binary values.
    """
    for item in ['Sectors', 'Technologies']:    
        #Extract unique `item` categories from list of dictionaries
        unique_cats = set()
        for cats in data[item]:
            for cat in cats:
                if item == 'Sectors':
                    unique_cats.add(f"Sector_{cat['id']}")
                else:
                    unique_cats.add(f"Tech_{cat['categoryId']}")

        #Create new columns for each unique `item` category
        for cat in unique_cats:
            data[cat] = 0

        #Populate new columns with binary values
        for i in range(len(data)):
            for cat in data[item][i]:
                if item == 'Sectors':
                    data.loc[i, f"Sector_{cat['id']}"] = 1
                else:
                    data.loc[i, f"Tech_{cat['categoryId']}"] = 1

    #Drop original `item` columns
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


