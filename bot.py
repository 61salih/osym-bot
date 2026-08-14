import time
import requests
from bs4 import BeautifulSoup
from flask import Flask
import threading

# Render uykusunu engellemek için minik bir web sunucusu
app = Flask(__name__)

@app.route('/')
def home():
    return "ÖSYM Nöbetçi Botu Aktif ve Çalışıyor!"

def run_flask():
    app.run(host='0.0.0.0', port=10000)

# =========================================================
# TELEGRAM BİLGİLERİN
# =========================================================
TELEGRAM_BOT_TOKEN = "8530756809:AAEuMa-8tmuQVILMSlY5cDpdeQlgAM3J1Ms"
TELEGRAM_CHAT_ID = "6351535347"

URL_DUYURU = "https://www.osym.gov.tr/TR,2/duyurular.html"
URL_SONUC_KAPISI = "https://sonuc.osym.gov.tr"

ARANAN_KELIMELER = ["yks", "tercih", "yerleştirme", "sonuçları açıklanmıştır", "yerleştirme sonuçları"]

def telegram_bildirim_gonder(mesaj):
    telegram_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": mesaj,
        "parse_mode": "Markdown",
        "disable_notification": False # Bildirimin yüksek sesle çıkmasını zorlar
    }
    try:
        res = requests.post(telegram_url, data=payload)
        if res.status_code == 200:
            print("--> [BAŞARILI] Yüksek öncelikli bildirim gönderildi!")
    except Exception as e:
        print(f"--> [HATA] Bildirim hatası: {e}")

def interneti_tara():
    print("\n[+] Render Nöbetçisi Devriyede... ÖSYM taranıyor...")
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
            if any(kelime in metin for kelime in ARANAN_KELIMELER):
                duyuru_basligi = duyuru.text.strip()
                bildirim_metni = (
                    "🚨 *AGA MÜJDE / ACİL DUYURU!* 🚨\n\n"
                    f"📌 *Başlık:* {duyuru_basligi}\n\n"
                    "🔥 *Tercih sonuçları açıklandı!* Aşağıdaki linke tıklayıp e-Devlet ile direkt sonucuna bakabilirsin:\n\n"
                    f"🔗 *Sonuç Ekranı:* {URL_SONUC_KAPISI}"
                )
                print(f"[!] DUYURU YAKALANDI: {duyuru_basligi}")
                telegram_bildirim_gonder(bildirim_metni)
                bulundu = True
                break

        if not bulundu:
            print("[-] Yeni duyuru yok. Nöbet devam ediyor...")

    except Exception as e:
        print(f"--> [HATA] Bağlantı hatası: {e}")

def bot_loop():
    while True:
        interneti_tara()
        time.sleep(60) # 1 dakikada bir kontrol et

if __name__ == "__main__":
    print("🤖 Bot Başlatıldı!")
    
    # Arka planda t tarama döngüsünü başlat
    t = threading.Thread(target=bot_loop)
    t.daemon = True
    t.start()
    
    # Flask sunucusunu çalıştır (Render için)
    run_flask()
