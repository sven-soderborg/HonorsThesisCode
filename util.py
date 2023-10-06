import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def create_bar_chart(row, color):    
    return sns.barplot(
        y=row.index.str.capitalize().values,
        x=row.values,
        orient="h",
        saturation=1,
        color=color,
        width=0.75,
    )


def egen_pretty_latex(df: pd.DataFrame, file_path: str, new_names: dict = None) -> bool:
    """Export dataframes to latex with better formatting"""
    if new_names:
        # Rename the columns
        data_renamed = data.rename(columns={
            "year": "Year",
            "genMWH": "Megawatthours Generated"
        })

    # Round the "Megawatthours Generated" column to the nearest integer and format with commas
    data_renamed["Megawatthours Generated"] = data_renamed["Megawatthours Generated"].round(0).astype(int).apply(lambda x: '{:,}'.format(x))

    # Convert the DataFrame to LaTeX
    latex_output = data_renamed.to_latex(index=False)