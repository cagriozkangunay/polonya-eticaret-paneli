import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="Polonya E-Ticaret Paneli", layout="wide", page_icon="🛍️")

PROD_FILE = "urunler.csv"
SALES_FILE = "satislar.csv"

# Varsayılan şablon verileri (Yoksa sıfırdan oluşturur)
if not os.path.exists(PROD_FILE):
    rows = []
    for i in range(1, 21):
        rows.append({"SKU": f"IM-{i:03d}", "Ürün Adı": f"Islak Mendil Çeşit {i}", "Kategori": "Islak Mendil", "Alış Fiyatı (PLN)": 0.0, "Satış Fiyatı (PLN)": 0.0, "Stok": 0})
    for i in range(1, 21):
        rows.append({"SKU": f"OK-{i:03d}", "Ürün Adı": f"Oda Kokusu Çeşit {i}", "Kategori": "Oda Kokusu", "Alış Fiyatı (PLN)": 0.0, "Satış Fiyatı (PLN)": 0.0, "Stok": 0})
    for i in range(1, 21):
        rows.append({"SKU": f"KZ-{i:03d}", "Ürün Adı": f"Kozmetik Çeşit {i}", "Kategori": "Kozmetik", "Alış Fiyatı (PLN)": 0.0, "Satış Fiyatı (PLN)": 0.0, "Stok": 0})
    pd.DataFrame(rows).to_csv(PROD_FILE, index=False)

if not os.path.exists(SALES_FILE):
    pd.DataFrame(columns=["Tarih", "Kanal", "SKU", "Ürün Adı", "Adet", "Satış Fiyatı (PLN)", "Kargo Maliyeti (PLN)", "Reklam Maliyeti (PLN)", "Ödeme Kesintisi (PLN)", "Net Kar (PLN)"]).to_csv(SALES_FILE, index=False)

st.title("🛍️ Polonya E-Ticaret Yönetim Paneli")
st.caption("Działalność nierejestrowana (Kayıtsız Faaliyet) Stok ve Finans Takip Sistemi")

tab1, tab2, tab3 = st.tabs(["📦 Ürün Kataloğu & Stok", "🛒 Yeni Satış Gir", "📊 Finans & Yasal Limit Özeti"])

# TAB 1: KATALOG & STOK
with tab1:
    st.header("Mevcut Ürün Kataloğu ve Stok Durumu")
    df_p = pd.read_csv(PROD_FILE)
    
    col_k1, col_k2 = st.columns([1, 3])
    with col_k1:
        st.subheader("Yeni Ürün Ekle")
        with st.form("yeni_urun_form"):
            sku = st.text_input("Ürün Kodu (SKU)", placeholder="Örn: IM-021")
            ad = st.text_input("Ürün Adı", placeholder="Örn: Lavanta Oda Kokusu")
            kat = st.selectbox("Kategori", ["Islak Mendil", "Oda Kokusu", "Kozmetik"])
            alis = st.number_input("Alış Fiyatı (PLN)", min_value=0.0, step=0.5)
            satis = st.number_input("Satış Fiyatı (PLN)", min_value=0.0, step=0.5)
            stok = st.number_input("Başlangıç Stoğu", min_value=0, step=1)
            
            if st.form_submit_button("Ürünü Kaydet"):
                yeni_row = pd.DataFrame([{"SKU": sku, "Ürün Adı": ad, "Kategori": kat, "Alış Fiyatı (PLN)": alis, "Satış Fiyatı (PLN)": satis, "Stok": stok}])
                df_p = pd.concat([df_p, yeni_row], ignore_index=True)
                df_p.to_csv(PROD_FILE, index=False)
                st.success(f"{sku} koda sahip ürün başarıyla eklendi!")
                st.rerun()

    with col_k2:
        st.subheader("Ürün / Stok Düzenleme")
        edited_df = st.data_editor(df_p, use_container_width=True, num_rows="dynamic")
        if st.button("Fiyat ve Stok Değişikliklerini Kaydet"):
            edited_df.to_csv(PROD_FILE, index=False)
            st.success("Tüm değişiklikler başarıyla güncellendi!")
            st.rerun()

# TAB 2: SATIŞ GİRİŞİ
with tab2:
    st.header("Yeni Satış Kaydı Oluştur")
    df_p = pd.read_csv(PROD_FILE)
    
    with st.form("yeni_satis_form"):
        col1, col2, col3 = st.columns(3)
        tarih = col1.date_input("Satış Tarihi")
        kanal = col2.selectbox("Satış Kanalı", [
            "Instagram - Islak Mendil", "TikTok - Islak Mendil", 
            "Instagram - Oda Kokusu", "TikTok - Oda Kokusu", 
            "Instagram - Kozmetik", "TikTok - Kozmetik", "Facebook / Diğer"
        ])
        secilen_sku = col3.selectbox("Satılan Ürünü Seç (SKU)", df_p["SKU"].tolist())
        
        col4, col5, col6, col7 = st.columns(4)
        adet = col4.number_input("Satış Adedi", min_value=1, value=1)
        kargo = col5.number_input("Kargo Gideri (PLN)", min_value=0.0, value=12.0)
        reklam = col6.number_input("Reklam Payı (PLN)", min_value=0.0, value=5.0)
        kesinti = col7.number_input("Ödeme Komisyonu (PLN)", min_value=0.0, value=2.0)
        
        if st.form_submit_button("Satışı Kaydet ve Stoğu Düş"):
            prod_info = df_p[df_p["SKU"] == secilen_sku].iloc[0]
            satis_fiyati = prod_info["Satış Fiyatı (PLN)"]
            alis_fiyati = prod_info["Alış Fiyatı (PLN)"]
            urun_adi = prod_info["Ürün Adı"]
            
            toplam_ciro = satis_fiyati * adet
            toplam_gider = (alis_fiyati * adet) + kargo + reklam + kesinti
            net_kar = toplam_ciro - toplam_gider
            
            df_s = pd.read_csv(SALES_FILE)
            yeni_satis = pd.DataFrame([{
                "Tarih": str(tarih), "Kanal": kanal, "SKU": secilen_sku, "Ürün Adı": urun_adi,
                "Adet": adet, "Satış Fiyatı (PLN)": toplam_ciro, 
                "Kargo Maliyeti (PLN)": kargo, "Reklam Maliyeti (PLN)": reklam, 
                "Ödeme Kesintisi (PLN)": kesinti, "Net Kar (PLN)": net_kar
            }])
            df_s = pd.concat([df_s, yeni_satis], ignore_index=True)
            df_s.to_csv(SALES_FILE, index=False)
            
            # Stok Güncelleme
            df_p.loc[df_p["SKU"] == secilen_sku, "Stok"] -= adet
            df_p.to_csv(PROD_FILE, index=False)
            st.success(f"Satış Kaydedildi! Net Kar: {net_kar:.2f} PLN | Kalan Stok: {prod_info['Stok'] - adet}")

# TAB 3: FİNANS VE SATIŞ SİLME PANELSİ
with tab3:
    st.header("Finansal Analiz & Polonya Çeyreklik Limit Göstergesi")
    df_s = pd.read_csv(SALES_FILE)
    df_p = pd.read_csv(PROD_FILE)
    
    toplam_ciro = df_s["Satış Fiyatı (PLN)"].sum() if not df_s.empty else 0.0
    toplam_kar = df_s["Net Kar (PLN)"].sum() if not df_s.empty else 0.0
    limit = 10813.50
    kalan_limit = limit - toplam_ciro
    
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Toplam Ciro", f"{toplam_ciro:.2f} PLN")
    m2.metric("Toplam Net Kar", f"{toplam_kar:.2f} PLN")
    m3.metric("Çeyreklik Yasal Limit", f"{limit:.2f} PLN")
    m4.metric("Kalan Ciro Limiti", f"{kalan_limit:.2f} PLN", delta_color="normal")
    
    st.progress(min(toplam_ciro / limit, 1.0), text=f"Yasal Ciro Limiti Kullanım Oranı: %{(toplam_ciro/limit)*100:.1f}")
    
    st.divider()
    st.subheader("Geçmiş Satış Kayıtları ve Satış İptali / Silme")
    
    if df_s.empty:
        st.info("Henüz kaydedilmiş bir satış bulunmuyor.")
    else:
        st.dataframe(df_s, use_container_width=True)
        
        st.write("---")
        st.subheader("🗑️ Deneme / Hatalı Satış Silme")
        
        # Silinecek satırı seçme listesi
        satis_listesi = [
            f"Satır {idx} | Tarih: {row['Tarih']} | Ürün: {row['SKU']} ({row['Ürün Adı']}) | Adet: {row['Adet']} | Tutar: {row['Satış Fiyatı (PLN)']} PLN"
            for idx, row in df_s.iterrows()
        ]
        
        silinecek_satis = st.selectbox("Silmek İstediğiniz Satışı Seçin:", satis_listesi)
        
        if st.button("Seçilen Satışı Sil ve Stoğu İade Et", type="primary"):
            secilen_index = int(silinecek_satis.split(" | ")[0].replace("Satır ", ""))
            
            # Silinecek kaydın stok bilgisini al
            silinen_row = df_s.iloc[secilen_index]
            silinen_sku = silinen_row["SKU"]
            silinen_adet = silinen_row["Adet"]
            
            # 1. Satışı listeden çıkar
            df_s = df_s.drop(secilen_index).reset_index(drop=True)
            df_s.to_csv(SALES_FILE, index=False)
            
            # 2. Düşülen stoğu ürüne geri iade et
            if silinen_sku in df_p["SKU"].values:
                df_p.loc[df_p["SKU"] == silinen_sku, "Stok"] += silinen_adet
                df_p.to_csv(PROD_FILE, index=False)
            
            st.success("Satış kaydı başarıyla silindi ve stok tekrar güncellendi!")
            st.rerun()
