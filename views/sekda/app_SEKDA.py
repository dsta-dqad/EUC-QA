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
import io

divider_style = """
    <hr style="border: none; 
    height: 2px; 
    background-color: black; 
    border-radius: 10px; 
    margin: 20px 0;
    opacity: 0.2">
"""

# Set Streamlit to use the wider layout mode
# st.set_page_config(layout="wide", page_title="EUC QA")


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
    google_drive_id = "1AAjRJ8Pbje0XYJq5xw2r7tZg1K-pgF2l"
    file_path = f"https://drive.google.com/uc?export=download&id={google_drive_id}"
    response = requests.get(file_path)
    data = response.json()
    
    # File CSV
    # file_path_json = "https://drive.google.com/uc?export=download&id=1WZkdWbm-RMp4lNf5BYI7Idm5nIcGiRsQ"
    # response_json = requests.get(file_path_json)
    # json_data = response_json.json()
    # df = pd.DataFrame(json_data)
    # csv = df.to_csv(index=False)

    google_drive_id_csv = "1ubRdzJlZiWm8Mm1zGvaqcgBV5k5im1KE"
    file_path_csv = f"https://drive.google.com/uc?export=download&id={google_drive_id_csv}"
    df = pd.read_csv(file_path_csv)
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

    clean_data = data['vertikal_data_clean']
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

    summary_data = data['vertikal_data_summary']
    sum_keys_list = list(summary_data.keys())

    horizontal_clean_data = data['horizontal_clean_data']
    horizontal_clean_keys_list = list(horizontal_clean_data.keys())
    hor_filtered_keys_list = [key for key in horizontal_clean_keys_list if horizontal_clean_data.get(key, []) != []]  

    beforeafter_data = data['beforeafter_data']
    beforeafter_data_keys_list = list(beforeafter_data.keys())
    ba_filtered_keys_list = [key for key in beforeafter_data_keys_list if beforeafter_data.get(key, []) != []]
    
    final_filtered_keys_list = sorted(list(set(filtered_keys_list + hor_filtered_keys_list + ba_filtered_keys_list)))
    distinct_numbers = sorted(list(set(key.split('-')[0] for key in final_filtered_keys_list)))  

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

    total_horizontal = ringkasan_df['Total Horizontal'].values[0]
    total_vertikal = ringkasan_df['Total Vertikal'].values[0]
    total_beforeafter = ringkasan_df['Total Before After'].values[0]
    correct_count = ringkasan_df['Provinsi Lolos QA'].values[0]
    error_count = ringkasan_df['Provinsi Tidak Lolos QA'].values[0]
    total_count = ringkasan_df['Total provinsi'].values[0]
    ver_error_tabel = ringkasan_df['Error Vertikal'].values[0]
    hor_error_tabel = ringkasan_df['Error Horizontal'].values[0]
    ba_error_tabel = ringkasan_df['Error Before After'].values[0]
    periode_publikasi = ringkasan_df['Periode Publikasi'].values[0]
    total_horizontal = int(total_horizontal)
    total_vertikal = int(total_vertikal)
    total_beforeafter = int(total_beforeafter)
    correct_count = int(correct_count)
    error_count = int(error_count)
    total_count = int(total_count)
    ver_error_tabel = int(ver_error_tabel)
    hor_error_tabel = int(hor_error_tabel)
    ba_error_tabel = int(ba_error_tabel)

    # Calculate mismatch ratio
    mismatch_ratio_prov = calculate_mismatch_ratio(error_count, total_count)
    mismatch_ratio_ver = calculate_mismatch_ratio(ver_error_tabel, total_vertikal)
    mismatch_ratio_hor = calculate_mismatch_ratio(hor_error_tabel, total_horizontal)
    mismatch_ratio_ba = calculate_mismatch_ratio(ba_error_tabel, total_beforeafter)

    # Centered title using custom class
    st.markdown(f"<h1 class='centered-title'>LAPORAN QUALITY ASSURANCE SEKDA - {periode_publikasi.upper()} </h1>", unsafe_allow_html=True)
    st.markdown(divider_style, unsafe_allow_html=True)

    # Define the main two-column layout: left for pie charts and right for col4_g
    left_col, col4_g = st.columns((6, 3))  # Adjust width ratio as needed
    
    # In the left column, create two rows with two pie charts each
    with left_col:
        # First row: pie chart 1 and pie chart 2
        row1_col1, row1_col2 = st.columns(2)
        
        with row1_col1:
            st.markdown(
                "<p style='text-align: center;'><span style='font-weight: bold; text-decoration: underline;'>Rasio Konsistensi Vertical Check</span></p>",
                unsafe_allow_html=True)
            ver_correct_count = total_vertikal - ver_error_tabel
            create_pie_chart(ver_error_tabel, ver_correct_count, "Konsisten", "Tidak Konsisten")
            st.markdown(
                f"<p style='text-align: center;'><span style='font-weight: bold; text-decoration: underline;'>{mismatch_ratio_ver:.2f}%</span> data tidak konsisten.</p>",
                unsafe_allow_html=True)
    
        with row1_col2:
            st.markdown(
                "<p style='text-align: center;'><span style='text-align: center;font-weight: bold; text-decoration: underline;'>Rasio Konsistensi Horizontal Check</span></p>",
                unsafe_allow_html=True)
            hor_correct_count = total_horizontal - hor_error_tabel
            create_pie_chart(hor_error_tabel, hor_correct_count, "Konsisten", "Tidak Konsisten")
            st.markdown(
                f"<p style='text-align: center;'><span style='font-weight: bold; text-decoration: underline;'>{mismatch_ratio_hor:.2f}%</span> data tidak konsisten.</p>",
                unsafe_allow_html=True)
    
        # Second row: pie chart 3 and pie chart 4
        row2_col1, row2_col2 = st.columns(2)
        
        with row2_col1:
            st.markdown(
                "<p style='text-align: center;'><span style='text-align: center;font-weight: bold; text-decoration: underline;'>Rasio Konsistensi Before After Check</span></p>",
                unsafe_allow_html=True)
            ba_correct_count = total_beforeafter - ba_error_tabel
            create_pie_chart(ba_error_tabel, ba_correct_count, "Konsisten", "Tidak Konsisten")
            st.markdown(
                f"<p style='text-align: center;'><span style='font-weight: bold; text-decoration: underline;'>{mismatch_ratio_ba:.2f}%</span> data tidak konsisten.</p>",
                unsafe_allow_html=True)
    
        with row2_col2:
            st.markdown(
                "<p style='text-align: center;'><span style='text-align: center;font-weight: bold; text-decoration: underline;'>Rasio Provinsi Lolos dan Tidak Lolos QA</span></p>",
                unsafe_allow_html=True)
            create_pie_chart(error_count, correct_count, "Lolos", "Tidak Lolos")
            st.markdown(
                f"<p style='text-align: center;'><span style='font-weight: bold; text-decoration: underline;'>{mismatch_ratio_prov:.2f}%</span> provinsi tidak lolos.</p>",
                unsafe_allow_html=True)
    
    # Right column for col4_g
    with col4_g:
        st.markdown("<h1 style='text-align: center;'>Ringkasan Singkat</h1>", unsafe_allow_html=True)
        st.markdown(divider_style, unsafe_allow_html=True)
        # Use an expander to show the dataframe in a dropdown-like view
        with st.expander("Lihat rincian:"):
            st.markdown(html_rincian_df, unsafe_allow_html=True)
        
        st.download_button(
            label="Unduh Data Rekapitulasi",
            data=csv,
            file_name='Data Rekap Uji Konsistensi.csv',
            mime='text/csv',use_container_width=True
        )

    col1, col2 = st.columns((1, 4))

    if "show_all_results_verti" not in st.session_state:
        st.session_state.show_all_results_verti = False
    if "show_all_results_hori" not in st.session_state:
        st.session_state.show_all_results_hori = False
    if "show_all_results_beforeafter" not in st.session_state:
        st.session_state.show_all_results_beforeafter = False
    if "selected_table" not in st.session_state:
        st.session_state.selected_table = None

    with col1:
        st.markdown("<h4 style='text-align: left;'>Apa yang ingin dilakukan?</h4>", unsafe_allow_html=True)

        if st.button("Lihat Hasil Vertikal Check Keseluruhan"):
            st.session_state.show_all_results_verti = True
            st.session_state.show_all_results_hori = False
            st.session_state.show_all_results_beforeafter = False
            st.session_state.selected_table = None

        if st.button("Lihat Hasil Horizontal Check Keseluruhan"):
            st.session_state.show_all_results_verti = False
            st.session_state.show_all_results_hori = True
            st.session_state.show_all_results_beforeafter = False
            st.session_state.selected_table = None

        if st.button("Lihat Hasil Before After Check Keseluruhan"):
            st.session_state.show_all_results_verti = False
            st.session_state.show_all_results_hori = False
            st.session_state.show_all_results_beforeafter = True
            st.session_state.selected_table = None

        # Create a button for each distinct number, replace number with province name
        for num in distinct_numbers:
            # Get the province name from the mapping, default to num if not found
            province_name = provinsi_mapping.get(num, [num])[0]

            # Create an expander (dropdown) for each province
            with st.expander(f"Lihat hasil Provinsi {province_name}"):
                # Inside the expander, display buttons for matching keys from filtered_keys_list
                matching_keys = [key for key in final_filtered_keys_list if key.startswith(num)]
                for table in matching_keys:
                    table_label = table.split('-')[1]

                    # Use a unique key for each button by appending the full table name
                    if st.button(f"Lihat Tabel {table_label}", key=f"button_{table}"):
                        st.session_state.selected_table = table
                        st.session_state.show_all_results_verti = False
                        st.session_state.show_all_results_hori = False
                        st.session_state.show_all_results_beforeafter = False


    with col2:
        if 'selected_table' in st.session_state and st.session_state.selected_table:
            selected_number = st.session_state.selected_table
            filtered_keys = [key for key in clean_keys_list if key.startswith(selected_number)]
            for i in filtered_keys:
                df_clean = pd.DataFrame(clean_data[i])
                if df_clean is not None and not df_clean.empty and not (len(df_clean.columns) == 2 and 'Keterangan' in df_clean.columns):
                    st.markdown("<h1 class='centered-title'>VERTICAL CHECK</h1>", unsafe_allow_html=True)
                    df_summary = pd.DataFrame(summary_data[i])
                    st.markdown(divider_style, unsafe_allow_html=True)
                    kode_provinsi, tabel = i.split('-')
                    nama_provinsi = provinsi_mapping.get(kode_provinsi, ['Unknown'])[0]
                    i_new = f"{nama_provinsi} ({kode_provinsi}) - Tabel {tabel}"

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

            if selected_number in horizontal_clean_data:
                df_clean_hori = pd.DataFrame(horizontal_clean_data[selected_number])
                if df_clean_hori is not None and not df_clean_hori.empty:
                    st.markdown("<h1 class='centered-title'>HORIZONTAL CHECK</h1>", unsafe_allow_html=True)
                    kode_provinsi, tabel = selected_number.split('-')
                    nama_provinsi = provinsi_mapping.get(kode_provinsi, ['Unknown'])[0]
                    selected_number_new = f"{nama_provinsi} ({kode_provinsi}) - Tabel {tabel}"
                    st.subheader(f"{selected_number_new}")
                    st.dataframe(
                        df_clean_hori.style.set_properties(**{'text-align': 'center'})
                            .set_table_styles([{'selector': 'th',
                                                'props': [('text-align', 'center'),
                                                          ('background-color', '#E8F6F3')]}])
                    )
                    st.markdown('**Keterangan**')
                    st.text('✓: Data sudah konsisten pada periode tersebut')

            if selected_number in beforeafter_data:
                df_clean_ba = pd.DataFrame(beforeafter_data[selected_number])
                if df_clean_ba is not None and not df_clean_ba.empty:
                    st.markdown("<h1 class='centered-title'>BEFORE AFTER CHECK</h1>", unsafe_allow_html=True)
                    kode_provinsi, tabel = selected_number.split('-')
                    nama_provinsi = provinsi_mapping.get(kode_provinsi, ['Unknown'])[0]
                    selected_number_new = f"{nama_provinsi} ({kode_provinsi}) - Tabel {tabel}"
                    st.subheader(f"{selected_number_new}")
                    st.dataframe(
                        df_clean_ba.style.set_properties(**{'text-align': 'center'})
                            .set_table_styles([{'selector': 'th',
                                                'props': [('text-align', 'center'),
                                                          ('background-color', '#E8F6F3')]}])
                    )
                    st.markdown('**Keterangan**')
                    st.text('✓: Data sudah konsisten pada periode tersebut')

        if st.session_state.show_all_results_verti:
            st.markdown("<h1 class='centered-title'>VERTICAL CHECK</h1>", unsafe_allow_html=True)
            for i in range(len(clean_data)):
                df_clean = pd.DataFrame(clean_data[clean_keys_list[i]])
                if df_clean is not None and not df_clean.empty and not (len(df_clean.columns) == 2 and 'Keterangan' in df_clean.columns):
                    df_summary = pd.DataFrame(summary_data[sum_keys_list[i]])
                    kode_provinsi, tabel = clean_keys_list[i].split('-')
                    nama_provinsi = provinsi_mapping.get(kode_provinsi, ['Unknown'])[0]
                    inew = f"{nama_provinsi} ({kode_provinsi}) - Tabel {tabel}"
    
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
                        st.dataframe(df_clean.style.apply(lambda row: highlight_rows(row, df_clean), axis=1)
                            .set_properties(**{'text-align': 'center'})  # Set text alignment to center
                            .set_table_styles([  # Apply styling to the header
                            {'selector': 'th', 'props': [('text-align', 'center'), ('background-color', '#E8F6F3')]}])
                            .format(precision=2)  # Format numerical values with two decimal places
                        )
                        
        elif st.session_state.show_all_results_hori:
            st.markdown("<h1 class='centered-title'>HORIZONTAL CHECK</h1>", unsafe_allow_html=True)
            for item in horizontal_clean_keys_list:
                df_clean_hori = pd.DataFrame(horizontal_clean_data[item])
                if df_clean_hori is not None and not df_clean_hori.empty:
                    kode_provinsi, tabel = item.split('-')
                    nama_provinsi = provinsi_mapping.get(kode_provinsi, ['Unknown'])[0]
                    item_new = f"{nama_provinsi} ({kode_provinsi}) - Tabel {tabel}"
                    st.subheader(f"{item_new}")
                    st.dataframe(df_clean_hori.style.set_properties(**{'text-align': 'center'}).set_table_styles(
                        [{'selector': 'th', 'props': [('text-align', 'center'), ('background-color', '#E8F6F3')]}]
                    ).format(precision=2))
                    st.markdown('**Keterangan**')
                    st.text('✓: Data sudah konsisten pada periode tersebut')

        elif st.session_state.show_all_results_beforeafter:
            st.markdown("<h1 class='centered-title'>BEFORE AFTER CHECK</h1>", unsafe_allow_html=True)
            for item in beforeafter_data_keys_list:
                df_clean_ba = pd.DataFrame(beforeafter_data[item])
                if df_clean_ba is not None and not df_clean_ba.empty:
                    kode_provinsi, tabel = item.split('-')
                    nama_provinsi = provinsi_mapping.get(kode_provinsi, ['Unknown'])[0]
                    item_new = f"{nama_provinsi} ({kode_provinsi}) - Tabel {tabel}"
                    st.subheader(f"{item_new}")
                    st.dataframe(df_clean_ba.style.set_properties(**{'text-align': 'center'}).set_table_styles(
                        [{'selector': 'th', 'props': [('text-align', 'center'), ('background-color', '#E8F6F3')]}]
                    ).format(precision=2))
                    st.markdown('**Keterangan**')
                    st.text('✓: Data sudah konsisten pada periode tersebut')
                            
        elif not st.session_state.selected_table and not (st.session_state.show_all_results_verti or 
                                                      st.session_state.show_all_results_hori or 
                                                      st.session_state.show_all_results_beforeafter):
            st.markdown("<h1 class='centered-title'>VERTICAL CHECK</h1>", unsafe_allow_html=True)
            for i in range(len(clean_data)):
                df_clean = pd.DataFrame(clean_data[clean_keys_list[i]])
                if df_clean is not None and not df_clean.empty and not (len(df_clean.columns) == 2 and 'Keterangan' in df_clean.columns):
                    df_summary = pd.DataFrame(summary_data[sum_keys_list[i]])
                    kode_provinsi, tabel = clean_keys_list[i].split('-')
                    nama_provinsi = provinsi_mapping.get(kode_provinsi, ['Unknown'])[0]
                    inew = f"{nama_provinsi} ({kode_provinsi}) - Tabel {tabel}"

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
                        
            st.markdown("<h1 class='centered-title'>HORIZONTAL CHECK</h1>", unsafe_allow_html=True)
            for item in horizontal_clean_keys_list:
                df_clean_hori = pd.DataFrame(horizontal_clean_data[item])
                if df_clean_hori is not None and not df_clean_hori.empty:
                    kode_provinsi, tabel = item.split('-')
                    nama_provinsi = provinsi_mapping.get(kode_provinsi, ['Unknown'])[0]
                    item_new = f"{nama_provinsi} ({kode_provinsi}) - Tabel {tabel}"
                    st.subheader(f"{item_new}")
                    st.dataframe(df_clean_hori.style.set_properties(**{'text-align': 'center'}).set_table_styles(
                        [{'selector': 'th', 'props': [('text-align', 'center'), ('background-color', '#E8F6F3')]}]
                    ).format(precision=2))
                    st.markdown('**Keterangan**')
                    st.text('✓: Data sudah konsisten pada periode tersebut')

            st.markdown("<h1 class='centered-title'>BEFORE AFTER CHECK</h1>", unsafe_allow_html=True)
            for item in beforeafter_data_keys_list:
                df_clean_ba = pd.DataFrame(beforeafter_data[item])
                if df_clean_ba is not None and not df_clean_ba.empty:
                    kode_provinsi, tabel = item.split('-')
                    nama_provinsi = provinsi_mapping.get(kode_provinsi, ['Unknown'])[0]
                    item_new = f"{nama_provinsi} ({kode_provinsi}) - Tabel {tabel}"
                    st.subheader(f"{item_new}")
                    st.dataframe(df_clean_ba.style.set_properties(**{'text-align': 'center'}).set_table_styles(
                        [{'selector': 'th', 'props': [('text-align', 'center'), ('background-color', '#E8F6F3')]}]
                    ).format(precision=2))
                    st.markdown('**Keterangan**')
                    st.text('✓: Data sudah konsisten pada periode tersebut')

if __name__ == "__main__":
    main()
