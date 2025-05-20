from flask import Flask, jsonify, request, render_template
import json
import os
import librosa
import numpy as np
from tensorflow.keras.models import load_model

# Load the model
model = load_model('kaydet.h5')

# Define labels for model output in one-hot encoding format
etiketler = {
    (0, 1, 0, 0): "happy",
    (1, 0, 0, 0): "angry",
    (0, 0, 1, 0): "relax",
    (0, 0, 0, 1): "sad"
}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['ALLOWED_EXTENSIONS'] = {'mp3'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def şarkı_degerler():
    tüm_degerler = []
    dizin = os.listdir(app.config['UPLOAD_FOLDER'])
    for i in dizin:
        if i.endswith(".mp3"):
            try:
                dizi = []
                audio_file = os.path.join(app.config['UPLOAD_FOLDER'], i)
                y, sr = librosa.load(audio_file, sr=None)
                
                # Feature extraction
                rms_mean = np.mean(librosa.feature.rms(y=y))
                dizi.append(rms_mean)
                
                tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
                dizi.append(float(tempo))
                
                brightness_mean = np.mean(librosa.feature.spectral_centroid(y=y, sr=sr))
                dizi.append(brightness_mean)
                
                mfcc_means = np.mean(librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13), axis=1).mean()
                dizi.append(mfcc_means)
                
                roughness_mean = np.mean(librosa.feature.spectral_contrast(y=y, sr=sr))
                dizi.append(roughness_mean)
                
                zero_crossing_mean = np.mean(librosa.feature.zero_crossing_rate(y=y))
                dizi.append(zero_crossing_mean)
                
                chroma_means = np.mean(librosa.feature.chroma_stft(y=y, sr=sr))
                dizi.append(chroma_means)
                
                tüm_degerler.append(np.array(dizi))
            except Exception as e:
                print(f"Error processing {i}: {e}")
    return np.array(tüm_degerler)

def model_tahmin():
    try:
        şarkı_degerleri = şarkı_degerler()
        tahmin = model.predict(şarkı_degerleri)
        
        # Convert each prediction to a one-hot tuple and map it to the label
        predicted_labels = []
        for pred in tahmin:
            one_hot = tuple((pred > 0.5).astype(int))  # Convert probabilities to one-hot
            label = etiketler.get(one_hot, "Unknown")  # Map to label or return "Unknown"
            predicted_labels.append(label)
        
        return predicted_labels
    except Exception as e:
        print(f"Prediction error: {e}")
        return ["Prediction error"]

@app.route('/')
def index_sayfası():
    return render_template('index.html')

@app.route('/sarkilar', methods=['GET'])
def get_songs():
    try:
        with open("cevirmis_dosya.json", 'r', encoding='utf-8') as json_file:
            data = json.load(json_file)
        return jsonify(data)
    except FileNotFoundError:
        return jsonify({"error": "File not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    if file and allowed_file(file.filename):
        filename = file.filename
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        tahmin = model_tahmin()
        return jsonify({"message": "File uploaded and model prediction done", "prediction": tahmin}), 200
    else:
        return render_template('index.html')

if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    app.run(debug=True,host='0.0.0.0', port=8000)
