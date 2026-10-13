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

st.set_page_config(page_title="PyBuddy", page_icon="🐍")

# ---------------------------------------------------------------
# SIDEBAR: INFORMASI APLIKASI & PENGATURAN
# ---------------------------------------------------------------
with st.sidebar:
    st.header("🐍 Tentang PyBuddy")

    st.subheader("👥 Target pengguna")
    st.write(
        "Mahasiswa dan pelajar **pemula** yang baru belajar pemrograman "
        "Python dan sering bingung saat menemui konsep baru atau error."
    )

    st.subheader("💡 Bagaimana PyBuddy membantu?")
    st.markdown(
        "- Menjelaskan konsep Python dengan bahasa sederhana\n"
        "- Membantu mencari penyebab error pada kode\n"
        "- Memberi contoh kode dan latihan soal\n"
        "- Bisa digunakan kapan saja selama layanan API tersedia"
    )

    # Ambil API key dari Streamlit Secrets saat deploy.
    # Jika belum ada, pengguna dapat memasukkannya lewat sidebar.
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
        "🗑️ Hapus percakapan",
        help="Hapus riwayat chat dan mulai dari awal",
    )

# ---------------------------------------------------------------
# INISIALISASI RIWAYAT CHAT
# ---------------------------------------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

# Buat client baru saat pertama kali digunakan atau API key berubah.
# Mengikuti materi training: client dan chat disimpan di session_state
# agar konteks percakapan tidak hilang saat Streamlit melakukan rerun.
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

# Buat sesi chat Gemini jika belum ada.
if google_api_key and "genai_client" in st.session_state and "chat" not in st.session_state:
    try:
        st.session_state.chat = st.session_state.genai_client.chats.create(
            model=MODEL,
            config={"system_instruction": SYSTEM_PROMPT},
        )
    except Exception as e:
        st.error(f"Gagal membuat sesi chat Gemini: {e}")
        st.stop()

# ---------------------------------------------------------------
# TOMBOL RESET
# ---------------------------------------------------------------
if reset_button:
    st.session_state.pop("chat", None)
    st.session_state.messages = []
    st.rerun()

# ---------------------------------------------------------------
# HALAMAN UTAMA
# ---------------------------------------------------------------
st.title("🐍 PyBuddy")
st.caption("Teman belajar Python kamu. Tanya apa saja soal coding!")

if not google_api_key:
    st.info(
        "Masukkan Google AI API Key di sidebar untuk mulai chat. "
        "Kamu bisa membuat key di https://aistudio.google.com/apikey",
        icon="🗝️",
    )
    st.stop()

# Tampilkan riwayat chat yang disimpan di st.session_state.
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Input dan respons chatbot.
prompt = st.chat_input("Contoh: Apa bedanya list dan tuple?")

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            response = st.session_state.chat.send_message_stream(prompt)
            reply = st.write_stream(
                chunk.text for chunk in response if getattr(chunk, "text", None)
            )
            st.session_state.messages.append(
                {"role": "assistant", "content": reply}
            )
        except Exception as e:
            st.error(
                "Terjadi kesalahan saat menghubungi Gemini. "
                "Periksa API key, koneksi internet, kuota, atau nama model. "
                f"Detail: {e}"
            )
            # Hapus pesan user yang gagal diproses agar bisa dicoba lagi.
            if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
                st.session_state.messages.pop()
