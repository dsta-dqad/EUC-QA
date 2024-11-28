import pandas as pd
import streamlit as st

def pivot_dataframe(input_df, raw_df):
    # Pivot the dataframe
    formatted_df = input_df.pivot_table(
        index=["No_Komponen", "Komponen"],  # Rows
        columns="Periode",                 # Columns
        values="Nilai",                    # Values
        aggfunc="first"                    # Aggregation function
    ).reset_index()

    # Rename and clean up the dataframe
    formatted_df.rename(columns={"No_Komponen": "No."}, inplace=True)
    formatted_df.columns.name = None  
    formatted_df.fillna("", inplace=True) 

    # Identify outliers
    outlier_values = raw_df[raw_df["Outlier"] == "Ya"]["Nilai"].values

    # Highlight cells if they are outliers
    def highlight_outliers(cell):
        if cell in outlier_values:
            return "background-color: #CBF3F9"
        return ""

    # Apply highlighting using a style
    styled_df = formatted_df.style.applymap(highlight_outliers)

    return styled_df

# Example usage
# Read the CSV file
df = pd.read_csv("/Users/ferroyudisthira/Downloads/data_pencilan_sski (2).csv", sep=",")

# Filter rows where the "Tabel" column has the value "1"
df = df[df["Tabel"] == "1"]

# Generate the formatted dataframe with highlighting
styled_formatted_df = pivot_dataframe(df, df)

# Display the styled dataframe in Streamlit
st.dataframe(styled_formatted_df)
