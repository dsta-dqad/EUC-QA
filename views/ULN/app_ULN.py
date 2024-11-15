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
    google_drive_id = "1iQW7p_PC7RC7a1sQPk47sZDb29CHCdcj"
    file_path = f"https://drive.google.com/uc?export=download&id={google_drive_id}"
    response = requests.get(file_path)
    data = response.json()
    
    # File CSV
    # file_path_json = "https://drive.google.com/uc?export=download&id=1WZkdWbm-RMp4lNf5BYI7Idm5nIcGiRsQ"
    # response_json = requests.get(file_path_json)
    # json_data = response_json.json()
    # df = pd.DataFrame(json_data)
    # csv = df.to_csv(index=False)

    google_drive_id_csv = "1e-WYFymKuogUST0DDcP9A8Go_gCNB0Bz"
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

    # def highlight_rows(row, df):
    #     # Apply green to the first row
    #     if row.name == 0:
    #         return ['background-color: #A9DFBF; color: black'] * len(row)  # Green background for the first row

    #     # Apply red if 'Keterangan' is 'Selisih'
    #     elif row['Keterangan'] == 'Selisih':
    #         return ['background-color: #F1948A; color: black'] * len(row)  # Red background

    #     # Apply green to the row after a 'Selisih' row
    #     elif row.name > 0 and df.iloc[row.name - 1]['Keterangan'] == 'Selisih':
    #         return ['background-color: #A9DFBF; color: black'] * len(row)  # Green background

    #     # Apply yellow for all other rows
    #     else:
    #         return ['background-color: #F9E79F; color: black'] * len(row)  # Yellow background for other rows

    def highlight_rows(row, df):
        
        # Apply green to the first row
        if 'SULNI.' in row['Keterangan']:
            return ['background-color: #B381D9; color: black'] * len(row)  # Red background
            
        # Apply red if 'Keterangan' is 'Selisih'
        elif row['Keterangan'] == 'Selisih':
            return ['background-color: #F1948A; color: black'] * len(row)  # Red background

        # Apply green to the row after a 'Selisih' row
        elif 'SEKI.' in row['Keterangan']:
            return ['background-color: #A9DFBF; color: black'] * len(row)  # Green background

        # Apply yellow for all other rows
        else:
            return ['background-color: #83CBEB; color: black'] * len(row)  # Yellow background for other rows


    # Function to display the DataFrame
    def display_dataframe(input_df):
        st.dataframe(input_df.style.set_properties(**{'text-align': 'center'}).set_table_styles(
            [{'selector': 'th', 'props': [('text-align', 'center'), ('background-color', '#E8F6F3')]}]
        ).format(precision=2))

    clean_data = data['df_clean']
    summary_data = data['df_summary']
    ringkasan_data = data['ringkasan_data']
    ringkasan_df = pd.DataFrame(ringkasan_data)
    periode_publikasi = data['periode']['periode']
    

    def calculate_mismatch_ratio(error_count, total_count):
        # Avoid division by zero
        if total_count == 0:
            return 0  # If no data, return 0
        return (error_count / total_count) * 100

    total_sel = ringkasan_df['Jumlah Sel'].values[0]
    total_selisih = ringkasan_df['Jumlah Selisih'].values[0]
    total_benar = ringkasan_df['Jumlah Benar'].values[0]
    total_sel = int(total_sel)
    total_selisih = int(total_selisih)
    total_benar = int(total_benar)

    # Calculate mismatch ratio
    mismatch_ratio = calculate_mismatch_ratio(total_selisih, total_sel)

    # Centered title using custom class
    st.markdown(f"<h1 class='centered-title'>LAPORAN QUALITY ASSURANCE ANTAR PUBLIKASI KOMPONEN ULN - {periode_publikasi.upper()} </h1>", unsafe_allow_html=True)
    st.markdown(divider_style, unsafe_allow_html=True)

    # Define the main two-column layout: left for pie charts and right for col4_g
    col1_g, col2_g = st.columns((3, 6))  # Adjust width ratio as needed
    
    # In the left column, create two rows with two pie charts each
    with col1_g:
        st.markdown(
            "<p style='text-align: center;'><span style='font-weight: bold; text-decoration: underline;'>Rasio Konsistensi Antar Publikasi Komponen ULN</span></p>",
            unsafe_allow_html=True)
        create_pie_chart(total_selisih, total_benar, "Konsisten", "Tidak Konsisten")
        st.markdown(
            f"<p style='text-align: center;'><span style='font-weight: bold; text-decoration: underline;'>{mismatch_ratio:.2f}%</span> data tidak konsisten.</p>",
            unsafe_allow_html=True)
    
    
    # Right column for col4_g
    with col2_g:
        st.download_button(
            label="Unduh Data Rekapitulasi",
            data=csv,
            file_name='Data Rekap Uji Konsistensi.csv',
            mime='text/csv',use_container_width=True
        )
        
    df_summary = pd.DataFrame(summary_data)
    if df_summary is not None and not df_summary.empty and not (len(df_summary.columns) == 2 and 'Keterangan' in df_summary.columns):
        df_clean = pd.DataFrame(clean_data)
        st.markdown(divider_style, unsafe_allow_html=True)
        display_dataframe(df_clean)

        st.markdown('**Keterangan**')
        st.text('✓: Data sudah konsisten pada periode tersebut')

        with st.expander("Lihat Detail"):
            st.write("""
            **Penjelasan Warna:**
            - 🟦 : Komponen SDDS:External Debt 
            - 🟪 : Komponen SULNI
            - 🟩 : Komponen SEKI
            - 🟥 : Selisih
            """)
            st.dataframe(df_summary.style.apply(lambda row: highlight_rows(row, df_summary),axis=1)
            .set_properties(**{'text-align': 'center'})  # Set text alignment to center
            .set_table_styles([  # Apply styling to the header
            {'selector': 'th', 'props': [('text-align', 'center'), ('background-color', '#E8F6F3')]}])
            .format(precision=2)  # Format numerical values with two decimal places
            )


# Example usage of the main function
if __name__ == "__main__":
    main()
