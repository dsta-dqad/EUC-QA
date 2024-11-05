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

file_path = "https://raw.githubusercontent.com/YudisthiraPutra/EUC_QA/a71ab9cb64890af49881cd25327b2d153c1d0bf2/data/data_pencilan_sski.csv"

# Load the Excel file into a DataFrame
outlier_df = pd.read_csv(file_path)
outlier_df = outlier_df[["Tabel", "No_Komponen", "Komponen", "Tahun", "Nilai", "Outlier"]]



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

def prepare_dataframe(super_sheet, sheet_name):
    if sheet_name in ['11','16']:
        input_df = super_sheet.parse(sheet_name, header=[3, 4])
    else:
        input_df = super_sheet.parse(sheet_name, header=[4, 3 + 2])
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

def prepare_dataframe_5(super_sheet,sheet_name): 
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

divider_style = """
    <hr style="border: none; 
    height: 2px; 
    background-color: black; 
    border-radius: 10px; 
    margin: 20px 0;
    opacity: 0.2">
"""

@st.cache_data
def create_dataframe(_super_sheet, sheet_to_check):
    if sheet_to_check.startswith("5"):
        start_df, invalid = prepare_dataframe_5(_super_sheet,sheet_to_check)
        start_df.columns = [''.join(str(item).strip() for item in col if item is not None) for col in start_df.columns]
        start_df.columns = [re.sub(r'Unnamed:\s*\d+(_level_1)?', '-', col).strip() for col in start_df.columns]
    else:
        start_df, invalid = prepare_dataframe(_super_sheet,sheet_to_check)
        start_df.columns = [
            '-'.join(str(item).strip() for item in col if item is not None) 
            if isinstance(col, tuple)  # Only join if the column is a tuple (multi-level)
            else str(col)  # Keep single-level columns as is
            for col in start_df.columns
        ]
    
    return start_df

def highlight_outliers(row, sheet_to_check):
    tokens = sheet_to_check.split(":")
    # Here we assume outlier_df is accessible in this scope
    if any((row['NO'] == outlier_df['No_Komponen']) & 
        (row['Komponen'] == outlier_df['Komponen']) & 
        (tokens[0] == outlier_df['Tabel'])):
        return ['background-color: #CBF3F9'] * len(row)  
    return [''] * len(row)  


def show_table_content(super_sheet, sheet_to_check):
    tokens = sheet_to_check.split(":")
    if st.session_state['selected_table'] != None and len(tokens) > 1:
        token_table = tokens[0]
        token_data = tokens[1].replace("-","")
        
        # print(token_table)
        # print(token_data)
        start_df = create_dataframe(super_sheet, token_table)
        first_column = start_df.iloc[:, 0]
        second_column = start_df.iloc[:, 1]
        matching_columns = [col for col in start_df.columns if token_data.lower() in col.lower()]
        start_df = start_df[matching_columns]
        start_df.insert(0, 'NO', first_column)
        start_df.insert(1, 'Komponen', second_column)
    else:
        start_df = create_dataframe(super_sheet, sheet_to_check)
        
    st.markdown(divider_style, unsafe_allow_html=True)
    st.title(f'Tabel {sheet_to_check.replace(":", " - ")}')

    # Display a legend above the table
    legend_html = """
    <div style="display: flex; align-items: center; margin-bottom: 10px;">
        <div style="width: 20px; height: 20px; background-color: #CBF3F9; border: 0.5px solid black; margin-right: 5px;"></div>
        <span>Baris dengan warna ini menandakan terdapat pencilan dalam data komponen.</span>
    </div>
    """
    st.markdown(legend_html, unsafe_allow_html=True)

    styled_df = start_df.style.apply(highlight_outliers, axis=1, args=(sheet_to_check,))
    st.dataframe(styled_df.format(precision=2), hide_index=True)

    if st.session_state['selected_table'] != None:
        show_dropdown(sheet_to_check, start_df)


def show_dropdown(sheet_to_check, start_df):
    # Initialize session state for the selected component
    placeholder = f'Pilih Komponen Tabel {sheet_to_check.replace(":", " - ")}'
    if 'selected_component' not in st.session_state:
        st.session_state['selected_component'] = placeholder

    # Dropdown for selecting component
    components = [placeholder] + [f"{row['NO']} - {row['Komponen']}" for _, row in start_df.iterrows()]
    selected_component = st.selectbox("Lihat Grafik Data Komponen:", components)

    # Update session state if selection changes
    if selected_component != st.session_state.selected_component:
        st.session_state.selected_component = selected_component

    # Process component selection
    if st.session_state.selected_component != placeholder:
        selected_no, selected_komponen = st.session_state.selected_component.split(" - ", 1)
        filtered_data = start_df[(start_df['NO'] == int(selected_no)) & (start_df['Komponen'] == selected_komponen)]

        if not filtered_data.empty:
            # Display selected item information and plot
            number = filtered_data.iloc[0]['NO']
            component = filtered_data.iloc[0]['Komponen']

            with st.expander("Selected Item Information", expanded=True):
                col1_e, col2_e, col3_e, col4_e = st.columns((2, 1, 1, 1))
                with col1_e:
                    st.markdown(f'<p style="margin:0;"><strong>Tabel:</strong> {sheet_to_check.split(":")[0]}</p>', unsafe_allow_html=True)
                    st.markdown(f'<p style="margin:0;"><strong>Nomor Komponen:</strong> {number}</p>', unsafe_allow_html=True)
                    st.markdown(f'<p style="margin:0;"><strong>Komponen:</strong> {component}</p>', unsafe_allow_html=True)

                st.dataframe(filtered_data.round(2))
                data_columns = start_df.columns[2:]
                row_data = filtered_data.iloc[0]
                numeric_data = row_data[2:].apply(pd.to_numeric, errors='coerce')

                mean_data = round(numeric_data.mean(), 2)
                median_data = round(numeric_data.median(), 2)

                tokens = sheet_to_check.split(":")
                filtered_outliers = outlier_df[
                    (outlier_df['No_Komponen'] == number) & 
                    (outlier_df['Komponen'] == component) & 
                    (outlier_df['Tabel'] == tokens[0])
                ]
                # Assuming filtered_outliers is your DataFrame
                filtered_outliers['Tahun'] = filtered_outliers['Tahun'].astype(str).str.replace("-", "", regex=False)

                # print(filtered_outliers)

                if len(tokens) > 1:
                    filtered_rows = filtered_outliers[filtered_outliers.apply(lambda row: row.astype(str).str.contains(tokens[1].replace("-","")).any(), axis=1)]
                    row_count = filtered_rows.shape[0]
                else:
                    row_count = filtered_outliers.shape[0]

                # Count the number of rows that matched the filter

                with col2_e:
                    card_component("Jumlah Pencilan", row_count)
                with col3_e:
                    card_component("Mean Data", mean_data)
                with col4_e:
                    card_component("Median Data", median_data)

                for col in data_columns:
                    filtered_data[col] = pd.to_numeric(filtered_data[col], errors='coerce')

                plot_data = filtered_data[data_columns].transpose()
                plot_data.columns = [f"{number} - {component}"]
                plot_data = plot_data.dropna()

                # Prepare data for echart
                x_values = list(plot_data.index)
                x_values = [x.replace("-","").lower() for x in x_values]
                y_values = list(plot_data[f"{number} - {component}"].values)
                outlier_x = [outlier_row['Tahun'] for _, outlier_row in filtered_outliers.iterrows()]
                outlier_x = [x.lower() for x in outlier_x]
                outlier_y = [outlier_row['Nilai'] for _, outlier_row in filtered_outliers.iterrows()]
                # print(x_values)
                # print(outlier_x)
                # Convert outlier data to match x_values format for ECharts
                outliers = [{'xAxis': x, 'yAxis': y} for x, y in zip(outlier_x, outlier_y)]

                # Define ECharts options
                options = {
                    "title": {"text": f"Data for {number} - {component}", "left": "center"},
                    "tooltip": {"trigger": "axis"},
                    "xAxis": {
                        "type": "category",
                        "data": x_values,
                        "axisLabel": {"rotate": 45}
                    },
                    "yAxis": {"type": "value"},
                    "series": [
                        {
                            "name": f"{number} - {component}",
                            "type": "line",
                            "data": y_values,
                            "lineStyle": {"color": "black", "width": 2},
                        },
                        {
                            "name": "Outliers",
                            "type": "scatter",
                            "data": [{"value": [x, y]} for x, y in zip(outlier_x, outlier_y)],
                            "itemStyle": {"color": "red"},
                            "markPoint": {"data": outliers},
                        }
                    ]
                }

                # Render EChart in Streamlit
                st_echarts(options=options, height="500px")

def card_component(title,data):
    # Display card with the total count of outliers
    st.markdown(
        f"""
        <div style="padding:5px; border-radius:2px; border:1px black solid; text-align:center; margin-bottom:20px;">
            <p style="color:#333333; margin:0;">{title}</p>
            <p style="font-weight:bold;font-size:25px;margin:0;">{data}</p>
        </div>
        """, 
        unsafe_allow_html=True
    )

# st.set_page_config(layout="wide", page_title="Development", page_icon="📊")
def main():
    st.title("UJI KEWAJARAN SSKI OKTOBER 2024")
    file_path = "https://raw.githubusercontent.com/YudisthiraPutra/EUC_QA/3792a5695653dbbe2b98bffa9c704571edc1be23/data/SSKI%20EKSTERNAL_25%20Okt%202024.xlsx"

    super_sheet = pd.ExcelFile(file_path)
    # Filter dataset table list
    sheet_list = super_sheet.sheet_names
    filtered_list = [name for name in sheet_list if re.search(r'\d', name)]

    col1_o, col2_o = st.columns((1.7, 2))

    with col1_o:
        st.title("RINGKASAN SINGKAT")

        st.subheader("Ringkasan Komponen dengan Pencilan")

        unique_outliers = outlier_df.drop_duplicates(subset=['Komponen'])

        unique_outliers_display = unique_outliers[['Tabel', 'No_Komponen', 'Komponen']].rename(
            columns={
                'Tabel': 'Tabel',
                'No_Komponen': 'Nomor',
                'Komponen': 'Komponen'
            }
        )

        # Display only the first three rows
        st.dataframe(unique_outliers_display)

    with col2_o:
        col1_c, col2_c, col3_c = st.columns((1, 1, 1))

        with col2_c:
            total_outliers = outlier_df.drop_duplicates(subset=['No_Komponen', 'Tabel']).shape[0]
            card_component("Jumlah Komponen Pencilan", total_outliers)
        with col3_c:
            card_component("Tanggal Di Proses", "2024-10-25")

        # Group by 'table' and count outliers for each table
        outlier_counts = outlier_df.groupby('Tabel')['No_Komponen'].nunique()
        print(outlier_counts)
        desired_order = ["1","2","3","4","5a","5b","5c","5d","5d.1","5.d.2","6","7","8","9","10","11","11a","12","13","14","15","16","16a","17","18","19","20"]  # Replace with actual sheet names

        # Convert index to categorical type with the specified order
        outlier_counts.index = pd.Categorical(outlier_counts.index, categories=desired_order, ordered=True)
        print(outlier_counts)
        # Sort the Series by the new categorical index
        sorted_outlier_counts = outlier_counts.sort_index()
        print(sorted_outlier_counts)

        # Output the sorted Series
        # print(sorted_outlier_counts)

        # Prepare options for st_echarts
        options = {
            "xAxis": {
                "type": "category",
                "data": sorted_outlier_counts.index.tolist(),  # Table numbers as x-axis data
            },
            "yAxis": {"type": "value"},
            "series": [{
                "data": sorted_outlier_counts.values.tolist(),  # Outlier counts as y-axis data
                "type": "bar",
                "color": "#CBF3F9"
            }],
            "title": {
                "text": "Outlier Count per Table",
                "left": "left"
            },
            "tooltip": {"trigger": "axis"},
            "label": {"show": True, "position": "top"},
        }
        st_echarts(options=options, height="500px")

    if 'selected_table' not in st.session_state:
        st.session_state.selected_table = None  # Placeholder for first run

    col1, col2 = st.columns((1, 4))

    with col1:
        st.markdown("<h4 style='text-align: left;'>Apa yang ingin dilakukan?</h4>", unsafe_allow_html=True)
        for table in filtered_list:
            # For tables starting with "5", use an expander with multiple buttons
            unique_tahun = outlier_df[outlier_df['Tabel'] == table]
            unique_tahun = list(unique_tahun['Tahun'].unique())

            extracted_data = set()
            for item in unique_tahun:
                split_data = item.split("-")
                if len(split_data) > 2:  # Ensure there are at least three parts
                    extracted_value = "-".join(split_data[2:])  # Join the parts after the second hyphen
                    extracted_data.add(extracted_value)
            
            if table.startswith("5"):
                with st.expander(f"Lihat Kewajaran SSKI Tabel {table}"):
                    # Add multiple buttons within the expander for this table
                    for item in extracted_data:
                        if st.button(f"Lihat {item}", key=f"{table}:{item}", use_container_width=True):
                            st.session_state.selected_table = f"{table}:{item}"

            # For other tables, display a single button that updates session state
            else:
                if st.button(f"Lihat Kewajaran SSKI Tabel {table}", use_container_width=True):
                    st.session_state.selected_table = table

    with col2:
        if st.session_state.selected_table != None:
            selected_number = st.session_state.selected_table
            show_table_content(super_sheet, selected_number)
        else:
            for sheet_to_check in filtered_list:
                show_table_content(super_sheet, sheet_to_check)

if __name__ == "__main__":
    main()
