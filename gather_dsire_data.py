import ast
import pandas as pd
import urllib.request, json


def get_raw_json() -> pd.DataFrame:
    """
    Get raw json data from DSIRE API and return as a pandas dataframe
    """
    with urllib.request.urlopen(
        "https://programs.dsireusa.org/api/v1/programs?&draw=3&columns%5B0%5D%5Bdata%5D=name&columns%5B0%5D%5Bname%5D=&columns%5B0%5D%5Bsearchable%5D=true&columns%5B0%5D%5Borderable%5D=true&columns%5B0%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B0%5D%5Bsearch%5D%5Bregex%5D=false&columns%5B1%5D%5Bdata%5D=stateObj.abbreviation&columns%5B1%5D%5Bname%5D=&columns%5B1%5D%5Bsearchable%5D=true&columns%5B1%5D%5Borderable%5D=true&columns%5B1%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B1%5D%5Bsearch%5D%5Bregex%5D=false&columns%5B2%5D%5Bdata%5D=categoryObj.name&columns%5B2%5D%5Bname%5D=&columns%5B2%5D%5Bsearchable%5D=true&columns%5B2%5D%5Borderable%5D=true&columns%5B2%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B2%5D%5Bsearch%5D%5Bregex%5D=false&columns%5B3%5D%5Bdata%5D=typeObj.name&columns%5B3%5D%5Bname%5D=&columns%5B3%5D%5Bsearchable%5D=true&columns%5B3%5D%5Borderable%5D=true&columns%5B3%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B3%5D%5Bsearch%5D%5Bregex%5D=false&columns%5B4%5D%5Bdata%5D=published&columns%5B4%5D%5Bname%5D=&columns%5B4%5D%5Bsearchable%5D=true&columns%5B4%5D%5Borderable%5D=true&columns%5B4%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B4%5D%5Bsearch%5D%5Bregex%5D=false&columns%5B5%5D%5Bdata%5D=createdTs&columns%5B5%5D%5Bname%5D=&columns%5B5%5D%5Bsearchable%5D=true&columns%5B5%5D%5Borderable%5D=true&columns%5B5%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B5%5D%5Bsearch%5D%5Bregex%5D=false&columns%5B6%5D%5Bdata%5D=updatedTs&columns%5B6%5D%5Bname%5D=&columns%5B6%5D%5Bsearchable%5D=true&columns%5B6%5D%5Borderable%5D=true&columns%5B6%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B6%5D%5Bsearch%5D%5Bregex%5D=false&order%5B0%5D%5Bcolumn%5D=6&order%5B0%5D%5Bdir%5D=desc&start=0&length=-1&search%5Bvalue%5D=&search%5Bregex%5D=false&_=1694800269871"
    ) as url:
        data = json.load(url)

    # Save raw json just in case you need to reference it later
    with open("Data/raw_dsire_data.json", "w") as f:
        json.dump(data, f)

    data = data["data"]
    return pd.DataFrame(data)


def clean_dsire_df(df) -> pd.DataFrame:
    """
    Clean raw DSIRE dataframe.
    Break out the data from the state, type, category, and sector objects into
    their own columns. Also drop columns that repeat data.
    return cleaned dataframe
    """
    # Convert string representations of dictionaries into actual dictionary objects
    columns_to_convert = ["stateObj", "typeObj", "categoryObj", "sectorObj"]

    for col in columns_to_convert:
        df[col] = df[col].apply(
            lambda x: ast.literal_eval(x) if isinstance(x, str) else x
        )

    # Iterate over each specified column and extract the dictionary keys to create new columns
    for col in columns_to_convert:
        # Extract dictionary keys and create new columns with the specified format
        for key in df[col].iloc[0].keys():
            new_col_name = f"{col.split('Obj')[0]}_{key}"
            df[new_col_name] = df[col].apply(
                lambda x: x.get(key) if isinstance(x, dict) else None
            )

    df.drop(columns=columns_to_convert + ["type_categoryObj"], inplace=True)
    return df


if __name__ == "__main__":
    uc_data = get_raw_json()
    clean_dsire_df(uc_data).to_csv("Data/cleaned_dsire_data.csv", index=False)
