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
st.set_page_config(layout="wide", page_title="EUC QA", page_icon="📊")
divider_style = """
    <hr style="border: none; 
    height: 2px; 
    background-color: black; 
    border-radius: 10px; 
    margin: 20px 0;
    opacity: 0.2">
"""
def create_pie_chart(miss_data, corr_data):
    options = {
                "tooltip": {"trigger": "item"},
                "legend": {
                    "top": "5%", 
                    "left": "center",  # Legend text color to white
                },
                "series": [
                    {
                        "name": "Rasio Konsistensi",
                        "type": "pie",
                        "radius": ["40%", "70%"],
                        "avoidLabelOverlap": False,
                        "itemStyle": {
                            "borderRadius": 0,
                            "borderWidth": 0,
                        },
                        "label": {
                            "show": False,
                            "position": "center",
                            "fontColor":"white",
                            "fontSize": 16,
                            "fontWeight": "bold"
                        },
                        "labelLine": {"show": False},
                        "data": [
                            {"value": miss_data, "name": "Tidak Konsisten", "itemStyle": {"color": "#ff6961"}},  # Soft red for mismatch
                            {"value":  corr_data, "name": "Konsisten", "itemStyle": {"color": "#90ee90"}},  # Soft green for correct
                        ],
                    }
                ],
            }
        
    st_echarts(
        options=options, height="400px",
    )
def main():
    if st.button("Kembali Ke Halaman Utama"):
        st.session_state['page'] = 'main'
    st.markdown("""
        <style>
        @import url('https://db.onlinewebfonts.com/c/c214e055a9aae386324285c45892f7b5?family=Frutiger+LT+W02+45+Light');

        *, html, body,h3,h4 [class="css"] {
            font-family: 'Frutiger LT W02 45 Light', sans-serif;
        }
        </style>
        """, unsafe_allow_html=True)
    # Custom CSS to center the title
    st.markdown("""
        <style>
        .centered-title {
            text-align: center;
            text-decoration: underline;
        }
        </style>
        """, unsafe_allow_html=True)
    
    current_year = datetime.now().year
    current_month = datetime.now().month -1

    
    month = calendar.month_name[current_month]
    month = month.upper()
    # Centered title using custom class
    st.markdown(f"<h1 class='centered-title'>SSKI QUALITY ASSURANCE REPORT - {month} {current_year}</h1>", unsafe_allow_html=True)
    st.markdown(divider_style, unsafe_allow_html=True)

    def highlight_rows(row):
        # Index will be used to check the first and last rows
        if row.name == 0:
            return ['background-color: #A9DFBF; color: black'] * len(row)  # Green background for the first row
        elif row.name == len(df_clean) - 1:
            return ['background-color: #F5B7B1; color: black'] * len(row)  # Yellow background for the last row
        else:
            return ['background-color: #F9E79F; color: black'] * len(row)  # Red background for all other rows

    # Function to display the DataFrame
    def display_dataframe(input_df):
        st.dataframe(input_df.style.set_properties(**{'text-align': 'center'}).set_table_styles(
            [{'selector': 'th', 'props': [('text-align', 'center'), ('background-color', '#E8F6F3')]}]
        ).format(precision=2))

    file_path = "https://raw.githubusercontent.com/YudisthiraPutra/EUC_QA/e003f8db149b5e5d91eca723f8deecff5ba78360/data/data_sski.json"

    # Load the JSON file
    response = requests.get(file_path)
    data = response.json()

    # Specify the local file path
    # file_path = "/Users/ferroyudisthira/Desktop/DSTA_DQAD/V&H_Check/data_test.json"

    # # Load the JSON file from the local path
    # with open(file_path, 'r') as f:
    #     data = json.load(f)
    raw_data = data['raw_data']
    raw_keys_list = list(raw_data.keys())

    clean_data = data['clean_data']
    clean_keys_list = list(clean_data.keys())

    summary_data = data['summary_data']
    sum_keys_list = list(summary_data.keys())

    horizontal_clean_data = data['horizontal_clean_data']
    hor_clean_keys_list = list(horizontal_clean_data.keys())

    horizontal_raw_data = data['horizontal_raw_data']
    hor_raw_keys_list = list(horizontal_raw_data.keys())

    error_counts = {}
    ver_error_count = 0
    ver_total_count = 0

    for i in range(len(clean_data)):
        df_clean = pd.DataFrame(clean_data[clean_keys_list[i]])
        df_raw = pd.DataFrame(raw_data[raw_keys_list[i]])

        sski_path = df_clean['Path'][0]  # Assuming 'Path' column exists
        sski_number = sski_path.split('.')[1]  # Extract the number after 'SSKI'

        column_count_error = len(df_clean.columns) - 2
        column_count_total = len(df_raw.columns) - 2
        column_count_correct = column_count_total - column_count_error  # Calculate correct count

        ver_error_count += column_count_error
        ver_total_count += column_count_total

        if sski_number not in error_counts:
            error_counts[sski_number] = {"Vertikal - Jumlah Selisih": 0, "Vertikal - Jumlah Benar": 0, "Vertikal - Jumlah Total": 0}

        error_counts[sski_number]["Vertikal - Jumlah Selisih"] += column_count_error
        error_counts[sski_number]["Vertikal - Jumlah Benar"] += column_count_correct
        error_counts[sski_number]["Vertikal - Jumlah Total"] += column_count_total

    total_error_rows = 0
    total_correct_rows = 0
    total_rows = 0
    hor_error = {}

    for item in hor_raw_keys_list:
        final = pd.DataFrame(horizontal_raw_data[item])
        
        if final is not None and not final.empty:
            total_rows_in_table = len(final)  # Total rows in the table
            correct_rows = total_rows_in_table  # Assume all rows are correct initially

            if item in horizontal_clean_data:
                clean = pd.DataFrame(horizontal_clean_data[item])
                error_rows = len(clean)  # Error rows come from `clean`
                correct_rows = total_rows_in_table - error_rows  # Correct rows are the difference
            else:
                error_rows = 0  # If there's no `clean` data, assume no errors

            hor_error[item] = {
                "Horizontal - Jumlah Selisih": error_rows,
                "Horizontal - Jumlah Benar": correct_rows,
                "Horizontal - Jumlah Total": total_rows_in_table
            }

            total_error_rows += error_rows
            total_correct_rows += correct_rows
            total_rows += total_rows_in_table

    # Assuming error_counts and hor_error are already calculated

    # Create DataFrame from hor_error
    df_hor_error = pd.DataFrame.from_dict(hor_error, orient='index').reset_index()
    df_hor_error.rename(columns={'index': 'table_name'}, inplace=True)

    # Create DataFrame from error_counts
    df_error_counts = pd.DataFrame.from_dict(error_counts, orient='index').reset_index()
    df_error_counts.rename(columns={'index': 'table_name'}, inplace=True)

    # Merge both DataFrames on 'table_name'
    df_combined = pd.merge(df_hor_error, df_error_counts, on='table_name', how='outer')

    # Fill NaN values with 0
    df_combined.fillna(0, inplace=True)

    # Convert all numeric columns to integer
    numeric_columns = df_combined.select_dtypes(include=['float64']).columns
    df_combined[numeric_columns] = df_combined[numeric_columns].astype(int)

    # Sort by the table number extracted from the table_name
    # Assuming table names are in the format 'table_X' where X is the number
    df_combined['table_number'] = df_combined['table_name'].str.extract('(\d+)').astype(int)
    df_combined.sort_values(by='table_number', inplace=True)

    # Drop the auxiliary column used for sorting
    df_combined.drop(columns=['table_number'], inplace=True)
    # Add the new column to the DataFrame

    # Display the combined DataFrame before merging

    # Define the merging pairs
    merge_pairs = {
        '5d.1': '5d1',
        '5d2': '5.d.2'
    }

    # Iterate through the DataFrame and sum the relevant rows
    for table, merge_with in merge_pairs.items():
        row_to_merge = df_combined[df_combined['table_name'] == table]
        row_to_merge_with = df_combined[df_combined['table_name'] == merge_with]

        if not row_to_merge.empty and not row_to_merge_with.empty:
            merged_index = row_to_merge.index[0]  # Use the index of the first row
            # Sum the values and assign to the existing row
            df_combined.loc[merged_index, df_combined.columns[2:]] += row_to_merge_with.iloc[0, 2:]
            # Remove the merged row
            df_combined = df_combined.drop(row_to_merge_with.index)

    # Reset index for clarity (optional)
    df_combined.reset_index(drop=True, inplace=True)
    
    last_period = f"{month} {current_year}"
    df_combined['Last Period'] = last_period

    # Display the final merged DataFrame
    print("Final merged DataFrame:")
    csv = df_combined.to_csv(index=False).encode('utf-8')

    error_counts = {}
    ver_error_count = 0
    ver_total_count = 0
    for i in range(len(clean_data)):
        df_clean = pd.DataFrame(clean_data[clean_keys_list[i]])
        df_raw = pd.DataFrame(raw_data[raw_keys_list[i]])

        sski_path = df_clean['Path'][0]  # Assuming 'Path' column exists
        sski_number = sski_path.split('.')[1]  # Extract the number after 'SSKI'


        column_count_error = len(df_clean.columns) - 2
        ver_error_count += column_count_error

        column_count_correct = len(df_raw.columns) -2
        ver_total_count += column_count_correct
        error_counts[sski_number] = error_counts.get(sski_number, 0) + column_count_error

    print(error_counts)
    total_error_rows = 0
    total_correct_rows = 0
    total_rows = 0
    hor_error = {}
    for item in hor_raw_keys_list:
        hor_error[item] = 0
        final = pd.DataFrame(horizontal_raw_data[item])
        if final is not None and not final.empty:
            if item in horizontal_clean_data:
                clean = pd.DataFrame(horizontal_clean_data[item])
                total_rows_in_table = len(final)  # Total rows in the table
                error_rows = len(clean)  # Error rows come from `clean`
                correct_rows = total_rows_in_table - error_rows  # Correct rows are the difference
                hor_error[item] = error_rows
                total_error_rows += error_rows
            
            total_correct_rows += correct_rows
            total_rows += total_rows_in_table

    # Define layout with two columns
    col1_g, col2_g, col3_g = st.columns((2, 2,4))
    with col1_g:
        st.markdown("<h5 style='text-align: center;'><span style='text-align: center;font-weight: bold;'>Rasio Konsistensi Vertical Check</span></h5>", unsafe_allow_html=True)
        create_pie_chart(ver_error_count,ver_total_count)
        st.markdown(f"<p style='text-align: center;'><span style='font-weight: bold; text-decoration: underline;'>{(ver_error_count/(ver_error_count + ver_total_count)) * 100:.2f}%</span> data tidak konsisten.</p>", unsafe_allow_html=True)

    with col2_g:
        st.markdown("<h5 style='text-align: center;'><span style='text-align: center;font-weight: bold;'>Rasio Konsistensi Horizontal Check</span></h5>", unsafe_allow_html=True)
        create_pie_chart(total_error_rows,total_rows)
        st.markdown(f"<p style='text-align: center;'><span style='font-weight: bold; text-decoration: underline;'>{(total_error_rows/total_rows) * 100:.2f}%</span> data tidak konsisten.</p>", unsafe_allow_html=True)

    with col3_g:
        # Dictionary comprehension to filter out items with value 0
        filtered_dict = {key: value for key, value in error_counts.items() if value != 0}
        filtered_dict_hor = {key: value for key, value in hor_error.items() if value != 0}
        # Get the length of the filtered dictionary
        length = len(filtered_dict)
        st.markdown("<h1 style='text-align: center;'>Ringkasan Singkat</h1>", unsafe_allow_html=True)
        st.markdown(divider_style, unsafe_allow_html=True)
        st.markdown("<h4 style='margin: 0;'>Informasi Mengenai Konsistensi Vertical Check</4>", unsafe_allow_html=True)
        st.markdown(f"<p><strong>{23-length}/23</strong> Tabel Sudah Konsisten", unsafe_allow_html=True)
    
    
        with st.expander("Lihat Data Tidak Konsisten Vertical Check"):
            # Create two columns for better layout
            col1, col2 = st.columns(2)
            with col1:
                for i, (sski_number, count) in enumerate(error_counts.items()):
                    if i % 2 == 0:
                        softred_background = '#ff6961'  # Soft red color hex code
                        if count != 0:
                            st.markdown(f"<p style='background-color:{softred_background}; padding: 10px; border-radius:5px; "
                            f"font-weight:bold;'>SSKI - {sski_number}: {count} mismatch(es)</p>", 
                            unsafe_allow_html=True)
                        else:
                            st.markdown(f"SSKI - {sski_number}: {count} mismatch(es)")
        
            with col2:
                for i, (sski_number, count) in enumerate(error_counts.items()):
                    if i % 2 != 0:
                        softred_background = '#ff6961'  # Soft red color hex code
                        if count != 0:
                            st.markdown(f"<p style='background-color:{softred_background}; padding: 10px; border-radius:5px; "
                            f"font-weight:bold;'>SSKI - {sski_number}: {count} mismatch(es)</p>", 
                            unsafe_allow_html=True)
                        else:
                            st.markdown(f"SSKI - {sski_number}: {count} mismatch(es)")
        
        st.markdown("<h4 style='margin: 0;'>Informasi Mengenai Konsistensi Horizontal Check</4>", unsafe_allow_html=True)
        st.markdown(f"<p><strong>{25-len(filtered_dict_hor)}/25</strong> Tabel Sudah Konsisten</p>", unsafe_allow_html=True)

        
        # Expander for horizontal mismatch counts
        with st.expander("Lihat Data Tidak Konsisten Horizontal Check"):
            col1, col2 = st.columns(2)
            with col1:
                for i, (sski_number, count) in enumerate(hor_error.items()):
                    if i % 2 == 0:
                        softred_background = '#ff6961'  # Soft red color hex code
                        if count != 0:
                            st.markdown(f"<p style='background-color:{softred_background}; padding: 10px; border-radius:5px; "
                            f"font-weight:bold;'>SSKI - {sski_number}: {count} mismatch(es)</p>", 
                            unsafe_allow_html=True)
                        else:
                            st.markdown(f"SSKI - {sski_number}: {count} mismatch(es)")
            
            with col2:
                for i, (sski_number, count) in enumerate(hor_error.items()):
                    if i % 2 != 0:
                        if count != 0:
                            st.markdown(f"<p style='background-color:{softred_background}; padding: 10px; border-radius:5px; "
                            f"font-weight:bold;'>SSKI - {sski_number}: {count} mismatch(es)</p>", 
                            unsafe_allow_html=True)
                        else:
                            st.markdown(f"SSKI - {sski_number}: {count} mismatch(es)")
            # Create a download button
        st.download_button(
            label="Unduh Data Rekap",
            data=csv,
            file_name='Data Rekap.csv',
            mime='text/csv',use_container_width=True
        )

    st.markdown(divider_style, unsafe_allow_html=True)

    # Define layout with two columns
    col1, col2 = st.columns((1, 4))
    with col1:
        checked = None
        table_list = []
        
        # Iterate through each string in clean_keys_list
        for item in clean_keys_list:
            df_clean = pd.DataFrame(clean_data[item])
            if df_clean is not None and not (len(df_clean.columns) == 2 and 'Path' in df_clean.columns):
                # Split at the first hyphen to separate number and text
                number, text = item.split('-', 1)  
                # Strip any leading/trailing spaces
                number = number.strip()

                # Check if the current number is different from the previously checked number
                if number != checked:
                    # Append the number to table_list if it's not already in the list
                    if number not in table_list:
                        table_list.append(number)
                    # Update the checked value to the current number
                    checked = number

        # Display the list of unique numbers (optional for debugging)
        st.markdown("<h4 class='centered-title'>Apa yang ingin dilakukan?</h4>", unsafe_allow_html=True)

        # Dynamically create buttons for each item in the table_list
        for table in table_list:
            if st.button(f"Lihat Konsistensi SSKI Tabel {table}",use_container_width=True):
                st.session_state.selected_table = table

    with col2:
        if 'selected_table' in st.session_state:
            selected_number = st.session_state.selected_table
            filtered_keys = [key for key in clean_keys_list if key.split('-')[0] == str(selected_number)]
            count = 0
            for i in filtered_keys:
                df_clean = pd.DataFrame(clean_data[i])
                if df_clean is not None and not (len(df_clean.columns) == 2 and 'Path' in df_clean.columns):
                    df_summary = pd.DataFrame(summary_data[i])

                    if count == 0:
                        st.markdown("<h1 class='centered-title'>VERTICAL CHECK</h1>", unsafe_allow_html=True)
                        st.subheader(f"SSKI Tabel {selected_number}")

                    number, text = i.split('-', 1)  # Split at the first hyphen
                    text = text.strip()
                    st.markdown(f"<p>{text}</p>", unsafe_allow_html=True)

                    display_dataframe(df_summary)

                    with st.expander("Lihat detail data"):
                        st.write("""
                        **Penjelasan Warna:**
                        - 🟩 : Aggregat
                        - 🟨 : Calculated
                        - 🟥 : Selisih
                        """)
                        st.dataframe(df_clean.style.apply(highlight_rows, axis=1).set_properties(
                        **{'text-align': 'center'}).set_table_styles(
                        [{'selector': 'th', 'props': [('text-align', 'center'), ('background-color', '#E8F6F3')]}]
                        ).format(precision=2))
                    count +=1
            

            if selected_number in horizontal_clean_data:
                st.markdown("<h1 class='centered-title'>HORIZONTAL CHECK</h1>", unsafe_allow_html=True)
                df_clean = pd.DataFrame(horizontal_clean_data[selected_number])
                st.subheader(f"SSKI - {selected_number}")
                st.dataframe(
                    df_clean.style.set_properties(**{'text-align': 'center'})
                    .set_table_styles([{'selector': 'th', 
                                        'props': [('text-align', 'center'), 
                                                ('background-color', '#E8F6F3')]}])
                )
                count +=1

            if count == 0:
                st.text("Tabel ini sudah konsisten")

        else:
            st.markdown("<h1 class='centered-title'>VERTICAL CHECK</h1>", unsafe_allow_html=True)
            for i in range(len(clean_data)):        
                df_clean = pd.DataFrame(clean_data[clean_keys_list[i]])
                if df_clean is not None and not (len(df_clean.columns) == 2 and 'Path' in df_clean.columns):
                    df_summary = pd.DataFrame(summary_data[sum_keys_list[i]])
                    df_clean = df_clean.drop('Path', axis=1)

                    st.markdown(divider_style, unsafe_allow_html=True)
                    number, text = clean_keys_list[i].split('-', 1)  

                    # Strip any leading/trailing spaces
                    number = number.strip()
                    st.subheader(f"SSKI Tabel {number}")
                    st.markdown(f"<p>{text}</p>", unsafe_allow_html=True)

                    display_dataframe(df_summary)

                    with st.expander("See Detail?"):
                        st.write("""
                        **Penjelasan Warna:**
                        - 🟩 : Aggregat
                        - 🟨 : Calculated
                        - 🟥 : Selisih
                        """)
                        st.dataframe(df_clean.style.apply(highlight_rows, axis=1).set_properties(
                        **{'text-align': 'center'}).set_table_styles(
                        [{'selector': 'th', 'props': [('text-align', 'center'), ('background-color', '#E8F6F3')]}]
                        ).format(precision=2))

            st.markdown("<h1 class='centered-title'>HORIZONTAL CHECK</h1>", unsafe_allow_html=True)

            table_list = ["1", "2", "3", "4", "5a", "5b", "5c", "5d", "5d.1", "5.d.2", "6", 
                                "7", "8", "9", "10", "11a", "12", "13", "14", "15", "16a", 
                                "17", "18", "19", "20"]
            for item in hor_clean_keys_list:
                df_clean = pd.DataFrame(horizontal_clean_data[item])
                st.subheader(f"SSKI - {item}")
                st.dataframe(df_clean.style.set_properties(**{'text-align': 'center'}).set_table_styles(
                    [{'selector': 'th', 'props': [('text-align', 'center'), ('background-color', '#E8F6F3')]}]
                ).format(precision=2))

# Example usage of the main function
list_tahun = ['2022']  # Define list_tahun as needed
if __name__ == "__main__":
    main()
