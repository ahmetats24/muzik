import json
from flask import Flask, jsonify, request
from flask_compress import Compress

app = Flask(name)
Compress(app)

# JSON dosyalarını yükle
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

# Endpoint: İçecekler
@app.route('/icecek', methods=['GET'])
def get_icecekler():
    return jsonify(icecekler)

# Endpoint: Aburcubur
@app.route('/aburcubur', methods=['GET'])
def get_aburcubur():
    return jsonify(aburcubur)

# Endpoint: Donuk Ürünler
@app.route('/donuk_ürünler', methods=['GET'])
def get_donuk_ürünler():
    return jsonify(donuk_ürünler)

# Endpoint: Et Tavuk Balık
@app.route('/et_tavuk_balık', methods=['GET'])
def get_et_tavuk_balık():
    return jsonify(et_tavuk_balık)

# Endpoint: Tüm Ürünler
@app.route('/tum_urunler', methods=['GET'])
def get_all_products():
    # Tüm ürünleri tek bir listede birleştir
    all_products = icecekler + aburcubur + donuk_ürünler + et_tavuk_balık
    return jsonify(all_products)

# Endpoint: Arama
@app.route('/search', methods=['GET'])
def search_products():
    query = request.args.get('query', '').strip()
    if not query:
        return jsonify({"error": "Query parameter is missing"}), 400

    # Tüm ürünleri birleştir
    all_products = icecekler + aburcubur + donuk_ürünler + et_tavuk_balık

    # Arama işlemi
    filtered_products = [
        product for product in all_products
        if normalize_product_name(query) in normalize_product_name(product.get('urun_adi', ''))
    ]

    return jsonify(filtered_products)

if name == 'main':
    app.run(host='0.0.0.0', port=5001, debug=True, threaded=True)