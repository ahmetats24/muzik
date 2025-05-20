import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout, Input
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import EarlyStopping
import librosa
import os
import librosa.display
import matplotlib.pyplot as plt
from keras_tuner import HyperModel, RandomSearch

# Veri Okuma ve Ön İşleme
data = pd.read_excel("abc.xlsx")
from sklearn.preprocessing import LabelEncoder

label_encoder = LabelEncoder()
data["deger"] = label_encoder.fit_transform(data["deger"]) + 1  # Değerleri 1, 2, 3 şeklinde başlatıyoruz
data.to_excel("kaydet.xlsx")
data = data.dropna()
data = data.drop(columns=["Dosya Adı", "Unnamed: 0"])

# Veri ve Etiket Ayrımı
X = data.drop(columns=['deger'])
y = data['deger'] - 1  # Etiketler 0, 1, 2, 3 olacak

# Sınıf Dağılımını Kontrol
print("Class distribution:")
print(data['deger'].value_counts())

# Veri Ayrımı
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.1, random_state=24)

# Normalizasyon
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# --- Özellik Mühendisliği --- 
def extract_features(audio_file):
    y, sr = librosa.load(audio_file, sr=None)
    features = []

    # RMS
    rms_mean = np.mean(librosa.feature.rms(y=y))
    features.append(rms_mean)

    # Tempo
    tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
    features.append(float(tempo))

    # Brightness
    brightness_mean = np.mean(librosa.feature.spectral_centroid(y=y, sr=sr))
    features.append(brightness_mean)

    # MFCC
    mfcc_means = np.mean(librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13), axis=1).mean()
    features.append(mfcc_means)

    # Spectral Contrast
    roughness_mean = np.mean(librosa.feature.spectral_contrast(y=y, sr=sr))
    features.append(roughness_mean)

    # Zero Crossing Rate
    zero_crossing_mean = np.mean(librosa.feature.zero_crossing_rate(y=y))
    features.append(zero_crossing_mean)

    # Chroma
    chroma_means = np.mean(librosa.feature.chroma_stft(y=y, sr=sr))
    features.append(chroma_means)

    # Delta MFCC
    delta_mfcc = np.mean(librosa.feature.delta(librosa.feature.mfcc(y=y, sr=sr)))
    features.append(delta_mfcc)

    # Delta-Delta MFCC
    delta_delta_mfcc = np.mean(librosa.feature.delta(librosa.feature.mfcc(y=y, sr=sr), order=2))
    features.append(delta_delta_mfcc)

    # Spectral Roll-off
    spectral_rolloff = np.mean(librosa.feature.spectral_rolloff(y=y, sr=sr))
    features.append(spectral_rolloff)

    return np.array(features)

# --- Modeli Tanımlama ve Hiperparametre Optimizasyonu --- 
class MyModel(HyperModel):
    def build(self, hp):
        model = Sequential([
            Input(shape=(X_train_scaled.shape[1],)),
            Dense(hp.Int('units1', min_value=32, max_value=512, step=32), activation='relu', kernel_regularizer='l2'),
            Dropout(hp.Float('dropout', min_value=0.1, max_value=0.5, step=0.1)),
            Dense(64, activation='relu', kernel_regularizer='l2'),
            Dropout(0.3),
            Dense(32, activation='relu', kernel_regularizer='l2'),
            Dropout(0.3),
            Dense(16, activation='relu', kernel_regularizer='l2'),
            Dropout(0.3),
            Dense(4, activation='softmax')
        ])
        model.compile(
            optimizer=Adam(learning_rate=hp.Float('learning_rate', min_value=1e-5, max_value=1e-2, sampling='log')),
            loss='sparse_categorical_crossentropy',
            metrics=['accuracy']
        )
        return model

tuner = RandomSearch(
    MyModel(),
    objective='val_accuracy',
    max_trials=10,
    executions_per_trial=3,
    directory='hyperparam_tuning',
    project_name='audio_classification'
)

# Modeli eğitme ve optimizasyon
tuner.search(X_train_scaled, y_train, epochs=50, validation_split=0.1)

best_model = tuner.get_best_models(num_models=1)[0]

# --- Model Eğitim ve Test --- 
history = best_model.fit(
    X_train_scaled, y_train,
    epochs=50,
    batch_size=32,
    validation_split=0.1,
    callbacks=[EarlyStopping(monitor='val_loss', patience=5, restore_best_weights=True)]
)

# Test Performansı
test_loss, test_accuracy = best_model.evaluate(X_test_scaled, y_test)
print("Test accuracy:", test_accuracy)

# Performans Görselleştirme
plt.plot(history.history['accuracy'], label='Train Accuracy')
plt.plot(history.history['val_accuracy'], label='Validation Accuracy')
plt.legend()
plt.show()

plt.plot(history.history['loss'], label='Train Loss')
plt.plot(history.history['val_loss'], label='Validation Loss')
plt.legend()
plt.show()

# Modeli Kaydetme
best_model.save("best_model.h5")
