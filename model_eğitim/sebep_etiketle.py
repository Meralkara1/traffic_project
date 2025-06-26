import pandas as pd

# CSV dosyasını yükle (daha önce ilçe ve mahalle eklenmiş olmalı)
df = pd.read_csv("data/ibb_kaza_mahalle_ilce.csv")

# Sebep etiketleme fonksiyonu
def sebep_belirle(baslik):
    baslik = str(baslik).lower()

    if any(kelime in baslik for kelime in ["aşırı hız", "hız", "sürat", "hızlı araç", "hızlı seyir"]):
        return "hız problemi"

    elif any(kelime in baslik for kelime in ["şerit", "şerit ihlali", "şerit değişimi", "şerit kapalı", "sol şerit", "sağ şerit"]):
        return "şerit ihlali"

    elif any(kelime in baslik for kelime in ["kaygan", "zemin", "yağış", "yağmur", "kar", "buz", "don", "çamur", "ıslak"]):
        return "kaygan zemin"

    elif any(kelime in baslik for kelime in ["yoğun trafik", "yoğunluk", "sıkışıklık", "trafiğin yoğun", "trafik sıkışıklığı"]):
        return "yoğun trafik"

    elif any(kelime in baslik for kelime in ["ışık", "levha", "uyarı", "reflektör", "sinayal", "trafik levhası", "yol çizgisi"]):
        return "ışık/levha eksikliği"

    elif any(kelime in baslik for kelime in ["kavşak", "dönel kavşak", "kontrolsüz kavşak", "dönemeç", "viraj", "yol ayrımı"]):
        return "kavşak tasarımı"

    elif any(kelime in baslik for kelime in ["arızalı", "arıza", "lastik patlaması", "fren", "motor", "bozulma", "stop etti"]):
        return "araç arızası"

    elif any(kelime in baslik for kelime in ["yol çalışması", "bakım", "onarım", "yol yapım", "kazı", "altyapı"]):
        return "altyapı çalışması"

    elif any(kelime in baslik for kelime in ["yaya", "yaya çarpması", "yaya geçidi", "karşıdan karşıya", "yaya yolu"]):
        return "yaya kaynaklı"

    else:
        return "belirsiz"


# Yeni sütunu uygula
df["SEBEP"] = df["ANNOUNCEMENT_TITLE"].apply(sebep_belirle)

# Yeni CSV olarak kaydet
df.to_csv("data/ibb_kaza_etiketli.csv", index=False, encoding="utf-8-sig")

print("✅ Etiketleme tamamlandı. Dosya: data/ibb_kaza_etiketli.csv")
