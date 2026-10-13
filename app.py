import anthropic
import streamlit as st

# ---------------------------------------------------------------
# KONFIGURASI
# ---------------------------------------------------------------
MODEL = "claude-sonnet-5-5"  # ganti jika ingin model lain

SYSTEM_PROMPT = """Kamu adalah PyBuddy, asisten belajar Python yang ramah untuk
mahasiswa dan pelajar pemula di Indonesia.

Aturan:
- Jawab dalam Bahasa Indonesia yang santai tapi jelas.
- Jelaskan konsep dengan bahasa sederhana dan analogi sehari-hari.
- Sertakan contoh kode pendek (maksimal ~15 baris) bila relevan.
- Jika pengguna mengirim error, jelaskan penyebabnya lalu beri cara memperbaikinya.
- Jika pertanyaan di luar topik pemrograman, jawab singkat lalu arahkan kembali
  ke topik belajar coding.
- Dorong pengguna mencoba sendiri, jangan hanya memberi jawaban jadi."""

st.set_page_config(page_title="PyBuddy", page_icon="🐍")

# ---------------------------------------------------------------
# SIDEBAR: TARGET PENGGUNA & MANFAAT
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
        "- Tersedia 24/7, tanpa takut bertanya hal 'dasar'"
    )

    # API key: dari secrets (deploy) atau input manual (lokal)
    api_key = None
    try:
        api_key = st.secrets["ANTHROPIC_API_KEY"]
    except Exception:
        api_key = st.text_input("Anthropic API Key", type="password")

    if st.button("🗑️ Hapus percakapan"):
        st.session_state.messages = []
        st.rerun()

# ---------------------------------------------------------------
# HALAMAN UTAMA
# ---------------------------------------------------------------
st.title("🐍 PyBuddy")
st.caption("Teman belajar Python kamu. Tanya apa saja soal coding!")

if "messages" not in st.session_state:
    st.session_state.messages = []

# Tampilkan riwayat chat
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Input pengguna
if prompt := st.chat_input("Contoh: Apa bedanya list dan tuple?"):
    if not api_key:
        st.warning("Masukkan API key di sidebar dulu ya.")
        st.stop()

    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    client = anthropic.Anthropic(api_key=api_key)

    def stream_reply():
        with client.messages.stream(
            model=MODEL,
            max_tokens=1000,
            system=SYSTEM_PROMPT,
            messages=st.session_state.messages,
        ) as stream:
            for text in stream.text_stream:
                yield text

    with st.chat_message("assistant"):
        try:
            reply = st.write_stream(stream_reply())
            st.session_state.messages.append(
                {"role": "assistant", "content": reply}
            )
        except anthropic.AuthenticationError:
            st.error("API key tidak valid. Cek lagi ya.")
            st.session_state.messages.pop()
        except Exception as e:
            st.error(f"Terjadi kesalahan: {e}")
            st.session_state.messages.pop()
