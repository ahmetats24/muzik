import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler,MinMaxScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
import matplotlib.pyplot as plt
data = pd.read_excel("abc.xlsx")
from sklearn.preprocessing import LabelEncoder
label_encoder = LabelEncoder()
data["deger"] = label_encoder.fit_transform(data["deger"]) + 1  # +1 ekleyerek değerleri 1, 2, 3 şeklinde başlatıyoruz
data.to_excel("kaydet.xlsx")
data = data.dropna()
data = data.drop(columns=["Dosya Adı", "Unnamed: 0"])
X = data.drop(columns=['deger'])
y = data['deger'] - 1  # Bu durumda etiketleriniz 0, 1, 2, 3 olacaktır
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.1, random_state=24)
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)
from tensorflow.keras.layers import Dense, Input
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Input
from tensorflow.keras.optimizers import Adam

model = Sequential([
    Input(shape=(X_train_scaled.shape[1],)),
    Dense(32, activation='relu'),
    Dense(16, activation='relu'),
    Dense(8, activation='relu'),
    Dense(4, activation='softmax')  # Çok sınıflı sınıflandırma için softmax
])


model.compile(optimizer=Adam(learning_rate=0.0001), loss='sparse_categorical_crossentropy', metrics=['accuracy'])
history = model.fit(X_train_scaled, y_train, epochs=300, batch_size=32, validation_split=0.1)
test_loss, test_accuracy = model.evaluate(X_test_scaled, y_test)
print("Test accuracy:", test_accuracy)
model.save("kaydet.h5")