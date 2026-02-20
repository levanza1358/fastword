# AutoWord (Windows Text Expander)

Aplikasi desktop sederhana untuk Windows yang berfungsi sebagai *text expander* (mengganti singkatan menjadi teks panjang) dan *image paster* (otomatis copy-paste gambar).

Dibuat menggunakan Python + Tkinter + Windows API (ctypes) tanpa dependency berat.

## Fitur
- **Text Replacement**: Ketik `/up` -> otomatis jadi `WASDWASD`.
- **Image Paste**: Ketik trigger -> otomatis copy gambar ke clipboard dan paste (Ctrl+V).
- **Global Hook**: Bekerja di semua aplikasi Windows (Notepad, Word, Browser, Discord, Game, dll).
- **Lightweight**: Menggunakan library bawaan Python dan Windows API native.
- **GUI Manager**: Antarmuka mudah untuk tambah/edit/hapus rules.

## Persyaratan
- Windows 10 / 11
- Python 3.10 atau lebih baru

## Cara Instalasi
1. Clone atau download repository ini.
2. Pastikan Python sudah terinstall.
3. Tidak perlu `pip install` apapun (kecuali kamu mau mengembangkan lebih lanjut).

## Cara Menjalankan
Buka terminal (Command Prompt / PowerShell) di folder project:

```bash
python main.py
```

## Cara Penggunaan
1. Klik tombol **Start** di aplikasi.
2. Tambahkan Rule baru:
   - Klik **Add**.
   - **Trigger**: Kata kunci pemicu (contoh: `/logo`).
   - **Output Text**: Teks pengganti (opsional).
   - **Image Path**: Pilih file gambar jika ingin auto-paste gambar (opsional).
   - Klik **Save**.
3. Buka aplikasi lain (misal Notepad atau Discord).
4. Ketik trigger yang sudah dibuat. Teks akan terganti otomatis.

## Catatan Teknis
- Rules disimpan di `%APPDATA%\AutoWord\rules.json`.
- Aplikasi menggunakan `ctypes` untuk hook keyboard level rendah (`WH_KEYBOARD_LL`).
- Fitur gambar menggunakan PowerShell untuk memanipulasi clipboard tanpa library eksternal.

## Troubleshooting
- Jika tidak jalan: Pastikan tombol **Start** sudah diklik.
- Jika error permission: Coba jalankan terminal sebagai Administrator.
- Cek log di bagian bawah aplikasi untuk melihat status deteksi trigger.
