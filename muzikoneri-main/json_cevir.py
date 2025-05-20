import pandas as pd

# Excel dosyasını oku
excel_file_path = 'birlesmis_dosya.xlsx'  # Buraya çevirmek istediğin Excel dosyasının yolunu yaz
df = pd.read_excel(excel_file_path)

# DataFrame'i JSON formatına çevir
json_data = df.to_json(orient='records', indent=4)

# JSON verisini bir dosyaya kaydet
json_file_path = 'cevirmis_dosya.json'
with open(json_file_path, 'w', encoding='utf-8') as json_file:
    json_file.write(json_data)

print(f"Excel dosyası '{json_file_path}' olarak JSON formatına çevrildi.")