import requests

# API URL'si
url = "http://127.0.0.1:5000/api/get-response"  # Flask uygulaması yerel olarak çalışıyorsa bu URL'yi kullanın

# Gönderilecek veri
data = {
    "query": "me"  # Flask API'ye gönderilecek sorgu metni
}

try:
    # POST isteği gönder
    response = requests.post(url, json=data)

    # Yanıtı kontrol et
    if response.status_code == 200:
        print("API Yanıtı:")
        print(response.json())  # JSON formatında dönen cevabı yazdır
    else:
        print(f"API isteği başarısız oldu. Durum kodu: {response.status_code}")
        print(response.text)  # Hata durumunda detayları yazdır
except Exception as e:
    print(f"Bir hata oluştu: {e}")
