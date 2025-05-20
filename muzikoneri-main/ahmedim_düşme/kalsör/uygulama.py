import json
import google.generativeai as genai
from flask import Flask, jsonify
from flask_compress import Compress
from flask import Flask, request, jsonify

app = Flask(__name__)
Compress(app)
with open("tüm_ürünler.json", "r", encoding="utf-8") as file:
    data = json.load(file)

with open('içecek.json', encoding='utf-8') as f:
    icecekler = json.load(f)

with open('aburcubur.json', encoding='utf-8') as f:
    aburcubur = json.load(f)

with open('donuk_ürünler.json', encoding='utf-8') as f:
    donuk_ürünler = json.load(f)

with open('et_tavuk_balık_şarkuteri.json', encoding='utf-8') as f:
    et_tavuk_balık = json.load(f)

# Ürün adlarını normalize eden fonksiyon
def normalize_product_name(name):
    return name.lower().replace('ı', 'i').replace('ç', 'c').replace('ş', 's') \
        .replace('ğ', 'g').replace('ö', 'o').replace('ü', 'u') \
        .replace(' ', '').replace('-', '').replace('_', '')

@app.route('/icecek', methods=['GET'])
def get_icecekler():
    return jsonify(icecekler)

@app.route('/aburcubur', methods=['GET'])
def get_aburcubur():
    return jsonify(aburcubur)

@app.route('/donuk_ürünler', methods=['GET'])
def get_donuk_ürünler():
    return jsonify(donuk_ürünler)


@app.route('/et_tavuk_balık', methods=['GET'])
def get_et_tavuk_balık():
    return jsonify(et_tavuk_balık)

@app.route('/tum_urunler', methods=['GET'])
def get_all_products():
    all_products = icecekler + aburcubur + donuk_ürünler + et_tavuk_balık
    return jsonify(all_products)

@app.route('/search', methods=['GET'])
def search_products():
    query = request.args.get('query', '').strip()
    if not query:
        return jsonify({"error": "Query parameter is missing"}), 400
    all_products = icecekler + aburcubur + donuk_ürünler + et_tavuk_balık
    filtered_products = [
        product for product in all_products
        if normalize_product_name(query) in normalize_product_name(product.get('urun_adi', ''))
    ]

    return jsonify(filtered_products)


def configure_genai():
    genai.configure(api_key="AIzaSyBXm9iusJiLBLrn16E092PYWpYSfCQUc8E")
    return genai.GenerativeModel("gemini-1.5-flash")


def search_in_json(json_data, search_text):
    search_words = search_text.split()
    matching_items = []

    for item in json_data:
        urun_adi = item.get("urun_adi", "").lower()
        if any(word.lower() in urun_adi for word in search_words):
            matching_items.append(item)

    return matching_items

def generate_ai_response(model, search_text, matching_items):
    if matching_items:
        product_list = "\n".join([
            f"- {item['urun_adi']} (Fiyat: {item['urun_fiyati']}, Market: {item['market']})"
            for item in matching_items
        ])
        prompt = (
            "Sen, Elakce mobil uygulamasının yapay zeka asistanısın ve kullanıcılarla doğal, samimi bir sohbet gerçekleştirmek için tasarlandın.\n"
            f"Kullanıcı sana şunu yazdı: '{search_text}'.\n"
            f"Elimizdeki ürünler şunlar:\n{product_list}.\n"
            "Kullanıcının yazdığı metne göre, bu ürünler arasından onun ihtiyacını en iyi karşılayanları seç ve öner. Ürünün nasıl bir fayda sağlayacağını kısa ve net bir şekilde açıklayarak, kullanıcıyı memnun edecek bir tavsiye ver. Eğer kullanıcının ihtiyacını tam karşılayan bir ürün yoksa, ona alternatif bir çözüm öner veya yardımcı bir bilgi paylaş."
        )
    else:
        prompt = (
            "Sen, Elakce mobil uygulamasının yapay zeka asistanısın ve kullanıcılarla empati kurarak yardımcı olmak için buradasın.\n"
            f"Kullanıcı sana şunu yazdı: '{search_text}'.\n"
            "Elimizde, kullanıcının talebini tam olarak karşılayan bir ürün bulunmadı. Ancak, alternatif çözüm önerileri ya da başka bir yardımcı bilgi sunarak kullanıcıyı memnun et."
        )
    response = model.generate_content(prompt)
    return response.text

@app.route("/api/get-response", methods=["POST"]) #buraya post istegi atıcan
def get_response():
    try:
        user_input = request.json.get("query")
        if not user_input:
            return jsonify({"error": "No query provided"}), 400

        model = configure_genai()

        results = search_in_json(data, user_input)
        ai_response = generate_ai_response(model, user_input, results)

        return jsonify({"response": ai_response})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001,debug= True, threaded = True)
