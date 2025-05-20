from flask import Flask, request, jsonify
import google.generativeai as genai
import json
from colorama import Fore

app = Flask(__name__)

def configure_genai():
    genai.configure(api_key="AIzaSyBXm9iusJiLBLrn16E092PYWpYSfCQUc8E")
    return genai.GenerativeModel("gemini-1.5-flash")

with open("tüm_ürünler.json", "r", encoding="utf-8") as file:
    data = json.load(file)

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
            "Sen, Elakce mobil uygulamasının yapay zeka asistanısın ve kullanıcılarla yalnızca market ürünleri hakkında sohbet etmek için tasarlandın.\n"
            f"Kullanıcı sana şunu yazdı: '{search_text}'.\n"
            f"Elimizdeki ürünler şunlar:\n{product_list}.\n"
            "Kullanıcının ihtiyacına uygun ürünleri seç ve her birinin faydasını bir cümleyle açıkla. Kullanıcıya yalnızca ürünler hakkında bilgi ver ve sohbeti bu çerçevede tut."
        )

    else:
        prompt = (
            "Sen, Elakce mobil uygulamasının yapay zeka asistanısın ve kullanıcılarla empati kurarak yardımcı olmak için buradasın.\n"
            f"Kullanıcı sana şunu yazdı: '{search_text}'.\n"
            "Elimizde, kullanıcının talebini tam olarak karşılayan bir ürün bulunmadı. Ancak, alternatif çözüm önerileri ya da başka bir yardımcı bilgi sunarak kullanıcıyı memnun et."
        )
    response = model.generate_content(prompt)
    return response.text

@app.route("/api/get-response", methods=["POST"])
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

if __name__ == "__main__":
    app.run(debug=True)
