from tensorflow.keras.models import load_model

# Modeli eğitmişseniz veya yüklemişseniz
# model = Sequential(...) veya 
model = load_model('kaydet.h5')

# Modeli tahmin için kullanma
import numpy as np
input_data = np.array([[112, 12, 123, 1312, 123123, 123123, 123]])
tahmin = model.predict(input_data)
print("Tahmin Sonucu:", tahmin)

# Modeli .h5 dosyasına kaydetme
model.save("model_kayit.h5")