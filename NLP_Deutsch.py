import spacy
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components
from io import BytesIO
import xlsxwriter 
import base64
import pdfplumber
from PIL import Image


# Load spaCy model untuk analisis tata bahasa
nlp = spacy.load("de_core_news_sm")
nlp.max_length = 2000000



# Fungsi untuk mendeteksi kalimat perbandingan
def deteksi_perbandingan(teks):

    corpus = nlp(teks)
    kalimat_perbandingan = []

    for kalimat in corpus.sents: # Iterasi setiap kalimat
        
        pola_komparatif = []

        # pola_komparatif.append(re.findall(r'\w+er als ', kalimat.text.lower())) # Pola Komparativ + als
        # pola_komparatif.append(re.findall(r'mehr \w+ als ', kalimat.text.lower())) # Pola Mehr + Komparativ + als

        if 'als ' in kalimat.text.lower(): # Periksa apakah ada 'als

            for i, token in enumerate(kalimat): # Iterasi setiap token dalam kalimat

                if token.text == 'als' and kalimat[i-1].tag_ == "ADJD":

                    pola_komparatif.append(token)

                if token.text.lower() == 'als' and kalimat[i-1].text.lower() == 'mehr' or kalimat[i-1].text.lower() == 'weniger' :

                    pola_komparatif.append(token)

                if token.text == 'als' and kalimat[i-2].tag_ == "ADJA" or kalimat[i-2].text == 'mehr' or kalimat[i-2].text == 'lieber': # Tag ADJA sbg adjektiv (komparativ) atributif

                    pola_komparatif.append(token)

            if len(pola_komparatif) > 0: # Pastikan ada pola komparatif

                kalimat_perbandingan.append(kalimat.text)

    if kalimat_perbandingan == []:
        
        kalimat_perbandingan.append("Tidak ada kalimat perbandingan pada teks")

        return kalimat_perbandingan
    
    else:

        return list(set(kalimat_perbandingan))

# Fungsi untuk mendeteksi kalimat lampau
def deteksi_lampau(teks):

    corpus = nlp(teks)
    kalimat_lampau = []

    for kalimat in corpus.sents: # Iterasi setiap kalimat

        pola_lampau = []

        if "als " in kalimat.text.lower(): # Periksa apakah ada "als"

            for i, token in enumerate(kalimat):

                if kalimat[0].text == 'Als'and kalimat[1].pos_ in ["PRON","NOUN"] and token.text == "," and kalimat[i-1].pos_ in ["VERB", "AUX"]:

                    pola_lampau.append(token)
                
                elif token.text == 'als'and kalimat[i + 1].pos_ in ["PRON","NOUN"] and kalimat[-2].pos_ in ["VERB", "AUX"]:

                    pola_lampau.append(token)

            if len(pola_lampau) > 0: # Pastikan ada kata kerja

                kalimat_lampau.append(kalimat.text)

    if kalimat_lampau == []:
        
        kalimat_lampau.append("Tidak ada kalimat lampau pada teks")

        return kalimat_lampau
    
    else:

        return list(set(kalimat_lampau))

def program_utama(teks):

    a = deteksi_perbandingan(teks)
    b = deteksi_lampau(teks)

    if len(a) < len(b):

        for i in range (len(b)-len(a)):

            a.append(None)

    elif len(b) < len(a):

        for i in range (len(a)-len(b)):

            b.append(None)

    return a, b

def get_data_frame(teks):

    hasil = {'kalimat_perbandingan' : program_utama(teks)[0], 'kalimat_lampau' : program_utama(teks)[1]}

    df_main = pd.DataFrame(data = hasil)

    return df_main

def df_to_excel(df_main):

    df_main.to_excel('Hasil deteksi.xlsx')

def get_img_as_base64(file):
    with open(file, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()






# CODE UNTUK TAMPILAN WEB (USER INTERFACE)

with st.sidebar:
    
    st.header('§ Syntax Spion')
    st.html("""
        <p style="color: #ede1c7;
            font-family: Royal Avenue">
            <a style="font-weight: 600;">Created by:</a> Devita, Auryn, Leya, Kia, Yuya, Riri
        </p>
        <p style="color: #ede1c7; 
            margin: 0 0 .5rem; 
            font-weight: 600;
            font-family: Royal Avenue">
            Description: 
        </p>

        <style>
        /* Container styling */
        .scrollable-container {
            width: auto; /* Lebar container */
            height: 180px; /* Tinggi container */
            overflow-y: scroll; /* Aktifkan scrollbar vertikal */
            overflow-x: hidden; /* Nonaktifkan scrollbar horizontal */
            background-color: rgba(147, 55, 35, 0.4); /* Warna latar */
        }

        /* Styling untuk teks */
        .scrollable-text {
            font-size: 14px;
            line-height: 1.5;
            color: #ede1c7;
            text-align: justify;
        }
        </style>
                
        <!-- Scrollable container -->
        <div class="scrollable-container">
            <p class="scrollable-text">
                § (Syntax Spion) membantu pengguna untuk membedakan penggunaan als dalam kalimat perbandingan dan lampau melalui penyajian tabel yang mudah dipahami. Dirancang untuk pembelajar pemula bahasa Jerman, tetapi tetap relevan bagi siapa saja yang ingin belajar bahasa Jerman lebih dalam.
            </p>
        </div>
        """)

    img = get_img_as_base64("./Images/Sidebar.PNG")

    st.html(
        f"""
        <style>
        [data-testid="stSidebar"] {{
            background-image: url("data:image/png;base64,{img}");
            background-size: contain;
            background-position: bottom left; 
            background-repeat: no-repeat;
            background-attachment: fixed;
            /* width: 277px !important; Membatasi lebar maksimal */
        }}
        [data-testid="stSidebar"][aria-expanded="false"] {{
            max-width: 0px; /* Atur lebar maksimal */
            min-width: 0px;  /* Atur lebar minimal */
        }}
        [data-testid="stSidebar"][aria-expanded="true"] {{
            max-width: 278px; /* Atur lebar maksimal */
            min-width: 100px;  /* Atur lebar minimal */
        }}
        </style>
        """)



with st.container():

    st.title('Deteksi Kalimat Perbandingan dan Lampau')
    # st.caption('Created by: ')

    # Kotak kosong buat diisi
    teks_langsung = st.text_area("Masukkan Teks:", height=68)
    placeholder_langsung = st.empty()
    placeholder_langsung_2 = st.empty()

    # Upload file
    uploaded_file = st.file_uploader("Pilih File", type=["txt","pdf"])
    placeholder_file_teks = st.empty()
    placeholder_file = st.empty()

    # Kalau ada file yang di upload
    df_main = ""
    teks_dari_file = ""
    
    # Algoritma untuk deteksi dengan input Kalimat

    if teks_langsung == '':

        placeholder_langsung.empty()

    else:

        df_main = get_data_frame(teks_langsung)
        placeholder_langsung.dataframe(df_main)

        # Menyimpan DataFrame ke file Excel dalam memori
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df_main.to_excel(writer, index=False, sheet_name='Sheet1')
            # writer.save()

        # Mendapatkan data file Excel
        excel_data = output.getvalue()

        # Tombol untuk mengunduh file Excel
        placeholder_langsung_2.download_button(
            label="Download File Excel",
            data=excel_data,
            file_name="Hasil deteksi.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    # Algoritma untuk deteksi dengan input File 

    if uploaded_file is not None:

        # try:
        # st.write(uploaded_file.type)

        if uploaded_file.type == "text/plain": ### READ FILE TXT

            # Membuka file dan membaca isinya
            teks_dari_file = ''.join(
                line.strip() + ' ' for line in uploaded_file.read().decode('utf-8').splitlines()).strip()

        elif uploaded_file.type == "application/pdf": ### READ FILE TXT

            with pdfplumber.open(uploaded_file) as pdf:
                num_pages = len(pdf.pages)

            # Menampilkan isi setiap halaman
            for page_num, page in enumerate(pdf.pages):
                text = page.extract_text()

                teks_dari_file = teks_dari_file + text

                # st.subheader(f"Page {page_num + 1}")
            teks_dari_file = ''.join(
                line.strip() + ' ' for line in (teks_dari_file).splitlines()).strip()

        else:
            
            st.write("File tidak berhasil di read")
      
        df_main = get_data_frame(teks_dari_file)
        placeholder_file_teks.write(df_main)

        # Menyimpan DataFrame ke file Excel dalam memori
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df_main.to_excel(writer, index=False, sheet_name='Sheet1')
            # writer.save()

        # Mendapatkan data file Excel
        excel_data = output.getvalue()

        # Tombol untuk mengunduh file Excel
        placeholder_file.download_button(
    
            label="Download File Excel",
            data=excel_data,
            file_name="Hasil deteksi.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )



    if st.button("Hapus Semua Output"):
        placeholder_langsung.empty()
        placeholder_file.empty()
        placeholder_langsung_2.empty()
        placeholder_file_teks.empty()

# IMPORT FONT DARI GITHUB PAGES
st.html(
    f"""
    <style>
    @font-face {{
        font-family: "Royal Avenue";
        src: url('https://skyssaurora.github.io/royal-avenue-demo.ttf') format("truetype");
    }}
    </style>
    """
)
st.html(
    f"""
    <style>
    @font-face {{
        font-family: "Source Sans Pro";
        src: url('https://skyssaurora.github.io/royal-avenue-demo.ttf') format("truetype");
    }}
    </style>
    """
)

### Ubah font h1 (title) dan h2 (sub-header / yang di sidebar)
st.html(
    """
    <style>
    [data-testid="stMarkdownContainer"] h1{
        font-family: "Royal Avenue", cursive;
        color: #ede1c7;
    }
    </style>
    """
)
st.html(
    """
    <style>
    [data-testid="stMarkdownContainer"] h2{
        font-family: "Royal Avenue", cursive;
        color: #ede1c7;
        font-size: 1.75rem;
    }
    </style>
    """
)

### Header Menjadi Transparan
st.html(
    """
    <style>
    [data-testid="stHeader"] {
        background: rgba(0,0,0,0);
    }
    </style>
    """
)

### Warna svg (titik tiga dan panah)
components.html(
    """
    <script>
    const button = window.parent.document.querySelectorAll("button svg");
    button[0].style.color = '#FFF';
    button[1].style.color = '#FFF';
    button[2].style.color = '#FFF';
    </script>
    """,
    height=0,
    width=0,
)

### Warna svg (cloud)
st.html(
    """
    <style>
    [data-testid="stFileUploaderDropzoneInstructions"] svg {
        color: #933723;
    }
    </style>
    """
)

### Titik tiga menjadi punya background
st.html(
    """
    <style>
    [data-testid="stBaseButton-headerNoPadding"] {
        background: #933723;
    }
    </style>
    """
)

### Titik tiga dan panah di sidebar menjadi punya background hover
st.html(
    """
    <style>
    [data-testid="stBaseButton-headerNoPadding"]:hover{
        background: #ede1c7;
    }
    </style>
    """
)

### Panah sebelum di sidebar menjadi punya background hover
st.html(
    """
    <style>
    button[kind="headerNoPadding"]:hover{
        background: #ede1c7;
    }
    </style>
    """
)

### Background Image
st.html(
    f"""
    <style>
    [data-testid="stAppViewContainer"] {{
    background-image: url("data:image/png;base64,{get_img_as_base64("./Images/BARU.JPG")}");
    background-size: cover;
    background-position: center center; 
    background-repeat: no-repeat;
    background-attachment: fixed;
    }}
    """)

### Background Image HP biar tidak penyok
st.html(
    f"""
    <style>
    @media (max-width: 600px) {{
        [data-testid="stAppViewContainer"] {{
        background-image: url("data:image/png;base64,{get_img_as_base64("./Images/BARU_600.JPG")}");
        background-size: cover;
        background-position: center center; 
        background-repeat: no-repeat;
        background-attachment: fixed;
        }}
    }}
    """)

### Ubah BACKGROUND SATU CONTAINER
components.html(
    """
    <script>
    const container = window.parent.document.querySelectorAll("div.stVerticalBlock");
    container[1].style.backgroundColor = 'rgba(147, 55, 35, 0.4)';
    container[1].style.borderRadius = '10px';
    container[1].style.border = '2px solid #933723';
    container[1].style.paddingLeft = '1rem';
    container[1].style.paddingRight = '1rem';
    </script>
    """,
    height=0,
    width=0,
)

### Ubah warna isi kontainer
#### Ubah warna kolom masukkan text
st.html(
    """
    <style>
    [data-baseweb="textarea"] {
        background-color: rgba(0, 0, 0, 0);
    }
    </style>
    """
)
st.html(
    """
    <style>
    [data-baseweb="base-input"] {
        background-color: rgba(237, 225, 199, 0.5);
    }
    </style>
    """
)

#### Ubah warna kolom upload file
st.html(
    """
    <style>
    [data-testid="stFileUploaderDropzone"] {
        background-color: rgba(237, 225, 199, 0.5);
    }
    </style>
    """
)

### Ubah warna button
st.html(
    """
    <style>
    [data-testid="stBaseButton-secondary"] {
        background-color: rgba(237, 225, 199, 0.5);
    }
    </style>
    """
)

### Ganti Warna Tabel
# st.html(
#     """
#     <style>
#     div {
#         --gdg-bg-cell: rgba(237, 225, 199, 1) !important;
#         --gdg-bg-cell-medium: rgba(237, 225, 199, 1) !important;
#         --gdg-bg-header: rgba(237, 225, 199, 0.5) !important;
#         --gdg-bg-header-has-focus: rgba(237, 225, 199, 0.5) !important;
#         --gdg-bg-header-hovered: rgba(237, 225, 199, 0.5) !important;
#         --gdg-bg-bubble: rgba(237, 225, 199, 1) !important;
#         --gdg-bg-bubble-selected: rgba(237, 225, 199, 1) !important;
#     }
#     </style>
#     """
# )