import time
import json
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def scrape_padi_chrome_stealth():
    # 1. Gunakan undetected-chromedriver
    options = uc.ChromeOptions()
    
    # Opsional: Tambahkan user-agent custom (biasanya tidak perlu karena uc sudah handle)
    # options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    # Opsional: Headless mode (tidak muncul browser)
    # options.add_argument("--headless")
    
    # Inisialisasi driver dengan undetected-chromedriver
    driver = uc.Chrome(options=options)

    all_records = []
    
    # Daftar provinsi (Ditambahkan Jambi, Sumbar, Sumut, Aceh)
    provinsi_list = [
        {"nama": "Jawa Barat", "sub": "jabar"},
        {"nama": "Jawa Timur", "sub": "jatim"},
        {"nama": "Jawa Tengah", "sub": "jateng"},
        {"nama": "Banten", "sub": "banten"},
        {"nama": "Lampung", "sub": "lampung"},
        {"nama": "Sumatra Selatan", "sub": "sumsel"},
        {"nama": "Bengkulu", "sub": "bengkulu"},
        {"nama": "Jambi", "sub": "jambi"},
        {"nama": "Sumatra Barat", "sub": "sumbar"},
        {"nama": "Sumatra Utara", "sub": "sumut"},
        {"nama": "Aceh", "sub": "aceh"}
    ]
    
    # Rentang tahun target 2018-2024
    tahun_target = ["2024", "2023", "2022", "2021", "2020", "2019", "2018"]

    try:
        for prov in provinsi_list:
            for tahun in tahun_target:
                url = f"https://{prov['sub']}.bps.go.id/id/statistics-table/3/WmpaNk1YbGFjR0pOUjBKYWFIQlBSU3MwVHpOVWR6MDkjMw==/luas-panen--produktivitas--dan-produksi-padi-menurut-kabupaten-kota-di-provinsi-jawa-timur--2023.html?year={tahun}"
                
                print(f"\n--- Mengambil: {prov['nama']} ({tahun}) ---")
                driver.get(url)
                
                # Paksa refresh agar data benar-benar baru
                driver.refresh()
                
                # Tunggu verifikasi manusia jika muncul
                print("Menunggu tabel muncul... (Silakan klik verifikasi jika muncul di layar browser)")
                
                try:
                    # Menunggu sampai elemen tbody (isi tabel) benar-benar ada
                    wait = WebDriverWait(driver, 40)
                    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "tbody tr")))
                    
                    # Jeda tambahan agar render angka selesai
                    time.sleep(5) 

                    rows = driver.find_elements(By.CSS_SELECTOR, "tbody tr")
                    count_per_page = 0
                    
                    for row in rows:
                        cols = row.find_elements(By.TAG_NAME, "td")
                        if len(cols) >= 4:
                            wilayah = cols[0].text.strip()
                            produksi = cols[3].text.strip().replace('.', '').replace(',', '.')
                            
                            # Abaikan baris header/total
                            if not wilayah or prov['nama'].lower() in wilayah.lower() or "indonesia" in wilayah.lower():
                                continue
                                
                            all_records.append({
                                "provinsi": prov['nama'],
                                "kabupaten_kota": wilayah,
                                "tahun": tahun,
                                "produksi_ton": produksi if produksi and produksi != "-" else "0"
                            })
                            count_per_page += 1
                    
                    print(f"✅ Berhasil mengambil {count_per_page} record.")
                
                except Exception as e:
                    print(f"❌ Tabel tidak muncul di {prov['nama']} {tahun}. Error: {e}")

    finally:
        driver.quit()
        return all_records

def simpan_ke_json(data):
    if len(data) > 0:
        with open('data_padi_final.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        print(f"\n🔥 SELESAI! Total {len(data)} record berhasil disimpan.")
    else:
        print("\nData kosong. Pastikan kamu tidak menutup jendela Chrome saat script berjalan.")

if __name__ == "__main__":
    hasil = scrape_padi_chrome_stealth()
    simpan_ke_json(hasil)