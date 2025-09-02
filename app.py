
import json
from datetime import datetime, date
from pathlib import Path
import streamlit as st

APP_TITLE = "Sağlık & Alışkanlık Oyunlaştırıcı"
DATA_DIR = Path(".health_app_data")
DATA_DIR.mkdir(exist_ok=True)
STATE_FILE = DATA_DIR / "state.json"

# ------------ Default Tasks (tailored to Müge) ---------------
DEFAULT_TASKS = [
    # Category, Task ID, Label, Points, Help text
    ("Boyun", "chin_tuck", "Chin Tuck (10 tekrar)", 10, "Dik otur. Çeneni öne çıkarmadan geriye doğru çek (çift çene). 5 sn tut, bırak. 10 tekrar."),
    ("Boyun", "scap_squeeze", "Omuz Germe (10 tekrar)", 10, "Omuzlarını geriye çek, kürek kemiklerini birbirine yaklaştır. 5 sn tut, bırak. 10 tekrar."),
    ("Boyun", "lat_stretch", "Boyun Yan Esnetme (2x20 sn/yan)", 10, "Başını sağa eğ, elinle hafif destekle; 20 sn. Sonra sol. Ağrı yok."),
    ("Diz", "slr", "Düz Bacak Kaldırma (10 tekrar/bacak)", 10, "Yerde sırtüstü: bir bacak düz, diğeri bükülü. Düz bacağı 30 cm kaldır, 3 sn tut, indir."),
    ("Diz", "wall_sit", "Duvar Oturuşu (3x20 sn)", 10, "Sırt duvarda, dizler ~45°. 3 set x 20 sn, set arası dinlen."),
    ("Diz", "step_up", "Basamak Çıkma (10 tekrar/bacak)", 10, "Alçak bir basamak: sağ-sol dönüşümlü çık-in. Dizde keskin ağrı olursa dur."),
    ("Genel", "walk20", "Yürüyüş (en az 20 dk)", 15, "Tempolu ama dizini zorlamadan yürüyüş."),
    ("Genel", "water2l", "Su (en az 2L)", 10, "Gün boyu oda sıcaklığında su iç."),
    ("Genel", "screen_breaks", "Ekran Molası (saat başı 2 dk)", 10, "Her saat başı kalk, 2 dk yürü/gerin (en az 6 kez)."),
    ("Reflü", "dinner_before19", "Akşam Yemeği 19:00'dan önce", 10, "Yemekten sonra 3 saat yatmama kuralına destek."),
    ("Uyku", "sleep_23", "23:00'te Uyumaya Başla", 10, "7–8 saat uyku, başı hafif yükselterek."),
]

# Weekly targets per level (can scale)
LEVEL_RULES = {
    # level: (daily_min_points, days_to_level_up)
    1: (60, 7),
    2: (70, 7),
    3: (75, 7),
    4: (80, 7),
}

def load_state():
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    # default state
    return {
        "level": 1,
        "total_points": 0,
        "days_completed": 0,       # total days that met target
        "week_progress": 0,        # current cycle's completed days
        "history": {},             # date -> {"checked": [task_ids], "points": int, "met_target": bool}
        "custom_tasks": [],        # list of {category,id,label,points,help}
    }

def save_state(state):
    STATE_FILE.write_text(json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8")

def today_key():
    return date.today().isoformat()

def get_tasks(state):
    # merge default + custom
    tasks = DEFAULT_TASKS.copy()
    for t in state.get("custom_tasks", []):
        tasks.append((t["category"], t["id"], t["label"], t["points"], t.get("help","")))
    return tasks

def ensure_today(state):
    tkey = today_key()
    if tkey not in state["history"]:
        state["history"][tkey] = {"checked": [], "points": 0, "met_target": False}
    return tkey

def reset_today(state):
    tkey = ensure_today(state)
    state["history"][tkey] = {"checked": [], "points": 0, "met_target": False}

def compute_points(tasks, checked_ids):
    pts = 0
    for cat, tid, label, pts_val, help_txt in tasks:
        if tid in checked_ids:
            pts += pts_val
    return pts

def level_requirements(level):
    # default if level beyond defined
    return LEVEL_RULES.get(level, (80, 7))

def try_level_up(state):
    level = state["level"]
    daily_min, days_needed = level_requirements(level)
    # if user has completed enough "target days" in this cycle
    if state["week_progress"] >= days_needed:
        state["level"] += 1
        state["week_progress"] = 0

def main():
    st.set_page_config(page_title=APP_TITLE, page_icon="✨", layout="centered")
    st.title(APP_TITLE)
    st.caption("Kişisel sağlık & alışkanlık takip • Oyunlaştırma ve seviyeler")

    state = load_state()
    tkey = ensure_today(state)
    tasks = get_tasks(state)

    # Sidebar: profile & level
    with st.sidebar:
        st.subheader("Profil & Seviye")
        st.metric("Seviye", state["level"])
        daily_min, days_needed = level_requirements(state["level"])
        st.progress(min(state["week_progress"]/days_needed, 1.0), text=f"Haftalık ilerleme: {state['week_progress']}/{days_needed}")
        st.metric("Toplam Puan", state["total_points"])
        st.caption(f"Gün hedefi: ≥ {daily_min} puan")

        st.divider()
        st.subheader("Ödül Fikirleri")
        rewards = st.text_area("Kendine ödüller yaz (her level sonrası içinden seç):", "Kahve molası\nSinemaya git\nYeni bir kitap\nDoğa yürüyüşü")
        if st.button("Ödülleri kaydet"):
            # just store in a text file
            (DATA_DIR / "rewards.txt").write_text(rewards, encoding="utf-8")
            st.success("Ödüller kaydedildi.")

        st.divider()
        st.subheader("Yedekleme")
        if st.button("Veriyi .json olarak indir"):
            st.download_button("İndir (state.json)", data=json.dumps(state, ensure_ascii=False, indent=2), file_name="health_app_state.json")

    st.markdown(f"**Tarih:** {tkey}")
    st.info("Hedef: Günlük puanını topla → Gün hedefini tutturan her gün, haftalık ilerlemene +1 yazar. Haftalık hedefe ulaşınca seviye atlanır.")

    # Checklist UI
    st.header("Günlük Görevler")
    # group by category
    by_cat = {}
    for cat, tid, label, pts, help_txt in tasks:
        by_cat.setdefault(cat, []).append((tid, label, pts, help_txt))
    checked = set(state["history"][tkey]["checked"])

    for cat, items in by_cat.items():
        with st.expander(f"{cat}"):
            for tid, label, pts, help_txt in items:
                col1, col2 = st.columns([0.08, 0.92])
                with col1:
                    value = tid in checked
                    new_val = st.checkbox("", key=f"{tkey}_{tid}", value=value)
                with col2:
                    st.markdown(f"**{label}** · {pts} puan")
                    if help_txt:
                        st.caption(help_txt)
                # update checked live
                if new_val and tid not in checked:
                    checked.add(tid)
                if (not new_val) and tid in checked:
                    checked.remove(tid)

    # Save checked and recompute points
    state["history"][tkey]["checked"] = sorted(list(checked))
    today_points = compute_points(tasks, state["history"][tkey]["checked"])
    state["history"][tkey]["points"] = today_points

    daily_min, days_needed = level_requirements(state["level"])
    met_target = today_points >= daily_min
    state["history"][tkey]["met_target"] = met_target

    st.subheader("Bugünkü Puan")
    st.metric("Toplam", today_points)
    st.caption(f"Gün hedefi: {daily_min} puan • Durum: {'✅ Karşılandı' if met_target else '⏳ Hedefin altında'}")

    # Actions
    colA, colB, colC = st.columns(3)
    with colA:
        if st.button("Bugünü sıfırla"):
            reset_today(state)
            save_state(state)
            st.experimental_rerun()
    with colB:
        if st.button("Kaydet"):
            save_state(state)
            st.success("Güncel ilerleme kaydedildi.")

    with colC:
        if st.button("Günü Bitir & İlerle"):
            # If first time marking as met_target today, update counters
            prev_met = state["history"][tkey].get("counted", False)
            if met_target and not prev_met:
                state["days_completed"] += 1
                state["week_progress"] += 1
                state["history"][tkey]["counted"] = True
            # Update totals
            state["total_points"] += today_points
            # Check level up
            before_lvl = state["level"]
            try_level_up(state)
            save_state(state)
            if state["level"] > before_lvl:
                st.balloons()
                st.success(f"Tebrikler! Seviye {before_lvl} ➜ {state['level']}")
            else:
                st.success("Gün tamamlandı. İlerlemen kaydedildi.")

    st.divider()
    st.header("Özel Görev Ekle")
    with st.form("custom_task_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            category = st.selectbox("Kategori", ["Genel","Boyun","Diz","Reflü","Uyku","Beslenme","Stres"])
            label = st.text_input("Görev adı", placeholder="Örn: 10 dk nefes egzersizi")
        with c2:
            points = st.number_input("Puan", min_value=5, max_value=30, value=10, step=5)
            task_id = st.text_input("Benzersiz ID", placeholder="nefes_10dk")
        help_txt = st.text_area("Açıklama (isteğe bağlı)", "")
        submitted = st.form_submit_button("Ekle")
        if submitted:
            if not label or not task_id:
                st.error("Lütfen görev adı ve benzersiz ID girin.")
            else:
                # ensure unique id
                all_ids = {t[1] for t in DEFAULT_TASKS} | {t["id"] for t in state["custom_tasks"]}
                if task_id in all_ids:
                    st.error("Bu ID zaten var. Farklı bir ID seçin.")
                else:
                    state["custom_tasks"].append({
                        "category": category,
                        "id": task_id,
                        "label": label,
                        "points": int(points),
                        "help": help_txt
                    })
                    save_state(state)
                    st.success("Özel görev eklendi.")

    st.divider()
    st.header("Geçmiş")
    if state["history"]:
        items = sorted(state["history"].items(), key=lambda x: x[0], reverse=True)[:30]
        for dkey, rec in items:
            icon = "✅" if rec.get("met_target") else "•"
            st.write(f"{icon} {dkey} — {rec.get('points',0)} puan — {', '.join(rec.get('checked', []))}")

    # Save at the end
    save_state(state)

if __name__ == "__main__":
    main()
