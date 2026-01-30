import json, random, requests
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# --- HAFIZA YÖNETİMİ ---
def hafiza_isle(mod, veri=None):
    dosya = "EKIP_AI.json"
    try:
        if mod == "oku":
            with open(dosya, "r", encoding="utf-8") as f:
                return json.load(f)
        elif mod == "yaz":
            with open(dosya, "w", encoding="utf-8") as f:
                json.dump(veri, f, ensure_ascii=False, indent=4)
    except:
        return {} if mod == "oku" else None

# --- YANLIŞ BİLGİ VE KİMLİK KORUMA FİLTRESİ ---
def bilgi_dogrula(anahtar, deger):
    # Projeyi başkasına mal etmeye çalışanlara geçit yok
    yasakli_sahipler = ["pixel studios", "ultimate meteor studios", "google", "meta", "microsoft"]
    deger_low = deger.lower()
    
    if any(y in deger_low for y in yasakli_sahipler):
        return False, "Hata: Bu proje bağımsızdır ve bu kurumlara ait değildir!"
    
    if len(deger) < 3:
        return False, "Hata: Bilgi çok yetersiz veya anlamsız."
        
    # Küfür filtresi (Burayı istediğin gibi genişletebilirsin)
    kufurler = ["amk", "aq", "oç", "piç", "göt", "siktir"]
    if any(k in deger_low or k in anahtar.lower() for k in kufurler):
        return False, "Hata: Uygunsuz içerik kaydedilemez."
        
    return True, ""

@app.route('/')
def index():
    # HTML dosyanın adının index.html olduğundan emin ol
    return send_from_directory('.', 'index.html')

@app.route('/ekip_sor', methods=['POST'])
def cevap_ver():
    data = request.json
    soru = data.get("mesaj", "").lower().strip()
    taban = hafiza_isle("oku")
    
    # 1. ÖĞRENME MODU (Filtreli)
    if "öğren:" in soru or "ogren:" in soru:
        komut = "öğren:" if "öğren:" in soru else "ogren:"
        try:
            temiz_veri = soru.split(komut)[1].strip()
            parcalar = temiz_veri.split(" ", 1)
            
            if len(parcalar) == 2:
                anahtar, deger = parcalar[0].strip(), parcalar[1].strip()
                
                # Yanlış bilgi filtresini çalıştır
                gecerli, hata_mesaji = bilgi_dogrula(anahtar, deger)
                
                if gecerli:
                    taban[anahtar] = deger
                    hafiza_isle("yaz", taban)
                    return jsonify({"cevap": f"'{anahtar}' bilgisini doğruladım ve öğrendim ekip.", "bot_adi": "SİSTEM"})
                else:
                    return jsonify({"cevap": hata_mesaji, "bot_adi": "GÜVENLİK"})
        except:
            return jsonify({"cevap": "Öğrenme formatı yanlış. Örn: öğren: elma meyvedir", "bot_adi": "SİSTEM"})

    # 2. HAFIZA KONTROLÜ
    for anahtar, cevap in taban.items():
        if anahtar in soru:
            return jsonify({"cevap": random.choice(cevap) if isinstance(cevap, list) else cevap, "bot_adi": "SİSTEM"})

    # 3. İNTERNET ARAMASI
    try:
        res = requests.get(f"https://api.duckduckgo.com/?q={soru}&format=json&no_html=1", timeout=3).json()
        if res.get("AbstractText"):
            return jsonify({"cevap": res.get("AbstractText"), "bot_adi": "İNTERNET"})
    except: pass

    # 4. VARSAYILAN CEVAP
    return jsonify({"cevap": "Bunu henüz bilmiyorum ekip, bana 'öğren: [konu] [açıklama]' diyerek öğretebilirsin.", "bot_adi": "SİSTEM"})

if __name__ == '__main__':
    # Replit için port 8080 uygundur
    app.run(host='0.0.0.0', port=8080, debug=False)
