import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, MinMaxScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout, Input
from tensorflow.keras.optimizers import Adam

# Veri yükleme ve hazırlık
data = pd.read_excel("abc.xlsx")
label_encoder = LabelEncoder()
data["deger"] = label_encoder.fit_transform(data["deger"]) + 1
data.to_excel("kaydet.xlsx")
data = data.dropna()
data = data.drop(columns=["Dosya Adı", "Unnamed: 0"])

# Giriş ve hedef değişkenlerin ayrılması
X = data.drop(columns=['deger'])
y = data['deger'] - 1  # Etiketler 0, 1, 2, 3 olacak şekilde ayarlandı

# Veri setinin bölünmesi
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.1, random_state=24)

# Özellik ölçeklendirme
scaler = MinMaxScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# Model tanımlama
model = Sequential([
    Input(shape=(X_train_scaled.shape[1],)),
    Dense(128, activation='relu'),  # Daha fazla nöron
    Dropout(0.2),                  # Overfitting'i azaltmak için
    Dense(64, activation='relu'),
    Dropout(0.2),
    Dense(32, activation='relu'),
    Dense(4, activation='softmax')  # Çok sınıflı sınıflandırma için softmax
])

# Model derleme
model.compile(optimizer=Adam(learning_rate=0.001), loss='sparse_categorical_crossentropy', metrics=['accuracy'])

# Model eğitimi
history = model.fit(X_train_scaled, y_train, epochs=500, batch_size=64, validation_split=0.1)

# Test değerlendirmesi
test_loss, test_accuracy = model.evaluate(X_test_scaled, y_test)
print("Test accuracy:", test_accuracy)

# Model kaydetme
model.save("kaydet.h5")
