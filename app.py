from flask import Flask, render_template, request
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
    
    # Çarpım hesaplama
    carpim = 1
    for s in sayilar: carpim *= s
    
    # Fark (1. sayıdan diğerlerini çıkarır)
    fark = sayilar[0]
    if len(sayilar) > 1:
        for s in sayilar[1:]: fark -= s
            
    # Bölüm (1. sayıyı diğerlerine böler)
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

# --- ROTALAR ---

@app.route('/pc_hamle', methods=['POST'])
def pc_hamle():
    tahta = request.json.get('tahta') # Mevcut tahta durumu
    bos_kareler = [i for i, x in enumerate(tahta) if x == ""]
    
    if bos_kareler:
        secilen_kare = random.choice(bos_kareler)
        return {"hamle": secilen_kare}
    return {"hamle": None}

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
                # Kayıt işlemi
                with open(LOG_FILE, "a", encoding="utf-8") as f:
                    f.write(f"\n[{time.ctime()}] Veriler: {sayilar} -> Sonuçlar: {veriler}\n")
            except: pass
    return render_template('analiz.html', veriler=veriler)

@app.route('/oyun', methods=['GET', 'POST'])
def sayi_tahmin():
    mesaj = "1-100 arası bir sayı tuttum. Tahmin et!"
    durum = "mavi" # CSS sınıfı için (mavi, sari, yesil)
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
                mesaj = "TEBRİKLER! 🎉 Sayıyı doğru bildin. Yeni bir sayı tuttum!"
                durum = "yesil"
                gizli_sayi = random.randint(1, 100) # Kazanınca yeni sayı
        except:
            mesaj = "Lütfen geçerli bir sayı gir!"
            durum = "sari"

    return render_template('oyun.html', mesaj=mesaj, gizli_sayi=gizli_sayi, durum=durum)

if __name__ == '__main__':
    app.run(debug=True)

@app.route('/pc_hamle', methods=['POST'])
def pc_hamle():
    data = request.json
    tahta = data.get('tahta')
    
    import random
    # Boş hücreleri bul (X veya O olmayanlar)
    bos_yerler = [i for i, x in enumerate(tahta) if x == "" or x == None]
    
    if bos_yerler:
        secilen = random.choice(bos_yerler)
        return {"hamle": secilen}
    return {"hamle": None}