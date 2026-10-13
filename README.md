# 🐍 PyBuddy – Chatbot Teman Belajar Python

**Target pengguna:** mahasiswa/pelajar pemula yang baru belajar Python.

**Manfaat:** menjelaskan konsep dengan bahasa sederhana, membantu debugging
error, memberi contoh kode & latihan, tersedia kapan saja.

## Jalankan lokal

```bash
pip install -r requirements.txt
streamlit run app.py
```

Masukkan API key di sidebar, atau buat file `.streamlit/secrets.toml`:

```toml
ANTHROPIC_API_KEY = "sk-ant-xxxxx"
```

> Jangan commit `secrets.toml` ke GitHub! Tambahkan ke `.gitignore`.

## Deploy ke Streamlit Community Cloud

1. Upload folder ini (`app.py`, `requirements.txt`, `README.md`) ke repository GitHub.
2. Buka https://share.streamlit.io lalu login dengan GitHub.
3. Klik **Create app** → pilih repo, branch, dan file utama `app.py`.
4. Buka **Advanced settings → Secrets**, lalu isi:
   ```toml
   ANTHROPIC_API_KEY = "sk-ant-xxxxx"
   ```
5. Klik **Deploy**. Tunggu beberapa menit, lalu aplikasimu online.
