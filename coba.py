import streamlit as st
import pandas as pd
import json
import plotly.express as px
import pydeck as pdk

# Konfigurasi Halaman Streamlit
st.set_page_config(
    page_title="Dashboard Padi Final",
    page_icon="🌾",
    layout="wide"
)

# --- 1. Load Data ---
@st.cache_data
def load_data(file_path):
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
        df = pd.DataFrame(data)
        
        # Konversi tipe data
        df['produksi_ton'] = pd.to_numeric(df['produksi_ton'], errors='coerce')
        df['tahun'] = pd.to_numeric(df['tahun'], errors='coerce')
        
        # Pembersihan Teks
        df['provinsi'] = df['provinsi'].astype(str).str.strip().str.title()
        df['kabupaten_kota'] = df['kabupaten_kota'].astype(str).str.strip().str.title()
        
        return df
    except Exception as e:
        st.error(f"Error membaca file: {e}")
        return pd.DataFrame()

# --- 2. Database Koordinat ---
def get_coordinates():
    return {
        "Aceh": {"lat": 4.6951, "lon": 96.7494},
        "Sumatera Utara": {"lat": 2.1154, "lon": 99.5451},
        "Sumatera Barat": {"lat": -0.7399, "lon": 100.8000},
        "Riau": {"lat": 0.5071, "lon": 101.4478},
        "Jambi": {"lat": -1.6101, "lon": 103.6131},
        "Sumatera Selatan": {"lat": -3.3194, "lon": 104.9145},
        "Bengkulu": {"lat": -3.7928, "lon": 102.2608},
        "Lampung": {"lat": -4.5585, "lon": 105.4068},
        "Kepulauan Bangka Belitung": {"lat": -2.7411, "lon": 106.4406},
        "Kepulauan Riau": {"lat": 3.9159, "lon": 108.1961},
        "Dki Jakarta": {"lat": -6.2088, "lon": 106.8456},
        "Jawa Barat": {"lat": -6.9175, "lon": 107.6191},
        "Jawa Tengah": {"lat": -7.1510, "lon": 110.1403},
        "Di Yogyakarta": {"lat": -7.7956, "lon": 110.3695},
        "Jawa Timur": {"lat": -7.5361, "lon": 112.2384},
        "Banten": {"lat": -6.4058, "lon": 106.0640},
        "Bali": {"lat": -8.4095, "lon": 115.1889},
        "Nusa Tenggara Barat": {"lat": -8.6529, "lon": 117.3616},
        "Nusa Tenggara Timur": {"lat": -8.6574, "lon": 121.0794},
        "Kalimantan Barat": {"lat": -0.2787, "lon": 111.4753},
        "Kalimantan Tengah": {"lat": -1.6815, "lon": 113.3824},
        "Kalimantan Selatan": {"lat": -3.0926, "lon": 115.2838},
        "Kalimantan Timur": {"lat": 0.5387, "lon": 116.4194},
        "Kalimantan Utara": {"lat": 3.0731, "lon": 116.0414},
        "Sulawesi Utara": {"lat": 0.6247, "lon": 123.9750},
        "Sulawesi Tengah": {"lat": -1.4300, "lon": 121.4456},
        "Sulawesi Selatan": {"lat": -3.6687, "lon": 119.9740},
        "Sulawesi Tenggara": {"lat": -4.1449, "lon": 122.1746},
        "Gorontalo": {"lat": 0.6999, "lon": 122.4467},
        "Sulawesi Barat": {"lat": -2.8441, "lon": 119.2321},
        "Maluku": {"lat": -3.2385, "lon": 130.1453},
        "Maluku Utara": {"lat": 1.5709, "lon": 127.8087},
        "Papua": {"lat": -4.2699, "lon": 138.0804},
        "Papua Barat": {"lat": -1.3361, "lon": 133.1747},
        "Papua Selatan": {"lat": -7.4927, "lon": 139.6997},
        "Papua Tengah": {"lat": -4.1783, "lon": 136.2570},
        "Papua Pegunungan": {"lat": -4.0931, "lon": 139.1174}
    }

def add_coordinates(df):
    coords = get_coordinates()
    df_map = df.groupby(['provinsi','kabupaten_kota'])['produksi_ton'].sum().reset_index()
    df_map['lat'] = df_map['provinsi'].map(lambda x: coords.get(x, {}).get('lat'))
    df_map['lon'] = df_map['provinsi'].map(lambda x: coords.get(x, {}).get('lon'))
    
    return df_map.dropna(subset=['lat', 'lon'])



# --- Main Program ---
def main():
    st.title("🌾 Dashboard Monitoring Padi Nasional")
    st.markdown("Visualisasi Data Produksi Padi (1.504 Data Point)")

    # 1. LOAD DATA
    df = load_data('data_padi_final.json')
    if df.empty:
        st.warning("Data kosong.")
        return

    # --- Sidebar Filters ---
    st.sidebar.header("🔍 Filter Dashboard")
    
    # Filter Tahun (Tambahkan 'Semua Data')
    years_list = sorted(df['tahun'].dropna().unique().astype(int))
    year_options = ["Semua Data"] + years_list
    selected_year = st.sidebar.selectbox("Pilih Tahun Analisis", year_options)
    
    if selected_year == "Semua Data":
        df_filtered = df
        display_year_text = "Semua Tahun"
    else:
        df_filtered = df[df['tahun'] == selected_year]
        display_year_text = str(selected_year)

    # --- 2. KPI Metrics ---
    total_prod = df_filtered['produksi_ton'].sum()
    avg_prod = df_filtered['produksi_ton'].mean()
    count_data = len(df_filtered)

    c1, c2, c3 = st.columns(3)
    c1.metric(f"Total Produksi ({display_year_text})", f"{total_prod:,.0f} Ton")
    c2.metric("Rata-rata per Wilayah", f"{avg_prod:,.0f} Ton")
    c3.metric("Jumlah Titik Data", f"{count_data} Wilayah")

    st.markdown("---")

    # --- 3. Visualisasi GIS (3D Column Map seperti foto) ---
    st.subheader(f"🗺️ Peta Sebaran Produksi 3D ({display_year_text})")

    df_gis = add_coordinates(df_filtered)

    if not df_gis.empty:

        layer = pdk.Layer(
            "ColumnLayer",
            data=df_gis,
            get_position=["lon", "lat"],
            get_elevation="produksi_ton",
            elevation_scale=300,     # 🔥 bikin kolom TINGGI seperti foto
            radius=2000,               # 🔥 ramping / kurus
            get_fill_color=[255, 0, 0],
            pickable=True,
            auto_highlight=True,
        )

        view_state = pdk.ViewState(
            latitude=df_gis["lat"].mean(),
            longitude=df_gis["lon"].mean(),
            zoom=7,
            pitch=45,                   # 🔥 sudut miring seperti foto
        )

        deck = pdk.Deck(
            layers=[layer],
            initial_view_state=view_state,
            tooltip={
                "text": "Provinsi: {provinsi}\nProduksi: {produksi_ton} ton"
            },
        )

        st.pydeck_chart(deck, use_container_width=True)
    else:
        st.warning("Data peta tidak tersedia.")


    # --- 4. Visualisasi Grafik Detail (YANG DIPERBAIKI) ---
    st.subheader("📈 Peringkat Kabupaten/Kota")
    
    col_chart, col_filter = st.columns([3, 1])
    
    with col_filter:
        # PERBAIKAN 1: Semua opsi dijadikan String agar tidak error
        limit_options = ["10", "20", "50", "100", "Semua"]
        limit_show = st.selectbox("Tampilkan Top:", limit_options, index=1)
        
        prov_options = ["Semua"] + sorted(df_filtered['provinsi'].unique().tolist())
        selected_prov_chart = st.selectbox("Filter Wilayah:", prov_options)

    # Filter Data Grafik
    df_chart = df_filtered.copy()
    if selected_prov_chart != "Semua":
        df_chart = df_chart[df_chart['provinsi'] == selected_prov_chart]
    
    # Sort Data
    df_chart_final = df_chart.sort_values('produksi_ton', ascending=False)
    
    # PERBAIKAN 2: Logika Limit & Tinggi Grafik Dinamis
    # Jika user pilih "Semua", tinggi grafik menyesuaikan jumlah data
    if limit_show == "Semua":
        limit_int = len(df_chart_final)
        # Rumus: Minimal 600px, atau 20px per baris data (biar ga gepeng)
        dynamic_height = max(600, limit_int * 20)
    else:
        limit_int = int(limit_show)
        df_chart_final = df_chart_final.head(limit_int)
        dynamic_height = 600 # Tinggi standar
    
    fig_bar = px.bar(
        df_chart_final,
        x='produksi_ton',
        y='kabupaten_kota',
        orientation='h',
        color='produksi_ton',
        color_continuous_scale='Viridis',
        title=f"Ranking Wilayah ({display_year_text})",
        text_auto='.2s',
        height=dynamic_height  # Pasang tinggi dinamis disini
    )
    
    # Agar yang paling besar di atas
    fig_bar.update_layout(yaxis={'categoryorder':'total ascending'})
    st.plotly_chart(fig_bar, use_container_width=True)

    # --- 5. Tabel Data ---
    with st.expander(f"📂 Lihat Detail Data ({len(df_filtered)} Baris)"):
        st.dataframe(df_filtered, use_container_width=True)

if __name__ == "__main__":
    main()