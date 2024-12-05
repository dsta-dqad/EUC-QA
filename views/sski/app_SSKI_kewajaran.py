import numpy as np
import pandas as pd
from collections import Counter
from datetime import datetime
import streamlit as st # type: ignore
from streamlit_echarts import st_echarts # type: ignore

# st.set_page_config(layout="wide", page_title="EUC QA", page_icon="📊")
file_id = "1RUM0EHWnV1bAmxlTRBZ0UMEfCBkcBIeU"
raw_df = pd.read_csv(f'https://drive.google.com/uc?export=download&id={file_id}', sep=";")

divider_style = """
    <hr style="border: none; 
    height: 2px; 
    background-color: black; 
    border-radius: 10px; 
    margin: 20px 0;
    opacity: 0.2">
"""

def pivot_dataframe(input_df, raw_df):
    # Preserve the original order of "Periode" as it appears in input_df
    unique_periods = input_df["Periode"].unique()
    input_df.fillna("-", inplace=True)
    # Pivot the dataframe
    formatted_df = input_df.pivot_table(
        index=["No_Komponen", "Komponen"],  # Rows
        columns="Periode",                 # Columns
        values="Nilai",                    # Values
        aggfunc="first"                    # Aggregation function
    )
    
    # Reorder columns to match the original order of "Periode"
    formatted_df = formatted_df[unique_periods]

    # Reset index and clean up
    formatted_df.reset_index(inplace=True)
    formatted_df.rename(columns={"No_Komponen": "No."}, inplace=True)
    formatted_df.columns.name = None  
    formatted_df.fillna("-", inplace=True) 

    # Identify outliers
    outlier_values = raw_df[raw_df["Outlier"] == "Ya"]["Nilai"].values

    # Highlight cells if they are outliers
    def highlight_outliers(cell):
        if cell in outlier_values:
            return "background-color: #CBF3F9"
        return ""

    # Apply highlighting using a style
    styled_df = formatted_df.style.applymap(highlight_outliers)

    return formatted_df, styled_df



def show_dropdown(sheet_to_check, start_df):
    placeholder = f'Pilih Komponen Tabel {sheet_to_check}'
    if 'selected_component' not in st.session_state:
        st.session_state['selected_component'] = placeholder
    # Dropdown for selecting component
    components = [placeholder] + [
        f"{row['No.']} - {row['Komponen']} - Tabel {sheet_to_check}"
        for _, row in start_df.iterrows()
    ]
    selected_component = st.selectbox("Lihat Grafik Data Komponen:", components)

    # Update session state if selection changes
    if selected_component != st.session_state.selected_component:
        st.session_state.selected_component = selected_component

    # Process component selection
    if st.session_state.selected_component != placeholder:
        selected_no, selected_komponen, selected_table = st.session_state.selected_component.split(" - ")
        filtered_data = start_df[(start_df['No.'] == int(selected_no)) & (start_df['Komponen'] == selected_komponen)]

        if not filtered_data.empty:
            # Display selected item information and plot
            number = filtered_data.iloc[0]['No.']
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


                if "-" in raw_df[raw_df["Tabel"] == sheet_to_check.split(":")[0].strip()]["Detail"].unique():
                    filtered_outliers = raw_df[
                        (raw_df['No_Komponen'] == number) & 
                        (raw_df['Komponen'] == component) & 
                        (raw_df['Tabel'] == sheet_to_check.split(":")[0].strip())
                    ]
                else:
                    filtered_outliers = raw_df[
                        (raw_df['No_Komponen'] == number) & 
                        (raw_df['Komponen'] == component) & 
                        (raw_df['Tabel'] == sheet_to_check.split(":")[0].strip()) &
                        (raw_df["Detail"] ==  sheet_to_check.split(":")[1].strip())
                    ]

                outlier_count = len(filtered_outliers[filtered_outliers["Outlier"] == "Ya"])

                with col2_e:
                    card_component("Jumlah Pencilan", outlier_count)
                with col3_e:
                    card_component("Mean Data", mean_data)
                with col4_e:
                    card_component("Median Data", median_data)


                # Convert 'Nilai' to numeric (if not already)
                filtered_outliers["Nilai"] = pd.to_numeric(filtered_outliers["Nilai"], errors='coerce')

                # Extract the relevant columns for plotting (Periode and Nilai)
                plot_data = filtered_outliers[["Periode", "Nilai"]].dropna()

                # Prepare the x and y values for plotting
                x_values = plot_data["Periode"].tolist()
                y_values = plot_data["Nilai"].tolist()

                # Prepare the outlier data (filtering based on 'Outlier' column)
                outlier_rows = filtered_outliers[filtered_outliers["Outlier"] == "Ya"]
                outlier_x = outlier_rows["Periode"].tolist()
                outlier_y = outlier_rows["Nilai"].tolist()

                # Extract batas atas and batas bawah from the DataFrame (assuming they are columns in filtered_outliers)
                batas_atas = filtered_outliers["Batas Atas"].iloc[0]  # Take the first value if they are the same across the dataset
                batas_bawah = filtered_outliers["Batas Bawah"].iloc[0]  # Similarly for Batas_Bawah


                # Create outliers list for ECharts
                outliers = [{'xAxis': x, 'yAxis': y} for x, y in zip(outlier_x, outlier_y)]

                # Define the ECharts options
                options = {
                    "title": {"text": f"Pergerakan Nilai {component}", "left": "center"},
                    "tooltip": {"trigger": "axis"},
                    "xAxis": {
                        "type": "category",
                        "data": [str(x) for x in x_values],  # Ensure the periods are treated as strings
                        "axisLabel": {"rotate": 45}  # Rotate x-axis labels for better readability
                    },
                    "yAxis": {"type": "value"},
                    "series": [
                        {
                            "name": "Nilai",
                            "type": "line",
                            "data": y_values,
                            "lineStyle": {"color": "black", "width": 2},
                            # Add markLine for Batas Atas and Batas Bawah here
                            "markLine": {
                                "data": [
                                    {"name": "Batas Atas", "yAxis": batas_atas, "lineStyle": {"color": "blue", "type": "solid"}},
                                    {"name": "Batas Bawah", "yAxis": batas_bawah, "lineStyle": {"color": "blue", "type": "solid"}}
                                ]
                            },
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
                # Render EChart in Streamlit (you can use st_echarts if you are in Streamlit)
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

def main():
    st.title("UJI KEWAJARAN SSKI NOVEMBER 2024")

    sheet_names = ["1","2","3","4","5a","5b","5c","5d","5d.1","5.d.2","6","7","8","9","10","11","11a","12","13","14","15","16","16a","17","18","19","20"]
    
    # raw_df = pd.read_csv("/Users/ferroyudisthira/Downloads/data_pencilan_sski (2).csv", sep=",")

    col1_o, col2_o = st.columns((1.7, 2))

    with col1_o:
        st.title("RINGKASAN SINGKAT")

        st.subheader("Ringkasan Komponen dengan Pencilan")

        unique_outliers = raw_df.drop_duplicates(subset=['Komponen'])

        unique_outliers_display = unique_outliers[['Tabel', 'No_Komponen', 'Komponen']]

        # Display only the first three rows
        st.dataframe(unique_outliers_display)

    with col2_o:
        col1_c, col2_c, col3_c = st.columns((1, 1, 1))

        with col2_c:
            total_outliers = raw_df.drop_duplicates(subset=['No_Komponen', 'Tabel']).shape[0]
            card_component("Jumlah Komponen Pencilan", total_outliers)
        with col3_c:
            card_component("Tanggal Di Proses", "2024-11-28")

        # Group by 'table' and count outliers for each table
        outlier_counts = raw_df.groupby('Tabel')['No_Komponen'].nunique()
        desired_order = ["1","2","3","4","5a","5b","5c","5d","5d.1","5.d.2","6","7","8","9","10","11","11a","12","13","14","15","16","16a","17","18","19","20"]  # Replace with actual sheet names

        # Convert index to categorical type with the specified order
        outlier_counts.index = pd.Categorical(outlier_counts.index, categories=desired_order, ordered=True)
        sorted_outlier_counts = outlier_counts.reindex(desired_order, fill_value=0)
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

        # Render the chart
        st_echarts(options=options, height="500px")


    raw_df_selected = raw_df[["Detail", "Tabel", "Nilai", "Periode", "No_Komponen", "Komponen", "Outlier"]]
    col1,col2 = st.columns((1,4))
    if 'selected_table' not in st.session_state:
        st.session_state.selected_table = None  # Placeholder for first run


    with col1:
        list = ["1","2","3","4","5a","5b","5c","5d","5d.1","5.d.2","6","7","8","9","10","11","11a","12","13","14","15","16","16a","17","18","19","20"]  # Replace with actual sheet names

        for table in list:
            # For tables starting with "5", use an expander with multiple buttons
            df = raw_df[raw_df["Tabel"] == table]
            # Extract unique values from the "Detail" column where the value is not "-"
            unique_list = df[df["Detail"] != "-"]["Detail"].unique().tolist()
            
            if table.startswith("5"):
                with st.expander(f"Lihat Kewajaran SSKI Tabel {table}"):
                    # Add multiple buttons within the expander for this table
                    for item in unique_list:
                        if st.button(f"Lihat {item}", key=f"{table}:{item}", use_container_width=True):
                            st.session_state.selected_table = f"{table}:{item}"
            # For other tables, display a single button that updates session state
            else:
                if st.button(f"Lihat Kewajaran SSKI Tabel {table}", use_container_width=True):
                    st.session_state.selected_table = table

    with col2:
        if st.session_state.selected_table == None:
            for item in sheet_names:
                st.title(f"Tabel {item}")
                if item.startswith("5"):
                    detail_list_df = raw_df_selected[raw_df_selected["Tabel"] == item]

                    for detail in detail_list_df["Detail"].unique():
                        st.markdown(f"<p>{detail}</p>", unsafe_allow_html=True)
                        raw_df_1_filtered = raw_df_selected[
                            (raw_df_selected["Tabel"] == item) & (raw_df_selected["Detail"] == detail)
                        ]
                        formatted_df, styled_df = pivot_dataframe(raw_df_1_filtered,raw_df_1_filtered)
                        legend_html = """
                        <div style="display: flex; align-items: center; margin-bottom: 10px;">
                            <div style="width: 20px; height: 20px; background-color: #CBF3F9; border: 0.5px solid black; margin-right: 5px;"></div>
                            <span>Data dengan warna ini menandakan data tersebut merupakan pencilan.</span>
                        </div>
                        """
                        st.markdown(legend_html, unsafe_allow_html=True)
                        st.dataframe(styled_df)
                        sheet_name = f"{item}:{detail}"
                        show_dropdown(sheet_name, formatted_df)
                        st.markdown(divider_style, unsafe_allow_html=True)
                
                else:
                    detail_list_df = raw_df_selected[raw_df_selected["Tabel"] == item]
                    formatted_df, styled_df = pivot_dataframe(detail_list_df,detail_list_df)

                    legend_html = """
                    <div style="display: flex; align-items: center; margin-bottom: 10px;">
                        <div style="width: 20px; height: 20px; background-color: #CBF3F9; border: 0.5px solid black; margin-right: 5px;"></div>
                        <span>Data dengan warna ini menandakan data tersebut merupakan pencilan.</span>
                    </div>
                    """
                    st.markdown(legend_html, unsafe_allow_html=True)

                    st.dataframe(styled_df)
                    show_dropdown(item, formatted_df)
                
                st.markdown(divider_style, unsafe_allow_html=True)

        elif len(st.session_state.selected_table.split(":")) >1:
            item, detail = st.session_state.selected_table.split(":")
            detail_list_df = raw_df_selected[raw_df_selected["Tabel"] == item]
            st.text(detail)
            raw_df_1_filtered = raw_df_selected[
                (raw_df_selected["Tabel"] == item) & (raw_df_selected["Detail"] == detail)
            ]
            formatted_df, styled_df = pivot_dataframe(raw_df_1_filtered,raw_df_1_filtered)
            legend_html = """
            <div style="display: flex; align-items: center; margin-bottom: 10px;">
                <div style="width: 20px; height: 20px; background-color: #CBF3F9; border: 0.5px solid black; margin-right: 5px;"></div>
                <span>Data dengan warna ini menandakan data tersebut merupakan pencilan.</span>
            </div>
            """
            st.markdown(legend_html, unsafe_allow_html=True)
            st.dataframe(styled_df)
            sheet_name = f"{item}:{detail}"
            show_dropdown(sheet_name, formatted_df)
        else:
            detail_list_df = raw_df_selected[raw_df_selected["Tabel"] == st.session_state.selected_table]
            formatted_df, styled_df = pivot_dataframe(detail_list_df,detail_list_df)
            legend_html = """
            <div style="display: flex; align-items: center; margin-bottom: 10px;">
                <div style="width: 20px; height: 20px; background-color: #CBF3F9; border: 0.5px solid black; margin-right: 5px;"></div>
                <span>Data dengan warna ini menandakan data tersebut merupakan pencilan.</span>
            </div>
            """
            st.markdown(legend_html, unsafe_allow_html=True)
            st.dataframe(styled_df)
            show_dropdown(st.session_state.selected_table, formatted_df)
        


if __name__ == "__main__":
    main()
