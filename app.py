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

# --- OYUN ZEKASI (YENİ EKLENEN KISIM) ---
def kazanma_kontrol(tahta, oyuncu):
    # Olası kazanma kombinasyonları
    kombinasyonlar = [
        [0, 1, 2], [3, 4, 5], [6, 7, 8], # Yatay
        [0, 3, 6], [1, 4, 7], [2, 5, 8], # Dikey
        [0, 4, 8], [2, 4, 6]             # Çapraz
    ]
    for a, b, c in kombinasyonlar:
        if tahta[a] == oyuncu and tahta[b] == oyuncu and tahta[c] == "":
            return c
        if tahta[a] == oyuncu and tahta[c] == oyuncu and tahta[b] == "":
            return b
        if tahta[b] == oyuncu and tahta[c] == oyuncu and tahta[a] == "":
            return a
    return None

@app.route('/pc_hamle', methods=['POST'])
def pc_hamle():
    data = request.json
    tahta = data.get('tahta')
    zorluk = data.get('zorluk') # 'kolay' veya 'zor'

    bos_yerler = [i for i, x in enumerate(tahta) if x == ""]
    
    if not bos_yerler:
        return jsonify({"hamle": None})

    secilen = None

    if zorluk == 'zor':
        # 1. Bilgisayar kazanabiliyor mu? (O)
        secilen = kazanma_kontrol(tahta, "O")
        
        # 2. Oyuncu kazanmak üzere mi? Engelle! (X)
        if secilen is None:
            secilen = kazanma_kontrol(tahta, "X")
        
        # 3. Merkez boşsa al (Stratejik hamle)
        if secilen is None and 4 in bos_yerler:
            secilen = 4

    # Eğer zor modda hamle bulamadıysa veya kolaysa rastgele seç
    if secilen is None:
        secilen = random.choice(bos_yerler)

    return jsonify({"hamle": secilen})

# --- ROTALAR ---
@app.route('/')
def ana_sayfa():
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
                sayilar = [float(s.strip()) for s in raw_data.split(',') if s.strip()]
                veriler = analiz_et(sayilar)
                with open(LOG_FILE, "a", encoding="utf-8") as f:
                    f.write(f"\n[{time.ctime()}] Veriler: {sayilar} -> Sonuçlar: {veriler}\n")
            except: pass
    return render_template('analiz.html', veriler=veriler)

@app.route('/oyun', methods=['GET', 'POST'])
def sayi_tahmin():
    mesaj = "1-100 arası bir sayı tuttum. Tahmin et!"
    durum = "mavi"
    gizli_sayi = random.randint(1, 100)

    if request.method == 'POST':
        try:
            tahmin = int(request.form.get('tahmin'))
            gizli_sayi = int(request.form.get('gizli_sayi'))
            
            if tahmin < gizli_sayi:
                mesaj = f"{tahmin} çok düşük! Daha YÜKSEK bir sayı söyle. ⬆️"
                durum = "sari"
            elif tahmin > gizli_sayi:
                mesaj = f"{tahmin} çok yüksek! Daha DÜŞÜK bir sayı söyle. ⬇️"
                durum = "sari"
            else:
                mesaj = "TEBRİKLER! 🎉 Sayıyı doğru bildin."
                durum = "yesil"
                gizli_sayi = random.randint(1, 100)
        except:
            mesaj = "Lütfen geçerli bir sayı gir!"
            durum = "sari"

    return render_template('oyun.html', mesaj=mesaj, gizli_sayi=gizli_sayi, durum=durum)

if __name__ == '__main__':
    app.run(debug=True)