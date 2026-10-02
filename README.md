<div align="center">

# 🖥️ Console Daemon Manager

**Jalankan banyak task terjadwal (seperti cron job) dengan console terpisah per task — output real-time, konfigurasi GUI, tanpa edit file manual.**

[![Python](https://img.shields.io/badge/Python-3.9%2B-blue.svg)](https://www.python.org/)
[![PyQt5](https://img.shields.io/badge/PyQt5-5.15%2B-green.svg)](https://pypi.org/project/PyQt5/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

</div>

---

## 🎯 Kegunaan

Aplikasi desktop untuk menjalankan **task terjadwal** — sama seperti cron job 
— tapi dengan pengalaman GUI yang nyaman:

- Setiap task punya **console sendiri** (tab terpisah)
- **Output real-time** streaming ke layar
- Konfigurasi via **form**, tersimpan otomatis
- **Auto-restart** kalau request gagal
- **Multi-task** dalam 1 aplikasi

Cocok untuk:

- 🔄 Hit API internal secara berkala
- 📊 Jalankan script PHP laporan ke Google Sheets
- 🩺 Monitoring health endpoint
- ⚙️ Trigger worker / job queue
- 📥 Sinkronisasi data antar sistem
- 🕐 Apapun yang butuh "dipanggil berkala"

| Aspek | Cron Biasa | Console Daemon Manager |
|---|---|---|
| Output | Hilang / ke email | Real-time di console |
| Multi-task | Banyak baris crontab | Multi tab 1 aplikasi |
| Debug | Cek log manual | Error tampil merah |
| Konfigurasi | Edit crontab | Form GUI |
| Range tanggal | Script sendiri | Otomatis, update tiap ganti hari |
| Paginasi | Coding loop | Centang, langsung jalan |
| Distribusi | Setup server | Copy .exe, double-click |

---

## 📦 Requirement

- **Python 3.9+** dan `pip`
- (Opsional) **PHP 7.4+** kalau mau menjalankan script PHP

Install dependency:

```bash
pip install PyQt5 requests charset_normalizer certifi
```

---

## 🚀 Cara Pakai

### 1. Jalankan Aplikasi

```bash
python main.py
```

Window terbuka dengan toolbar di atas dan area tab kosong.

### 2. Tambah Task

Klik **➕ Add Console**, isi form:

| Field | Wajib | Keterangan |
|---|---|---|
| **Nama Console** | ✅ | Nama unik task, mis. `Sync Encounter` |
| **Base URL** | ⚠️ | Host/root, mis. `https://api.example.com` |
| **Endpoint** | ⚠️ | Path setelah base, mis. `bulk/sync` |
| Extra Params (Path) | ❌ | Segmen URL, mis. `1/false` → `/endpoint/1/false` |
| Extra Query String | ❌ | Query tambahan, mis. `role=admin` |
| ☑ Range tanggal | ❌ | Kirim `start_date` & `end_date` otomatis |
| ☑ Limit per page | ❌ | Kirim `per_page=N` |
| ☑ Paginasi | ❌ | Loop `page=1,2,3...` sampai data habis |
| Sleep | ❌ | Jeda antar siklus (detik) |

> ⚠️ **Base URL** dan **Endpoint** boleh salah satu kosong, tapi tidak dua-duanya.

### 3. Jalankan Task

Di tab console, klik **▶ Start**. Status jadi **▶ Running** (hijau), engine 
mulai hit URL berkala.

Tombol lain: **⏹ Stop**, **🔄 Restart**, **🧹 Clear**.

### 4. Lihat Output

Output streaming real-time ke console:

```
[2026-10-02 10:15:32] [SYSTEM] === SYNC ENCOUNTER DAEMON START ===
[2026-10-02 10:15:32] [SYSTEM] Range tanggal diperbarui: 2026-09-02 s/d 2026-10-02
[2026-10-02 10:15:32] --> Proses page 1
[2026-10-02 10:15:45] Total data  : 100
[2026-10-02 10:15:46] --> Proses page 2
[2026-10-02 10:16:00] Page terakhir (total=45 < per_page=100)
[2026-10-02 10:16:00] Siklus selesai. Tidur 1800 detik...
```

URL asli yang sedang di-hit tampil di bawah console (`🔗 URL:`).

### 5. Kelola Task

Klik **📋 List Console** untuk:

- ✅ **Centang/uncheck** — aktifkan/nonaktifkan tab
- ⬆⬇ **Reorder** — atur urutan tab
- ✏️ **Edit** — ubah konfigurasi
- 🗑 **Delete** — hapus permanen

> 💡 **Klik X di tab** = sembunyikan (bisa diaktifkan lagi dari List).  
> **Delete di List** = hapus permanen.

### 6. Atur Urutan Tab

Drag tab di main window **atau** klik ⬆⬇ di List Console. Urutan tersimpan.

---

## 📋 Pola Penggunaan

### Pola 1 — Cron Sederhana (1 request per siklus)

| Field | Nilai |
|---|---|
| Base URL | `https://internal.example.com` |
| Endpoint | `cron/refresh-cache.php` |
| Range/limit/paginasi | ☐ uncheck semua |
| Sleep | `300` |

**URL:** `https://internal.example.com/cron/refresh-cache.php`

---

### Pola 2 — API dengan Range Tanggal & Paginasi

| Field | Nilai |
|---|---|
| Base URL | `https://api.example.com` |
| Endpoint | `bulk/syncEncounter` |
| ☑ Range tanggal | 30 hari |
| ☑ Limit per page | 100 |
| ☑ Paginasi | aktif |
| Sleep | `1800` |

**URL page 1:** `...bulk/syncEncounter?start_date=2026-09-02&end_date=2026-10-02&per_page=100&page=1`

---

### Pola 3 — API dengan Path Parameter

| Field | Nilai |
|---|---|
| Base URL | `https://api.example.com` |
| Endpoint | `sync` |
| Extra Params (Path) | `1/true` |

**URL:** `https://api.example.com/sync/1/true`

---

### Pola 4 — API dengan Query Tambahan

| Field | Nilai |
|---|---|
| Base URL | `https://api.example.com` |
| Endpoint | `sync` |
| Extra Query String | `role=admin&force=true` |

**URL:** `https://api.example.com/sync?role=admin&force=true`

---

### Pola 5 — Kombinasi

**URL:**
```
https://api.example.com/sync/1/false?start_date=2026-09-25&end_date=2026-10-02&per_page=50&page=1&role=admin
```

---

## 🐘 Contoh Script PHP

### Contoh 1 — Script Sederhana (Tanpa Parameter)

**`cron/refresh-cache.php`**
```php
<?php
echo "[" . date('Y-m-d H:i:s') . "] Refresh cache dimulai\n";

$data = file_get_contents('https://internal.example.com/data-source');
file_put_contents('/tmp/cache.json', $data);

echo "Cache di-refresh, " . strlen($data) . " bytes\n";
```

**Setup:** Base URL `https://internal.example.com`, Endpoint `cron/refresh-cache.php`, semua opsi uncheck, Sleep `300`.

---

### Contoh 2 — PHP dengan Range Tanggal

**`cron/laporan.php`**
```php
<?php
$startDate = $_GET['start_date'] ?? date('Y-m-01');
$endDate   = $_GET['end_date']   ?? date('Y-m-d');
$page      = (int)($_GET['page']     ?? 1);
$perPage   = (int)($_GET['per_page'] ?? 100);
$offset    = ($page - 1) * $perPage;

echo "[{$startDate} s/d {$endDate}] page {$page}\n";

$conn = new mysqli('localhost', 'user', 'pass', 'dbname');
$stmt = $conn->prepare("
    SELECT * FROM transactions
    WHERE DATE(created_at) BETWEEN ? AND ?
    ORDER BY created_at ASC LIMIT ? OFFSET ?
");
$stmt->bind_param('ssii', $startDate, $endDate, $perPage, $offset);
$stmt->execute();
$result = $stmt->get_result();

$count = 0;
while ($row = $result->fetch_assoc()) {
    echo "Processed: {$row['id']}\n";
    $count++;
}

echo "Total data  : {$count}\n";

if ($count === 0) {
    echo "Tidak ada data di page ini.\n";
}
```

**Setup:** ☑ Range tanggal 30 hari, ☑ Limit per page 100, ☑ Paginasi aktif.

---

### Contoh 3 — PHP dengan Path Parameter

**`cron/sync.php`** (via `.../sync.php/1/false`):
```php
<?php
$pathInfo = $_SERVER['PATH_INFO'] ?? '';
$parts = array_values(array_filter(explode('/', $pathInfo)));

$userId = $parts[0] ?? null;
$force  = $parts[1] ?? null;

echo "UserId: {$userId}, Force: {$force}\n";
```

**Setup:** Extra Params (Path) = `1/false`.

---

### Contoh 4 — PHP ke Google Sheets (Single-Shot)

**`cron/laporan-sheet.php`**
```php
<?php
require __DIR__ . '/vendor/autoload.php';
use Google\Client;
use Google\Service\Sheets;

$startDate = $_GET['start_date'] ?? date('Y-m-01');
$endDate   = $_GET['end_date']   ?? date('Y-m-d');

echo "Range: {$startDate} s/d {$endDate}\n";

$conn = new mysqli('localhost', 'user', 'pass', 'dbname');
$result = $conn->query("
    SELECT * FROM reports
    WHERE DATE(created_at) BETWEEN '{$startDate}' AND '{$endDate}'
");

$rows = [['No', 'Tanggal', 'Nilai']];
$i = 1;
while ($r = $result->fetch_assoc()) {
    $rows[] = [$i++, $r['created_at'], $r['value']];
}

$client = new Client();
$client->setAuthConfig(__DIR__ . '/credentials.json');
$client->addScope(Sheets::SPREADSHEETS);
$service = new Sheets($client);

$body = new Sheets\ValueRange(['values' => $rows]);
$service->spreadsheets_values->update(
    'SPREADSHEET_ID_HERE', 'Sheet1!A1', $body,
    ['valueInputOption' => 'RAW']
);

echo "Data berhasil dikirim ke Google Spreadsheet.\n";
```

**Setup:** Semua opsi uncheck (single-shot), Sleep `3600`.

---

### Konvensi Deteksi Status

Kalau script PHP ingin kompatibel dengan engine paginasi, cetak salah satu:

| Output dari script | Efek |
|---|---|
| `Total data  : 42` | Engine tahu jumlah baris page ini |
| `Tidak ada data di page ini.` | Engine stop paginasi |

---

## 🛠️ Build Executable

```bash
pip install pyinstaller
python -m PyInstaller --onefile --noconsole --name "ConsoleDaemonManager" --collect-all PyQt5 --collect-all certifi main.py
```

Hasil: `dist/ConsoleDaemonManager.exe` (~45 MB).

`consoles.json` akan dibuat otomatis di folder yang sama dengan `.exe`.

---

## 🔧 Troubleshooting

| Masalah | Solusi |
|---|---|
| `No module named 'PyQt5'` | `pip install PyQt5 requests charset_normalizer certifi` |
| Warning `chardet` / `charset_normalizer` | `pip install charset_normalizer` |
| `DLL load failed` di Windows | Matikan **Smart App Control** di Settings → Windows Security |
| Task tidak muncul di tab | Buka List Console, centang task-nya |
| Config rusak | Hapus/rename `consoles.json`, input ulang |

---

## ❓ FAQ

**Beda dengan cron biasa?**  
Cron untuk server production tanpa UI. Console Daemon Manager untuk desktop 
monitoring dengan visual output & kontrol GUI.

**Bisa dijalankan di Linux/Mac?**  
Ya — kode Python cross-platform. `.exe` hanya untuk Windows.

**Kalau PC restart, task auto-start?**  
Tidak — perlu klik **▶ Start All** lagi. Bisa ditambahkan ke Windows Startup 
kalau butuh.

**Bisa POST?**  
Belum — hanya GET. Tambahkan field `method` + `body` kalau butuh.

**Output disimpan ke file?**  
Belum — hanya di memory (max 5000 baris per console).

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