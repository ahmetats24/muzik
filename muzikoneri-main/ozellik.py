import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Input
from tensorflow.keras.optimizers import Adam

# Veri yükleme
data = pd.read_excel("abc.xlsx")

# Kategorik veriler için etiketleme
label_encoder = LabelEncoder()
data["deger"] = label_encoder.fit_transform(data["deger"]) + 1  # Sınıfları 1, 2, 3 şeklinde başlatıyoruz

# Eksik verileri temizleme
data = data.dropna()

# Kullanılmayan sütunları kaldırma
data = data.drop(columns=["Dosya Adı", "Unnamed: 0"], errors='ignore')

# **Özellik Detayları Algoritması**
# Numerik sütunlarda özet istatistiklerin çıkarılması
for column in data.select_dtypes(include=[np.number]).columns:
    data[f"{column}_mean"] = data[column].mean()  # Ortalamayı özellik olarak ekle
    data[f"{column}_std"] = data[column].std()    # Standart sapmayı özellik olarak ekle
    data[f"{column}_max"] = data[column].max()    # Maksimum değeri ekle
    data[f"{column}_min"] = data[column].min()    # Minimum değeri ekle
    data[f"{column}_range"] = data[column].max() - data[column].min()  # Aralık

# Kategorik sütunlar için frekans bazlı özellikler
for column in data.select_dtypes(include=['object']).columns:
    freq_map = data[column].value_counts().to_dict()
    data[f"{column}_freq"] = data[column].map(freq_map)

# Yeni özellikler eklenmiş veriyi kaydetme
data.to_excel("kaydet_with_features.xlsx")

# Hedef ve bağımsız değişkenlerin ayrılması
X = data.drop(columns=['deger'])
y = data['deger'] - 1  # Etiketler 0, 1, 2, 3 olacak şekilde ayarlanıyor

# Eğitim ve test seti ayrımı
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.1, random_state=24)

# Veriyi ölçeklendirme
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# Model oluşturma
model = Sequential([
    Input(shape=(X_train_scaled.shape[1],)),
    Dense(32, activation='relu'),
    Dense(16, activation='relu'),
    Dense(8, activation='relu'),
    Dense(4, activation='softmax')  # Çok sınıflı sınıflandırma için softmax
])

# Model derleme
model.compile(optimizer=Adam(learning_rate=0.0001), loss='sparse_categorical_crossentropy', metrics=['accuracy'])

# Model eğitimi
history = model.fit(X_train_scaled, y_train, epochs=300, batch_size=32, validation_split=0.1)

# Modeli değerlendirme
test_loss, test_accuracy = model.evaluate(X_test_scaled, y_test)
print("Test accuracy:", test_accuracy)

# Modeli kaydetme
model.save("kaydet_with_features.h5")
