
# Sağlık & Alışkanlık Oyunlaştırıcı (Streamlit)

Bu, Müge için özelleştirilmiş bir mini uygulamadır. Günlük görevleri (boyun/diz egzersizleri, su, yürüyüş, reflü dostu alışkanlıklar) işaretledikçe puan kazanırsın. 7 gün hedefi tutturarak seviye atlarsın.

## Kurulum (Windows / macOS)
1) Python 3.9+ kurulu değilse kur (https://www.python.org/downloads/).
2) Bu klasöre terminal/komut satırıyla gel.
3) Sanal ortam (opsiyonel ama önerilir):
   - Windows: `python -m venv .venv && .venv\\Scripts\\activate`
   - macOS/Linux: `python3 -m venv .venv && source .venv/bin/activate`
4) Gerekli paketleri kur:  
   `pip install -r requirements.txt`
5) Uygulamayı başlat:  
   `streamlit run app.py`

Tarayıcı otomatik açılır. Kapatmak için terminalde `Ctrl+C`.

## Kullanım İpuçları
- Sol menüde seviye, haftalık ilerleme ve toplam puanı görürsün.
- "Günü Bitir & İlerle" ile günlük hedefi (level'e göre 60–80 puan) tuttuysan haftalık ilerlemen +1 artar.
- "Özel Görev Ekle" kısmından kendi görevlerini ekleyebilirsin.
- Veriler `.health_app_data/state.json` içinde saklanır. "Veriyi .json olarak indir" ile yedek alabilirsin.

## Özelleştirme
- Varsayılan görevler, senin sağlık geçmişine göre seçildi (boyun düzleşmesi, patellar tilt, reflü, masa başı çalışma).
- Puanlar ve hedef eşikleri `app.py` içinde `DEFAULT_TASKS` ve `LEVEL_RULES` bölümlerinde düzenlenebilir.

Sağlıklı ve keyifli kullanım ✨
