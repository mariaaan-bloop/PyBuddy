import streamlit as st
from google import genai

# ---------------------------------------------------------------
# KONFIGURASI
# ---------------------------------------------------------------
MODEL = "gemini-2.5-flash"

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

QUICK_STARTS = [
    "Apa bedanya list dan tuple?",
    "Jelaskan perulangan for dengan analogi",
    "Kenapa muncul IndentationError?",
    "Beri aku latihan soal tentang if-else",
]

st.set_page_config(page_title="PyBuddy", page_icon="🐍", layout="centered")

# ---------------------------------------------------------------
# GAYA (CSS) ALA DUOLINGO
# ---------------------------------------------------------------
CSS = """
@import url('https://fonts.googleapis.com/css2?family=Nunito:wght@600;700;800;900&display=swap');

:root {
  --green: #58CC02;  --green-d: #58A700;
  --blue: #1CB0F6;   --blue-d: #1899D6;  --blue-bg: #DDF4FF;  --blue-line: #84D8FF;
  --yellow: #FFC800; --yellow-d: #E5B400;
  --orange: #FF9600;
  --red: #FF4B4B;    --red-d: #EA2B2B;
  --ink: #3C3C3C;    --muted: #777777;
  --line: #E5E5E5;   --snow: #F7F7F7;
}

/* Dasar */
.stApp { background: #FFFFFF; color: var(--ink); }
.stApp, .stApp p, .stApp li, .stApp label, .stApp h1, .stApp h2, .stApp h3,
.stApp h4, .stApp button, .stApp input, .stApp textarea {
  font-family: 'Nunito', sans-serif;
}
.stApp p, .stApp li { font-weight: 600; font-size: 1.02rem; line-height: 1.6; }
.stApp h1, .stApp h2, .stApp h3, .stApp h4 { font-weight: 900; color: var(--ink); }
#MainMenu, footer { visibility: hidden; }
header[data-testid="stHeader"] { background: transparent; }
.block-container { max-width: 760px; padding-top: 1.2rem; padding-bottom: 6rem; }

/* Bar atas: logo + statistik */
.topbar { display: flex; align-items: center; justify-content: space-between;
  gap: 12px; flex-wrap: wrap; margin-bottom: 8px; }
.brand { font-weight: 900; font-size: 1.9rem; color: var(--green); letter-spacing: -0.5px; }
.stats { display: flex; gap: 8px; flex-wrap: wrap; }
.pill { font-weight: 900; font-size: 1rem; padding: 6px 14px; border-radius: 14px;
  border: 2px solid var(--line); background: #fff; white-space: nowrap; }
.pill.fire { color: var(--orange); }
.pill.xp { color: var(--yellow-d); }
.pill.lvl { color: var(--blue-d); }

/* Progres level */
.level-row { display: flex; align-items: center; gap: 12px; margin: 4px 0 22px; }
.level-name { font-weight: 800; color: var(--muted); font-size: .9rem; white-space: nowrap; }
.track { flex: 1; height: 16px; background: var(--line); border-radius: 99px;
  overflow: hidden; position: relative; }
.fill { height: 100%; background: var(--green); border-radius: 99px;
  position: relative; transition: width .5s ease; min-width: 16px; }
.fill::after { content: ""; position: absolute; left: 8px; right: 8px; top: 3px;
  height: 4px; background: rgba(255,255,255,.35); border-radius: 99px; }

/* Maskot + gelembung bicara */
.hero { display: flex; align-items: center; gap: 18px; margin: 18px 0 26px; }
.mascot { font-size: 5.2rem; line-height: 1; animation: bob 2.4s ease-in-out infinite; }
@keyframes bob { 0%,100% { transform: translateY(0); } 50% { transform: translateY(-8px); } }
.bubble { position: relative; border: 2px solid var(--line); border-radius: 18px;
  padding: 14px 18px; font-weight: 800; font-size: 1.15rem; color: var(--ink); }
.bubble::before { content: ""; position: absolute; left: -12px; top: 50%;
  margin-top: -10px; border: 10px solid transparent; border-right-color: var(--line);
  border-left: 0; }
.bubble::after { content: ""; position: absolute; left: -9px; top: 50%;
  margin-top: -8px; border: 8px solid transparent; border-right-color: #fff;
  border-left: 0; }
.hint { font-weight: 800; color: var(--muted); margin: 0 0 10px; }

/* Tombol 3D */
.stButton > button {
  background: #fff; color: var(--blue-d); font-weight: 800; font-size: 1rem;
  border: 2px solid var(--line); border-bottom-width: 4px; border-radius: 16px;
  padding: 10px 14px; min-height: 52px; width: 100%; text-align: left;
  transition: transform .05s, background .15s;
}
.stButton > button:hover { background: var(--snow); border-color: var(--line); color: var(--blue-d); }
.stButton > button:active { transform: translateY(2px); border-bottom-width: 2px; }
.stButton > button:focus-visible { outline: 3px solid var(--blue-line); outline-offset: 2px; }

.st-key-reset button { background: var(--red); color: #fff; border-color: var(--red-d);
  text-align: center; font-weight: 900; }
.st-key-reset button:hover { background: #ff6161; color: #fff; border-color: var(--red-d); }

/* Gelembung chat */
[data-testid="stChatMessage"] {
  background: #fff; border: 2px solid var(--line); border-radius: 20px;
  padding: 14px 18px; margin-bottom: 14px;
}
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]),
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) {
  background: var(--blue-bg); border-color: var(--blue-line);
}
[data-testid="stChatMessageAvatarAssistant"], [data-testid="stChatMessageAvatarUser"],
[data-testid="chatAvatarIcon-assistant"], [data-testid="chatAvatarIcon-user"] {
  background: #fff; border: 2px solid var(--line); border-radius: 50%;
}

/* Blok kode */
[data-testid="stCode"] pre, .stMarkdown pre {
  background: var(--snow) !important; border: 2px solid var(--line);
  border-radius: 14px;
}
.stMarkdown code { border-radius: 8px; font-weight: 700; }

/* Kolom input chat */
[data-testid="stBottom"] > div { background: #fff; }
[data-testid="stChatInput"] { border: 2px solid var(--line); border-radius: 18px;
  background: var(--snow); }
[data-testid="stChatInput"]:focus-within { border-color: var(--blue); }
[data-testid="stChatInput"] textarea { font-weight: 700; }

/* Sidebar */
[data-testid="stSidebar"] { background: #fff; border-right: 2px solid var(--line); }
.side-card { border: 2px solid var(--line); border-radius: 18px; padding: 14px 16px;
  margin-bottom: 14px; }
.side-card h4 { margin: 0 0 6px; font-size: 1.05rem; }
.side-card p, .side-card li { font-size: .95rem; margin: 0; }
.side-card ul { padding-left: 18px; margin: 0; }
[data-testid="stSidebar"] input { border-radius: 14px; font-weight: 700; }

@media (max-width: 600px) {
  .hero { flex-direction: column; text-align: center; }
  .bubble::before, .bubble::after { display: none; }
  .brand { font-size: 1.6rem; }
}
@media (prefers-reduced-motion: reduce) {
  .mascot { animation: none; }
  .fill { transition: none; }
}
"""
st.markdown(f"<style>{CSS}</style>", unsafe_allow_html=True)


# ---------------------------------------------------------------
# FUNGSI BANTU
# ---------------------------------------------------------------
def render_stats(slot):
    """Gambar bar statistik (jumlah tanya, XP, level) ke slot yang diberikan."""
    xp = st.session_state.xp
    level = xp // XP_PER_LEVEL + 1
    progress = (xp % XP_PER_LEVEL) / XP_PER_LEVEL * 100
    title = LEVEL_TITLES[min(level - 1, len(LEVEL_TITLES) - 1)]
    slot.markdown(
        f"""<div class="topbar">
<div class="brand">🐍 pybuddy</div>
<div class="stats">
<span class="pill fire">🔥 {st.session_state.asked}</span>
<span class="pill xp">⭐ {xp} XP</span>
<span class="pill lvl">🏆 Level {level}</span>
</div></div>
<div class="level-row">
<span class="level-name">{title}</span>
<div class="track"><div class="fill" style="width:{progress}%"></div></div>
</div>""",
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------
# SIDEBAR
# ---------------------------------------------------------------
with st.sidebar:
    st.markdown(
        """<div class="side-card"><h4>👥 Untuk siapa?</h4>
<p>Mahasiswa dan pelajar <b>pemula</b> yang baru belajar Python dan sering
bingung saat bertemu konsep baru atau error.</p></div>
<div class="side-card"><h4>💡 PyBuddy bisa bantu</h4>
<ul>
<li>Menjelaskan konsep dengan bahasa sederhana</li>
<li>Mencari penyebab error di kodemu</li>
<li>Memberi contoh kode dan latihan soal</li>
</ul></div>""",
        unsafe_allow_html=True,
    )

    # Ambil API key dari Streamlit Secrets saat deploy.
    try:
        saved_api_key = st.secrets.get("GEMINI_API_KEY", "")
    except Exception:
        saved_api_key = ""

    google_api_key = st.text_input(
        "Google AI API Key",
        value=saved_api_key,
        type="password",
        help="Buat API key di https://aistudio.google.com/apikey",
    )

    reset_button = st.button(
        "Hapus percakapan",
        key="reset",
        icon="🗑️",
        help="Hapus riwayat chat dan mulai dari awal",
    )

# ---------------------------------------------------------------
# STATE
# ---------------------------------------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []
st.session_state.setdefault("xp", 0)
st.session_state.setdefault("asked", 0)

if google_api_key and (
    "genai_client" not in st.session_state
    or getattr(st.session_state, "_last_key", None) != google_api_key
):
    try:
        st.session_state.genai_client = genai.Client(api_key=google_api_key)
        st.session_state._last_key = google_api_key
        st.session_state.pop("chat", None)
        st.session_state.messages = []
    except Exception as e:
        st.error(f"Tidak bisa menginisialisasi Gemini. Periksa API key kamu. Detail: {e}")
        st.stop()

if google_api_key and "genai_client" in st.session_state and "chat" not in st.session_state:
    try:
        st.session_state.chat = st.session_state.genai_client.chats.create(
            model=MODEL,
            config={"system_instruction": SYSTEM_PROMPT},
        )
    except Exception as e:
        st.error(f"Gagal membuat sesi chat Gemini: {e}")
        st.stop()

if reset_button:
    st.session_state.pop("chat", None)
    st.session_state.messages = []
    st.session_state.xp = 0
    st.session_state.asked = 0
    st.rerun()

# ---------------------------------------------------------------
# HALAMAN UTAMA
# ---------------------------------------------------------------
stats_slot = st.empty()
render_stats(stats_slot)

if not google_api_key:
    st.markdown(
        """<div class="hero"><div class="mascot">🐍</div>
<div class="bubble">Halo! Masukkan API key di sidebar dulu, lalu kita mulai belajar Python bareng.</div></div>""",
        unsafe_allow_html=True,
    )
    st.info("Buat key gratis di https://aistudio.google.com/apikey", icon="🗝️")
    st.stop()

pending = st.session_state.pop("pending", None)

# Layar sambutan + tombol pertanyaan cepat
if not st.session_state.messages and not pending:
    st.markdown(
        """<div class="hero"><div class="mascot">🐍</div>
<div class="bubble">Hai, aku PyBuddy! Mau belajar apa hari ini?</div></div>
<p class="hint">Mulai dari sini, atau ketik pertanyaanmu di bawah:</p>""",
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
            response = st.session_state.chat.send_message_stream(prompt)
            reply = st.write_stream(
                chunk.text for chunk in response if getattr(chunk, "text", None)
            )
            st.session_state.messages.append({"role": "assistant", "content": reply})

            # Beri XP setiap pertanyaan berhasil dijawab.
            old_level = st.session_state.xp // XP_PER_LEVEL
            st.session_state.xp += XP_PER_QUESTION
            st.session_state.asked += 1
            render_stats(stats_slot)
            if st.session_state.xp // XP_PER_LEVEL > old_level:
                st.toast("Naik level! Kamu hebat 🎉", icon="🏆")
            else:
                st.toast(f"+{XP_PER_QUESTION} XP", icon="⭐")
        except Exception as e:
            st.error(
                "Terjadi kesalahan saat menghubungi Gemini. "
                "Periksa API key, koneksi internet, kuota, atau nama model. "
                f"Detail: {e}"
            )
            # Hapus pesan user yang gagal diproses agar bisa dicoba lagi.
            if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
                st.session_state.messages.pop()
