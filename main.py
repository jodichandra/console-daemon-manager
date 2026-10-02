import sys
import os
import json
import time
import signal
import threading
from pathlib import Path
from datetime import date, timedelta, datetime

import requests

from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt5.QtGui import QFont, QColor, QTextCursor
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QTabWidget, QLabel, QDialog, QFormLayout,
    QLineEdit, QSpinBox, QCheckBox, QMessageBox, QDialogButtonBox,
    QToolBar, QAction, QPlainTextEdit, QMenu, QStatusBar, QInputDialog,
    QSizePolicy, QScrollArea, QFrame
)


# ============================================================
# HELPER
# ============================================================
def get_app_dir() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent
    return Path(__file__).parent


CONFIG_FILE = get_app_dir() / "consoles.json"
APP_TITLE   = "Console Manager - Daemon Runner"


# ============================================================
# HELPER: BANGUN URL UNTUK PREVIEW
# ============================================================
def build_preview_url(cfg: dict) -> str:
    """
    Bangun URL preview (untuk ditampilkan di bawah console).
    Hanya menampilkan parameter yang benar-benar aktif.
    """
    base = (cfg.get("base_url") or "").rstrip("/")
    endpoint = (cfg.get("endpoint") or "").strip("/")

    if base and endpoint:
        url = f"{base}/{endpoint}"
    elif base:
        url = base
    elif endpoint:
        url = endpoint
    else:
        return "(URL kosong)"

    # Path params
    pp = cfg.get("path_params")
    if pp:
        pp = str(pp).strip().strip("/")
        if pp:
            url += "/" + pp

    # Query params — hanya yang aktif
    params = []

    if cfg.get("use_range"):
        range_days = cfg.get("range_days") or 30
        today = date.today()
        start = (today - timedelta(days=range_days)).strftime("%Y-%m-%d")
        end = today.strftime("%Y-%m-%d")
        params.append(f"start_date={start}")
        params.append(f"end_date={end}")

    if cfg.get("use_per_page"):
        params.append(f"per_page={cfg.get('per_page') or 100}")

    if cfg.get("use_page", True):
        params.append("page=<n>")

    # Extra query
    eq = cfg.get("extra_query")
    if eq:
        eq = str(eq).strip().lstrip("?")
        if eq:
            params.append(eq)

    if params:
        url += "?" + "&".join(params)

    return url


# ============================================================
# ENGINE: GENERIC DAEMON
# ============================================================
class DaemonEngine:
    """
    Engine generik untuk semua jenis bulk daemon.
    """

    def __init__(self, config: dict, log_cb, stop_event: threading.Event,
                 url_cb=None):
        self.cfg = config
        self.log = log_cb
        self.stop_event = stop_event
        self.url_cb = url_cb

        self._cached_start_date = None
        self._cached_end_date = None
        self._cached_date_obj = None

    # -------------------- Logging helpers --------------------
    def _log(self, msg: str, color: str = "#d4d4d4"):
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.log(f"[{ts}] {msg}\n", color)

    def _log_system(self, msg: str):
        self._log(f"[SYSTEM] {msg}", "#4ec9b0")

    def _log_info(self, msg: str):
        self._log(msg, "#dcdcaa")

    def _log_error(self, msg: str):
        self._log(msg, "#f48771")

    # -------------------- Date handling --------------------
    def _get_date_range(self):
        if not self.cfg.get("use_range"):
            return None, None

        today = date.today()
        range_days = self.cfg.get("range_days") or 30

        if self._cached_date_obj != today:
            self._cached_date_obj = today
            self._cached_start_date = (
                today - timedelta(days=range_days)
            ).strftime("%Y-%m-%d")
            self._cached_end_date = today.strftime("%Y-%m-%d")

            self._log_system(
                f"Range tanggal diperbarui: "
                f"{self._cached_start_date} s/d {self._cached_end_date}"
            )

            if self.url_cb:
                try:
                    self.url_cb(self.build_current_url())
                except Exception:
                    pass

        return self._cached_start_date, self._cached_end_date

    # -------------------- URL & query builder --------------------
    def _build_url(self) -> str:
        """
        Bangun base URL. Mendukung base_url atau endpoint kosong.
        """
        base = (self.cfg.get("base_url") or "").rstrip("/")
        endpoint = (self.cfg.get("endpoint") or "").strip("/")

        if base and endpoint:
            url = f"{base}/{endpoint}"
        elif base:
            url = base
        elif endpoint:
            url = endpoint
        else:
            url = ""

        pp = self.cfg.get("path_params")
        if pp and isinstance(pp, str):
            pp = pp.strip().strip("/")
            if pp:
                if url:
                    url += "/" + pp
                else:
                    url = pp

        return url

    def _apply_extra_query(self, params: dict) -> dict:
        extra_q = self.cfg.get("extra_query")
        if extra_q and isinstance(extra_q, str):
            q = extra_q.strip()
            if q.startswith("?"):
                q = q[1:]
            if q:
                for pair in q.split("&"):
                    if not pair:
                        continue
                    if "=" in pair:
                        k, v = pair.split("=", 1)
                        params[k.strip()] = v.strip()
                    else:
                        params[pair.strip()] = ""
        return params

    def _build_query(self, page=None) -> dict:
        params = {}
        start, end = self._get_date_range()

        if start:
            params["start_date"] = start
        if end:
            params["end_date"] = end

        if self.cfg.get("use_per_page"):
            params["per_page"] = self.cfg.get("per_page") or 100

        # Kirim parameter page hanya kalau use_page aktif
        if page is not None and self.cfg.get("use_page", True):
            params["page"] = page

        params = self._apply_extra_query(params)
        return params

    def build_current_url(self, page=None) -> str:
        url = self._build_url()
        params = self._build_query(page=page)

        ordered_keys = []
        for k in ("start_date", "end_date", "per_page"):
            if k in params:
                ordered_keys.append(k)
        for k in params:
            if k not in ordered_keys and k != "page":
                ordered_keys.append(k)
        if "page" in params:
            ordered_keys.append("page")

        if ordered_keys:
            qs = "&".join(
                f"{k}={params[k]}" for k in ordered_keys
                if params[k] is not None
            )
            if qs:
                url += "?" + qs

        return url

    # -------------------- HTTP helpers --------------------
    def _process_page(self, page):
        params = self._build_query(page=page)
        url = self._build_url()

        if not url:
            self._log_error("URL kosong. Cek Base URL / Endpoint.")
            return None

        timeout = self.cfg.get("request_timeout") or 3600

        is_empty = False
        total_data = None

        try:
            with requests.get(
                url, params=params, stream=True, timeout=timeout
            ) as r:
                r.raise_for_status()

                # Update URL real-time (URL asli yang sedang di-hit)
                if self.url_cb:
                    try:
                        self.url_cb(r.url)
                    except Exception:
                        pass

                for line in r.iter_lines(decode_unicode=True):
                    if self.stop_event.is_set():
                        return None

                    if line is None:
                        continue

                    self.log(line + "\n", "#d4d4d4")

                    low = line.lower()
                    if ("tidak ada data di page ini" in low
                            or "tidak ada data eligible" in low
                            or "tidak ada staff untuk designation ini" in low
                            or "tidak ada encounter di range tanggal ini" in low
                            or "tidak ada data patient untuk diproses" in low):
                        is_empty = True

                    if "Total data" in line and ":" in line:
                        try:
                            total_data = int(line.split(":")[1].strip())
                        except (ValueError, IndexError):
                            pass

            return {"is_empty": is_empty, "total_data": total_data}

        except requests.exceptions.RequestException as e:
            self._log_error(f"ERROR page {page}: {e}")
            return None

    # -------------------- Main loop --------------------
    def run_forever(self):
        cfg_name = self.cfg.get("name", "daemon")
        sleep_sec = self.cfg.get("sleep_seconds") or 1800
        per_page = self.cfg.get("per_page") or 100
        use_page = self.cfg.get("use_page", True)

        self._log_system(f"=== {cfg_name.upper()} DAEMON START ===")

        # Update URL preview di awal
        if self.url_cb:
            try:
                self.url_cb(self.build_current_url())
            except Exception:
                pass

        while not self.stop_event.is_set():
            try:
                if use_page:
                    # ===== MODE PAGINASI =====
                    page = 1
                    while not self.stop_event.is_set():
                        self._log_info(f"--> Proses page {page}")
                        hasil = self._process_page(page)

                        if self.stop_event.is_set():
                            break

                        if hasil is None:
                            self._log_error("Gagal ambil page, stop siklus ini.")
                            break

                        if hasil.get("is_empty"):
                            self._log_info("Page kosong, data habis.")
                            break

                        td = hasil.get("total_data")
                        if (td is not None and td < per_page and page > 1):
                            self._log_info(
                                f"Page terakhir (total={td} < per_page={per_page})."
                            )
                            break

                        page += 1
                        if not self._interruptible_sleep(1):
                            break
                else:
                    # ===== MODE SINGLE-SHOT =====
                    self._log_info("--> Request single-shot (tanpa paginasi)")
                    hasil = self._process_page(None)

                    if self.stop_event.is_set():
                        break

                    if hasil is None:
                        self._log_error("Gagal request, stop siklus ini.")

                if self.stop_event.is_set():
                    break

                self._log_info(f"Siklus selesai. Tidur {sleep_sec} detik...")
                self._interruptible_sleep(sleep_sec)

            except Exception as e:
                self._log_error(f"ERROR tak terduga: {e}. Tidur 60 detik...")
                self._interruptible_sleep(60)

        self._log_system("Daemon dihentikan.")

    def _interruptible_sleep(self, seconds: float) -> bool:
        elapsed = 0.0
        while elapsed < seconds:
            if self.stop_event.is_set():
                return False
            chunk = min(0.5, seconds - elapsed)
            time.sleep(chunk)
            elapsed += chunk
        return True


# ============================================================
# WORKER THREAD
# ============================================================
class DaemonWorker(QThread):
    log_signal = pyqtSignal(str, str)
    state_signal = pyqtSignal(str)
    url_signal = pyqtSignal(str)

    def __init__(self, config: dict, parent=None):
        super().__init__(parent)
        self.cfg = config
        self.stop_event = threading.Event()
        self.engine = None

    def run(self):
        self.state_signal.emit("running")
        self.engine = DaemonEngine(
            self.cfg,
            log_cb=lambda text, color: self.log_signal.emit(text, color),
            stop_event=self.stop_event,
            url_cb=lambda url: self.url_signal.emit(url),
        )
        try:
            self.engine.run_forever()
        except Exception as e:
            self.log_signal.emit(f"[FATAL] {e}\n", "#f48771")
        finally:
            self.state_signal.emit("stopped")

    def stop(self):
        self.stop_event.set()


# ============================================================
# DIALOG ADD / EDIT CONSOLE
# ============================================================
class ConsoleConfigDialog(QDialog):
    def __init__(self, parent=None, initial: dict | None = None):
        super().__init__(parent)
        self.setWindowTitle("Konfigurasi Console")
        self.setMinimumWidth(620)

        self.result_config = None
        self._initial = initial or {}

        self._build_ui()
        self._apply_style()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(8)

        # ---------- FIELD WAJIB ----------
        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignRight)

        self.inp_name = QLineEdit(self._initial.get("name", ""))
        self.inp_name.setPlaceholderText("Contoh: Encounter, Condition, Patient")
        form.addRow("Nama Console *", self.inp_name)

        self.inp_base_url = QLineEdit(self._initial.get("base_url", ""))
        self.inp_base_url.setPlaceholderText(
            "http://djamil.test/simrs/admin/ss/ipdEncounterBulk"
        )
        form.addRow("Base URL", self.inp_base_url)

        self.inp_endpoint = QLineEdit(self._initial.get("endpoint", ""))
        self.inp_endpoint.setPlaceholderText(
            "bulkSendEncounterAll   (boleh dikosongkan)"
        )
        form.addRow("Endpoint", self.inp_endpoint)

        layout.addLayout(form)

        # ---------- EXTRA PARAMS ----------
        lbl_extra = QLabel("── Extra Parameters (opsional) ──")
        lbl_extra.setStyleSheet(
            "color: #888; font-size: 11px; padding-top: 6px;"
        )
        layout.addWidget(lbl_extra)

        form_extra = QFormLayout()
        form_extra.setLabelAlignment(Qt.AlignRight)

        self.inp_path_params = QLineEdit(
            self._initial.get("path_params") or ""
        )
        self.inp_path_params.setPlaceholderText(
            "1/false   →  /bulkSendX/1/false"
        )
        form_extra.addRow("Extra Params (Path)", self.inp_path_params)

        self.inp_extra_query = QLineEdit(
            self._initial.get("extra_query") or ""
        )
        self.inp_extra_query.setPlaceholderText(
            "role=1&update=false   (boleh pakai ? atau tidak)"
        )
        form_extra.addRow("Extra Query String", self.inp_extra_query)

        layout.addLayout(form_extra)

        lbl_hint = QLabel(
            "💡 Extra Params (Path) = segmen URL setelah endpoint, "
            "contoh '1/false' → /endpoint/1/false. "
            "Extra Query String = query mentah, contoh 'role=1' → ?role=1."
        )
        lbl_hint.setWordWrap(True)
        lbl_hint.setStyleSheet("color: #666; font-size: 10px;")
        layout.addWidget(lbl_hint)

        # ---------- TOGGLE PARAMETER ----------
        lbl_toggle = QLabel("── Parameter yang dikirim ke URL ──")
        lbl_toggle.setStyleSheet(
            "color: #888; font-size: 11px; padding-top: 6px;"
        )
        layout.addWidget(lbl_toggle)

        # Range tanggal
        self.chk_use_range = QCheckBox("Gunakan range tanggal (start_date & end_date)")
        self.chk_use_range.setChecked(self._initial.get("use_range", True))
        self.chk_use_range.toggled.connect(self._on_use_range_toggle)
        layout.addWidget(self.chk_use_range)

        form2 = QFormLayout()
        form2.setLabelAlignment(Qt.AlignRight)

        self.inp_range_days = QSpinBox()
        self.inp_range_days.setRange(0, 3650)
        self.inp_range_days.setValue(self._initial.get("range_days") or 30)
        self.inp_range_days.setSuffix(" hari")
        form2.addRow("Range (hari ke belakang)", self.inp_range_days)

        layout.addLayout(form2)

        # Limit per page
        self.chk_use_per_page = QCheckBox("Gunakan limit per page (per_page)")
        self.chk_use_per_page.setChecked(
            self._initial.get("use_per_page", True)
        )
        self.chk_use_per_page.toggled.connect(self._on_use_per_page_toggle)
        layout.addWidget(self.chk_use_per_page)

        form3 = QFormLayout()
        form3.setLabelAlignment(Qt.AlignRight)

        self.inp_per_page = QSpinBox()
        self.inp_per_page.setRange(1, 10000)
        self.inp_per_page.setValue(self._initial.get("per_page") or 100)
        form3.addRow("Per Page", self.inp_per_page)

        layout.addLayout(form3)

        # Paginasi
        self.chk_use_page = QCheckBox(
            "Gunakan paginasi (loop page 1, 2, 3, ...) "
            "— uncheck untuk script single-shot"
        )
        self.chk_use_page.setChecked(self._initial.get("use_page", True))
        self.chk_use_page.setToolTip(
            "Kalau dicentang: engine akan request page=1, page=2, ... "
            "sampai data habis.\n"
            "Kalau tidak dicentang: hanya 1 request per siklus, "
            "tanpa parameter 'page' (cocok untuk script PHP single-shot "
            "seperti spreadsheet generator)."
        )
        layout.addWidget(self.chk_use_page)

        # ---------- SLEEP ----------
        form4 = QFormLayout()
        form4.setLabelAlignment(Qt.AlignRight)

        self.inp_sleep = QSpinBox()
        self.inp_sleep.setRange(1, 86400)
        self.inp_sleep.setValue(self._initial.get("sleep_seconds") or 1800)
        self.inp_sleep.setSuffix(" detik")
        form4.addRow("Sleep saat data habis", self.inp_sleep)

        layout.addLayout(form4)

        # ---------- BUTTONS ----------
        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        buttons.accepted.connect(self._on_ok)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self._on_use_range_toggle(self.chk_use_range.isChecked())
        self._on_use_per_page_toggle(self.chk_use_per_page.isChecked())

    def _on_use_range_toggle(self, checked: bool):
        self.inp_range_days.setEnabled(checked)

    def _on_use_per_page_toggle(self, checked: bool):
        self.inp_per_page.setEnabled(checked)

    def _apply_style(self):
        self.setStyleSheet("""
            QDialog { background: #2d2d30; }
            QLabel { color: #ddd; }
            QLineEdit, QSpinBox {
                background: #1e1e1e;
                color: #ddd;
                border: 1px solid #3f3f46;
                border-radius: 4px;
                padding: 6px;
                selection-background-color: #264f78;
            }
            QLineEdit:focus, QSpinBox:focus { border: 1px solid #007acc; }
            QCheckBox { color: #ddd; spacing: 8px; }
            QCheckBox::indicator {
                width: 16px; height: 16px;
                border: 1px solid #3f3f46;
                background: #1e1e1e;
                border-radius: 3px;
            }
            QCheckBox::indicator:checked {
                background: #007acc;
                border: 1px solid #007acc;
            }
            QPushButton {
                background: #3c3c3c;
                color: #ddd;
                border: 1px solid #555;
                border-radius: 4px;
                padding: 6px 16px;
                min-width: 80px;
            }
            QPushButton:hover { background: #4a4a4a; }
            QPushButton:default {
                background: #0e639c;
                border: 1px solid #1177bb;
            }
            QPushButton:default:hover { background: #1177bb; }
        """)

    def _on_ok(self):
        name = self.inp_name.text().strip()
        base_url = self.inp_base_url.text().strip()
        endpoint = self.inp_endpoint.text().strip()

        if not name:
            QMessageBox.warning(self, "Validasi", "Nama console wajib diisi.")
            return

        # Base URL & Endpoint boleh kosong salah satu, tapi tidak boleh dua-duanya
        if not base_url and not endpoint:
            QMessageBox.warning(
                self, "Validasi",
                "Base URL dan Endpoint tidak boleh kosong dua-duanya.\n"
                "Isi minimal salah satu."
            )
            return

        path_params = self.inp_path_params.text().strip()
        if path_params:
            path_params = path_params.strip("/")
        if not path_params:
            path_params = None

        extra_query = self.inp_extra_query.text().strip() or None
        if extra_query and extra_query.startswith("?"):
            extra_query = extra_query[1:]
        if extra_query == "":
            extra_query = None

        base_url = base_url.rstrip("/")

        cfg = {
            "name": name,
            "base_url": base_url,
            "endpoint": endpoint,
            "path_params": path_params,
            "extra_query": extra_query,
            "use_range": self.chk_use_range.isChecked(),
            "range_days": self.inp_range_days.value()
                          if self.chk_use_range.isChecked() else None,
            "use_per_page": self.chk_use_per_page.isChecked(),
            "per_page": self.inp_per_page.value()
                        if self.chk_use_per_page.isChecked() else None,
            "use_page": self.chk_use_page.isChecked(),
            "sleep_seconds": self.inp_sleep.value(),
            "enabled": self._initial.get("enabled", True),
        }

        self.result_config = cfg
        self.accept()


# ============================================================
# DIALOG LIST CONSOLE
# ============================================================
class ConsoleListDialog(QDialog):
    def __init__(self, parent, consoles: list):
        super().__init__(parent)
        self.setWindowTitle("List Console")
        self.setMinimumSize(880, 600)

        self.consoles = consoles
        self.changed = False

        self._build_ui()
        self._apply_style()
        self._populate()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(8)

        self.lbl_info = QLabel(
            "Centang untuk aktifkan console di tab. "
            "Gunakan ⬆ / ⬇ untuk atur urutan tab."
        )
        self.lbl_info.setStyleSheet("color: #aaa; font-size: 11px;")
        layout.addWidget(self.lbl_info)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QFrame.NoFrame)

        self.container = QWidget()
        self.container_layout = QVBoxLayout(self.container)
        self.container_layout.setContentsMargins(0, 0, 0, 0)
        self.container_layout.setSpacing(4)
        self.container_layout.addStretch()

        self.scroll.setWidget(self.container)
        layout.addWidget(self.scroll, 1)

        btn_layout = QHBoxLayout()

        self.btn_select_all = QPushButton("☑ Check All")
        self.btn_select_all.clicked.connect(lambda: self._set_all(True))
        btn_layout.addWidget(self.btn_select_all)

        self.btn_unselect_all = QPushButton("☐ Uncheck All")
        self.btn_unselect_all.clicked.connect(lambda: self._set_all(False))
        btn_layout.addWidget(self.btn_unselect_all)

        btn_layout.addStretch()

        self.btn_close = QPushButton("Tutup")
        self.btn_close.clicked.connect(self.accept)
        btn_layout.addWidget(self.btn_close)

        layout.addLayout(btn_layout)

    def _apply_style(self):
        self.setStyleSheet("""
            QDialog { background: #2d2d30; }
            QLabel { color: #ddd; }
            QScrollArea { background: #252526; }
            QWidget#row { background: #2d2d30; border: 1px solid #3f3f46;
                          border-radius: 4px; }
            QWidget#row:hover { background: #333336; }
            QCheckBox { color: #ddd; }
            QCheckBox::indicator {
                width: 18px; height: 18px;
                border: 1px solid #3f3f46;
                background: #1e1e1e;
                border-radius: 3px;
            }
            QCheckBox::indicator:checked {
                background: #007acc;
                border: 1px solid #007acc;
            }
            QPushButton {
                background: #3c3c3c;
                color: #ddd;
                border: 1px solid #555;
                border-radius: 4px;
                padding: 6px 12px;
            }
            QPushButton:hover { background: #4a4a4a; }
            QPushButton:disabled { color: #555; background: #2a2a2a; }
            QPushButton#btn_edit { background: #2d4a2d; border-color: #4a7a4a; }
            QPushButton#btn_edit:hover { background: #3a5f3a; }
            QPushButton#btn_delete { background: #5a2d2d; border-color: #7a4a4a; }
            QPushButton#btn_delete:hover { background: #6f3a3a; }
            QPushButton#btn_up, QPushButton#btn_down {
                min-width: 32px; max-width: 32px;
                padding: 6px 4px;
                font-weight: bold;
            }
        """)

    def _populate(self):
        while self.container_layout.count() > 1:
            item = self.container_layout.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()

        if not self.consoles:
            empty = QLabel("(belum ada console)")
            empty.setStyleSheet("color: #666; padding: 20px;")
            self.container_layout.insertWidget(0, empty)
            return

        for i, cfg in enumerate(self.consoles):
            row = self._make_row(i, cfg)
            self.container_layout.insertWidget(i, row)

    def _make_row(self, idx: int, cfg: dict) -> QWidget:
        row = QWidget()
        row.setObjectName("row")
        h = QHBoxLayout(row)
        h.setContentsMargins(10, 8, 10, 8)
        h.setSpacing(8)

        btn_up = QPushButton("⬆")
        btn_up.setObjectName("btn_up")
        btn_up.setToolTip("Naikkan urutan")
        btn_up.setEnabled(idx > 0)
        btn_up.clicked.connect(lambda _=False, i=idx: self._on_move_up(i))
        h.addWidget(btn_up)

        btn_down = QPushButton("⬇")
        btn_down.setObjectName("btn_down")
        btn_down.setToolTip("Turunkan urutan")
        btn_down.setEnabled(idx < len(self.consoles) - 1)
        btn_down.clicked.connect(lambda _=False, i=idx: self._on_move_down(i))
        h.addWidget(btn_down)

        chk = QCheckBox()
        chk.setChecked(bool(cfg.get("enabled", True)))
        chk.setToolTip("Centang untuk aktifkan tab console")
        chk.stateChanged.connect(
            lambda state, i=idx: self._on_check(i, state)
        )
        h.addWidget(chk)

        info = QVBoxLayout()
        info.setSpacing(2)

        lbl_name = QLabel(f"#{idx + 1}  {cfg.get('name', '?')}")
        lbl_name.setStyleSheet(
            "color: #fff; font-weight: bold; font-size: 13px;"
        )
        info.addWidget(lbl_name)

        preview = build_preview_url(cfg)
        lbl_url = QLabel(preview)
        lbl_url.setStyleSheet("color: #888; font-size: 11px;")
        lbl_url.setWordWrap(True)
        info.addWidget(lbl_url)

        h.addLayout(info, 1)

        btn_edit = QPushButton("✏ Edit")
        btn_edit.setObjectName("btn_edit")
        btn_edit.clicked.connect(lambda _=False, i=idx: self._on_edit(i))
        h.addWidget(btn_edit)

        btn_delete = QPushButton("🗑 Delete")
        btn_delete.setObjectName("btn_delete")
        btn_delete.clicked.connect(lambda _=False, i=idx: self._on_delete(i))
        h.addWidget(btn_delete)

        return row

    def _on_check(self, idx: int, state: int):
        if 0 <= idx < len(self.consoles):
            self.consoles[idx]["enabled"] = (state == Qt.Checked)
            self.changed = True

    def _on_move_up(self, idx: int):
        if idx <= 0 or idx >= len(self.consoles):
            return
        self.consoles[idx - 1], self.consoles[idx] = (
            self.consoles[idx], self.consoles[idx - 1]
        )
        self.changed = True
        self._populate()
        QTimer.singleShot(0, lambda: self._scroll_to_row(idx - 1))

    def _on_move_down(self, idx: int):
        if idx < 0 or idx >= len(self.consoles) - 1:
            return
        self.consoles[idx + 1], self.consoles[idx] = (
            self.consoles[idx], self.consoles[idx + 1]
        )
        self.changed = True
        self._populate()
        QTimer.singleShot(0, lambda: self._scroll_to_row(idx + 1))

    def _scroll_to_row(self, idx: int):
        item = self.container_layout.itemAt(idx)
        if item and item.widget():
            self.scroll.ensureWidgetVisible(item.widget())

    def _on_edit(self, idx: int):
        if not (0 <= idx < len(self.consoles)):
            return
        cfg = self.consoles[idx]
        dlg = ConsoleConfigDialog(self, initial=cfg)
        if dlg.exec_() != QDialog.Accepted or not dlg.result_config:
            return

        new_cfg = dlg.result_config
        for i, c in enumerate(self.consoles):
            if i != idx and c.get("name") == new_cfg["name"]:
                QMessageBox.warning(
                    self, "Duplikat",
                    f"Nama '{new_cfg['name']}' sudah dipakai."
                )
                return

        self.consoles[idx] = new_cfg
        self.changed = True
        self._populate()

    def _on_delete(self, idx: int):
        if not (0 <= idx < len(self.consoles)):
            return
        cfg = self.consoles[idx]
        reply = QMessageBox.question(
            self, "Hapus Console",
            f"Hapus console '{cfg.get('name')}' dari daftar?\n"
            f"(Config akan dihapus permanen)",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply != QMessageBox.Yes:
            return

        self.consoles.pop(idx)
        self.changed = True
        self._populate()

    def _set_all(self, checked: bool):
        for c in self.consoles:
            c["enabled"] = checked
        self.changed = True
        self._populate()


# ============================================================
# WIDGET CONSOLE
# ============================================================
class ConsoleWidget(QWidget):
    state_changed = pyqtSignal(str, str)

    def __init__(self, config: dict, parent=None):
        super().__init__(parent)
        self.cfg = config
        self.worker = None
        self.is_running = False
        self._restart_pending = False
        self._build_ui()
        self._apply_style()
        self._update_url_label()

    @property
    def name(self):
        return self.cfg["name"]

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(6, 6, 6, 6)
        layout.setSpacing(6)

        # ========== TOP BAR ==========
        top = QHBoxLayout()

        self.lbl_info = QLabel(f"⚙ {self.cfg['name']}")
        self.lbl_info.setStyleSheet("font-weight: bold; color: #ddd;")
        top.addWidget(self.lbl_info)

        # Meta info ringkas
        info_parts = []
        if self.cfg.get("use_range"):
            info_parts.append(f"range={self.cfg.get('range_days')}h")
        if self.cfg.get("use_per_page"):
            info_parts.append(f"per_page={self.cfg.get('per_page')}")
        if not self.cfg.get("use_page", True):
            info_parts.append("single-shot")
        info_parts.append(f"sleep={self.cfg.get('sleep_seconds')}s")

        extra_bits = []
        pp = self.cfg.get("path_params")
        if pp:
            extra_bits.append(f"/{pp}")
        eq = self.cfg.get("extra_query")
        if eq:
            extra_bits.append(f"?{eq}")
        if extra_bits:
            info_parts.append(" ".join(extra_bits))

        self.lbl_meta = QLabel(" | ".join(info_parts))
        self.lbl_meta.setStyleSheet("color: #888; font-size: 11px;")
        self.lbl_meta.setWordWrap(False)
        self.lbl_meta.setMinimumWidth(0)
        self.lbl_meta.setTextFormat(Qt.PlainText)
        self.lbl_meta.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.lbl_meta.setSizePolicy(
            QSizePolicy.Expanding, QSizePolicy.Preferred
        )
        top.addWidget(self.lbl_meta, 1)

        self.lbl_status = QLabel("⏹ Stopped")
        self.lbl_status.setStyleSheet(
            "padding: 2px 8px; border-radius: 8px; "
            "background: #444; color: #ccc; font-size: 11px;"
        )
        top.addWidget(self.lbl_status)

        self.btn_start = QPushButton("▶ Start")
        self.btn_start.clicked.connect(self.start)
        top.addWidget(self.btn_start)

        self.btn_stop = QPushButton("⏹ Stop")
        self.btn_stop.clicked.connect(self.stop)
        self.btn_stop.setEnabled(False)
        top.addWidget(self.btn_stop)

        self.btn_restart = QPushButton("🔄 Restart")
        self.btn_restart.clicked.connect(self.restart)
        top.addWidget(self.btn_restart)

        self.btn_clear = QPushButton("🧹 Clear")
        self.btn_clear.clicked.connect(self.clear_output)
        top.addWidget(self.btn_clear)

        layout.addLayout(top)

        # ========== OUTPUT ==========
        self.output = QPlainTextEdit()
        self.output.setReadOnly(True)
        self.output.setMaximumBlockCount(5000)
        layout.addWidget(self.output, 1)

        # ========== BOTTOM: URL ASLI ==========
        bottom = QHBoxLayout()
        bottom.setSpacing(6)

        lbl_url_tag = QLabel("🔗 URL:")
        lbl_url_tag.setStyleSheet(
            "color: #888; font-size: 11px; font-weight: bold;"
        )
        bottom.addWidget(lbl_url_tag)

        self.lbl_url = QLabel("")
        self.lbl_url.setStyleSheet(
            "color: #4ec9b0; font-size: 11px; "
            "background: #1a1a1a; border: 1px solid #333; "
            "border-radius: 3px; padding: 4px 8px;"
        )
        self.lbl_url.setWordWrap(False)
        self.lbl_url.setMinimumWidth(0)
        self.lbl_url.setTextFormat(Qt.PlainText)
        self.lbl_url.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.lbl_url.setSizePolicy(
            QSizePolicy.Expanding, QSizePolicy.Preferred
        )
        bottom.addWidget(self.lbl_url, 1)

        self.btn_copy_url = QPushButton("📋 Copy")
        self.btn_copy_url.clicked.connect(self._copy_url)
        bottom.addWidget(self.btn_copy_url)

        layout.addLayout(bottom)

    def _apply_style(self):
        self.output.setStyleSheet("""
            QPlainTextEdit {
                background-color: #1e1e1e;
                color: #d4d4d4;
                border: 1px solid #333;
                font-family: 'Consolas', 'Courier New', monospace;
                font-size: 12px;
                padding: 4px;
            }
        """)

    # ---------------------- URL label ----------------------
    def _update_url_label(self):
        url = build_preview_url(self.cfg)
        self.lbl_url.setText(url)
        self.lbl_url.setToolTip(url)

    def set_runtime_url(self, url: str):
        self.lbl_url.setText(url)
        self.lbl_url.setToolTip(url)

    def _copy_url(self):
        txt = self.lbl_url.text()
        if not txt:
            return
        QApplication.clipboard().setText(txt)
        self._append("[SYSTEM] URL dicopy ke clipboard.\n", "#4ec9b0")

    # ---------------------- Logging ----------------------
    def _append(self, text: str, color: str = "#d4d4d4"):
        cursor = self.output.textCursor()
        cursor.movePosition(QTextCursor.End)

        fmt = cursor.charFormat()
        fmt.setForeground(QColor(color))
        cursor.setCharFormat(fmt)

        cursor.insertText(text)
        self.output.setTextCursor(cursor)
        self.output.ensureCursorVisible()

    # ---------------------- Control ----------------------
    def start(self):
        if self.is_running:
            return

        self.worker = DaemonWorker(self.cfg, self)
        self.worker.log_signal.connect(self._on_log)
        self.worker.state_signal.connect(self._on_state)
        self.worker.url_signal.connect(self.set_runtime_url)
        self.worker.finished.connect(self._on_worker_finished)
        self.worker.start()

        self.is_running = True
        self.btn_start.setEnabled(False)
        self.btn_stop.setEnabled(True)
        self._set_status("▶ Running", "#2d5a2d", "#a6e3a1")

    def stop(self):
        if not self.worker or not self.is_running:
            return
        self._restart_pending = False
        self._append("[SYSTEM] Menghentikan daemon...\n", "#4ec9b0")
        self.worker.stop()

    def restart(self):
        if self._restart_pending:
            return

        if self.is_running:
            self._restart_pending = True
            self._set_status("🔄 Restarting", "#5a4a2d", "#f0c674")
            self.worker.stop()
        else:
            self.start()

    def clear_output(self):
        self.output.clear()

    # ---------------------- Signals ----------------------
    def _on_log(self, text: str, color: str):
        self._append(text, color)

    def _on_state(self, state: str):
        if state == "running":
            self._set_status("▶ Running", "#2d5a2d", "#a6e3a1")
        else:
            self._set_status("⏹ Stopped", "#444", "#ccc")

    def _on_worker_finished(self):
        self.is_running = False
        self.btn_start.setEnabled(True)
        self.btn_stop.setEnabled(False)
        self.worker = None
        self.state_changed.emit(self.name, "stopped")

        if self._restart_pending:
            self._restart_pending = False
            self._append("[SYSTEM] Restart dalam 1 detik...\n", "#4ec9b0")
            QTimer.singleShot(1000, self.start)

    def _set_status(self, text, bg, fg):
        self.lbl_status.setText(text)
        self.lbl_status.setStyleSheet(
            f"padding: 2px 8px; border-radius: 8px; "
            f"background: {bg}; color: {fg}; font-size: 11px;"
        )

    def refresh_meta(self):
        self.lbl_info.setText(f"⚙ {self.cfg['name']}")
        info_parts = []
        if self.cfg.get("use_range"):
            info_parts.append(f"range={self.cfg.get('range_days')}h")
        if self.cfg.get("use_per_page"):
            info_parts.append(f"per_page={self.cfg.get('per_page')}")
        if not self.cfg.get("use_page", True):
            info_parts.append("single-shot")
        info_parts.append(f"sleep={self.cfg.get('sleep_seconds')}s")

        extra_bits = []
        pp = self.cfg.get("path_params")
        if pp:
            extra_bits.append(f"/{pp}")
        eq = self.cfg.get("extra_query")
        if eq:
            extra_bits.append(f"?{eq}")
        if extra_bits:
            info_parts.append(" ".join(extra_bits))

        self.lbl_meta.setText(" | ".join(info_parts))
        self._update_url_label()

    def shutdown(self):
        self._restart_pending = False
        if self.worker and self.is_running:
            self.worker.stop()
            self.worker.wait(3000)


# ============================================================
# MAIN WINDOW
# ============================================================
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(APP_TITLE)
        self.resize(1250, 800)
        self.consoles = []
        self.widgets = {}
        self._build_ui()
        self._load_config()
        self._rebuild_tabs()
        self._apply_style()

    # ---------------------- UI ----------------------
    def _build_ui(self):
        toolbar = QToolBar("Main")
        toolbar.setMovable(False)
        self.addToolBar(toolbar)

        act_add = QAction("➕ Add Console", self)
        act_add.triggered.connect(self.add_console)
        toolbar.addAction(act_add)

        act_list = QAction("📋 List Console", self)
        act_list.triggered.connect(self.show_list_console)
        toolbar.addAction(act_list)

        toolbar.addSeparator()

        act_start_all = QAction("▶ Start All", self)
        act_start_all.triggered.connect(self.start_all)
        toolbar.addAction(act_start_all)

        act_stop_all = QAction("⏹ Stop All", self)
        act_stop_all.triggered.connect(self.stop_all)
        toolbar.addAction(act_stop_all)

        act_restart_all = QAction("🔄 Restart All", self)
        act_restart_all.triggered.connect(self.restart_all)
        toolbar.addAction(act_restart_all)

        toolbar.addSeparator()

        act_deactivate = QAction("🗑 Deactivate Current", self)
        act_deactivate.triggered.connect(self.deactivate_current)
        toolbar.addAction(act_deactivate)

        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.setMovable(True)
        self.tabs.tabCloseRequested.connect(self._close_tab)
        self.tabs.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tabs.customContextMenuRequested.connect(self._tab_context_menu)
        self.tabs.tabBar().tabMoved.connect(self._on_tab_moved)

        self.setCentralWidget(self.tabs)

        self.status = QStatusBar()
        self.setStatusBar(self.status)

    def _apply_style(self):
        self.setStyleSheet("""
            QMainWindow { background: #252526; }
            QToolBar {
                background: #333333;
                border: none;
                padding: 4px;
                spacing: 4px;
            }
            QToolBar QToolButton {
                color: #ddd;
                background: #3c3c3c;
                padding: 6px 12px;
                border-radius: 4px;
                margin: 2px;
            }
            QToolBar QToolButton:hover { background: #4a4a4a; }
            QTabWidget::pane {
                border: 1px solid #333;
                background: #1e1e1e;
            }
            QTabBar::tab {
                background: #2d2d2d;
                color: #bbb;
                padding: 8px 16px;
                border: 1px solid #333;
                border-bottom: none;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background: #1e1e1e;
                color: #fff;
            }
            QTabBar::tab:hover { background: #3a3a3a; }
            QPushButton {
                background: #3c3c3c;
                color: #ddd;
                border: 1px solid #555;
                border-radius: 4px;
                padding: 5px 10px;
            }
            QPushButton:hover { background: #4a4a4a; }
            QPushButton:disabled { color: #666; background: #2a2a2a; }
        """)

    # ---------------------- Config ----------------------
    def _load_config(self):
        if not CONFIG_FILE.exists():
            self.consoles = []
            return

        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            QMessageBox.warning(
                self, "Config Rusak",
                f"Gagal baca {CONFIG_FILE}:\n{e}\n\n"
                f"Config akan di-reset."
            )
            self.consoles = []
            return

        REQUIRED_KEYS = {"name"}
        valid = []
        skipped = []

        for c in data.get("consoles", []):
            if not isinstance(c, dict):
                continue
            if REQUIRED_KEYS.issubset(c.keys()):
                # Migrasi config lama
                if c.get("extra_params") and not c.get("path_params"):
                    ep = c["extra_params"]
                    if isinstance(ep, dict):
                        c["path_params"] = "/".join(
                            str(v) for v in ep.values()
                        )
                c.pop("extra_params", None)

                c.setdefault("base_url", "")
                c.setdefault("endpoint", "")
                c.setdefault("path_params", None)
                c.setdefault("extra_query", None)
                c.setdefault("use_range", True)
                c.setdefault("range_days", 30)
                c.setdefault("use_per_page", True)
                c.setdefault("per_page", 100)
                c.setdefault("use_page", True)
                c.setdefault("sleep_seconds", 1800)
                c.setdefault("enabled", True)

                # Validasi: minimal salah satu URL/endpoint ada
                if not c["base_url"] and not c["endpoint"]:
                    skipped.append(c.get("name", "?"))
                    continue

                valid.append(c)
            else:
                skipped.append(c.get("name", "?"))

        self.consoles = valid

        if skipped:
            QMessageBox.information(
                self, "Config Dilewati",
                f"{len(skipped)} console dilewati karena tidak lengkap:\n"
                f"  • " + "\n  • ".join(skipped)
            )

    def _save_config(self):
        try:
            with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump({"consoles": self.consoles}, f,
                          indent=2, ensure_ascii=False)
        except Exception as e:
            QMessageBox.warning(self, "Gagal simpan config", str(e))

    # ---------------------- Tab Management ----------------------
    def _rebuild_tabs(self):
        """
        Smart rebuild: hanya ubah apa yang perlu diubah.

        - Widget yang console-nya masih enabled → pertahankan
          (running tetap running, output utuh)
        - Widget yang console-nya baru disabled → shutdown & hapus
        - Console baru yang enabled → buat widget baru
        - Urutan tab disesuaikan dengan urutan self.consoles
        """
        enabled_names = [
            c["name"] for c in self.consoles if c.get("enabled", True)
        ]
        enabled_set = set(enabled_names)

        # 1) Hapus widget yang sudah tidak enabled (di-disable / dihapus)
        for name in list(self.widgets.keys()):
            if name not in enabled_set:
                w = self.widgets.pop(name)
                try:
                    w.shutdown()
                except Exception:
                    pass
                idx = self._find_tab_index(w)
                if idx >= 0:
                    self.tabs.blockSignals(True)
                    self.tabs.removeTab(idx)
                    self.tabs.blockSignals(False)
                w.deleteLater()

        # 2) Tambahkan widget baru / sinkronkan cfg yang sudah ada
        for c in self.consoles:
            if not c.get("enabled", True):
                continue
            name = c["name"]
            if name not in self.widgets:
                # Widget baru
                w = ConsoleWidget(c)
                w.state_changed.connect(lambda n, s: self._update_status())
                self.widgets[name] = w
                self.tabs.blockSignals(True)
                self.tabs.addTab(w, name)
                self.tabs.blockSignals(False)
            else:
                # Widget sudah ada — sinkron cfg hanya kalau objeknya beda
                existing = self.widgets[name]
                if existing.cfg is not c:
                    # Kalau widget sedang running, worker masih pakai cfg lama.
                    # Sync ini hanya untuk metadata & siklus berikutnya.
                    existing.cfg = c
                    existing.refresh_meta()

        # 3) Urutkan ulang tab sesuai urutan enabled_names
        self.tabs.blockSignals(True)
        for target_idx, name in enumerate(enabled_names):
            w = self.widgets.get(name)
            if not w:
                continue
            current_idx = self._find_tab_index(w)
            if current_idx < 0:
                continue
            if current_idx != target_idx:
                self.tabs.tabBar().moveTab(current_idx, target_idx)
        self.tabs.blockSignals(False)

        self._update_status()

    def _find_tab_index(self, widget) -> int:
        """Cari index tab dari widget."""
        for i in range(self.tabs.count()):
            if self.tabs.widget(i) is widget:
                return i
        return -1

    def _add_tab(self, cfg: dict) -> ConsoleWidget:
        if cfg["name"] in self.widgets:
            return self.widgets[cfg["name"]]

        w = ConsoleWidget(cfg)
        w.state_changed.connect(lambda n, s: self._update_status())
        self.tabs.addTab(w, cfg["name"])
        self.widgets[cfg["name"]] = w
        return w

    def _close_tab(self, index: int):
        """
        Close tab = nonaktifkan (enabled=False), bukan hapus dari config.
        """
        w = self.tabs.widget(index)
        if not isinstance(w, ConsoleWidget):
            return

        # Kalau running, tanya dulu
        if w.is_running:
            reply = QMessageBox.question(
                self, "Tutup Tab",
                f"Console '{w.name}' sedang running.\n"
                f"Stop dan tutup tab?",
                QMessageBox.Yes | QMessageBox.No
            )
            if reply != QMessageBox.Yes:
                return
            w.shutdown()

        # Set enabled=False di config
        for c in self.consoles:
            if c["name"] == w.name:
                c["enabled"] = False
                break

        # Hapus tab & widget dari memori
        self.tabs.blockSignals(True)
        self.tabs.removeTab(index)
        self.tabs.blockSignals(False)
        if w.name in self.widgets:
            del self.widgets[w.name]
        w.deleteLater()

        self._save_config()
        self._update_status()

    def _on_tab_moved(self, from_idx: int, to_idx: int):
        new_order = []
        for i in range(self.tabs.count()):
            w = self.tabs.widget(i)
            if isinstance(w, ConsoleWidget):
                new_order.append(w.name)

        active_map = {c["name"]: c for c in self.consoles
                      if c.get("enabled", True)}
        inactive = [c for c in self.consoles if not c.get("enabled", True)]

        reordered = []
        for name in new_order:
            if name in active_map:
                reordered.append(active_map[name])

        reordered.extend(inactive)

        old_names = [c["name"] for c in self.consoles]
        new_names = [c["name"] for c in reordered]
        if old_names != new_names:
            self.consoles = reordered
            self._save_config()

    def deactivate_current(self):
        idx = self.tabs.currentIndex()
        if idx >= 0:
            self._close_tab(idx)

    def _tab_context_menu(self, pos):
        index = self.tabs.tabBar().tabAt(pos)
        if index < 0:
            return
        w = self.tabs.widget(index)
        if not isinstance(w, ConsoleWidget):
            return

        menu = QMenu(self)
        act_start = menu.addAction("▶ Start")
        act_stop = menu.addAction("⏹ Stop")
        act_restart = menu.addAction("🔄 Restart")
        menu.addSeparator()
        act_edit = menu.addAction("✏ Edit Config")
        act_rename = menu.addAction("📝 Rename Tab")
        act_deactivate = menu.addAction("🗑 Deactivate Tab")
        menu.addSeparator()
        act_clear = menu.addAction("🧹 Clear Output")

        action = menu.exec_(self.tabs.tabBar().mapToGlobal(pos))

        if action == act_start:
            w.start()
        elif action == act_stop:
            w.stop()
        elif action == act_restart:
            w.restart()
        elif action == act_clear:
            w.clear_output()
        elif action == act_rename:
            self._rename_tab(index, w)
        elif action == act_edit:
            self._edit_config(index, w)
        elif action == act_deactivate:
            self._close_tab(index)

    def _rename_tab(self, index: int, w: ConsoleWidget):
        new_name, ok = QInputDialog.getText(
            self, "Rename Tab", "Nama baru:", text=w.name
        )
        if ok and new_name.strip():
            old_name = w.name
            new_name = new_name.strip()

            if any(c["name"] == new_name and c["name"] != old_name
                   for c in self.consoles):
                QMessageBox.warning(
                    self, "Duplikat",
                    f"Nama '{new_name}' sudah dipakai."
                )
                return

            w.cfg["name"] = new_name
            self.tabs.setTabText(index, new_name)
            for c in self.consoles:
                if c["name"] == old_name:
                    c["name"] = new_name
                    break
            if old_name in self.widgets:
                self.widgets[new_name] = self.widgets.pop(old_name)
            w.refresh_meta()
            self._save_config()

    def _edit_config(self, index: int, w: ConsoleWidget):
        if w.is_running:
            QMessageBox.warning(
                self, "Sedang Running",
                "Stop console dulu sebelum edit konfigurasi."
            )
            return
        dlg = ConsoleConfigDialog(self, initial=w.cfg)
        if dlg.exec_() != QDialog.Accepted or not dlg.result_config:
            return

        new_cfg = dlg.result_config
        old_name = w.cfg["name"]

        if any(c["name"] == new_cfg["name"] and c["name"] != old_name
               for c in self.consoles):
            QMessageBox.warning(
                self, "Duplikat",
                f"Nama '{new_cfg['name']}' sudah dipakai."
            )
            return

        for i, c in enumerate(self.consoles):
            if c["name"] == old_name:
                self.consoles[i] = new_cfg
                break

        w.cfg = new_cfg
        self.tabs.setTabText(index, new_cfg["name"])
        if old_name in self.widgets:
            self.widgets[new_cfg["name"]] = self.widgets.pop(old_name)
        w.refresh_meta()
        self._save_config()
        self._update_status()

    # ---------------------- List Console ----------------------
    def show_list_console(self):
        before = json.dumps(self.consoles, sort_keys=True, ensure_ascii=False)

        dlg = ConsoleListDialog(self, self.consoles)
        dlg.exec_()

        after = json.dumps(self.consoles, sort_keys=True, ensure_ascii=False)
        if before != after:
            self._save_config()
            self._rebuild_tabs()

    # ---------------------- Actions ----------------------
    def add_console(self):
        dlg = ConsoleConfigDialog(self)
        if dlg.exec_() != QDialog.Accepted or not dlg.result_config:
            return

        cfg = dlg.result_config

        if any(c["name"] == cfg["name"] for c in self.consoles):
            QMessageBox.warning(
                self, "Duplikat",
                f"Nama console '{cfg['name']}' sudah ada."
            )
            return

        self.consoles.append(cfg)
        self._save_config()
        # Pakai smart rebuild supaya konsisten & tidak reset widget lain
        self._rebuild_tabs()
        self._update_status()

    def start_all(self):
        for w in self.widgets.values():
            if not w.is_running:
                w.start()

    def stop_all(self):
        for w in self.widgets.values():
            if w.is_running:
                w.stop()

    def restart_all(self):
        for w in self.widgets.values():
            w.restart()

    def _update_status(self):
        total = len(self.consoles)
        active = len(self.widgets)
        running = sum(1 for w in self.widgets.values() if w.is_running)
        self.status.showMessage(
            f"Total config: {total}  |  Tab aktif: {active}  |  "
            f"Running: {running}  |  Config: {CONFIG_FILE}"
        )

    # ---------------------- Close ----------------------
    def closeEvent(self, event):
        running = [w for w in self.widgets.values() if w.is_running]
        if running:
            reply = QMessageBox.question(
                self, "Konfirmasi Keluar",
                f"Masih ada {len(running)} console running.\n"
                f"Yakin keluar dan matikan semuanya?",
                QMessageBox.Yes | QMessageBox.No
            )
            if reply != QMessageBox.Yes:
                event.ignore()
                return

        for w in self.widgets.values():
            w.shutdown()
        event.accept()


# ============================================================
# ENTRY POINT
# ============================================================
def main():
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    # Fusion style biar dialog-dialog konsisten (rename, messagebox, dll.)
    QApplication.setStyle("Fusion")

    app = QApplication(sys.argv)
    app.setApplicationName(APP_TITLE)
    app.setFont(QFont("Segoe UI", 9))

    win = MainWindow()
    win.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()