<div align="center">

# 🖥️ Console Daemon Manager

**Jalankan banyak task terjadwal (seperti cron job) dengan console terpisah per task — output real-time, konfigurasi GUI, tanpa edit file manual.**

[![Python](https://img.shields.io/badge/Python-3.9%2B-blue.svg)](https://www.python.org/)
[![PyQt5](https://img.shields.io/badge/PyQt5-5.15%2B-green.svg)](https://pypi.org/project/PyQt5/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

</div>

---

## 📖 Daftar Isi

- [Apa Itu Console Daemon Manager?](#-apa-itu-console-daemon-manager)
- [Kenapa Pakai Ini?](#-kenapa-pakai-ini)
- [Fitur Utama](#-fitur-utama)
- [Instalasi](#-instalasi)
- [Cara Pakai — Panduan Bergambar](#-cara-pakai--panduan-bergambar)
  - [1. Menjalankan Aplikasi](#1-menjalankan-aplikasi)
  - [2. Menambah Task Baru](#2-menambah-task-baru)
  - [3. Menjalankan Task](#3-menjalankan-task)
  - [4. Melihat Output](#4-melihat-output)
  - [5. Mengelola Semua Task](#5-mengelola-semua-task)
  - [6. Mengedit Konfigurasi Task](#6-mengedit-konfigurasi-task)
  - [7. Mengatur Urutan Tab](#7-mengatur-urutan-tab)
  - [8. Menutup Tab vs Menghapus Task](#8-menutup-tab-vs-menghapus-task)
- [Penjelasan Field Konfigurasi](#-penjelasan-field-konfigurasi)
- [Pola Penggunaan Umum](#-pola-penggunaan-umum)
- [Contoh Penggunaan di Script PHP](#-contoh-penggunaan-di-script-php)
- [Build Executable (.exe)](#-build-executable-exe)
- [Struktur Project](#-struktur-project)
- [Troubleshooting](#-troubleshooting)
- [FAQ](#-faq)
- [Lisensi](#-lisensi)

---

## 🎯 Apa Itu Console Daemon Manager?

Console Daemon Manager adalah aplikasi desktop yang menjalankan **task-task terjadwal** — sama seperti **cron job** di Linux atau **Task Scheduler** di Windows — tapi dengan pengalaman yang jauh lebih nyaman:

- Setiap task punya **console sendiri** (tab terpisah)
- **Output real-time** streaming ke layar
- Konfigurasi via **form GUI**, tersimpan otomatis
- **Restart otomatis** kalau request gagal
- **Multi-task dalam 1 aplikasi**

Cocok untuk:

- 🔄 Hit API internal secara berkala
- 📊 Jalankan script PHP laporan ke Google Sheets
- 🩺 Monitoring health endpoint
- ⚙️ Trigger worker / job queue
- 📥 Sinkronisasi data antar sistem
- 🕐 Apapun yang butuh "dipanggil berkala"

---

## 💡 Kenapa Pakai Ini?

| Aspek | Cron Biasa | Console Daemon Manager |
|---|---|---|
| **Output** | Hilang / ke email | Real-time di console, bisa scroll |
| **Multi-task** | Banyak baris di crontab | Multi tab dalam 1 aplikasi |
| **Debug** | Susah, harus cek log | Error tampil merah jelas |
| **Konfigurasi** | Edit file crontab | Form GUI + JSON |
| **Interval** | Syntax cron rumit | Isi angka detik |
| **Range tanggal** | Harus script sendiri | Otomatis, update tiap ganti hari |
| **Paginasi** | Harus coding loop | Centang, langsung jalan |
| **Distribusi** | Setup di tiap server | Copy .exe, double-click |

---

## ✨ Fitur Utama

### 🖥️ Multi Console dalam Tab
Setiap task punya tab sendiri dengan output terpisah. Bisa dijalankan paralel.

### ➕ Add / Edit / Remove via Form
Tidak perlu edit file konfigurasi manual. Klik tombol, isi form, selesai.

### ▶️ Start / Stop / Restart
Kontrol per task atau massal (Start All / Stop All / Restart All).

### 💾 Auto-Save Config
Semua task tersimpan di `consoles.json` di folder yang sama dengan aplikasi.

### 🔄 Auto-Load
Saat aplikasi dibuka lagi, semua task otomatis dimuat dengan pengaturan terakhir.

### 📅 Range Tanggal Dinamis
Kalau task pakai range tanggal (mis. 30 hari terakhir), tanggal otomatis 
di-update ketika hari berganti — tidak perlu restart aplikasi.

### 📄 Paginasi Opsional
Untuk API multi-halaman, centang "Gunakan paginasi" — engine akan loop 
`page=1, 2, 3, ...` sampai data habis.

### 🎯 Single-Shot Mode
Untuk task yang cuma butuh 1 request per siklus (mis. cron biasa), 
uncheck "Gunakan paginasi".

### 🔗 Extra Params Fleksibel
- **Path Params** — tambah segmen URL (mis. `1/false` → `/endpoint/1/false`)
- **Query String** — tambah query mentah (mis. `role=admin&update=false`)

### 🌐 URL Preview Real-Time
Di bawah console ada baris `🔗 URL:` yang menampilkan URL asli yang sedang 
di-hit. Berubah otomatis saat task jalan.

### ⏱️ Interval Configurable
Atur jeda antar eksekusi dalam detik (mis. 300 = 5 menit, 3600 = 1 jam).

### 🛡️ Auto-Restart saat Error
Kalau request gagal (server down, network error), task otomatis retry.

### 🖱️ Drag Tab untuk Reorder
Ubah urutan tab dengan drag. Urutan tersimpan permanen.

---

## 📦 Instalasi

### Prasyarat

- Python **3.9 atau lebih baru**
- `pip` (biasanya sudah include)
- (Opsional) PHP 7.4+ kalau mau menjalankan script PHP

### Langkah Install

**1. Clone atau download project ini**

```bash
git clone https://github.com/jodichandra/console-daemon-manager.git
cd console-daemon-manager
```

Atau download ZIP dari GitHub dan extract.

**2. Install dependency Python**

```bash
pip install PyQt5 requests charset_normalizer certifi
```

Atau kalau pakai virtual environment (recommended):

```bash
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Linux/Mac
pip install PyQt5 requests charset_normalizer certifi
```

**3. Jalankan aplikasi**

```bash
python main.py
```

Aplikasi akan terbuka dengan window kosong (belum ada task).

---

## 🚀 Cara Pakai — Panduan Bergambar

### 1. Menjalankan Aplikasi

```bash
python main.py
```

Anda akan melihat window dengan **toolbar** di atas dan **area tab kosong** di tengah:

```
┌────────────────────────────────────────────────────────────────────┐
│  ➕ Add Console  📋 List Console  │  ▶ Start All  ⏹ Stop All  🔄 Restart All  │  🗑 Deactivate Current  │
├────────────────────────────────────────────────────────────────────┤
│                                                                    │
│                                                                    │
│                  (belum ada tab — tambah task dulu)                │
│                                                                    │
│                                                                    │
├────────────────────────────────────────────────────────────────────┤
│  Total config: 0  |  Tab aktif: 0  |  Running: 0  |  Config: ...  │
└────────────────────────────────────────────────────────────────────┘
```

### 2. Menambah Task Baru

Klik tombol **➕ Add Console** di toolbar. Dialog konfigurasi akan muncul:

```
┌────────────── Konfigurasi Console ──────────────┐
│                                                 │
│  Nama Console *  [Sync Encounter_____________]  │
│                                                 │
│  Base URL        [https://api.example.com___]   │
│                                                 │
│  Endpoint        [bulk/syncEncounter________]   │
│                                                 │
│  ── Extra Parameters (opsional) ──              │
│                                                 │
│  Extra Params (Path)  [____________________]    │
│                                                 │
│  Extra Query String   [____________________]    │
│                                                 │
│  💡 Extra Params (Path) = segmen URL...         │
│                                                 │
│  ── Parameter yang dikirim ke URL ──            │
│                                                 │
│  ☑ Gunakan range tanggal                       │
│      Range (hari ke belakang)  [30__] hari      │
│                                                 │
│  ☑ Gunakan limit per page                      │
│      Per Page  [100_]                           │
│                                                 │
│  ☑ Gunakan paginasi (loop page 1, 2, 3, ...)   │
│                                                 │
│  Sleep saat data habis  [1800_] detik           │
│                                                 │
│                          [  OK  ]  [ Cancel ]   │
└─────────────────────────────────────────────────┘
```

**Field yang wajib diisi:**

| Field | Keterangan |
|---|---|
| **Nama Console** | Nama unik task. Bebas, mis. `Sync Encounter`, `Refresh Cache` |
| **Base URL** | URL host/root, mis. `https://api.example.com` |
| **Endpoint** | Path setelah base, mis. `bulk/sync` |

> 💡 **Base URL** dan **Endpoint** boleh salah satu dikosongkan (tapi tidak dua-duanya). Misalnya:
> - Base URL: `https://api.example.com/health` + Endpoint: *(kosong)*
> - Base URL: *(kosong)* + Endpoint: `https://api.example.com/full/path`

Klik **OK** → tab baru muncul dengan nama task.

### 3. Menjalankan Task

Setiap tab console punya toolbar sendiri:

```
┌────────────────────────────────────────────────────────────────────┐
│  ⚙ Sync Encounter  range=30h | per_page=100 | sleep=1800s           │
│                                              [⏹ Stopped]            │
│                              [▶ Start] [⏹ Stop] [🔄 Restart] [🧹 Clear] │
├────────────────────────────────────────────────────────────────────┤
│                                                                    │
│  (output akan muncul di sini saat task dijalankan)                 │
│                                                                    │
├────────────────────────────────────────────────────────────────────┤
│  🔗 URL: https://api.example.com/bulk/syncEncounter?start_date=... │
│                                                          [📋 Copy] │
└────────────────────────────────────────────────────────────────────┘
```

Klik **▶ Start** untuk mulai. Status berubah jadi **▶ Running** (hijau), 
dan engine mulai hit URL secara berkala.

### 4. Melihat Output

Output dari server akan streaming real-time ke console:

```
[2026-10-02 10:15:32] [SYSTEM] === SYNC ENCOUNTER DAEMON START ===
[2026-10-02 10:15:32] [SYSTEM] Range tanggal diperbarui: 2026-09-02 s/d 2026-10-02
[2026-10-02 10:15:32] --> Proses page 1
[2026-10-02 10:15:33] [SYNC] Start syncing 100 encounters...
[2026-10-02 10:15:34] [SYNC] Patient ID 01234567 → success
[2026-10-02 10:15:34] [SYNC] Patient ID 01234568 → success
...
[2026-10-02 10:15:45] Total data  : 100
[2026-10-02 10:15:46] --> Proses page 2
[2026-10-02 10:15:47] [SYNC] Start syncing 45 encounters...
...
[2026-10-02 10:16:00] Page terakhir (total=45 < per_page=100)
[2026-10-02 10:16:00] Siklus selesai. Tidur 1800 detik...
```

**Warna output:**

| Warna | Arti |
|---|---|
| 🟢 Hijau muda | `[SYSTEM]` — pesan dari engine |
| 🟡 Kuning | Info progres (`--> Proses page 1`) |
| 🔴 Merah | Error |
| ⚪ Putih | Output dari server |

### 5. Mengelola Semua Task

Klik **📋 List Console** di toolbar. Dialog muncul menampilkan semua task:

```
┌────────────────────── List Console ─────────────────────────┐
│  Centang untuk aktifkan console di tab.                     │
│  Gunakan ⬆ / ⬇ untuk atur urutan tab.                      │
├─────────────────────────────────────────────────────────────┤
│  ⬆ ⬇ ☑  #1  Sync Encounter                                  │
│          https://api.example.com/bulk/syncEncounter?...     │
│                              [✏ Edit]  [🗑 Delete]           │
├─────────────────────────────────────────────────────────────┤
│  ⬆ ⬇ ☑  #2  Refresh Cache                                   │
│          https://internal.example.com/cron/refresh.php      │
│                              [✏ Edit]  [🗑 Delete]           │
├─────────────────────────────────────────────────────────────┤
│  ⬆ ⬇ ☐  #3  Send to Spreadsheet                             │
│          https://internal.example.com/cron/sheet.php        │
│                              [✏ Edit]  [🗑 Delete]           │
├─────────────────────────────────────────────────────────────┤
│  [☑ Check All]  [☐ Uncheck All]                    [Tutup]  │
└─────────────────────────────────────────────────────────────┘
```

**Kegunaan:**

- **Checkbox** — centang = muncul tab-nya, uncheck = sembunyikan (task tidak dihapus)
- **⬆ / ⬇** — ubah urutan tab
- **✏ Edit** — ubah konfigurasi
- **🗑 Delete** — hapus permanen
- **Check All / Uncheck All** — bulk toggle

### 6. Mengedit Konfigurasi Task

**Cara 1** — dari List Console: klik **✏ Edit** pada task.

**Cara 2** — dari tab: klik kanan tab → **✏ Edit Config**.

**Cara 3** — dari tab: klik kanan tab → **📝 Rename Tab** untuk ganti nama saja.

⚠️ **Task harus dalam keadaan Stopped** sebelum bisa diedit. Kalau sedang 
running, akan ada peringatan.

### 7. Mengatur Urutan Tab

**Cara 1** — drag tab di main window:

```
[Encounter]  [Condition]  [Patient]
    ↑            ↑            ↑
    drag "Patient" ke kiri → [Patient]  [Encounter]  [Condition]
```

Urutan otomatis tersimpan.

**Cara 2** — buka **📋 List Console**, klik **⬆ / ⬇** pada task.

### 8. Menutup Tab vs Menghapus Task

⚠️ **Penting** — dua aksi ini berbeda:

| Aksi | Efek | Task masih ada? |
|---|---|---|
| **Klik X di tab** | Sembunyikan tab (set `enabled=false`) | ✅ Ya, bisa diaktifkan lagi dari List |
| **🗑 Delete di List Console** | Hapus permanen dari config | ❌ Tidak |

**Untuk memunculkan tab yang sudah di-close:**

1. Buka **📋 List Console**
2. Centang task tersebut
3. Klik **Tutup**
4. Tab akan muncul kembali

---

## 📋 Penjelasan Field Konfigurasi

### Nama Console
Nama unik task. Dipakai sebagai label tab. Tidak boleh sama dengan task lain.

### Base URL
Root URL, tanpa trailing slash. Contoh:
- `https://api.example.com`
- `http://192.168.1.100/simrs/api`

### Endpoint
Path setelah base URL. Boleh kosong kalau Base URL sudah URL lengkap.

### Extra Params (Path)
Segmen tambahan yang disisipkan **setelah endpoint**, sebelum query string.

**Contoh:**

| Isi Field | URL Akhir |
|---|---|
| `1/false` | `.../endpoint/1/false` |
| `dokter/aktif` | `.../endpoint/dokter/aktif` |
| *(kosong)* | `.../endpoint` |

Cocok untuk API yang pakai **path parameter** seperti `/sync/{userId}/{force}`.

### Extra Query String
Query string tambahan yang ditempel **setelah `?`**.

**Contoh:**

| Isi Field | URL Akhir |
|---|---|
| `role=admin` | `.../endpoint?role=admin` |
| `?role=admin&debug=false` | `.../endpoint?role=admin&debug=false` |
| *(kosong)* | `.../endpoint` |

Cocok untuk API yang pakai **query parameter** tambahan.

### ☑ Gunakan range tanggal
Kalau dicentang, engine akan mengirim `start_date` dan `end_date` 
otomatis berdasarkan **hari ini minus N hari**.

**Contoh** kalau hari ini `2026-10-02` dan range = `30`:
```
start_date=2026-09-02&end_date=2026-10-02
```

**Auto-update**: kalau aplikasi dibiarkan jalan sampai ganti hari, tanggal 
otomatis di-update. Tidak perlu restart.

### ☑ Gunakan limit per page
Kalau dicentang, engine akan mengirim `per_page=N` di query string.

### ☑ Gunakan paginasi
Kalau dicentang, engine akan **loop** `page=1, 2, 3, ...` sampai:
- Server membalas "Tidak ada data di page ini.", **atau**
- Total data di page ini < per_page

Kalau **tidak** dicentang → **single-shot mode**: hanya 1 request per siklus, 
tanpa parameter `page`. Cocok untuk:
- Script PHP yang tidak pakai paginasi
- Cron biasa (mis. refresh cache)
- Endpoint yang hanya butuh 1 hit

### Sleep saat data habis
Jeda (dalam detik) antar siklus. Contoh:
- `60` = 1 menit
- `300` = 5 menit
- `1800` = 30 menit
- `3600` = 1 jam

---

## 🎨 Pola Penggunaan Umum

### Pola 1 — Cron Sederhana (single-shot, tanpa parameter)

Hit satu URL tiap X detik, tidak ada parameter dinamis.

| Field | Nilai |
|---|---|
| Nama Console | `Refresh Cache` |
| Base URL | `https://internal.example.com` |
| Endpoint | `cron/refresh-cache.php` |
| ☐ Range tanggal | uncheck |
| ☐ Limit per page | uncheck |
| ☐ Paginasi | uncheck |
| Sleep | `300` |

**URL:** `https://internal.example.com/cron/refresh-cache.php`

---

### Pola 2 — API dengan Range Tanggal & Paginasi

Sync data 30 hari terakhir, per halaman 100.

| Field | Nilai |
|---|---|
| Nama Console | `Sync Encounter` |
| Base URL | `https://api.example.com` |
| Endpoint | `bulk/syncEncounter` |
| ☑ Range tanggal | 30 hari |
| ☑ Limit per page | 100 |
| ☑ Paginasi | aktif |
| Sleep | `1800` |

**URL page 1:** 
```
https://api.example.com/bulk/syncEncounter?start_date=2026-09-02&end_date=2026-10-02&per_page=100&page=1
```
**URL page 2:** `...&page=2` (otomatis)

---

### Pola 3 — API dengan Path Parameter

Endpoint butuh path param seperti `/sync/{userId}/{force}`.

| Field | Nilai |
|---|---|
| Nama Console | `Sync User 1` |
| Base URL | `https://api.example.com` |
| Endpoint | `sync` |
| Extra Params (Path) | `1/true` |
| Sleep | `600` |

**URL:** `https://api.example.com/sync/1/true`

---

### Pola 4 — API dengan Query Param Statis

Endpoint butuh query tambahan seperti `?role=admin`.

| Field | Nilai |
|---|---|
| Base URL | `https://api.example.com` |
| Endpoint | `sync` |
| Extra Query String | `role=admin&force=true` |
| Sleep | `600` |

**URL:** `https://api.example.com/sync?role=admin&force=true`

---

### Pola 5 — Kombinasi Semua

| Field | Nilai |
|---|---|
| Base URL | `https://api.example.com` |
| Endpoint | `sync` |
| Extra Params (Path) | `1/false` |
| Extra Query String | `role=admin` |
| ☑ Range tanggal | 7 hari |
| ☑ Limit per page | 50 |
| ☑ Paginasi | aktif |

**URL page 1:**
```
https://api.example.com/sync/1/false?start_date=2026-09-25&end_date=2026-10-02&per_page=50&page=1&role=admin
```

---

## 🐘 Contoh Penggunaan di Script PHP

Console Daemon Manager bisa memanggil script PHP via URL. Script PHP-mu 
tinggal baca parameter dari `$_GET`.

### Contoh 1 — Script PHP Sederhana (tanpa parameter)

**`cron/refresh-cache.php`**
```php
<?php
// Dipanggil berkala oleh Console Daemon Manager
// Setup: Base URL = https://internal.example.com
//        Endpoint = cron/refresh-cache.php
//        Semua opsi (range/limit/paginasi): uncheck

echo "[" . date('Y-m-d H:i:s') . "] Refresh cache dimulai\n";

// Lakukan apa saja di sini
$data = file_get_contents('https://internal.example.com/data-source');
file_put_contents('/tmp/cache.json', $data);

echo "Cache di-refresh, " . strlen($data) . " bytes\n";
echo "[" . date('Y-m-d H:i:s') . "] Selesai\n";
```

---

### Contoh 2 — PHP dengan Range Tanggal

Console Daemon Manager akan mengirim `start_date`, `end_date`, `per_page`, `page`.

**`cron/laporan.php`**
```php
<?php
// Baca parameter dari URL
$startDate = $_GET['start_date'] ?? date('Y-m-01');
$endDate   = $_GET['end_date']   ?? date('Y-m-d');
$page      = (int)($_GET['page']     ?? 1);
$perPage   = (int)($_GET['per_page'] ?? 100);
$offset    = ($page - 1) * $perPage;

echo "[{$startDate} s/d {$endDate}] page {$page}\n";

// Koneksi database
$conn = new mysqli('localhost', 'user', 'pass', 'dbname');

$stmt = $conn->prepare("
    SELECT * FROM transactions
    WHERE DATE(created_at) BETWEEN ? AND ?
    ORDER BY created_at ASC
    LIMIT ? OFFSET ?
");
$stmt->bind_param('ssii', $startDate, $endDate, $perPage, $offset);
$stmt->execute();
$result = $stmt->get_result();

$count = 0;
while ($row = $result->fetch_assoc()) {
    // Proses tiap baris di sini
    echo "Processed: {$row['id']}\n";
    $count++;
}

echo "Total data  : {$count}\n";      // ← Console Manager deteksi ini

if ($count === 0) {
    echo "Tidak ada data di page ini.\n";  // ← deteksi stop paginasi
}

$conn->close();
```

**Setup di Console Manager:**
- Base URL: `https://internal.example.com`
- Endpoint: `cron/laporan.php`
- ☑ Range tanggal: 30 hari
- ☑ Limit per page: 100
- ☑ Paginasi: aktif

---

### Contoh 3 — PHP dengan Path Parameter

Kalau Console Manager dikonfigurasi dengan path params (mis. `1/false`), 
URL jadi `.../sync/1/false`. PHP bisa tangkap via `PATH_INFO` atau rewrite.

**Opsi A — Pakai `PATH_INFO` (paling simpel)**

**`cron/sync.php`** diakses via `.../sync.php/1/false`:

```php
<?php
// URL: https://example.com/cron/sync.php/1/false
// Setup: Base URL = https://example.com
//        Endpoint = cron/sync.php
//        Extra Params (Path) = 1/false

$pathInfo = $_SERVER['PATH_INFO'] ?? '';  // hasil: "/1/false"
$parts = array_values(array_filter(explode('/', $pathInfo)));

$userId = $parts[0] ?? null;   // "1"
$force  = $parts[1] ?? null;   // "false"

echo "UserId: {$userId}, Force: {$force}\n";

if ($force === 'true') {
    echo "Force mode aktif — skip cache\n";
}

// Lakukan sinkronisasi...
```

**Opsi B — Pakai `.htaccess` (Apache)**

**`cron/.htaccess`**
```apache
RewriteEngine On
RewriteRule ^sync/([^/]+)/([^/]+)/?$ sync.php?userId=$1&force=$2 [L,QSA]
```

**`cron/sync.php`**
```php
<?php
$userId = $_GET['userId'] ?? null;
$force  = $_GET['force']  ?? null;

echo "UserId: {$userId}, Force: {$force}\n";
```

Setup di Console Manager:
- Base URL: `https://example.com`
- Endpoint: `cron/sync` (atau `cron/sync.php` kalau tidak pakai rewrite)
- Extra Params (Path): `1/true`

---

### Contoh 4 — PHP Kirim ke Google Sheets (Single-Shot)

Script yang **sekali jalan** — cocok untuk cron biasa.

**`cron/laporan-sheet.php`**
```php
<?php
require __DIR__ . '/vendor/autoload.php';

use Google\Client;
use Google\Service\Sheets;

// Parameter opsional — bisa di-override via URL
$startDate = $_GET['start_date'] ?? date('Y-m-01');
$endDate   = $_GET['end_date']   ?? date('Y-m-d');

echo "Range: {$startDate} s/d {$endDate}\n";

// Koneksi DB
$conn = new mysqli('localhost', 'user', 'pass', 'dbname');
$result = $conn->query("
    SELECT * FROM reports
    WHERE DATE(created_at) BETWEEN '{$startDate}' AND '{$endDate}'
");

// Bangun data
$rows = [['No', 'Tanggal', 'Nilai']];
$i = 1;
while ($r = $result->fetch_assoc()) {
    $rows[] = [$i++, $r['created_at'], $r['value']];
}

// Kirim ke Google Sheets
$client = new Client();
$client->setAuthConfig(__DIR__ . '/credentials.json');
$client->addScope(Sheets::SPREADSHEETS);
$service = new Sheets($client);

$body = new Sheets\ValueRange(['values' => $rows]);
$service->spreadsheets_values->update(
    'SPREADSHEET_ID_HERE',
    'Sheet1!A1',
    $body,
    ['valueInputOption' => 'RAW']
);

echo "Data berhasil dikirim ke Google Spreadsheet.\n";
```

**Setup di Console Manager:**
- Base URL: `https://internal.example.com`
- Endpoint: `cron/laporan-sheet.php`
- ☐ Range tanggal (biar PHP yang atur default)
- ☐ Paginasi (single-shot)
- Sleep: `3600` (1 jam)

---

### Konvensi Deteksi Status (Opsional)

Kalau script-mu mau **kompatibel dengan engine paginasi**, cetak salah satu:

| Output dari script | Efek di engine |
|---|---|
| `Total data  : 42` | Engine tahu jumlah baris di page ini |
| `Tidak ada data di page ini.` | Engine stop paginasi |
| `Tidak ada data eligible` | Engine stop paginasi |

Kalau tidak ada, engine tetap lanjut ke page berikutnya sampai request gagal.

---

## 🛠️ Build Executable (.exe)

Kalau mau distribusikan tanpa perlu install Python:

### 1. Install PyInstaller

```bash
pip install pyinstaller
```

### 2. Build

```bash
python -m PyInstaller --onefile --noconsole --name "ConsoleDaemonManager" ^
    --collect-all PyQt5 ^
    --collect-all certifi ^
    main.py
```

> Windows CMD pakai `^` untuk line continuation. Kalau pakai PowerShell, 
> tulis dalam 1 baris atau pakai backtick.

### 3. Hasil

- `dist/ConsoleDaemonManager.exe` — file tunggal (~45 MB)
- Copy ke mana saja, double-click → jalan

### 4. Letak `consoles.json`

Saat `.exe` dijalankan, file `consoles.json` akan dibuat **di folder yang 
sama dengan `.exe`**. Jadi taruh `.exe` di folder yang bisa ditulis (bukan 
`C:\Program Files\`).

### 5. Troubleshooting Build

| Error | Solusi |
|---|---|
| `Qt platform plugin "windows"` | Tambah `--collect-all PyQt5` |
| `No module named 'requests'` | Tambah `--hidden-import=requests` |
| SSL error di HTTPS | Tambah `--collect-all certifi` |
| `.exe` langsung close | Build versi debug (tanpa `--noconsole`), jalankan dari CMD untuk lihat error |

---

## 📁 Struktur Project

```
ConsoleDaemonManager/
├── main.py                    # Aplikasi utama
├── consoles.json              # Config (auto-generated, tidak di-commit)
├── consoles.example.json      # Contoh config (di-commit)
├── README.md                  # File ini
├── .gitignore                 # File yang diabaikan Git
└── (script PHP/Python-mu)     # Task yang dipanggil via URL
```

### File `.gitignore` yang Direkomendasikan

```
# Python
__pycache__/
*.py[cod]
*.egg-info/
build/
dist/
*.spec

# Virtual env
venv/
env/
.venv/

# IDE
.vscode/
.idea/

# Config pribadi
consoles.json

# Kredensial
config.php
*.pem
*.key
credentials.json
*-credentials.json
.env
```

---

## 🔧 Troubleshooting

### Q: Aplikasi tidak mau jalan — `ModuleNotFoundError: No module named 'PyQt5'`

Install dependency:
```bash
pip install PyQt5 requests charset_normalizer certifi
```

### Q: Warning `RequestsDependencyWarning: Unable to find acceptable character detection dependency`

Install `charset_normalizer`:
```bash
pip install charset_normalizer
```

Kalau error `DLL load failed` di Windows karena **Smart App Control**:
1. Buka **Settings** → **Privacy & security** → **Windows Security** → 
   **App & browser control** → **Smart App Control settings**
2. Set ke **Off**
3. Restart komputer

### Q: Task tidak muncul di tab setelah dibuka dari List Console

Cek di **📋 List Console** — pastikan checkbox-nya ✅ dicentang. Kalau tidak, 
centang lalu Tutup.

### Q: Output sudah numpuk banyak, mau bersihkan

Klik **🧹 Clear** di toolbar tab, atau klik kanan tab → **🧹 Clear Output**.

### Q: Task running, tapi tidak ada output selama berjam-jam

Normal — task mungkin sedang menunggu interval (`sleep`). Cek log terakhir 
untuk memastikan statusnya. Kalau memang stuck, klik **⏹ Stop** lalu 
**▶ Start** ulang.

### Q: Bagaimana kalau server down?

Engine akan menampilkan error merah dan tetap mencoba ulang sesuai interval. 
Tidak perlu intervensi manual.

### Q: Config `consoles.json` rusak — aplikasi tidak bisa dibuka

Hapus atau rename `consoles.json`, aplikasi akan start dengan config kosong. 
Kamu akan perlu input ulang task-task-nya.

### Q: Bagaimana cara backup konfigurasi?

Cukup copy file `consoles.json`. Semua task & pengaturan ada di situ.

### Q: Bisa jalan tanpa GUI (headless)?

Tidak — aplikasi ini GUI-based. Untuk headless, pakai cron biasa.

---

## ❓ FAQ

**Q: Beda dengan cron biasa?**  
A: Cron lebih cocok untuk server production tanpa UI. Console Daemon Manager 
cocok untuk **desktop monitoring** dengan visual output & kontrol GUI.

**Q: Bisa handle HTTPS dengan self-signed certificate?**  
A: Belum — engine pakai `verify=True` default. Kalau butuh, tambahkan opsi 
`verify=False` di `DaemonEngine._process_page()`.

**Q: Bisa kirim POST, bukan GET?**  
A: Saat ini hanya GET. Kalau butuh POST, tambahkan field `method` + `body` 
di dialog dan engine.

**Q: Berapa banyak task yang bisa dijalankan sekaligus?**  
A: Tidak ada batas keras. Tapi karena tiap task pakai 1 thread, jangan 
berlebihan (rekomendasi: ≤ 20 task).

**Q: Kalau PC restart, task auto-start lagi?**  
A: Tidak — kamu perlu klik **▶ Start All** lagi setelah buka aplikasi. 
Kalau butuh auto-start, tambahkan aplikasi ini ke **Startup** Windows 
atau buat Windows Task Scheduler yang launch aplikasi ini.

**Q: Bisa dijalankan di Linux/Mac?**  
A: Ya, kode Python-nya cross-platform. Build `.exe` hanya untuk Windows; 
di Linux/Mac tinggal jalankan `python main.py`.

**Q: Data output disimpan ke file?**  
A: Belum — output hanya ada di memory (max 5000 baris per console). 
Kalau butuh logging ke file, tambahkan handler di `ConsoleWidget._append()`.

**Q: Kalau 2 task hit URL yang sama, apa yang terjadi?**  
A: Keduanya jalan paralel. Server akan menerima 2 request. Kalau server 
tidak siap, bisa jadi race condition — biasanya tidak masalah untuk 
endpoint cron.

**Q: Ada REST API-nya?**  
A: Tidak — ini aplikasi desktop, bukan service. Kalau butuh API, 
jalankan saja task-nya pakai cron di server.

---

## 🤝 Kontribusi

Pull request dan issue sangat welcome. Untuk perubahan besar, buka issue 
dulu untuk diskusi.

### Setup Development

```bash
git clone https://github.com/jodichandra/console-daemon-manager.git
cd console-daemon-manager
python -m venv venv
venv\Scripts\activate
pip install PyQt5 requests charset_normalizer certifi
python main.py
```

### Struktur Kode

- `DaemonEngine` — engine generik (HTTP client, date handling, paginasi)
- `DaemonWorker` — QThread wrapper untuk engine
- `ConsoleWidget` — UI per tab (output, URL preview, tombol start/stop)
- `ConsoleConfigDialog` — form add/edit task
- `ConsoleListDialog` — dialog list semua task
- `MainWindow` — window utama (toolbar, tabs, config management)

---

## 📄 Lisensi

MIT License — bebas dipakai, dimodifikasi, dan didistribusikan.

```
Copyright (c) 2026 jodichandra

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND.
```

---

<div align="center">

**Dibuat dengan ❤️ untuk mempermudah pekerjaan yang berulang.**

[⬆ Kembali ke atas](#-console-daemon-manager)

</div>