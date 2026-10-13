import os
import time

import streamlit as st
from groq import Groq

# ---------------------------------------------------------------
# KONFIGURASI
# ---------------------------------------------------------------
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

TOPICS = [
    ("🐣", "Dasar Python", "Jelaskan dasar-dasar Python untuk pemula: variabel, tipe data, dan print."),
    ("📦", "List, Tuple & Dict", "Jelaskan perbedaan list, tuple, dan dictionary, beserta kapan memakainya."),
    ("🔁", "Perulangan & Kondisi", "Jelaskan if-else dan perulangan for/while dengan analogi sehari-hari."),
    ("🧩", "Fungsi & Modul", "Jelaskan cara membuat fungsi di Python dan cara memakai modul."),
    ("🐞", "Debug Error", "Ajari aku cara membaca pesan error Python dan menemukan penyebabnya."),
    ("📝", "Latihan Soal", "Beri aku satu latihan soal Python untuk pemula, tanpa kunci jawaban dulu."),
]

QUICK_STARTS = [
    ("📦", "Apa bedanya list dan tuple?"),
    ("🔁", "Jelaskan perulangan for dengan analogi"),
    ("🐞", "Kenapa muncul IndentationError?"),
    ("📝", "Beri aku latihan soal tentang if-else"),
]

# ---------------------------------------------------------------
# TEMA & WARNA BUBBLE CHAT
# ---------------------------------------------------------------
THEMES = {
    "light": {
        "icon": "☀️",
        "name": "Terang",
        "scheme": "light",
        "vars": {
            "bg": "#F4F7FC", "bg_solid": "#F4F7FC", "surface": "#FFFFFF",
            "soft": "#EAEFF7", "side_bg": "#FFFFFF", "line": "#D5DFEF",
            "ink": "#182642", "muted": "#647493",
            "accent": "#2B6CB0", "accent_d": "#2C5282", "accent_soft": "#EBF8FF",
            "on_accent": "#FFFFFF", "hl": "#ECC94B", "danger": "#E53E3E",
            # Warna Bubble Chat User (Biru lembut yang kontras dengan background bot)
            "user_bg": "#DCEEFE", "user_line": "#90CDF4", "user_ink": "#1A365D",
            "hero_1": "#3182CE", "hero_2": "#2B6CB0", "code_ink": "#2C5282",
            "term_bg": "#1A202C", "shadow": "rgba(49,130,206,.2)",
        },
        "extra": "",
    },
    "dark": {
        "icon": "🌙",
        "name": "Gelap",
        "scheme": "dark",
        "vars": {
            "bg": "#0B132B", "bg_solid": "#0B132B", "surface": "#1C2541",
            "soft": "#283559", "side_bg": "#080F22", "line": "#3A4D78",
            "ink": "#F0F4F8", "muted": "#9FB3C8",
            "accent": "#4FD1C5", "accent_d": "#319795", "accent_soft": "#1D3B48",
            "on_accent": "#0B132B", "hl": "#F6E05E", "danger": "#FEB2B2",
            # Warna Bubble Chat User (Hijau/Teal Gelap yang beda dari bot)
            "user_bg": "#134E4A", "user_line": "#2DD4BF", "user_ink": "#CCFBF1",
            "hero_1": "#2B6CB0", "hero_2": "#1A365D", "code_ink": "#F6E05E",
            "term_bg": "#070B16", "shadow": "rgba(0,0,0,.4)",
        },
        "extra": """
[data-testid="stAlert"] p { color: #F0F4F8; }
""",
    },
    "sunset": {
        "icon": "🌇",
        "name": "Senja",
        "scheme": "light",
        "vars": {
            "bg": "#FFF5F0", "bg_solid": "#FFF5F0", "surface": "#FFFFFF",
            "soft": "#FEEBC8", "side_bg": "#FFFAF0", "line": "#FBD38D",
            "ink": "#2D3748", "muted": "#7B341E",
            "accent": "#DD6B20", "accent_d": "#C05621", "accent_soft": "#FFFAF0",
            "on_accent": "#FFFFFF", "hl": "#D69E2E", "danger": "#E53E3E",
            # Warna Bubble Chat User (Keoranyean/Krem hangat)
            "user_bg": "#FEEBC8", "user_line": "#FBD38D", "user_ink": "#7B341E",
            "hero_1": "#ED8936", "hero_2": "#DD6B20", "code_ink": "#C05621",
            "term_bg": "#2C1A1D", "shadow": "rgba(221,107,32,.2)",
        },
        "extra": "",
    },
}

# Konfigurasi Halaman + Membuat Sidebar Selalu Terbuka (expanded)
st.set_page_config(
    page_title="PyBuddy", 
    page_icon="🐍", 
    layout="centered",
    initial_sidebar_state="expanded"
)

theme = st.session_state.setdefault("theme", "light")
if theme not in THEMES:
    theme = st.session_state.theme = "light"

# ---------------------------------------------------------------
# GAYA (CSS)
# ---------------------------------------------------------------
FONT_CSS = (
    "@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@500;600;700;800"
    "&family=JetBrains+Mono:wght@500;700&display=swap');"
)

THEME_CSS = (
    ":root{color-scheme:" + THEMES[theme]["scheme"] + ";"
    + ";".join(f"--{k.replace('_', '-')}:{v}" for k, v in THEMES[theme]["vars"].items())
    + "}"
)

BASE_CSS = """
/* ---------- Pengaturan Sidebar Permanen ---------- */
/* Sembunyikan tombol panah penutup/pembuka sidebar */
[data-testid="stSidebarCollapseButton"],
[data-testid="stExpandSidebarButton"] {
    display: none !important;
}

.stApp { background: var(--bg); background-attachment: fixed; color: var(--ink); }
[data-testid="stAppViewContainer"], [data-testid="stMain"] { background: transparent; }
.stApp, .stApp p, .stApp li, .stApp label, .stApp h1, .stApp h2, .stApp h3,
.stApp h4, .stApp button, .stApp input, .stApp textarea { font-family: 'Plus Jakarta Sans', sans-serif; }
:is([data-testid="stMain"], [data-testid="stSidebar"], [data-testid="stBottom"])
  :is(p, li, label, h1, h2, h3, h4) { color: var(--ink); }
.stApp p, .stApp li { font-weight: 500; font-size: 1rem; line-height: 1.65; }
.stApp h1, .stApp h2, .stApp h3, .stApp h4 { font-weight: 800; letter-spacing: -.01em; }
.stApp a { color: var(--accent); font-weight: 600; }
footer, [data-testid="stToolbar"], [data-testid="stDecoration"] { display: none; }
header[data-testid="stHeader"] { background: transparent; }
.block-container { max-width: 800px; padding-top: 1.6rem; padding-bottom: 6rem; }

/* ---------- Header Aplikasi ---------- */
.appbar { background: linear-gradient(135deg, var(--hero-1), var(--hero-2)); color: #fff;
  border-radius: 22px; padding: 20px 24px 18px; margin-bottom: 28px;
  box-shadow: 0 14px 30px -18px var(--shadow); }
.appbar-top { display: flex; align-items: center; justify-content: space-between;
  gap: 14px; flex-wrap: wrap; }
.brand { display: flex; align-items: center; gap: 14px; }
.logo { width: 54px; height: 54px; border-radius: 16px; background: rgba(255,255,255,.18);
  display: grid; place-items: center; font-size: 1.9rem; }
.app-name { font-weight: 800; font-size: 1.6rem; line-height: 1.1; letter-spacing: -.02em; color: #fff; }
.app-tag { font-weight: 500; font-size: .92rem; color: rgba(255,255,255,.85); margin-top: 2px; }
.stats { display: flex; gap: 8px; flex-wrap: wrap; }
.pill { font-weight: 700; font-size: .9rem; padding: 6px 12px; border-radius: 999px;
  background: rgba(255,255,255,.16); color: #fff; white-space: nowrap; }
.level-meta { display: flex; justify-content: space-between; font-weight: 700;
  font-size: .85rem; margin: 20px 0 8px; color: #fff; }
.track { height: 10px; background: rgba(0,0,0,.25); border-radius: 99px; overflow: hidden; }
.fill { height: 100%; background: var(--hl); border-radius: 99px; transition: width .5s ease; }

/* ---------- Hero Terminal ---------- */
.hero { display: flex; align-items: center; gap: 18px; margin: 4px 0 26px; }
.mascot { flex: none; width: 84px; height: 84px; border-radius: 24px; display: grid;
  place-items: center; font-size: 3rem; background: var(--surface); border: 1px solid var(--line);
  box-shadow: 0 10px 24px -16px var(--shadow); }
.term { flex: 1; min-width: 0; background: var(--term-bg); border-radius: 16px; overflow: hidden;
  border: 1px solid rgba(255,255,255,.08); box-shadow: 0 14px 30px -18px var(--shadow); }
.term-bar { display: flex; align-items: center; gap: 6px; padding: 9px 14px;
  background: rgba(255,255,255,.05); }
.dot { width: 10px; height: 10px; border-radius: 50%; display: inline-block; }
.dot.r { background: #FF6B6B; } .dot.y { background: #FFD43B; } .dot.g { background: #51CF66; }
.term-bar .file { margin-left: 8px; font: 600 .75rem 'JetBrains Mono', monospace; color: #8FA2C4; }
.term-body { padding: 14px 18px 16px; font-family: 'JetBrains Mono', monospace; font-size: .9rem;
  line-height: 1.75; color: #E8EEF9; white-space: pre-wrap; word-break: break-word; }
.term-body .pr { color: #7488AD; }
.term-body .fn { color: #FFD43B; font-weight: 700; }
.term-body .st { color: #8EE0A5; }
.cursor { display: inline-block; width: .55em; height: 1.05em; background: var(--hl);
  vertical-align: -.18em; margin-left: 2px; animation: blink 1.1s steps(1) infinite; }
@keyframes blink { 50% { opacity: 0; } }
.hint { font-weight: 600; font-size: .92rem; color: var(--muted); margin: 0 0 12px; }

/* ---------- Tombol Utilitas ---------- */
.stButton, [data-testid="stButton"] { width: 100%; }
.stButton > button {
  width: 100%; background: var(--surface); color: var(--ink); font-weight: 600; font-size: .98rem;
  border: 1px solid var(--line); border-radius: 14px; padding: 10px 16px; min-height: 52px;
  box-shadow: 0 1px 0 var(--line);
  transition: border-color .15s, background .15s, transform .1s;
}
.stButton > button p { color: inherit !important; font-weight: inherit; font-size: inherit;
  margin: 0; line-height: 1.35; }
.stButton > button:hover { background: var(--soft); border-color: var(--accent); color: var(--ink); }
.stButton > button:active { transform: translateY(1px); }
.stButton > button:focus-visible { outline: 2px solid var(--accent); outline-offset: 2px; }

div[class*="st-key-chip_"] button { justify-content: flex-start; text-align: left;
  min-height: 64px; padding: 12px 16px; }
div[class*="st-key-chip_"] button div { justify-content: flex-start; text-align: left; width: 100%; }
div[class*="st-key-chip_"] button p { white-space: normal; }

/* ---------- Kustomisasi Bubble Chat (Bot vs User) ---------- */
/* Gelembung Asisten / Bot */
[data-testid="stChatMessage"] { 
  background: var(--surface) !important; 
  border: 1px solid var(--line);
  border-radius: 16px; 
  padding: 14px 18px; 
  margin-bottom: 12px; 
}
[data-testid="stChatMessage"] :is(p, li, h1, h2, h3, h4, strong, em, td, th, blockquote, span.katex) {
  color: var(--ink) !important; 
}

/* Gelembung User / Pengguna (Dibuat Beda) */
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]),
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) {
  background: var(--user-bg) !important; 
  border: 1px solid var(--user-line) !important; 
}
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) :is(p, li, h1, h2, h3, h4, strong, em, td, th, blockquote, span.katex),
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) :is(p, li, h1, h2, h3, h4, strong, em, td, th, blockquote, span.katex) {
  color: var(--user-ink) !important; 
}

[data-testid="stChatMessageAvatarAssistant"], [data-testid="stChatMessageAvatarUser"],
[data-testid="chatAvatarIcon-assistant"], [data-testid="chatAvatarIcon-user"] {
  background: var(--surface); border: 1px solid var(--line); border-radius: 50%; }

/* ---------- Kode ---------- */
[data-testid="stCode"] pre, .stMarkdown pre { background: var(--soft) !important;
  border: 1px solid var(--line); border-radius: 12px; }
[data-testid="stCode"] pre, [data-testid="stCode"] code, [data-testid="stCode"] code span,
.stMarkdown pre, .stMarkdown pre code { font-family: 'JetBrains Mono', monospace;
  font-size: .88rem; color: var(--ink) !important; }
.stMarkdown :not(pre) > code { background: var(--soft); color: var(--code-ink);
  font-family: 'JetBrains Mono', monospace; font-size: .86em; font-weight: 700;
  border-radius: 6px; padding: .1em .4em; }

/* ---------- Input Bar ---------- */
[data-testid="stBottom"] > div { background: var(--bg-solid); }
[data-testid="stChatInput"] { background: var(--surface); border: 1px solid var(--line);
  border-radius: 16px; box-shadow: 0 6px 20px -14px var(--shadow); }
[data-testid="stChatInput"] > div { background: transparent !important; }
[data-testid="stChatInput"] textarea { background: transparent; color: var(--ink) !important;
  font-weight: 500; }
[data-testid="stChatInput"] textarea::placeholder { color: var(--muted) !important; opacity: 1; }
[data-testid="stChatInput"]:focus-within { border-color: var(--accent);
  box-shadow: 0 0 0 3px var(--accent-soft); }
[data-testid="stChatInputSubmitButton"] { background: var(--accent); color: var(--on-accent);
  border-radius: 10px; }
[data-testid="stChatInputSubmitButton"]:disabled { background: var(--soft); color: var(--muted); }

/* ---------- Sidebar Style ---------- */
[data-testid="stSidebar"] { background: var(--side-bg); border-right: 1px solid var(--line); }
[data-testid="stSidebarHeader"] { padding: .6rem 1rem 0; min-height: 0; height: auto; }
[data-testid="stSidebar"] [data-testid="stSidebarContent"] { padding: 0 1rem 1.4rem; }
[data-testid="stSidebar"] [data-testid="stVerticalBlock"] { gap: .4rem; }
[data-testid="stSidebar"] [data-testid="stElementContainer"],
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] { overflow: visible; }

.side-brand { display: flex; align-items: center; gap: 12px; padding: 4px 2px 14px; }
.logo-sm { flex: none; width: 44px; height: 44px; border-radius: 13px; font-size: 1.4rem;
  background: linear-gradient(135deg, var(--hero-1), var(--hero-2)); display: grid;
  place-items: center; }
.side-name { font-weight: 800; font-size: 1.2rem; color: var(--ink); line-height: 1.15;
  letter-spacing: -.01em; }
.side-sub { font-weight: 500; font-size: .84rem; color: var(--muted); line-height: 1.3; }
.side-label { display: block; font-weight: 700; font-size: .82rem; color: var(--muted);
  line-height: 1.3; padding: 16px 4px 6px; }
.side-divider { height: 1px; background: var(--line); margin: 14px 0 6px; }
.side-foot { font-weight: 500; font-size: .8rem; color: var(--muted); text-align: center;
  padding-top: 10px; }

div[class*="st-key-nav"] button { justify-content: flex-start; background: transparent;
  color: var(--ink); border: 1px solid transparent; border-radius: 12px; min-height: 44px;
  padding: 6px 12px; box-shadow: none; }
div[class*="st-key-nav"] button div { justify-content: flex-start; text-align: left; width: 100%; }
div[class*="st-key-nav"] button p { text-align: left; white-space: nowrap; font-weight: 600;
  font-size: .95rem; }
div[class*="st-key-nav"] button:hover { background: var(--soft); border-color: transparent; color: var(--ink); }
div[class*="st-key-navon_"] button { background: var(--accent-soft); box-shadow: inset 3px 0 0 var(--accent); }
div[class*="st-key-navon_"] button p { font-weight: 800; }

div[class*="st-key-theme"] button { justify-content: center; background: var(--surface);
  border: 1px solid var(--line); border-radius: 12px; min-height: 44px; padding: 4px;
  box-shadow: none; }
div[class*="st-key-theme"] button p { font-size: 1.2rem; line-height: 1; }
div[class*="st-key-theme"] button:hover { background: var(--soft); border-color: var(--accent); }
div[class*="st-key-themeon_"] button { background: var(--accent-soft); border-color: var(--accent);
  box-shadow: 0 0 0 1px var(--accent); }

div.st-key-reset button { background: transparent; color: var(--danger);
  border: 1px solid var(--danger); justify-content: center; font-weight: 700;
  min-height: 44px; box-shadow: none; }
div.st-key-reset button:hover { background: var(--danger); color: var(--on-accent);
  border-color: var(--danger); }

[data-testid="stSidebar"] [data-testid="stExpander"] details { background: var(--surface);
  border: 1px solid var(--line); border-radius: 12px; }
[data-testid="stSidebar"] [data-testid="stExpander"] summary { padding: .55rem .8rem; }
[data-testid="stSidebar"] [data-testid="stExpander"] summary p { color: var(--ink);
  font-weight: 700; font-size: .93rem; }
[data-testid="stSidebar"] [data-testid="stExpanderDetails"] p { font-size: .9rem; line-height: 1.55; }

@media (max-width: 600px) {
  .hero { flex-direction: column; align-items: stretch; }
  .mascot { width: 68px; height: 68px; font-size: 2.4rem; border-radius: 20px; }
  .app-name { font-size: 1.4rem; }
  .logo { width: 46px; height: 46px; font-size: 1.6rem; }
}
@media (prefers-reduced-motion: reduce) {
  .cursor { animation: none; }
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
    try:
        key = st.secrets.get("GROQ_API_KEY", "")
    except Exception:
        key = ""
    return key or os.environ.get("GROQ_API_KEY", "")


def is_busy(error):
    text = str(error).upper()
    return any(k in text for k in ("503", "429", "502", "504", "RATE LIMIT", "OVERLOADED", "TEMPORARILY UNAVAILABLE"))


def stream_reply():
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


def hero_html(body):
    return (
        '<div class="hero"><div class="mascot">🐍</div><div class="term">'
        '<div class="term-bar"><span class="dot r"></span><span class="dot y"></span>'
        '<span class="dot g"></span><span class="file">pybuddy.py</span></div>'
        f'<div class="term-body">{body}</div></div></div>'
    )


def py_line(fn, arg):
    return (
        f'<div><span class="pr">&gt;&gt;&gt;</span> <span class="fn">{fn}</span>'
        f'(<span class="st">"{arg}"</span>)</div>'
    )


def py_out(text, cursor=False):
    return f'<div>{text}{"<span class=cursor></span>" if cursor else ""}</div>'


def render_header(slot):
    xp = st.session_state.xp
    level = xp // XP_PER_LEVEL + 1
    into_level = xp % XP_PER_LEVEL
    title = LEVEL_TITLES[min(level - 1, len(LEVEL_TITLES) - 1)]
    pct = into_level / XP_PER_LEVEL * 100
    min_w = 12 if pct else 0
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
<div class="track"><div class="fill" style="width:{pct}%;min-width:{min_w}px"></div></div>
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
<div><div class="side-name">PyBuddy</div><div class="side-sub">Teman belajar Python</div></div></div>""",
        unsafe_allow_html=True,
    )

    st.markdown('<div class="side-label">Pilih topik belajar</div>', unsafe_allow_html=True)
    for i, (emoji, label, question) in enumerate(TOPICS):
        key = f"navon_{i}" if st.session_state.topic == i else f"nav_{i}"
        if st.button(f"{emoji}  {label}", key=key):
            st.session_state.topic = i
            st.session_state.pending = question
            st.rerun()

    st.markdown('<div class="side-label">Tampilan</div>', unsafe_allow_html=True)
    theme_cols = st.columns(3, gap="small")
    for col, (name, t) in zip(theme_cols, THEMES.items()):
        key = f"themeon_{name}" if name == theme else f"theme_{name}"
        if col.button(t["icon"], key=key, help=t["name"]):
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

    groq_api_key = load_api_key()

    st.markdown('<div class="side-divider"></div>', unsafe_allow_html=True)
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
        hero_html(
            py_line("print", "Groq API key belum diatur")
            + py_out("Groq API key belum diatur, jadi aku belum bisa menjawab.", cursor=True)
        ),
        unsafe_allow_html=True,
    )
    st.error(
        "Tambahkan `GROQ_API_KEY` di Streamlit Secrets (atau file `.streamlit/secrets.toml`), lalu jalankan ulang aplikasi.",
        icon="🗝️",
    )
    st.stop()

pending = st.session_state.pop("pending", None)

if not st.session_state.messages and not pending:
    st.markdown(
        hero_html(
            py_line("print", "Hai, aku PyBuddy!")
            + py_out("Hai, aku PyBuddy!")
            + py_line("input", "Mau belajar apa hari ini? ")
            + py_out("Mau belajar apa hari ini? ", cursor=True)
        )
        + '<p class="hint">Coba salah satu pertanyaan ini, atau pilih topik di menu samping.</p>',
        unsafe_allow_html=True,
    )
    cols = st.columns(2, gap="small")
    for i, (icon, text) in enumerate(QUICK_STARTS):
        if cols[i % 2].button(f"{icon}  {text}", key=f"chip_{i}"):
            st.session_state.pending = text
            st.rerun()

for msg in st.session_state.messages:
    avatar = "🐍" if msg["role"] == "assistant" else "🧑‍🎓"
    with st.chat_message(msg["role"], avatar=avatar):
        st.markdown(msg["content"])

prompt = st.chat_input("Contoh: Apa bedanya list dan tuple?") or pending

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("user", avatar="🧑‍🎓"):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar="🐍"):
        try:
            reply = st.write_stream(stream_reply())
            st.session_state.messages.append({"role": "assistant", "content": reply})

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
            if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
                st.session_state.messages.pop()
