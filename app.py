from flask import Flask, render_template, request, jsonify
import time
import os
import random

# Flask uygulamasını başlatıyoruz
app = Flask(__name__)

# --- DOSYA AYARLARI ---
# Log dosyasının nerede oluşturulacağını kesinleştiriyoruz
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_FILE = os.path.join(BASE_DIR, "analiz_merkezi.txt")

# --- YARDIMCI FONKSİYON: ANALİZ MOTORU ---
def analiz_et(sayilar):
    if not sayilar: return None
    # Temel Hesaplamalar
    toplam = sum(sayilar)
    ortalama = round(toplam / len(sayilar), 2)
    en_buyuk = max(sayilar)
    en_kucuk = min(sayilar)
    
    # Çarpım Hesaplama
    carpim = 1
    for s in sayilar: carpim *= s
    
    # Fark Hesaplama
    fark = sayilar[0]
    if len(sayilar) > 1:
        for s in sayilar[1:]: fark -= s
        
    # Bölüm Hesaplama (Hata korumalı)
    bolum = sayilar[0]
    if len(sayilar) > 1:
        try:
            for s in sayilar[1:]:
                if s == 0:
                    bolum = "Tanımsız (0'a bölme)"
                    break
                bolum /= s
            if isinstance(bolum, float): bolum = round(bolum, 4)
        except: bolum = "Hata"
            
    return {
        "toplam": toplam, "ortalama": ortalama, "en_buyuk": en_buyuk, 
        "en_kucuk": en_kucuk, "carpim": carpim, "fark": fark, "bolum": bolum
    }

# --- ROTALAR (SAYFALAR) ---

@app.route('/')
def ana_sayfa():
    # Ana sayfa HTML dosyanın adı tam olarak buysa çalışır
    return render_template('ana_sayfa.html')

@app.route('/tetris')
def tetris_oyunu():
    return render_template('tetris.html')

@app.route('/xox')
def xox_oyunu():
    return render_template('xox.html')

@app.route('/analiz', methods=['GET', 'POST'])
def analiz_sayfasi():
    veriler = None
    if request.method == 'POST':
        raw_data = request.form.get('sayilar')
        if raw_data:
            try:
                # Virgülle ayrılan sayıları temizleyip listeye çeviriyoruz
                sayilar = [float(s.strip()) for s in raw_data.split(',') if s.strip()]
                veriler = analiz_et(sayilar)
                
                # --- BURASI TAKİP SİSTEMİ ---
                # Kullanıcının IP'sini ve verilerini kaydediyoruz
                ip_adresi = request.remote_addr
                zaman = time.ctime()
                with open(LOG_FILE, "a", encoding="utf-8") as f:
                    f.write(f"[{zaman}] IP: {ip_adresi} | Girdi: {sayilar}\n")
                # ----------------------------
                
            except: 
                # Hata olursa sessizce geç, site çökmesin
                pass
    return render_template('analiz.html', veriler=veriler)

@app.route('/oyun', methods=['GET', 'POST'])
def sayi_tahmin():
    # Sayı tahmin oyunu mantığı
    mesaj, durum, gizli_sayi = "Tahmin et!", "mavi", random.randint(1, 100)
    
    # Not: Bu basit versiyonda gizli_sayi her yenilemede değişir.
    # Sabit kalması için veritabanı gerekir ama şimdilik böyle çalışsın.
    if request.method == 'POST':
        try:
            tahmin = int(request.form.get('tahmin'))
            gelen_gizli = request.form.get('gizli_sayi')
            if gelen_gizli:
                gizli_sayi = int(gelen_gizli)
            
            if tahmin < gizli_sayi:
                mesaj, durum = f"{tahmin} daha büyük söyle! ⬆️", "sari"
            elif tahmin > gizli_sayi:
                mesaj, durum = f"{tahmin} daha küçük söyle! ⬇️", "sari"
            else:
                mesaj, durum = f"TEBRİKLER! Sayı {gizli_sayi} idi. 🎉", "yesil"
                gizli_sayi = random.randint(1, 100) # Yeni sayı tut
        except: pass
        
    return render_template('oyun.html', mesaj=mesaj, durum=durum, gizli_sayi=gizli_sayi)

# --- YENİ EKLENEN ADMIN PANELİ ---
@app.route('/admin-panel-ozel')
def admin_panel():
    kayitlar = []
    # Dosya varsa oku, yoksa boş liste gönder (Hata vermez)
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            kayitlar = f.readlines()[::-1] # Ters çevir (en yeni en üstte)
    return render_template('admin.html', kayitlar=kayitlar)

# --- KRİTİK NOKTA: UYGULAMAYI BAŞLATMA ---
# Bu kısım dosyanın EN SONUNDA ve TEK SEFER olmalı.
if __name__ == '__main__':
    # Render'da host='0.0.0.0' önemlidir, dışarıdan erişime açar.
    app.run(host='0.0.0.0', port=10000, debug=True)

    # --- XOX BİLGİSAYAR HAMLESİ (Burası app.py en altına gelecek) ---
@app.route('/pc_hamle', methods=['POST'])
def pc_hamle():
    data = request.json
    tahta = data.get('tahta') 
    zorluk = data.get('zorluk')

    bos_yerler = [i for i, x in enumerate(tahta) if x == ""]

    if not bos_yerler:
        return jsonify({'hamle': None})

    secilen_hamle = None

    if zorluk == "zor":
        # Kazanma hamlesi
        secilen_hamle = kazanma_kontrolu(tahta, "O", bos_yerler)
        # Engelleme hamlesi
        if secilen_hamle is None:
            secilen_hamle = kazanma_kontrolu(tahta, "X", bos_yerler)

    if secilen_hamle is None:
        secilen_hamle = random.choice(bos_yerler)

    return jsonify({'hamle': secilen_hamle})

def kazanma_kontrolu(tahta, oyuncu, bos_yerler):
    kombinasyonlar = [
        [0, 1, 2], [3, 4, 5], [6, 7, 8],
        [0, 3, 6], [1, 4, 7], [2, 5, 8],
        [0, 4, 8], [2, 4, 6]
    ]
    for k in kombinasyonlar:
        hucreler = [tahta[i] for i in k]
        if hucreler.count(oyuncu) == 2 and hucreler.count("") == 1:
            for indeks in k:
                if tahta[indeks] == "":
                    return indeks
    return None