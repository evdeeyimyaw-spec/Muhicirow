from flask import Flask, render_template, request, jsonify
import time
import os
import random

app = Flask(__name__)

# Dosya yolu güvenliği ve Log kaydı
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_FILE = os.path.join(BASE_DIR, "analiz_merkezi.txt")

# --- GELİŞMİŞ ANALİZ MOTORU ---
def analiz_et(sayilar):
    if not sayilar: return None
    toplam = sum(sayilar)
    ortalama = round(toplam / len(sayilar), 2)
    en_buyuk = max(sayilar)
    en_kucuk = min(sayilar)
    carpim = 1
    for s in sayilar: carpim *= s
    fark = sayilar[0]
    if len(sayilar) > 1:
        for s in sayilar[1:]: fark -= s
    bolum = sayilar[0]
    if len(sayilar) > 1:
        try:
            for s in sayilar[1:]:
                if s == 0:
                    bolum = "Sıfıra Bölme!"
                    break
                bolum /= s
            if isinstance(bolum, float): bolum = round(bolum, 4)
        except: bolum = "Hata"
    return {
        "toplam": toplam, "ortalama": ortalama, "en_buyuk": en_buyuk,
        "en_kucuk": en_kucuk, "carpim": carpim, "fark": fark, "bolum": bolum
    }

# --- XOX ZEKA SİSTEMİ ---
def kazanma_kontrol(tahta, oyuncu):
    kombolar = [[0,1,2],[3,4,5],[6,7,8],[0,3,6],[1,4,7],[2,5,8],[0,4,8],[2,4,6]]
    for a, b, c in kombolar:
        if tahta[a] == oyuncu and tahta[b] == oyuncu and tahta[c] == "": return c
        if tahta[a] == oyuncu and tahta[c] == oyuncu and tahta[b] == "": return b
        if tahta[b] == oyuncu and tahta[c] == oyuncu and tahta[a] == "": return a
    return None

@app.route('/pc_hamle', methods=['POST'])
def pc_hamle():
    data = request.json
    tahta = data.get('tahta')
    zorluk = data.get('zorluk', 'kolay')
    bos_yerler = [i for i, x in enumerate(tahta) if x == ""]
    
    if not bos_yerler: return jsonify({"hamle": None})

    secilen = None
    if zorluk == 'zor':
        secilen = kazanma_kontrol(tahta, "O") # Bilgisayar kazanabilir mi?
        if secilen is None: secilen = kazanma_kontrol(tahta, "X") # Oyuncuyu engelle
        if secilen is None and 4 in bos_yerler: secilen = 4 # Merkezi al

    if secilen is None: secilen = random.choice(bos_yerler) # Rastgele oyna
    return jsonify({"hamle": secilen})

# --- ROTALAR ---
@app.route('/')
def ana_sayfa(): return render_template('ana_sayfa.html')

@app.route('/tetris')
def tetris_oyunu(): return render_template('tetris.html')

@app.route('/xox')
def xox_oyunu(): return render_template('xox.html')

@app.route('/analiz', methods=['GET', 'POST'])
def analiz_sayfasi():
    veriler = None
    if request.method == 'POST':
        raw_data = request.form.get('sayilar')
        if raw_data:
            try:
                sayilar = [float(s.strip()) for s in raw_data.split(',') if s.strip()]
                veriler = analiz_et(sayilar)
                with open(LOG_FILE, "a", encoding="utf-8") as f:
                    f.write(f"\n[{time.ctime()}] Veriler: {sayilar} -> Sonuçlar: {veriler}\n")
            except: pass
    return render_template('analiz.html', veriler=veriler)

@app.route('/oyun', methods=['GET', 'POST'])
def sayi_tahmin():
    mesaj, durum, gizli_sayi = "Tahmin et!", "mavi", random.randint(1, 100)
    if request.method == 'POST':
        try:
            tahmin = int(request.form.get('tahmin'))
            gizli_sayi = int(request.form.get('gizli_sayi'))
            if tahmin < gizli_sayi: mesaj, durum = "Daha YÜKSEK! ⬆️", "sari"
            elif tahmin > gizli_sayi: mesaj, durum = "Daha DÜŞÜK! ⬇️", "sari"
            else: mesaj, durum, gizli_sayi = "TEBRİKLER! 🎉", "yesil", random.randint(1, 100)
        except: mesaj = "Geçerli bir sayı gir!"
    return render_template('oyun.html', mesaj=mesaj, gizli_sayi=gizli_sayi, durum=durum)

# ... senin mevcut kodların (analiz_et, ana_sayfa vb.) ...

@app.route('/analiz', methods=['GET', 'POST'])
def analiz_sayfasi():
    veriler = None
    if request.method == 'POST':
        raw_data = request.form.get('sayilar')
        if raw_data:
            try:
                sayilar = [float(s.strip()) for s in raw_data.split(',') if s.strip()]
                veriler = analiz_et(sayilar)
                
                # --- PROFESYONEL TAKİP SİSTEMİ BURADA BAŞLIYOR ---
                user_info = f"IP: {request.remote_addr} | Cihaz: {request.headers.get('User-Agent')[:50]}..."
                with open(LOG_FILE, "a", encoding="utf-8") as f:
                    f.write(f"\n[{time.ctime()}] {user_info} | Veriler: {sayilar}\n")
                # --- TAKİP SİSTEMİ BİTTİ ---

            except: pass
    return render_template('analiz.html', veriler=veriler)

# --- ŞİMDİ BU GİZLİ PANELİ EN ALTA (if __name__'den önce) YAPIŞTIR ---

@app.route('/admin-panel-ozel')
def admin_panel():
    kayitlar = []
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            kayitlar = f.readlines()[::-1] # En yeni kayıt en üstte
    return render_template('admin.html', kayitlar=kayitlar)

if __name__ == '__main__':
    app.run(debug=True)

if __name__ == '__main__':
    app.run(debug=True)