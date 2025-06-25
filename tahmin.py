import os
import pickle
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.sequence import pad_sequences

#  Model dosyalarının yolu
MODEL_YOLU = "models/sebep_model.h5"
TOKENIZER_YOLU = "models/tokenizer.pkl"
ENCODER_YOLU = "models/label_encoder.pkl"

#  Model ve yardımcı dosyaları yükle
def modeli_yukle():
    if not os.path.exists(MODEL_YOLU):
        print(" Model dosyası bulunamadı:", MODEL_YOLU)
        return None, None, None

    print(" Model yükleniyor...")
    model = load_model(MODEL_YOLU)

    with open(TOKENIZER_YOLU, "rb") as f:
        tokenizer = pickle.load(f)

    with open(ENCODER_YOLU, "rb") as f:
        label_encoder = pickle.load(f)

    print(" Model, tokenizer ve encoder yüklendi.")
    return model, tokenizer, label_encoder

# 🔹 Tahmin fonksiyonu
def tahmin_yap(metin, model, tokenizer, label_encoder):
    sekans = tokenizer.texts_to_sequences([metin.lower()])
    padded = pad_sequences(sekans, maxlen=30)
    tahmin = model.predict(padded)
    return label_encoder.inverse_transform([tahmin.argmax()])[0]

# 🔹 Ana test bölümü
if __name__ == "__main__":
    model, tokenizer, label_encoder = modeli_yukle()
    if model is None:
        exit()

    while True:
        metin = input("\n İhbar metni gir (çıkmak için q): ").strip()
        if metin.lower() == "q":
            print(" Görüşmek üzere!")
            break

        try:
            sonuc = tahmin_yap(metin, model, tokenizer, label_encoder)
            print(" Tahmin edilen sebep:", sonuc)
        except Exception as e:
            print(" Tahmin yapılırken hata oluştu:", str(e))
