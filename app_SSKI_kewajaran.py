import numpy as np
import pandas as pd
from collections import Counter
from datetime import datetime
from copy import copy
from IPython.display import display, HTML
import streamlit as st # type: ignore
from streamlit_echarts import st_echarts # type: ignore
import json
import requests
from datetime import datetime
import calendar
import re
import matplotlib.pyplot as plt


st.set_page_config(layout="wide", page_title="Development", page_icon="📊")
super_sheet = pd.ExcelFile("/Users/ferroyudisthira/Desktop/DSTA_DQAD/V&H_Check/Sumber_Data_Lama/SSKI/SSKI EKSTERNAL_25 Okt 2024.xlsx")

# Dummy outlier data (this would normally come from your outlier DataFrame)
outlier_data = {
    'Komponen': ['Non Performing Loan (NPL) Gross Bank Umum'] * 16,
    'Tahun': [
        '2021-Mar', '2021-Jun', '2021-Sep', '2021-Dec', 
        '2022-Jan', '2022-Feb', '2022-Mar', '2022-Apr', 
        '2022-May', '2022-Jun', '2022-Jul', '2022-Aug', 
        '2022-Sep', '2022-Oct', '2022-Nov', '2022-Dec'
    ],
    'Nilai': [
        2.927337843747314, 2.5944197700368843, 2.3657472065402336,
        2.5250950416732856, 3.0594823804092517, None, 
        3.1660036231534976, 3.206630994716228, 3.168682219007614, 
        3.2191738685653712, 3.3466405299048922, 3.237707474256429, 
        3.3459906381515436, 3.3542849758081057, 3.21745757909552,
        None
    ],
    'Outlier': ['Ya', 'Ya', 'Ya', 'Ya', 'Ya', 'Tidak', 
                'Ya', 'Ya', 'Ya', 'Ya', 'Ya', 'Ya', 
                'Ya', 'Ya', 'Ya', 'Ya']
}

# Create the DataFrame
outlier_df = pd.DataFrame(outlier_data)

def is_numeric(x):
    # Convert to string and strip whitespace
    x = str(x).strip()  
    
    # Remove unwanted characters (like asterisks and tabs)
    x = x.replace('*', '').replace('\t', '').replace(',', '').strip()  # Remove asterisks and tabs, and replace commas
    
    if x == '-':  # Ignore the "-" string
        return True
    if x in ['0', '.']:  # Include valid values
        return True
    try:
        float(x)  # Try to convert to a float
        return True
    except (ValueError, TypeError):  # If conversion fails, it's not a valid number
        return False

def prepare_dataframe(sheet_name, header_count):
    if sheet_name in ['11','16']:
        input_df = super_sheet.parse(sheet_name, header=[3, 4])
    else:
         input_df = super_sheet.parse(sheet_name, header=[4, 3 + header_count])
    # Load the sheet with dynamic header handling

    # Adjust the column names
    input_df.columns = input_df.columns.map(lambda x: str(x[0]).upper() if 'Unnamed' in str(x) else x)
    input_df.columns = input_df.columns.map(lambda x: (x[0], x[1].strip()) if isinstance(x, tuple) and isinstance(x[1], str) else x)

    # Extract the first two columns
    first_column = input_df.iloc[:, 0]
    second_column = input_df.iloc[:, 1]

    # Step 2: Filter columns that have the year in the name (using regex)
    output_df = input_df.filter(regex=str('20'))

    # Reinsert 'NO' and 'Komponen' columns at the beginning of the filtered DataFrame
    output_df.insert(0, 'NO', first_column)
    output_df.insert(1, 'Komponen', second_column)

    # Step 3: Remove rows after 'keterangan' if found
    index_keterangan = output_df[output_df.apply(lambda row: row.astype(str).str.contains('keterangan', case=False).any(), axis=1)].index
    if not index_keterangan.empty:
        first_keterangan_index = index_keterangan[0]
        output_df = output_df.iloc[:first_keterangan_index]

    # Step 4: Apply numeric validation only to numeric columns
    numeric_columns = output_df.columns[2:]  # Only consider columns after 'NO' and 'Komponen'
    mask_non_numeric = output_df[numeric_columns].map(lambda x: not is_numeric(x))  # True for non-numeric entries

    # Step 5: Create invalid entries DataFrame including 'NO' and 'Komponen'
    invalid_entries = output_df[mask_non_numeric.any(axis=1)]  # Rows with any non-numeric entries
    invalid_entries.insert(0,'Tabel',sheet_name)
    output_df = output_df.replace([None], [''], regex=True)

    return output_df, invalid_entries  # Return both valid DataFrame and invalid entries

# Use the combined function
# df, invalid_entries = prepare_dataframe("2", 2)
# df

def prepare_dataframe_5(sheet_name): 
    # Set the header based on the sheet name
    if sheet_name == '5a':
        header_array = [3, 4, 5]
    else:
        header_array = [2, 3, 4, 5]

    # Parse the sheet into a DataFrame
    input_df = super_sheet.parse(sheet_name, header=header_array)
    
    # Adjust the column names
    input_df.columns = input_df.columns.map(
        lambda x: tuple(
            str(x[i]).upper() if i == 0 and 'Unnamed' in str(x[1]) else x[i].strip() if isinstance(x[i], str) else x[i]
            for i in range(len(x))
        ) if isinstance(x, tuple) else x
    )

    # Step 1: Filter columns that have the year in the name (using regex)
    output_df = input_df.filter(regex='20')

    # Step 2: Insert 'NO' and 'Komponen' columns
    output_df.insert(0, 'NO', input_df[list(input_df.columns)[0]])
    output_df.insert(1, 'Komponen', input_df[list(input_df.columns)[1]])
    
    # Step 3: Remove rows after "keterangan"
    index_keterangan = output_df[output_df.apply(lambda row: row.astype(str).str.contains('keterangan', case=False).any(), axis=1)].index
    if not index_keterangan.empty:
        first_keterangan_index = index_keterangan[0]
        output_df = output_df.iloc[:first_keterangan_index]

    # Step 4: Apply numeric validation only to numeric columns
    numeric_columns = output_df.columns[2:]  # Only consider columns after 'NO' and 'Komponen'
    mask_non_numeric = output_df[numeric_columns].applymap(lambda x: not is_numeric(x))  # True for non-numeric entries

    # Step 5: Create invalid entries DataFrame including 'NO' and 'Komponen'
    invalid_entries = output_df[mask_non_numeric.any(axis=1)]  # Rows with any non-numeric entries
    invalid_entries.insert(0,'Tabel',sheet_name)
    
    # Step 6: Remove rows with any non-numeric entries from the outut DataFrame
    output_df = output_df[~mask_non_numeric.any(axis=1)]  # Keep only valid entries
    output_df = output_df.replace([None], [''], regex=True)

    return output_df, invalid_entries  # Return both valid DataFrame and invalid entries

# # Example usage
# start_df, invalid_entries = prepare_dataframe_5("5.d.2")
# print(start_df.head())
# print(invalid_entries)

def main():
    # Example list of sheet names; replace with your data source
    super_sheet = pd.ExcelFile("/Users/ferroyudisthira/Desktop/DSTA_DQAD/V&H_Check/Sumber_Data_Lama/SSKI/SSKI EKSTERNAL_25 Okt 2024.xlsx")

    sheet_list = super_sheet.sheet_names

    filtered_list = [name for name in sheet_list if re.search(r'\d', name)]
    
    for sheet_to_check in filtered_list:
        st.title(sheet_to_check)

        # Select the appropriate data preparation function based on the sheet name
        if sheet_to_check.startswith("5"):
            start_df, invalid = prepare_dataframe_5(sheet_to_check)
                    # Combine multi-level headers into a single header
            start_df.columns = [' '.join(str(item).strip().upper() for item in col if item is not None) for col in start_df.columns]

            # Remove the entire "UNNAMED: <number>_LEVEL_1" component from headers
            start_df.columns = [re.sub(r'UNNAMED:\s*\d+(_LEVEL_1)?', '', col).strip() for col in start_df.columns]

        else:
            start_df, invalid = prepare_dataframe(sheet_to_check, 2)
            start_df.columns = [
                '-'.join(str(item).strip() for item in col if item is not None) 
                if isinstance(col, tuple)  # Only join if the column is a tuple (multi-level)
                else str(col)  # Keep single-level columns as is
                for col in start_df.columns
            ]

            # # Remove the entire "UNNAMED: <number>_LEVEL_1" component from headers
            # start_df.columns = [re.sub(r'UNNAMED:\s*\d+(_LEVEL_1)?', '', col).strip() for col in start_df.columns]

        # Clean the DataFrame

        event = st.dataframe(
            start_df,
            on_select='rerun',
            selection_mode='single-row',
            hide_index=True
        )

        if event.selection and 'rows' in event.selection and len(event.selection['rows']) > 0:
            selected_row = event.selection['rows'][0]
            number = start_df.iloc[selected_row]['NO']
            component = start_df.iloc[selected_row]['Komponen']  # Make sure this matches your actual column name

            # Display the selected number and component
            # Show selected information in a modal popup
            with st.expander("Selected Item Information", expanded=True):
                st.write(f"**Selected Number:** {number}")
                st.write(f"**Selected Component:** {component}")

                # Filter the DataFrame based on the selected row
                filtered_data = start_df[start_df['NO'] == number]  
                
                # Display filtered data
                st.write("Filtered Data:", filtered_data)

                # Get the data columns for plotting
                data_columns = start_df.columns[2:]  # Adjust based on your DataFrame structure

                # Convert the data columns to numeric
                for col in data_columns:
                    filtered_data[col] = pd.to_numeric(filtered_data[col], errors='coerce')

                # Drop non-numeric columns for plotting
                plot_data = filtered_data[data_columns].transpose()
                plot_data.columns = [f"{number} - {component}"]  
                plot_data = plot_data.dropna()  # Drop rows with NaN values

                # Highlight outliers
                for outlier_index, outlier_row in outlier_df.iterrows():
                    outlier_value = outlier_row['Nilai']
                    outlier_label = outlier_row['Tahun']
                    if outlier_label in plot_data.index:
                        plot_data.loc[outlier_label, 'Outlier'] = outlier_value  # Mark outlier

                # Create a plot if there is data
                if not plot_data.empty:
                    fig, ax = plt.subplots(figsize=(18, 6))  # 2:1 aspect ratio

                    # Plot the data
                    plot_data.plot(ax=ax, color='blue')  # Regular values in blue
                    
                    # Overlay outliers
                    for outlier_index, outlier_row in outlier_df.iterrows():
                        if outlier_row['Tahun'] in plot_data.index:
                            ax.plot(outlier_row['Tahun'], outlier_row['Nilai'], 'ro', markersize=8, label='Outlier')

                    ax.set_title(f'Data for {number} - {component}', fontsize=10)
                    ax.set_xlabel('Year / Month', fontsize=8)
                    ax.set_ylabel('Values', fontsize=8)
                    ax.tick_params(axis='both', which='major', labelsize=8)

                    # Display the plot
                    st.pyplot(fig)
                else:
                    st.write("No numeric data available to plot.")




if __name__ == "__main__":
    main()
