import pandas as pd
import pickle
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.utils import to_categorical
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Embedding, LSTM, Dense, Dropout

# Veriyi yükle
df = pd.read_csv("data/kaza_verisi_etiketli.csv")
df = df.dropna(subset=["TEMIZ_BASLIK", "SEBEP"])

# Etiket kodlama
le = LabelEncoder()
df["label_encoded"] = le.fit_transform(df["SEBEP"])
num_classes = len(le.classes_)

# LabelEncoder'ı kaydet
with open("models/label_encoder.pkl", "wb") as f:
    pickle.dump(le, f)

# Metinleri sayıya çevir
tokenizer = Tokenizer(num_words=5000)
tokenizer.fit_on_texts(df["TEMIZ_BASLIK"])
X = tokenizer.texts_to_sequences(df["TEMIZ_BASLIK"])
X = pad_sequences(X, maxlen=30)

# Tokenizer'ı da kaydet (tahmin kısmında lazım olabilir)
with open("models/tokenizer.pkl", "wb") as f:
    pickle.dump(tokenizer, f)

# Etiketleri one-hot encode et
y = to_categorical(df["label_encoded"], num_classes=num_classes)

# Eğitim ve test bölmesi
X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, random_state=42)

# Model mimarisi
model = Sequential()
model.add(Embedding(input_dim=5000, output_dim=128, input_length=30))
model.add(LSTM(64, return_sequences=False))
model.add(Dropout(0.5))
model.add(Dense(num_classes, activation='softmax'))

# Derleme
model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])

# Eğitim
model.fit(X_train, y_train,
          epochs=50,
          batch_size=64,
          validation_data=(X_val, y_val),
          verbose=1)

# Modeli kaydet (hem .keras hem .h5 formatında)
model.save("models/sebep_model.keras")
model.save("models/sebep_model.h5")

# Test değerlendirmesi
score = model.evaluate(X_val, y_val, verbose=1)
print(f"✅ Test Doğruluğu: {score[1]:.4f}")
print("📁 Model, tokenizer ve etiketleyici başarıyla kaydedildi.")
