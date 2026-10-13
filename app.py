import os
import time

import streamlit as st
from groq import Groq

# ---------------------------------------------------------------
# KONFIGURASI
# ---------------------------------------------------------------
# Model Groq. Bisa diganti lewat Streamlit Secrets: GROQ_MODEL.
MODEL = os.environ.get("GROQ_MODEL", "openai/gpt-oss-20b")
RETRIES = 2

SYSTEM_PROMPT = """Kamu adalah PyBuddy, asisten belajar Python yang ramah untuk
mahasiswa dan pelajar pemula di Indonesia.

Aturan:
- Jawab dalam Bahasa Indonesia yang santai tapi jelas.
- Jelaskan konsep dengan bahasa sederhana dan analogi sehari-hari.
- Sertakan contoh kode pendek (maksimal sekitar 15 baris) bila relevan.
- Jika pengguna mengirim error, jelaskan penyebabnya lalu beri cara memperbaikinya.
- Jika pertanyaan di luar topik pemrograman, jawab singkat lalu arahkan kembali
  ke topik belajar coding.
- Dorong pengguna mencoba sendiri, jangan hanya memberi jawaban jadi."""

XP_PER_QUESTION = 10
XP_PER_LEVEL = 50
LEVEL_TITLES = ["Pemula", "Penjelajah", "Pendekar Kode", "Jagoan Python", "Master Python"]

# Menu topik di sidebar: (emoji, nama, pertanyaan yang dikirim ke PyBuddy)
TOPICS = [
    ("🐣", "Dasar Python", "Jelaskan dasar-dasar Python untuk pemula: variabel, tipe data, dan print."),
    ("📦", "List, Tuple & Dict", "Jelaskan perbedaan list, tuple, dan dictionary, beserta kapan memakainya."),
    ("🔁", "Perulangan & Kondisi", "Jelaskan if-else dan perulangan for/while dengan analogi sehari-hari."),
    ("🧩", "Fungsi & Modul", "Jelaskan cara membuat fungsi di Python dan cara memakai modul."),
    ("🐞", "Debug Error", "Ajari aku cara membaca pesan error Python dan menemukan penyebabnya."),
    ("📝", "Latihan Soal", "Beri aku satu latihan soal Python untuk pemula, tanpa kunci jawaban dulu."),
]

# Contoh pertanyaan di layar sambutan (berguna saat sidebar tertutup di HP)
QUICK_STARTS = [
    "Apa bedanya list dan tuple?",
    "Jelaskan perulangan for dengan analogi",
    "Kenapa muncul IndentationError?",
    "Beri aku latihan soal tentang if-else",
]

# ---------------------------------------------------------------
# TEMA
# ---------------------------------------------------------------
THEMES = {
    "light": {
        "label": "☀️  Terang",
        "scheme": "light",
        "vars": {
            "bg": "#FFFFFF", "bg_solid": "#FFFFFF", "surface": "#FFFFFF",
            "soft": "#F7F7F7", "side_bg": "#FBFCFA", "line": "#E5E5E5",
            "ink": "#3C3C3C", "muted": "#777777",
            "accent": "#58CC02", "accent_d": "#58A700", "accent_soft": "#E6F7D6",
            "link": "#1899D6", "chip_bg": "#F6F9F4", "chip_line": "#DCE6D6",
            "user_bg": "#DDF4FF", "user_line": "#84D8FF",
            "hero_1": "#6BD60A", "hero_2": "#2DB84C", "code_ink": "#58A700",
        },
        "extra": "",
    },
    "dark": {
        "label": "🌙  Gelap",
        "scheme": "dark",
        "vars": {
            "bg": "#131F24", "bg_solid": "#131F24", "surface": "#1B2B32",
            "soft": "#202F36", "side_bg": "#0F191D", "line": "#2E414B",
            "ink": "#E8F0F3", "muted": "#9DB0B9",
            "accent": "#58CC02", "accent_d": "#46A302", "accent_soft": "#1F3B22",
            "link": "#49C0F8", "chip_bg": "#1B2B32", "chip_line": "#2E414B",
            "user_bg": "#17394B", "user_line": "#2A6E92",
            "hero_1": "#4CB800", "hero_2": "#1E8F4E", "code_ink": "#8EE05A",
        },
        "extra": """
[data-testid="stCode"] pre, [data-testid="stCode"] code, [data-testid="stCode"] span
  { color: #E8F0F3 !important; }
[data-testid="stAlert"] p { color: #E8F0F3; }
""",
    },
    "sunset": {
        "label": "🌇  Senja",
        "scheme": "light",
        "vars": {
            "bg": "linear-gradient(180deg, #FFF4EA 0%, #FFE8EE 100%)",
            "bg_solid": "#FFF1E8", "surface": "#FFFFFF",
            "soft": "#FFF7F1", "side_bg": "#FFEBDD", "line": "#F5D5C0",
            "ink": "#4A2E2A", "muted": "#9A6F5E",
            "accent": "#FF7A45", "accent_d": "#D95B28", "accent_soft": "#FFE2CF",
            "link": "#D95B28", "chip_bg": "#FFF6EE", "chip_line": "#F5D5C0",
            "user_bg": "#FFE2CF", "user_line": "#FFB48A",
            "hero_1": "#FF9A5A", "hero_2": "#FF5E7E", "code_ink": "#D95B28",
        },
        "extra": "",
    },
}

st.set_page_config(page_title="PyBuddy", page_icon="🐍", layout="centered")

theme = st.session_state.setdefault("theme", "light")
if theme not in THEMES:
    theme = st.session_state.theme = "light"

# ---------------------------------------------------------------
# GAYA (CSS)
# ---------------------------------------------------------------
FONT_CSS = "@import url('https://fonts.googleapis.com/css2?family=Nunito:wght@600;700;800;900&display=swap');"

THEME_CSS = (
    ":root{color-scheme:" + THEMES[theme]["scheme"] + ";"
    + ";".join(f"--{k.replace('_', '-')}:{v}" for k, v in THEMES[theme]["vars"].items())
    + "}"
)

BASE_CSS = """
/* ---------- Dasar ---------- */
.stApp { background: var(--bg); background-attachment: fixed; color: var(--ink); }
[data-testid="stAppViewContainer"], [data-testid="stMain"] { background: transparent; }
.stApp, .stApp p, .stApp li, .stApp label, .stApp h1, .stApp h2, .stApp h3,
.stApp h4, .stApp button, .stApp input, .stApp textarea { font-family: 'Nunito', sans-serif; }
:is([data-testid="stMain"], [data-testid="stSidebar"], [data-testid="stBottom"])
  :is(p, li, label, h1, h2, h3, h4) { color: var(--ink); }
.stApp p, .stApp li { font-weight: 600; font-size: 1.02rem; line-height: 1.6; }
.stApp h1, .stApp h2, .stApp h3, .stApp h4 { font-weight: 900; }
footer, [data-testid="stToolbar"], [data-testid="stDecoration"] { display: none; }
header[data-testid="stHeader"] { background: transparent; }
[data-testid="stExpandSidebarButton"], [data-testid="stSidebarCollapseButton"] button { color: var(--ink); }
.block-container { max-width: 780px; padding-top: 1.4rem; padding-bottom: 6rem; }

/* ---------- Header aplikasi ---------- */
.appbar { background: linear-gradient(135deg, var(--hero-1), var(--hero-2)); color: #fff;
  border-radius: 24px; padding: 18px 22px; margin-bottom: 24px;
  box-shadow: 0 5px 0 var(--accent-d); }
.appbar-top { display: flex; align-items: center; justify-content: space-between;
  gap: 14px; flex-wrap: wrap; }
.brand { display: flex; align-items: center; gap: 14px; }
.logo { width: 56px; height: 56px; border-radius: 18px; background: rgba(255,255,255,.22);
  border: 2px solid rgba(255,255,255,.4); display: grid; place-items: center; font-size: 2rem; }
.app-name { font-weight: 900; font-size: 1.7rem; line-height: 1.1; letter-spacing: -.5px; }
.app-tag { font-weight: 700; font-size: .92rem; opacity: .92; }
.stats { display: flex; gap: 8px; flex-wrap: wrap; }
.pill { font-weight: 900; font-size: .95rem; padding: 6px 13px; border-radius: 14px;
  background: rgba(255,255,255,.2); border: 2px solid rgba(255,255,255,.35); white-space: nowrap; }
.level-meta { display: flex; justify-content: space-between; font-weight: 800;
  font-size: .88rem; margin: 16px 0 6px; }
.track { height: 14px; background: rgba(0,0,0,.18); border-radius: 99px; overflow: hidden; }
.fill { height: 100%; background: #fff; border-radius: 99px; min-width: 14px;
  transition: width .5s ease; }

/* ---------- Maskot + gelembung bicara ---------- */
.hero { display: flex; align-items: center; gap: 18px; margin: 8px 0 24px; }
.mascot { font-size: 5.2rem; line-height: 1; animation: bob 2.4s ease-in-out infinite; }
@keyframes bob { 0%,100% { transform: translateY(0); } 50% { transform: translateY(-8px); } }
.bubble { position: relative; background: var(--surface); border: 2px solid var(--line);
  border-radius: 18px; padding: 14px 18px; font-weight: 800; font-size: 1.15rem; color: var(--ink); }
.bubble::before { content: ""; position: absolute; left: -12px; top: 50%; margin-top: -10px;
  border: 10px solid transparent; border-right-color: var(--line); border-left: 0; }
.bubble::after { content: ""; position: absolute; left: -9px; top: 50%; margin-top: -8px;
  border: 8px solid transparent; border-right-color: var(--surface); border-left: 0; }
.hint { font-weight: 800; color: var(--muted); margin: 0 0 10px; }

/* ---------- Tombol 3D (area utama) ---------- */
.stButton > button {
  background: var(--surface); color: var(--link); font-weight: 800; font-size: 1rem;
  border: 2px solid var(--line); border-bottom-width: 4px; border-radius: 16px;
  padding: 10px 14px; min-height: 52px; width: 100%;
  transition: transform .05s, background .15s, border-color .15s;
}
.stButton > button p { color: inherit; font-weight: inherit; margin: 0; }
.stButton > button:hover { background: var(--soft); border-color: var(--line); color: var(--link); }
.stButton > button:active { transform: translateY(2px); border-bottom-width: 2px; }
.stButton > button:focus-visible { outline: 3px solid var(--user-line); outline-offset: 2px; }
div[class*="st-key-chip_"] button { justify-content: flex-start; text-align: left; }

/* ---------- Gelembung chat ---------- */
[data-testid="stChatMessage"] { background: var(--surface); border: 2px solid var(--line);
  border-radius: 20px; padding: 14px 18px; margin-bottom: 14px; }
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]),
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) {
  background: var(--user-bg); border-color: var(--user-line); }
[data-testid="stChatMessageAvatarAssistant"], [data-testid="stChatMessageAvatarUser"],
[data-testid="chatAvatarIcon-assistant"], [data-testid="chatAvatarIcon-user"] {
  background: var(--surface); border: 2px solid var(--line); border-radius: 50%; }

/* ---------- Kode ---------- */
[data-testid="stCode"] pre, .stMarkdown pre { background: var(--soft) !important;
  border: 2px solid var(--line); border-radius: 14px; }
.stMarkdown :not(pre) > code { background: var(--soft); color: var(--code-ink);
  border-radius: 8px; font-weight: 700; }

/* ---------- Kolom input ---------- */
[data-testid="stBottom"] > div { background: var(--bg-solid); }
[data-testid="stChatInput"] { background: var(--soft); border: 2px solid var(--line);
  border-radius: 18px; }
[data-testid="stChatInput"] > div, [data-testid="stChatInput"] textarea
  { background: transparent; color: var(--ink); font-weight: 700; }
[data-testid="stChatInput"]:focus-within { border-color: var(--accent); }

/* ---------- Sidebar ---------- */
[data-testid="stSidebar"] { background: var(--side-bg); border-right: 1px solid var(--line); }
[data-testid="stSidebar"] [data-testid="stVerticalBlock"] { gap: .38rem; }
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p { margin-bottom: .25rem; }
[data-testid="stSidebar"] [data-testid="stSidebarContent"] { padding: 1rem .85rem 1.25rem; }
.side-brand { display: flex; align-items: center; gap: 12px; }
.logo-sm { width: 42px; height: 42px; border-radius: 13px; font-size: 1.35rem;
  background: linear-gradient(135deg, var(--hero-1), var(--hero-2)); display: grid;
  place-items: center; box-shadow: 0 3px 0 var(--accent-d); }
.side-name { font-weight: 900; font-size: 1.2rem; color: var(--ink); line-height: 1.1; }
.side-sub { font-weight: 700; font-size: .82rem; color: var(--muted); }
.side-divider { height: 1px; background: var(--line); margin: 9px 0 3px; }
.side-title { font-weight: 900; font-size: 1.42rem; color: var(--ink); line-height: 1.2; }
.side-desc { font-weight: 600; font-size: .95rem; color: var(--muted); line-height: 1.4; margin-top: -2px; }
.side-label { font-weight: 800; font-size: .74rem; letter-spacing: .1em; color: var(--muted); margin-top: 6px; }
.side-foot { font-weight: 700; font-size: .8rem; color: var(--muted); text-align: center; margin-top: 4px; }

/* Menu topik */
div[class*="st-key-nav"] button { justify-content: flex-start; background: var(--chip-bg);
  color: var(--ink); border: 1px solid var(--chip-line); border-bottom-width: 1px;
  border-radius: 15px; min-height: 48px; padding: 5px 12px; box-shadow: none; }
div[class*="st-key-nav"] button p { text-align: left; font-weight: 800; font-size: .94rem; line-height: 1.2; }
div[class*="st-key-nav"] button:hover { background: var(--surface); border-color: var(--accent); color: var(--ink); }
div[class*="st-key-navon_"] button { background: var(--accent-soft); border-color: var(--accent);
  box-shadow: 0 3px 0 var(--accent-d); }

/* Pilihan tampilan */
div[class*="st-key-theme"] button { justify-content: center; background: var(--surface);
  color: var(--ink); border: 1px solid var(--line); border-bottom-width: 1px;
  border-radius: 13px; min-height: 42px; padding: 4px 7px; }
div[class*="st-key-theme"] button p { font-size: .85rem; font-weight: 800; }
div[class*="st-key-theme"] button:hover { background: var(--soft); border-color: var(--accent); color: var(--ink); }
div[class*="st-key-themeon_"] button { background: var(--accent-soft); border-color: var(--accent);
  box-shadow: 0 3px 0 var(--accent-d); }

/* Tombol hapus */
div.st-key-reset button { background: #FF4B4B; color: #fff; border-color: #EA2B2B;
  justify-content: center; font-weight: 900; }
div.st-key-reset button:hover { background: #ff6161; color: #fff; border-color: #EA2B2B; }

[data-testid="stExpander"] details { background: var(--surface); border: 1px solid var(--line);
  border-radius: 16px; }
[data-testid="stExpander"] summary, [data-testid="stExpander"] summary p
  { color: var(--ink); font-weight: 800; }

@media (max-width: 600px) {
  .hero { flex-direction: column; text-align: center; }
  .bubble::before, .bubble::after { display: none; }
  .app-name { font-size: 1.45rem; }
  .logo { width: 48px; height: 48px; font-size: 1.7rem; }
}
@media (prefers-reduced-motion: reduce) {
  .mascot { animation: none; }
  .fill, .stButton > button { transition: none; }
}
"""
st.markdown(
    f"<style>{FONT_CSS}{THEME_CSS}{BASE_CSS}{THEMES[theme]['extra']}</style>",
    unsafe_allow_html=True,
)


# ---------------------------------------------------------------
# FUNGSI BANTU
# ---------------------------------------------------------------
def load_api_key():
    """Ambil Groq API key dari Streamlit Secrets atau environment."""
    try:
        key = st.secrets.get("GROQ_API_KEY", "")
    except Exception:
        key = ""
    return key or os.environ.get("GROQ_API_KEY", "")


def is_busy(error):
    """Deteksi error sementara atau batas pemakaian API."""
    text = str(error).upper()
    return any(k in text for k in ("503", "429", "502", "504", "RATE LIMIT", "OVERLOADED", "TEMPORARILY UNAVAILABLE"))


def stream_reply(prompt):
    """Kirim riwayat chat ke Groq dan stream jawaban."""
    client = st.session_state.groq_client
    chat_messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    chat_messages.extend(st.session_state.messages)
    last_error = None

    for attempt in range(RETRIES):
        try:
            stream = client.chat.completions.create(
                model=MODEL,
                messages=chat_messages,
                max_tokens=1000,
                temperature=0.6,
                stream=True,
            )
            for chunk in stream:
                if not getattr(chunk, "choices", None):
                    continue
                delta = chunk.choices[0].delta
                content = getattr(delta, "content", None)
                if content:
                    yield content
            return
        except Exception as e:
            last_error = e
            if not is_busy(e) or attempt == RETRIES - 1:
                raise
            time.sleep(2 ** attempt)
    if last_error:
        raise last_error


def render_header(slot):
    """Gambar header aplikasi (logo, statistik, progres level) ke slot."""
    xp = st.session_state.xp
    level = xp // XP_PER_LEVEL + 1
    into_level = xp % XP_PER_LEVEL
    title = LEVEL_TITLES[min(level - 1, len(LEVEL_TITLES) - 1)]
    slot.markdown(
        f"""<div class="appbar">
<div class="appbar-top">
<div class="brand"><div class="logo">🐍</div>
<div><div class="app-name">PyBuddy</div><div class="app-tag">Teman belajar Python-mu</div></div></div>
<div class="stats">
<span class="pill">🔥 {st.session_state.asked} tanya</span>
<span class="pill">⭐ {xp} XP</span>
</div></div>
<div class="level-meta"><span>🏆 Level {level} · {title}</span><span>{into_level}/{XP_PER_LEVEL} XP</span></div>
<div class="track"><div class="fill" style="width:{into_level / XP_PER_LEVEL * 100}%"></div></div>
</div>""",
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------
# SIDEBAR
# ---------------------------------------------------------------
st.session_state.setdefault("topic", None)

with st.sidebar:
    st.markdown(
        """<div class="side-brand"><div class="logo-sm">🐍</div>
<div><div class="side-name">PyBuddy</div><div class="side-sub">Teman belajar Python</div></div></div>
<div class="side-divider"></div>
<div class="side-title">✨ Jelajahi</div>
<div class="side-desc">Pilih topik atau tanyakan sendiri</div>""",
        unsafe_allow_html=True,
    )

    # Menu topik: klik untuk langsung bertanya.
    for i, (emoji, label, question) in enumerate(TOPICS):
        key = f"navon_{i}" if st.session_state.topic == i else f"nav_{i}"
        if st.button(f"{emoji}  {label}", key=key):
            st.session_state.topic = i
            st.session_state.pending = question
            st.rerun()

    st.markdown('<div class="side-label">🎨 TAMPILAN</div>', unsafe_allow_html=True)
    theme_cols = st.columns(2, gap="small")
    theme_labels = {"light": "☀️ Terang", "dark": "🌙 Gelap", "sunset": "🌇 Senja"}
    for i, (name, t) in enumerate(THEMES.items()):
        key = f"themeon_{name}" if name == theme else f"theme_{name}"
        if theme_cols[i % 2].button(theme_labels[name], key=key, use_container_width=True):
            st.session_state.theme = name
            st.rerun()

    st.markdown('<div class="side-divider"></div>', unsafe_allow_html=True)
    with st.expander("ℹ️ Tentang PyBuddy"):
        st.markdown(
            "**Untuk siapa?** Mahasiswa dan pelajar pemula yang baru belajar Python "
            "dan sering bingung saat bertemu konsep baru atau error.\n\n"
            "**Bisa bantu apa?** Menjelaskan konsep dengan bahasa sederhana, "
            "mencari penyebab error, dan memberi contoh kode serta latihan soal."
        )

    # API key tidak ditampilkan di UI sama sekali.
    # Dibaca dari .streamlit/secrets.toml atau environment variable.
    groq_api_key = load_api_key()

    reset_button = st.button(
        "🗑️  Hapus percakapan",
        key="reset",
        help="Hapus riwayat chat dan mulai dari awal",
    )
    st.markdown('<div class="side-foot">Dibuat untuk pelajar Indonesia 💚</div>', unsafe_allow_html=True)

# ---------------------------------------------------------------
# STATE
# ---------------------------------------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []
st.session_state.setdefault("xp", 0)
st.session_state.setdefault("asked", 0)

if groq_api_key and (
    "groq_client" not in st.session_state
    or getattr(st.session_state, "_last_groq_api_key", None) != groq_api_key
):
    try:
        st.session_state.groq_client = Groq(api_key=groq_api_key)
        st.session_state._last_groq_api_key = groq_api_key
        st.session_state.messages = []
    except Exception as e:
        st.error(f"Tidak bisa menginisialisasi Groq. Periksa API key kamu. Detail: {e}")
        st.stop()

if reset_button:
    st.session_state.messages = []
    st.session_state.xp = 0
    st.session_state.asked = 0
    st.session_state.topic = None
    st.rerun()

# ---------------------------------------------------------------
# HALAMAN UTAMA
# ---------------------------------------------------------------
header_slot = st.empty()
render_header(header_slot)

if not groq_api_key:
    st.markdown(
        """<div class="hero"><div class="mascot">🐍</div>
<div class="bubble">Halo! Groq API key belum diatur, jadi aku belum bisa menjawab.</div></div>""",
        unsafe_allow_html=True,
    )
    st.error(
        "Tambahkan `GROQ_API_KEY` di Streamlit Secrets (atau file `.streamlit/secrets.toml`), lalu jalankan ulang aplikasi.",
        icon="🗝️",
    )
    st.stop()

pending = st.session_state.pop("pending", None)

# Layar sambutan + contoh pertanyaan
if not st.session_state.messages and not pending:
    st.markdown(
        """<div class="hero"><div class="mascot">🐍</div>
<div class="bubble">Hai, aku PyBuddy! Mau belajar apa hari ini?</div></div>
<p class="hint">Mulai dari sini, atau pilih topik di menu samping:</p>""",
        unsafe_allow_html=True,
    )
    cols = st.columns(2)
    for i, text in enumerate(QUICK_STARTS):
        if cols[i % 2].button(text, key=f"chip_{i}"):
            st.session_state.pending = text
            st.rerun()

# Riwayat chat
for msg in st.session_state.messages:
    avatar = "🐍" if msg["role"] == "assistant" else "🧑‍🎓"
    with st.chat_message(msg["role"], avatar=avatar):
        st.markdown(msg["content"])

# Input
prompt = st.chat_input("Contoh: Apa bedanya list dan tuple?") or pending

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("user", avatar="🧑‍🎓"):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar="🐍"):
        try:
            reply = st.write_stream(stream_reply(prompt))
            st.session_state.messages.append({"role": "assistant", "content": reply})

            # Beri XP setiap pertanyaan berhasil dijawab.
            old_level = st.session_state.xp // XP_PER_LEVEL
            st.session_state.xp += XP_PER_QUESTION
            st.session_state.asked += 1
            render_header(header_slot)
            if st.session_state.xp // XP_PER_LEVEL > old_level:
                st.toast("Naik level! Kamu hebat 🎉", icon="🏆")
            else:
                st.toast(f"+{XP_PER_QUESTION} XP", icon="⭐")
        except Exception as e:
            if is_busy(e):
                st.warning(
                    "Provider Groq sedang sibuk atau batas pemakaian tercapai. "
                    "Tunggu sebentar lalu kirim pertanyaanmu lagi.",
                    icon="⏳",
                )
            else:
                st.error(
                    "Terjadi kesalahan saat menghubungi Groq. "
                    "Periksa GROQ_API_KEY, batas pemakaian API, atau ketersediaan model. "
                    f"Detail: {e}"
                )
            # Hapus pesan user yang gagal diproses agar bisa dicoba lagi.
            if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
                st.session_state.messages.pop()
