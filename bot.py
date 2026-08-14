import time
import requests
from bs4 import BeautifulSoup

# =========================================================
# SENİN ÖZEL TELEGRAM BİLGİLERİN
# =========================================================
TELEGRAM_BOT_TOKEN = "8530756809:AAEuMa-8tmuQVILMSlY5cDpdeQlgAM3J1Ms"
TELEGRAM_CHAT_ID = "6351535347"

# ÖSYM Ana Duyurular Sayfası ve Sonuç Kapısı Linki
URL_DUYURU = "https://www.osym.gov.tr/TR,2/duyurular.html"
URL_SONUC_KAPISI = "https://sonuc.osym.gov.tr"

# YKS Tercih / Yerleştirme sonuçları için kilit kelimeler
ARANAN_KELIMELER = ["yks", "tercih", "yerleştirme", "sonuçları açıklanmıştır", "yerleştirme sonuçları"]

def telegram_bildirim_gonder(mesaj):
    """Telefonuna Telegram üzerinden anlık bildirim fırlatır."""
    telegram_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": mesaj,
        "parse_mode": "Markdown"
    }
    try:
        res = requests.post(telegram_url, data=payload)
        if res.status_code == 200:
            print("--> [BAŞARILI] Anlık bildirim telefonuna fırlatıldı!")
        else:
            print(f"--> [HATA] Telegram mesajı gönderilemedi! Kod: {res.status_code}")
    except Exception as e:
        print(f"--> [HATA] Bağlantı hatası: {e}")

def interneti_tara():
    """ÖSYM sitesini tarar ve sonuçların açıklanıp açıklanmadığını kontrol eder."""
    print("\n[+] ÖSYM Radar Devriyede... Yeni duyuru taranıyor...")
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    try:
        response = requests.get(URL_DUYURU, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")

        duyurular = soup.find_all("a")
        bulundu = False

        for duyuru in duyurular:
            metin = duyuru.text.strip().lower()
            
            # Aradığımız kelimelerden biri duyuruda geçiyor mu?
            if any(kelime in metin for kelime in ARANAN_KELIMELER):
                duyuru_basligi = duyuru.text.strip()
                
                bildirim_metni = (
                    "🚨 *AGA MÜJDE / ACİL DUYURU!* 🚨\n\n"
                    f"📌 *Başlık:* {duyuru_basligi}\n\n"
                    "🔥 *Tercih sonuçları açıklandı!* Aşağıdaki linke tıklayıp e-Devlet ile direkt sonucuna bakabilirsin:\n\n"
                    f"🔗 *Sonuç Ekranı:* {URL_SONUC_KAPISI}"
                )
                
                print(f"[!] KRİTİK DUYURU YAKALANDI: {duyuru_basligi}")
                telegram_bildirim_gonder(bildirim_metni)
                bulundu = True
                break

        if not bulundu:
            print("[-] Henüz YKS tercih sonuçları ilan edilmedi. Taramaya devam...")

    except Exception as e:
        print(f"--> [HATA] Siteye bağlanırken sorun oluştu: {e}")

if __name__ == "__main__":
    print("🤖 YKS Tercih Sonuç Nöbetçisi Başlatıldı!")
    
    # İlk çalıştırmada hemen bir kontrol yapalım
    interneti_tara()
    
    # Kaç saniyede bir kontrol etsin? (60 saniye = 1 Dakika)
    TARAMA_ARALIGI = 60 
    
    while True:
        time.sleep(TARAMA_ARALIGI)
        interneti_tara()
