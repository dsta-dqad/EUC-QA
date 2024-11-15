import streamlit as st
import importlib
app_SSKI = importlib.import_module('views.sski.app_SSKI')
app_SEKDA = importlib.import_module('views.sekda.app_SEKDA')
app_SEKDA_antartabel = importlib.import_module('views.sekda.app_SEKDA_antartabel')
app_SSKI_kewajaran = importlib.import_module('views.sski.app_SSKI_kewajaran')

st.set_page_config(layout="wide", page_title="EUC QA", page_icon="📊")

if 'page' not in st.session_state:
    st.session_state['page'] = 'main'  # Default to main page

st.markdown("""
    <style>
    @import url('https://fonts.cdnfonts.com/css/frutiger');
    h1 { 
        font-family: Frutiger; 
        font-style: normal;
        font-variant: normal; 
        font-weight: 700; 
        letter-spacing: 4px;
    } h3 { 
        font-family: Frutiger; 
        font-style: normal;
        font-variant: normal; 
        font-weight: 700;
        letter-spacing: 1px;
    }
    </style>
    """, unsafe_allow_html=True)

st.markdown("""
    <style>
    @import url('https://db.onlinewebfonts.com/c/c214e055a9aae386324285c45892f7b5?family=Frutiger+LT+W02+45+Light');

    p [class="css"] {
        font-family: 'Frutiger LT W02 45 Light', sans-serif;
    }
    </style>
    """, unsafe_allow_html=True)

# CSS styles for the container and elements
st.markdown("""
    <style>
        .outer-container {
            padding: 20px;
            border: 1px solid #444444;
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
            border: 1px solid #444444;
        }
        .title {
            font-size: 1.5rem; 
            font-weight: bold; 
        }
        .description {
            text-align: justify;
        }
        h3.centered-title {
            text-align: center;
        }
        h3,h4{
            margin: 0;
        }
    </style>
""", unsafe_allow_html=True)

# Main page content
def main_page():

    col01, col02 = st.columns((1.5, 4))
    with col02:
        st.markdown(f"<h1 class=centered-title>EUC QUALITY ASSURANCE</h1>", unsafe_allow_html=True)

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
            st.markdown("""<h4>Intra Tabel</h4>""", unsafe_allow_html=True)
            # Buttons for Uji Konsistensi and Uji Kewajaran under SSKI
            if st.button("Uji Konsistensi (SSKI)", use_container_width=True):
                st.session_state['page'] = 'app_SSKI'  # Navigate to SSKI page

            if st.button("Uji Kewajaran (SSKI)", use_container_width=True):
                st.session_state['page'] = 'app_SSKI_kewajaran'  # Navigate to SSKI page

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
            st.markdown("""<h4>Intra Tabel</h4>""", unsafe_allow_html=True)
            if st.button("Uji Konsistensi (SEKDA)", use_container_width=True):
                st.session_state['page'] = 'app_SEKDA'  # Navigate to SEKDA page

            # Section for Antar Tabel buttons (under SEKDA)
            st.markdown("""<h4>Inter Tabel</h4>""", unsafe_allow_html=True)
            if st.button("Antar Tabel (SEKDA)", use_container_width=True):
                st.session_state['page'] = 'app_SEKDA_antartabel'  # Navigate to SEKDA page

        with st.expander("Utang Luar Negeri (ULN)", expanded=False):
            # Section for Antar Tabel buttons (under SEKDA)
            st.subheader("Inter Tabel")
            if st.button("Antar Publikasi (ULN)", use_container_width=True):
                st.session_state['page'] = 'app_ULN'

    with col2:
        st.markdown("""
            <div class="outer-container">
            <h3 class="centered-title">INTRA TABEL</h3>
            <div class="inner-column">
                <h3 class="centered-title">Uji Konsistensi</h3>
                <div class="container">
                    <h4>Vertikal Cek</h4>
                    <p class="description">
                    Fitur pengecekan konsistensi nilai agregat dengan penjumlahan
                    nilai komponen-komponen pembentuk pada tabel secara vertikal.
                    </p>
                </div>
                <div class="container">
                    <h4>Horizontal Cek</h4>
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
                    <h4>Before-After Cek </h4>
                    <p class="description">
                    Fitur pengecekan konsistensi data periode yang akan dirilis dibandingkan dengan data periode terakhir dirilis.
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
                            <h4>Year on Year (YoY)</h4>
                            <p>Fitur pengecekan nilai pada posisi bulan/kuartal di suatu tahun dengan posisi bulan/kuartal yang sama di tahun sebelumnya.</p>
                        </div>
                    </div>
                </div>
            </div>
            <div class= "outer-container">
                <h3 class="centered-title">INTER TABEL</h3>
                <div class="inner-column-r">
                    <div class="container">
                        <h4>Antar Tabel</h4>
                        <p class="description">
                            Fitur pengecekan konsistensi nilai indikator yang sama pada satu tabel dengan indikator tersebut di tabel yang lain di publikasi statistik yang sama. 
                        </p>
                    </div>
                </div>
                <div class="inner-column-r">
                    <div class="container">
                        <h4>Antar Publikasi</h4>
                        <p class="description">
                            Fitur pengecekan konsistensi nilai indikator yang sama pada suatu publikasi statistik dengan indikator tersebut di publikasi statistik yang lain.
                        </p>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)

# Control page switching based on session state
if st.session_state['page'] == 'main':
    main_page()
elif st.session_state['page'] == 'app_SSKI':
    app_SSKI.main()  
elif st.session_state['page'] == 'app_SEKDA':
    app_SEKDA.main()  
elif st.session_state['page'] == 'app_SEKDA_antartabel':
    app_SEKDA_antartabel.main()
elif st.session_state['page'] == 'app_SSKI_kewajaran':
    app_SSKI_kewajaran.main()
