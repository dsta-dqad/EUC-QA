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

divider_style = """
    <hr style="border: none; 
    height: 2px; 
    background-color: black; 
    border-radius: 10px; 
    margin: 20px 0;
    opacity: 0.2">
"""

def create_pie_chart(miss_data, corr_data, a, b):
    options = {
        "tooltip": {"trigger": "item"},
        "legend": {
            "top": "5%",
            "left": "center",
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
                    {"value": miss_data, "name": b, "itemStyle": {"color": "#ff6961"}},  # Soft red for mismatch
                    {"value": corr_data, "name": a, "itemStyle": {"color": "#90ee90"}},  # Soft green for correct
                ],
            }
        ],
    }

    st_echarts(
        options=options, height="300px",
    )


def main():
    #file_path = "https://univindonesia-my.sharepoint.com/personal/annisa_zahra01_office_ui_ac_id/_layouts/15/download.aspx?share=Eb1RKnVLiYtGrdEtL03KxE0BCDODJE6LBw9VZ_VyTkBEvA"
    file_path = "https://drive.google.com/uc?export=download&id=1Yp4laeW-W6h4fPQTotZyM80qe3PLVVPA"
    response = requests.get(file_path)
    data = response.json()
    
    # File CSV
    # file_path_json = "https://drive.google.com/uc?export=download&id=1MgvKLLj8hao-qzt-iF2Tqm4MEL6zxqrs"
    # response_json = requests.get(file_path_json)
    # json_data = response_json.json()
    # df = pd.DataFrame(json_data)
    # csv = df.to_csv(index=False)
    
    file_path_csv = "https://drive.google.com/uc?export=download&id=1GwiUWyqbz2wrPR4xv1KT1huKO8MeafvZ"
    df = pd.DataFrame(file_path_csv)
    csv = df.to_csv(index=False)

    log_data = data["log_data"]

    col1a, col2a = st.columns([1, 3]) 
    
    with col1a:
        if st.button("Kembali Ke Halaman Utama"):
            st.session_state['page'] = 'main'

    with col2a:
        st.markdown(
            f"<p style='text-align: right; font-size:13px;'>Di proses pada {log_data['created_at']} WIB</p>",
            unsafe_allow_html=True
        )
        
    # Custom CSS to apply Frutiger45 font to the entire page using an external font link
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


    # Centralized styling for the DataFrames
    dataframe_style = {
        'text-align': 'center',
        'background-color': '#E8F6F3'
    }

    def highlight_rows(row, df):
        # Apply green to the first row
        if row.name == 0:
            return ['background-color: #A9DFBF; color: black'] * len(row)  # Green background for the first row

        # Apply red if 'Keterangan' is 'Selisih'
        elif row['Keterangan'] == 'Selisih':
            return ['background-color: #F1948A; color: black'] * len(row)  # Red background

        # Apply green to the row after a 'Selisih' row
        elif row.name > 0 and df.iloc[row.name - 1]['Keterangan'] == 'Selisih':
            return ['background-color: #A9DFBF; color: black'] * len(row)  # Green background

        # Apply yellow for all other rows
        else:
            return ['background-color: #F9E79F; color: black'] * len(row)  # Yellow background for other rows

    # Function to display the DataFrame
    def display_dataframe(input_df):
        st.dataframe(input_df.style.set_properties(**{'text-align': 'center'}).set_table_styles(
            [{'selector': 'th', 'props': [('text-align', 'center'), ('background-color', '#E8F6F3')]}]
        ).format(precision=2))


    raw_data = data['data_raw']
    raw_keys_list = list(raw_data.keys())

    clean_data = data['data_clean']
    clean_keys_list = list(clean_data.keys())
    filtered_keys_list = [key for key in clean_keys_list if clean_data.get(key, []) != []]

    # Province mapping
    provinsi_mapping = {
        '11': ['Aceh'],
        '36': ['Banten'],
        '17': ['Bengkulu'],
        '34': ['DI Yogyakarta'],
        '31': ['DKI Jakarta'],
        '75': ['Gorontalo'],
        '15': ['Jambi'],
        '14': ['Riau'],
        '32': ['Jawa Barat'],
        '33': ['Jawa Tengah'],
        '35': ['Jawa Timur'],
        '61': ['Kalimantan Barat'],
        '63': ['Kalimantan Selatan'],
        '62': ['Kalimantan Tengah'],
        '64': ['Kalimantan Timur'],
        '65': ['Kalimantan Utara'],
        '19': ['Kepulauan Bangka belitung'],
        '21': ['Kepulauan Riau'],
        '18': ['Lampung'],
        '81': ['Maluku'],
        '82': ['Maluku Utara'],
        '52': ['Nusa Tenggara Barat'],
        '53': ['Nusa Tenggara Timur'],
        '91': ['Papua'],
        '92': ['Papua Barat'],
        '76': ['Sulawesi Barat'],
        '73': ['Sulawesi Selatan'],
        '72': ['Sulawesi Tengah'],
        '74': ['Sulawesi Tenggara'],
        '71': ['Sulawesi Utara'],
        '13': ['Sumatera Barat'],
        '16': ['Sumatera Selatan'],
        '12': ['Sumatera Utara'],
        '51': ['Bali']
    }

    summary_data = data['data_summary']
    sum_keys_list = list(summary_data.keys())

    rincian_data = data['rincian_data']
    rincian_df = pd.DataFrame(rincian_data)
    html_rincian_df = rincian_df.to_html(escape=False, index=False)

    ringkasan_data = data['ringkasan_data']
    ringkasan_df = pd.DataFrame(ringkasan_data)

    def calculate_mismatch_ratio(error_count, total_count):
        # Avoid division by zero
        if total_count == 0:
            return 0  # If no data, return 0
        return (error_count / total_count) * 100

    correct_count = ringkasan_df['Provinsi Lolos QA'].values[0]
    error_count = ringkasan_df['Provinsi Tidak Lolos QA'].values[0]
    total_count = ringkasan_df['Total provinsi'].values[0]
    periode_publikasi = ringkasan_df['Periode Publikasi'].values[0]
    correct_count = int(correct_count)
    error_count = int(error_count)
    total_count = int(total_count)

    # Calculate mismatch ratio
    mismatch_ratio_prov = calculate_mismatch_ratio(error_count, total_count)

    # Centered title using custom class
    st.markdown(f"<h1 class='centered-title'>LAPORAN QUALITY ASSURANCE SEKDA - {periode_publikasi.upper()} </h1>", unsafe_allow_html=True)
    st.markdown(divider_style, unsafe_allow_html=True)

    col1_g, col2_g = st.columns((2, 2))

    with col1_g:
        st.markdown(
            "<p style='text-align: center;'><span style='text-align: center;font-weight: bold; text-decoration: underline;'>Rasio Provinsi Lolos dan Tidak Lolos QA</span></p>",
            unsafe_allow_html=True)

        # Create pie chart with mismatch (errors) and correct counts
        create_pie_chart(error_count, correct_count, "Lolos", "Tidak Lolos")

        # Display the mismatch ratio as a percentage
        st.markdown(
            f"<p style='text-align: center;'><span style='font-weight: bold; text-decoration: underline;'>{mismatch_ratio_prov:.2f}%</span> provinsi tidak lolos.</p>",
            unsafe_allow_html=True)

    with col2_g:
        st.markdown("<h1 style='text-align: center;'>Ringkasan Singkat</h1>", unsafe_allow_html=True)
        st.markdown(divider_style, unsafe_allow_html=True)
        # Use an expander to show the dataframe in a dropdown-like view
        with st.expander("Lihat rincian:"):
            st.markdown(html_rincian_df, unsafe_allow_html=True)

        st.download_button(
            label="Unduh Data Rekapitulasi",
            data=csv,
            file_name='Data Rekap Antar Tabel.csv',
            mime='text/csv',use_container_width=True
        )

    # Define layout with two columns
    col1, col2 = st.columns((1, 4))

    with col1:
        st.text("Apa yang ingin dilakukan?")

        # Create a button for each distinct number, replace number with province name
        for num in filtered_keys_list:
            # Get the province name from the mapping, default to num if not found
            province_name = provinsi_mapping.get(num, [num])[0]

            # Inside the expander, display buttons for matching keys from filtered_keys_list
            matching_keys = [key for key in filtered_keys_list if key.startswith(num)]
            print(f'matching_keys : {matching_keys}')
                # Use a unique key for each button by appending the full table name
            if st.button(f"Lihat hasil Provinsi {province_name}", key=f"button_{province_name}"):
                st.session_state.selected_table = matching_keys

    with col2:
        if 'selected_table' in st.session_state:
            selected_number = st.session_state.selected_table
            selected_number = selected_number[0]
            filtered_keys = [key for key in clean_keys_list if key.startswith(selected_number)]
            for i in filtered_keys:
                df_clean = pd.DataFrame(clean_data[i])
                if df_clean is not None and not df_clean.empty and not (len(df_clean.columns) == 2 and 'Keterangan' in df_clean.columns):
                    df_summary = pd.DataFrame(summary_data[i])
                    st.markdown(divider_style, unsafe_allow_html=True)
                    kode_provinsi = i
                    nama_provinsi = provinsi_mapping.get(kode_provinsi, ['Unknown'])[0]
                    i_new = f"{nama_provinsi} ({kode_provinsi})"

                    st.subheader(f"{i_new}")

                    display_dataframe(df_summary)

                    st.markdown('**Keterangan**')
                    st.text('✓: Data sudah konsisten pada periode tersebut')

                    with st.expander("Lihat Detail"):
                        st.write("""
                        **Penjelasan Warna:**
                        - 🟩 : Aggregat
                        - 🟨 : Calculated
                        - 🟥 : Selisih
                        """)
                        st.dataframe(df_clean.style.apply(lambda row: highlight_rows(row, df_clean),axis=1)
                        .set_properties(**{'text-align': 'center'})  # Set text alignment to center
                        .set_table_styles([  # Apply styling to the header
                        {'selector': 'th', 'props': [('text-align', 'center'), ('background-color', '#E8F6F3')]}])
                        .format(precision=2)  # Format numerical values with two decimal places
                        )


        else:
            for i in range(len(clean_data)):
                df_clean = pd.DataFrame(clean_data[clean_keys_list[i]])
                if df_clean is not None and not df_clean.empty and not (len(df_clean.columns) == 2 and 'Keterangan' in df_clean.columns):
                    df_summary = pd.DataFrame(summary_data[sum_keys_list[i]])
                    kode_provinsi = clean_keys_list[i]
                    nama_provinsi = provinsi_mapping.get(kode_provinsi, ['Unknown'])[0]
                    inew = f"{nama_provinsi} ({kode_provinsi})"

                    st.markdown(divider_style, unsafe_allow_html=True)
                    st.subheader(f"{inew}")

                    display_dataframe(df_summary)
                    st.markdown('**Keterangan**')
                    st.text('✓: Data sudah konsisten pada periode tersebut')

                    with st.expander("Lihat Detail"):
                        st.write("""
                        **Penjelasan Warna:**
                        - 🟩 : Aggregat
                        - 🟨 : Calculated
                        - 🟥 : Selisih
                        """)
                        st.dataframe(df_clean.style.apply(lambda row: highlight_rows(row, df_clean),axis=1)
                        .set_properties(**{'text-align': 'center'})  # Set text alignment to center
                        .set_table_styles([  # Apply styling to the header
                        {'selector': 'th', 'props': [('text-align', 'center'), ('background-color', '#E8F6F3')]}])
                        .format(precision=2)  # Format numerical values with two decimal places
                        )

# Example usage of the main function
list_tahun = []  # Define list_tahun as needed
if __name__ == "__main__":
    main()
