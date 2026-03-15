# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

## [2026-02-20]

### Added
- [15:45] **Fitur Image Paste**:
  - Menambahkan kolom `image_path` di GUI untuk memilih file gambar.
  - Mengimplementasikan `_handle_image_paste` di engine untuk menyalin gambar ke clipboard via PowerShell.
  - Otomatis mengirim `Ctrl+V` setelah trigger gambar terdeteksi.
- [15:30] **Logging System**:
  - Menambahkan panel log di GUI bagian bawah untuk memantau aktivitas engine.
  - Menambahkan callback logging di `FastWordEngine` untuk debug real-time.
- [15:15] **GUI Improvement**:
  - Memperbesar ukuran window default menjadi 800x600.
  - Menambahkan scrollbar untuk tabel rules.
  - Menambahkan tombol "Open rules.json" untuk akses cepat ke file konfigurasi.

### Fixed
- [15:00] **Engine Stability**:
  - Memperbaiki crash `LowLevelKeyboardProc` yang hilang saat refactor.
  - Mengembalikan fungsi helper `_async_down` dan `_vk_to_text` yang terhapus.
  - Memindahkan logika injeksi keystroke ke thread terpisah agar tidak memblokir hook utama.
- [14:45] **Compatibility**:
  - Memperbaiki definisi struct `INPUT` agar kompatibel dengan Windows 64-bit (alignment issue).
  - Menangani error `ctypes.wintypes` yang hilang (`ULONG_PTR`, `LRESULT`) di beberapa versi Python.

### Changed
- [14:30] **Initial Release**:
  - Implementasi dasar Global Keyboard Hook menggunakan `ctypes` dan `user32.dll`.
  - GUI dasar menggunakan `tkinter` untuk manajemen rules (Add/Edit/Delete).
  - Penyimpanan rules otomatis ke `%APPDATA%\FastWord\rules.json`.
