import streamlit as st
import app_SSKI  # Import SSKI page module
import app_SEKDA  # Import SEKDA page module

st.set_page_config(layout="wide", page_title="EUC QA", page_icon="📊")

# Initialize session state
if 'page' not in st.session_state:
    st.session_state['page'] = 'main'  # Default to main page

# CSS Styling to enhance appearance
# CSS styles for the bordered container and other elements
st.markdown("""
    <style>
    @import url('https://db.onlinewebfonts.com/c/c214e055a9aae386324285c45892f7b5?family=Frutiger+LT+W02+45+Light');

    *, html, body,h1,h2,h3,h4,h5, p [class="css"] {
        font-family: 'Frutiger LT W02 45 Light', sans-serif;
    }
    </style>
    """, unsafe_allow_html=True)
# CSS styles for the container and elements
st.markdown("""
    <style>
        .centered-title {
            text-align: center;
            text-decoration: underline;
        }
        .outer-container {
            padding: 20px;
            border: 3px solid #444444;
            border-radius: 15px;
            margin-bottom: 15px;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        }
        .inner-column {
            display: inline-block;
            width: 48%; /* Adjust as necessary for spacing */
            vertical-align: top;
            margin-right: 2%;
        }
        .inner-column-r {
            display: block;
            width: 100%; /* Adjust as necessary for spacing */
            vertical-align: top;
            margin-right: 2%;
        }
        .inner-column:last-child {
            margin-right: 0; /* Remove margin from last column */
        }
        .container {
            padding: 15px; 
            border: 2px solid #444444; 
            border-radius: 12px; 
            margin-bottom: 15px;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
            transition: all 0.3s ease-in-out;
        }
        .container:hover {
            transform: scale(1.02);
            border-color: black !important; 
        }
        .title {
            font-size: 1.5rem; 
            font-weight: bold; 
            margin-bottom: 8px;
        }
        .description {
            text-align: justify;
        }
        h3.centered-title {
            text-align: center;
            text-decoration: underline;
            margin-bottom: 15px;
        }
        button{
            color:black !important;
            background-color:white !important;
        }
        button:hover{
            border-color:black !important
        }
    </style>
""", unsafe_allow_html=True)

st.markdown(
    """
    <style>
    .coming-soon {
        background-color: #d3d3d3; /* Light gray */
        color: #ffffff;
        border: none;
        padding: 10px 20px;
        font-size: 16px;
        cursor: not-allowed;
        border-radius: 5px;
        display: inline-block;
        text-align: center;
        width: 100%;
    }
    </style>
    """, unsafe_allow_html=True
)

# Main page content
def main_page():
    st.markdown(f"<h1 class=centered-title>EUC QUALITY ASSURANCE</h1>", unsafe_allow_html=True)

    # Main layout: col1 (4 parts) and col2 (1 part)
    col1, col2 = st.columns((1.5, 4))

    with col1:
        st.markdown("""<h5>Ingin melakukan QA pada publikasi apa?</h5>""", unsafe_allow_html=True)

        with st.expander("Statistik Sistem Keuangan Indonesia (SSKI)", expanded=False):
            # Content for 'Apa Itu SSKI?'
            st.markdown("""
            <div class='container'>
                <div class='title'>Apa Itu SSKI?</div>
                <p class='description'>
                    SSKI adalah kumpulan data yang menggambarkan perkembangan elemen ekonomi terkait kebijakan Makroprudensial/Stabilitas Sistem Keuangan (SSK) di Indonesia. 
                    Data ini mencakup lembaga keuangan (bank dan IKNB), pasar keuangan (uang dan modal), infrastruktur keuangan (sistem pembayaran dan pengedaran uang), 
                    serta elemen ekonomi dari pemerintah, korporasi, dan rumah tangga.
                </p>
            </div>
            """, unsafe_allow_html=True)

            # Section for Intra Tabel buttons (under SSKI)
            st.subheader("Intra Tabel")
            # Buttons for Uji Konsistensi and Uji Kewajaran under SSKI
            if st.button("Uji Konsistensi (SSKI)", use_container_width=True):
                st.session_state['page'] = 'app_SSKI'  # Navigate to SSKI page

            if st.button("Uji Kewajaran (SSKI)", use_container_width=True,help="COMING SOON"):
                st.markdown("""<p class="description">Coming Soon.</p>""", unsafe_allow_html=True)

        # Expander for SEKDA
        with st.expander("Statistik Ekonomi dan Keuangan Daerah (SEKDA)", expanded=False):
            # Content for 'Apa Itu SEKDA?'
            st.markdown("""
            <div class='container'>
                <div class='title'>Apa Itu SEKDA?</div>
                <p class='description'>
                    SEKDA (Statistik Ekonomi dan Keuangan Daerah) adalah publikasi bulanan Bank Indonesia yang menyajikan data ekonomi, keuangan, dan perbankan untuk seluruh provinsi di Indonesia. 
                    Data ini berguna untuk menganalisis perkembangan ekonomi dan perbankan di setiap provinsi.
                </p>
            </div>
            """, unsafe_allow_html=True)

            # Section for Intra Tabel buttons (under SEKDA)
            st.subheader("Intra Tabel")
            if st.button("Uji Konsistensi (SEKDA)", use_container_width=True):
                st.session_state['page'] = 'app_SEKDA'  # Navigate to SEKDA page

            if st.button("Uji Kewajaran (SEKDA)", use_container_width=True,help="COMING SOON"):
                st.markdown("""<p class="description">Coming Soon.</p>""", unsafe_allow_html=True)


            # Section for Antar Tabel buttons (under SEKDA)
            st.subheader("Inter Tabel")
            if st.button("Antar Tabel", use_container_width=True, help="COMING SOON"):
                st.markdown("""<p class="description">Coming Soon.</p>""", unsafe_allow_html=True)


    with col2:
        st.markdown("""
            <div class="outer-container">
            <h3 class="centered-title">INTRA TABEL</h3>
            <div class="inner-column">
                <h3 class="centered-title">Uji Konsistensi</h3>
                <div class="container">
                    <h4>Horizontal Check</h4>
                    <p class="description">
                        Fitur pengecekan konsistensi nilai tahunan dengan nilai posisi atau
                        nilai transaksi pada komponen tabel.
                    </p>
                    <p class="description">
                        <strong>Data Posisi</strong>: Membandingkan nilai data pada kolom
                        tahunan dengan data dari posisi kolom akhir periode tahun tersebut
                        (Desember).
                    </p>
                    <p class="description">
                        <strong>Data Transaksi</strong>: Membandingkan data pada kolom
                        tahunan dengan hasil penjumlahan nilai seluruh periode di tahun
                        tersebut.
                    </p>
                </div>
                <div class="container">
                    <h4>Vertical Check</h4>
                    <p class="description">
                    Fitur pengecekan konsistensi nilai agregat dengan penjumlahan
                    nilai komponen-komponen pembentuk pada tabel secara vertikal.
                    </p>
                </div>

            </div>
                <div class="inner-column">
                    <h3 class="centered-title">Uji Kewajaran</h3>
                    <div class="container">
                        <div class="description">
                            <h4>Month to Month (MtM)</h4>
                            <p>Fitur pengecekan nilai pada suatu bulan dengan bulan sebelumnya.</p>
                            <h4>Quarter to Quarter (QtQ)</h4>
                            <p>Fitur pengecekan nilai pada suatu triwulan dengan triwulan sebelumnya.</p>
                            <h4>Year on Year (YOY)</h4>
                            <p>Fitur pengecekan nilai pada posisi bulan/kuartal di suatu tahun dengan posisi bulan/kuartal yang sama di tahun sebelumnya.</p>
                        </div>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)
        # Content for the second column (col2)
        st.markdown("""
            <div class= "outer-container">
                <h3 class="centered-title">INTER TABEL</h3>
                <div class="inner-column-r">
                    <div class="container">
                        <h4>Antar Tabel</h4>
                        <p class="description">
                            Fitur pengecekan konsistensi nilai indikator yang sama pada satu tabel dengan indikator tersebut di tabel yang lain. 
                        </p>
                    </div>
                </div>
                <div class="inner-column-r">
                    <div class="container">
                        <h4>Inter Tabel</h4>
                        <p class="description">
                            Fitur pengecekan konsistensi nilai indikator yang sama pada suatu publikasi statistik dengan indikator tersebut di publikasi statistik yang lain.
                        </p>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)
    # Second row: Explanation of SSKI and SEKDA with buttons

# Control page switching based on session state
if st.session_state['page'] == 'main':
    main_page()
elif st.session_state['page'] == 'app_SSKI':
    app_SSKI.main()  # Call the main function from app_SSKI.py
elif st.session_state['page'] == 'app_SEKDA':
    app_SEKDA.main()  # Call the main function from app_SEKDA.py
