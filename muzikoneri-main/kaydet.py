import pandas as pd

# Excel dosyasını oku
data = pd.read_excel("eren.xlsx")

# 'Tempo' sütununu liste veya string içinden float olarak dönüştür
data['Tempo'] = data['Tempo'].apply(lambda x: float(x[0]) if isinstance(x, list) else float(x.strip('[]')))

data.to_excel("abc.xlsx")