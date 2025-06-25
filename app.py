from flask import Flask, request, jsonify, render_template
from db import veri_ekle, veri_listele, get_db_connection  # ✅ Yeni eklendi
from datetime import datetime
import pandas as pd
import pickle
import numpy as np
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.sequence import pad_sequences

app = Flask(__name__)

#  NLP model dosyalarını yükle
model = load_model("models/sebep_model.h5")
with open("models/tokenizer.pkl", "rb") as f:
    tokenizer = pickle.load(f)
with open("models/label_encoder.pkl", "rb") as f:
    label_encoder = pickle.load(f)

#  Mahalle bazlı etiketli kaza verisi
try:
    kaza_df = pd.read_csv("data/kaza_verisi_etiketli.csv")
    kaza_df.columns = [col.strip().lower() for col in kaza_df.columns]
    kaza_df["mahalle"] = kaza_df["mahalle"].str.replace(" Mahallesi", "", regex=False).str.strip().str.lower()
except Exception as e:
    print("CSV dosyası okunamadı:", e)
    kaza_df = pd.DataFrame()

#  Ana sayfa
@app.route('/')
def index():
    return render_template('index.html')

#  Belediye paneli
@app.route('/belediye')
def belediye():
    return render_template('belediye.html')

#  Kayıtlı ihbarları göster
@app.route('/veriler')
def veriler():
    veriler = veri_listele()
    return render_template('veriler.html', veriler=veriler)

#  NLP tahmin ve veritabanı kaydı
@app.route('/tahmin', methods=['POST'])
def tahmin():
    veri = request.get_json()
    metin = veri.get("ihbar", "")
    mahalle = veri.get("mahalle", "")
    ilce = veri.get("ilce", "")
    acil_no = veri.get("acil", "")
    tarih = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    try:
        sekans = tokenizer.texts_to_sequences([metin.lower()])
        pad = pad_sequences(sekans, maxlen=100)
        olasiliklar = model.predict(pad)
        tahmin_indeksi = np.argmax(olasiliklar)
        tahmin = label_encoder.inverse_transform([tahmin_indeksi])[0]
        olasilik = round(float(olasiliklar[0][tahmin_indeksi]) * 100, 2)

        veri_ekle(acil_no, ilce, mahalle, metin, tahmin, tarih)

        return jsonify({
            "tahmin": tahmin,
            "riskYuzdesi": olasilik
        })

    except Exception as e:
        return jsonify({"hata": str(e)}), 500

#  İlçeye göre mahalle kaza dağılımı
@app.route('/kaza_tahmin', methods=['POST'])
def kaza_tahmin():
    veri = request.get_json()
    ilce = veri.get('ilce', '').strip().lower()

    filtre = kaza_df[kaza_df['ilce'].str.lower().str.strip() == ilce]
    if filtre.empty:
        return jsonify({
            "risk": "Veri bulunamadı",
            "seviye": "Bilinmiyor",
            "mahalle_kazalari": {}
        })

    mahalle_kazalari = filtre['mahalle'].value_counts().to_dict()
    return jsonify({
        "ilce": ilce,
        "mahalle_kazalari": mahalle_kazalari
    })

#  Mahalleye göre son 6 ay kaza geçmişi
@app.route('/mahalle_kaza_gecmisi', methods=['POST'])
def mahalle_kaza_gecmisi():
    veri = request.get_json()
    mahalle = veri.get('mahalle', '').replace(" Mahallesi", "").strip().lower()

    try:
        df = pd.read_csv("data/kaza_verisi_etiketli.csv")
        df.columns = [c.strip().lower() for c in df.columns]
        df['mahalle'] = df['mahalle'].str.replace(" Mahallesi", "", regex=False).str.lower().str.strip()
        df['tarih'] = pd.to_datetime(df['tarih'], errors='coerce')
        df = df[df['tarih'].notna() & (df['mahalle'] == mahalle)]

        son_6_ay = pd.Timestamp.now() - pd.DateOffset(months=6)
        df = df[df['tarih'] >= son_6_ay]
        aylik = df.groupby(df['tarih'].dt.to_period('M')).size().reset_index(name='kaza')
        aylik['tarih'] = aylik['tarih'].astype(str)

        return jsonify({
            "aylar": aylik['tarih'].tolist(),
            "kazalar": aylik['kaza'].tolist()
        })

    except Exception as e:
        return jsonify({"hata": str(e)}), 500

@app.route("/mahalle_sebep_oranlari", methods=["POST"])
def mahalle_sebep_oranlari():
    veri = request.get_json()
    mahalle = veri.get('mahalle', '').strip().lower()

    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT tahmin, COUNT(*) FROM ihbarlar
            WHERE LOWER(mahalle) = %s
            GROUP BY tahmin
        """, (mahalle,))
        rows = cur.fetchall()
        cur.close()
        conn.close()

        if not rows:
            return jsonify({"hata": "Bu mahalleye ait veri bulunamadı."})

        toplam = sum([r[1] for r in rows])
        oranlar = {r[0]: round(r[1] / toplam, 4) for r in rows}

        return jsonify(oranlar)

    except Exception as e:
        return jsonify({"hata": str(e)})
    
#  İlçeye göre mahalle kaza sayıları (grafik için)
@app.route('/ilce_kaza_dagilimi', methods=['POST'])
def ilce_kaza_dagilimi():
    veri = request.get_json()
    ilce = veri.get('ilce', '').strip().lower()
    mahalle = veri.get('mahalle', '').strip().lower()

    try:
        df = pd.read_csv("data/kaza_verisi_etiketli.csv")
        df.columns = [col.strip().lower() for col in df.columns]
        df["mahalle"] = df["mahalle"].str.lower().str.strip()
        df["ilce"] = df["ilce"].str.lower().str.strip()

        ilce_df = df[df["ilce"] == ilce]
        if ilce_df.empty:
            return jsonify({"hata": "İlçeye ait veri bulunamadı"})

        sayilar = ilce_df["mahalle"].value_counts().to_dict()
        return jsonify({
            "mahalleler": list(sayilar.keys()),
            "kazalar": list(sayilar.values()),
            "secilen": mahalle
        })

    except Exception as e:
        return jsonify({"hata": str(e)})

#  Uygulama başlat
if __name__ == '__main__':
    app.run(debug=True)
