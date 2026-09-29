"""
PTMusic Installer
Phoni Technology 2026
Version 26.9.3

Standalone Python installer — no NSIS required.
Run this file to install PTMusic.
Requires: pip install pillow
"""

import os
import sys
import json
import shutil
import winreg
import threading
import subprocess
import queue
import tkinter as tk
from tkinter import filedialog, messagebox
from pathlib import Path

try:
    from PIL import Image, ImageTk
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

# ── CONSTANTS ─────────────────────────────────────────────────────────────
APP_NAME      = "PTMusic"
APP_VERSION   = "26.9.3"
APP_PUBLISHER = "Phoni Technology"
APP_URL       = "https://phonitechnology.com"
APP_EXE       = "PTMusic.exe"
UNINSTALL_EXE = "Uninstall PTMusic.exe"
MANIFEST_NAME = "PTMusic.install.json"
# PTMusic settings live in the user's profile. A per-user install therefore
# avoids an unnecessary UAC prompt and never writes settings for Administrator.
DEFAULT_DIR   = os.path.join(os.environ.get("LOCALAPPDATA", os.path.expanduser("~")),
                             "Programs", "Phoni Technology", "PTMusic")
CONFIG_PATH   = os.path.join(os.path.expanduser("~"), ".ptmusic_config.json")
REG_KEY       = r"Software\Microsoft\Windows\CurrentVersion\Uninstall\PTMusic"
CLASSES_KEY   = r"Software\Classes"

PUBLIC_THEMES = ["Aero Light", "Aero Dark", "Mint", "Cherry", "Sand", "Ocean Teal"]
LANGUAGES     = ["English", "Deutsch"]

# ── TRANSLATIONS ─────────────────────────────────────────────────────────
STRINGS = {
    "English": {
        "welcome_title":   "Welcome to PTMusic Setup",
        "welcome_sub":     "This wizard will install PTMusic {v} on your computer.",
        "welcome_body":    "Click Next to continue with the setup.\nPTMusic will be installed on your computer and\nshortcuts will be created as configured.",
        "lang_title":      "Language",
        "lang_sub":        "Select the language for PTMusic.",
        "lang_more":       "More languages will be added in future versions.",
        "options_title":   "Options",
        "options_sub":     "Customise your PTMusic installation.",
        "theme_label":     "Default theme:",
        "shortcuts_label": "Shortcuts:",
        "desktop_sc":      "Create Desktop shortcut",
        "startmenu_sc":    "Create Start Menu shortcut",
        "behaviour_label": "Behaviour:",
        "scan_label":      "Scan for music on first launch",
        "notif_label":     "Enable track notifications",
        "dir_title":       "Install Location",
        "dir_sub":         "Choose where PTMusic will be installed.",
        "dir_label":       "Install PTMusic to:",
        "browse":          "Browse…",
        "free_space":      "Free space on drive: {n} MB",
        "req_space":       "Required space: ~60 MB",
        "install_title":   "Installing",
        "install_sub":     "Please wait while PTMusic is installed.",
        "install_ready":   "Ready to install.",
        "install_done_t":  "Installation Complete",
        "install_done_s":  "PTMusic has been installed successfully.",
        "install_done_b":  "PTMusic {v} is ready.",
        "publisher":       "Phoni Technology  ·  2026",
        "launch_now":      "Launch PTMusic now",
        "cancel_title":    "Cancel Setup",
        "cancel_msg":      "Are you sure you want to cancel the installation?",
        "btn_next":        "Next →",
        "btn_back":        "← Back",
        "btn_cancel":      "Cancel",
        "btn_install":     "Install ✔",
        "btn_close":       "Close",
        "btn_continue":    "Continue Anyway",
        "steps":           ["Welcome", "Language", "Options", "Location", "Install", "Done"],
        "setup_subtitle":  "Setup — Version {v}",
        "err_no_exe":      "{exe} not found next to installer.\nExpected: {path}",
        "log_created":     "  Created: {path}",
        "log_copied":      "  Copied: {f}",
        "log_cfg":         "  Config written: {path}",
        "log_desktop":     "  Desktop shortcut created",
        "log_startmenu":   "  Start Menu shortcut created",
        "log_registry":    "  Registered in Add/Remove Programs",
        "log_reg_warn":    "  Warning: Could not write registry ({e})",
        "log_done":        "\n✔  Installation complete!",
        "log_error":       "\n✖  Error: {e}",
        "install_fail":    "Installation failed — see log above.",
        "installing":      "Installing…",
        "complete":        "Installation complete!",
    },
    "Deutsch": {
        "welcome_title":   "Willkommen beim PTMusic-Setup",
        "welcome_sub":     "Dieser Assistent installiert PTMusic {v} auf Ihrem Computer.",
        "welcome_body":    "Klicken Sie auf Weiter, um fortzufahren.\nPTMusic wird auf Ihrem Computer installiert und\nVerknüpfungen werden wie konfiguriert erstellt.",
        "lang_title":      "Sprache",
        "lang_sub":        "Sprache für PTMusic auswählen.",
        "lang_more":       "Weitere Sprachen werden in zukünftigen Versionen hinzugefügt.",
        "options_title":   "Optionen",
        "options_sub":     "Passen Sie Ihre PTMusic-Installation an.",
        "theme_label":     "Standarddesign:",
        "shortcuts_label": "Verknüpfungen:",
        "desktop_sc":      "Desktop-Verknüpfung erstellen",
        "startmenu_sc":    "Startmenü-Verknüpfung erstellen",
        "behaviour_label": "Verhalten:",
        "scan_label":      "Musik beim ersten Start suchen",
        "notif_label":     "Titelbenachrichtigungen aktivieren",
        "dir_title":       "Installationsort",
        "dir_sub":         "Wählen Sie, wo PTMusic installiert werden soll.",
        "dir_label":       "PTMusic installieren in:",
        "browse":          "Durchsuchen…",
        "free_space":      "Freier Speicherplatz: {n} MB",
        "req_space":       "Benötigter Speicherplatz: ~60 MB",
        "install_title":   "Installiere",
        "install_sub":     "Bitte warten Sie, während PTMusic installiert wird.",
        "install_ready":   "Bereit zur Installation.",
        "install_done_t":  "Installation abgeschlossen",
        "install_done_s":  "PTMusic wurde erfolgreich installiert.",
        "install_done_b":  "PTMusic {v} ist bereit.",
        "publisher":       "Phoni Technology  ·  2026",
        "launch_now":      "PTMusic jetzt starten",
        "cancel_title":    "Setup abbrechen",
        "cancel_msg":      "Möchten Sie die Installation wirklich abbrechen?",
        "btn_next":        "Weiter →",
        "btn_back":        "← Zurück",
        "btn_cancel":      "Abbrechen",
        "btn_install":     "Installieren ✔",
        "btn_close":       "Schließen",
        "btn_continue":    "Trotzdem fortfahren",
        "steps":           ["Willkommen", "Sprache", "Optionen", "Ort", "Installiere", "Fertig"],
        "setup_subtitle":  "Setup — Version {v}",
        "err_no_exe":      "{exe} nicht neben dem Installer gefunden.\nErwartet: {path}",
        "log_created":     "  Erstellt: {path}",
        "log_copied":      "  Kopiert: {f}",
        "log_cfg":         "  Konfiguration geschrieben: {path}",
        "log_desktop":     "  Desktop-Verknüpfung erstellt",
        "log_startmenu":   "  Startmenü-Verknüpfung erstellt",
        "log_registry":    "  In Programme hinzufügen/entfernen registriert",
        "log_reg_warn":    "  Warnung: Registry-Eintrag fehlgeschlagen ({e})",
        "log_done":        "\n✔  Installation abgeschlossen!",
        "log_error":       "\n✖  Fehler: {e}",
        "install_fail":    "Installation fehlgeschlagen — siehe Protokoll.",
        "installing":      "Installiere…",
        "complete":        "Installation abgeschlossen!",
    },
}

def t(key, lang="English", **kw):
    """Get translated string."""
    s = STRINGS.get(lang, STRINGS["English"]).get(key, key)
    return s.format(**kw) if kw else s

# ── PALETTE ───────────────────────────────────────────────────────────────
A = {
    "win_bg":        "#0a1628",
    "glass_dark":    "#0d1f3c",
    "glass":         "#132840",
    "glass_mid":     "#1a3a58",
    "glass_light":   "#224d72",
    "border":        "#1e5a8a",
    "border_glow":   "#2e87cc",
    "accent":        "#3ea6e0",
    "accent_bright": "#7fd4ff",
    "accent_hot":    "#00aaff",
    "title_bar":     "#0f2340",
    "title_bar2":    "#162e50",
    "tb_border":     "#1a4a7a",
    "btn":           "#163352",
    "btn_top":       "#1e4570",
    "btn_hover":     "#1f4d7a",
    "btn_press":     "#0c1f33",
    "btn_border":    "#2a6aaa",
    "text":          "#ddeeff",
    "text_dim":      "#6a9cbb",
    "text_bright":   "#b8dff5",
    "sel":           "#164872",
    "sel_border":    "#3ab0ff",
    "prog_bg":       "#081828",
    "prog_fill":     "#1a8fd1",
    "prog_bright":   "#4dc8ff",
    "danger":        "#c0304a",
    "danger_hover":  "#e03050",
    "green":         "#00e080",
    "sidebar":       "#0e2238",
    "sidebar_sect":  "#0a1a2c",
}

FONT_UI    = ("Segoe UI", 9)
FONT_BOLD  = ("Segoe UI", 9, "bold")
FONT_SMALL = ("Segoe UI", 8)
FONT_TITLE = ("Segoe UI", 10, "bold")
FONT_BIG   = ("Segoe UI Light", 16)
FONT_LABEL = ("Segoe UI", 7, "bold")
FONT_MONO  = ("Consolas", 9)


# ── AERO BUTTON ───────────────────────────────────────────────────────────
class AeroBtn(tk.Label):
    def __init__(self, parent, text="", icon="", cmd=None,
                 w=120, h=28, danger=False, bg_override=None, **kw):
        kw.pop("square", None)
        self.cmd = cmd; self.text = text; self.icon = icon
        self.danger = danger; self._hov = False; self._press = False
        self._enabled = True
        lbl = (icon + (" " if icon and text else "") + text)
        super().__init__(parent, text=lbl, font=FONT_UI,
                         bg=A["btn"], fg=A["text"], relief="flat", bd=0,
                         padx=10, pady=4, cursor="hand2", **kw)
        self._refresh()
        self.bind("<Enter>",           lambda e: self._set(hov=True))
        self.bind("<Leave>",           lambda e: self._set(hov=False, press=False))
        self.bind("<ButtonPress-1>",   lambda e: self._set(press=True))
        self.bind("<ButtonRelease-1>", self._release)

    def _set(self, hov=None, press=None):
        if hov   is not None: self._hov   = hov
        if press is not None: self._press = press
        self._refresh()

    def _release(self, e):
        self._press = False; self._refresh()
        if self._enabled and self.cmd:
            self.cmd()

    def set_enabled(self, enabled):
        """Enable or disable the button without changing its layout."""
        self._enabled = enabled
        self._press = False
        self.config(cursor="hand2" if enabled else "arrow")
        self._refresh()

    def _refresh(self):
        if not self._enabled:
            bg = A["btn_press"]; fg = A["text_dim"]
        elif self._press: bg = A["btn_press"]; fg = A["text_dim"]
        elif self._hov:   bg = A["btn_hover"]; fg = A["accent_bright"]
        else:             bg = A["btn"];       fg = A["text"]
        if self.danger:   fg = A["danger_hover"] if self._hov else A["danger"]
        self.config(bg=bg, fg=fg,
                    highlightbackground=A["btn_border"], highlightthickness=1)


# ── INSTALLER ─────────────────────────────────────────────────────────────
class Installer:
    def __init__(self):
        # Find the folder containing this installer script/exe
        if getattr(sys, "_MEIPASS", None):
            self.src_dir = sys._MEIPASS
        else:
            self.src_dir = os.path.dirname(os.path.abspath(__file__))

        self.root = tk.Tk()
        self._lang = "English"  # updated when user picks
        self._events = queue.Queue()
        self._installing = False
        self._rebuild_pending = False

        # Variables must be created after tk.Tk()
        self.install_dir   = tk.StringVar(value=DEFAULT_DIR)
        self.theme_var     = tk.StringVar(value="Aero Light")
        self.lang_var      = tk.StringVar(value="English")
        self.desktop_var   = tk.BooleanVar(value=True)
        self.startmenu_var = tk.BooleanVar(value=True)
        self.scan_var      = tk.BooleanVar(value=True)
        self.notif_var     = tk.BooleanVar(value=True)
        self.lang_var.trace_add("write", self._language_changed)
        self.root.title(f"PTMusic {APP_VERSION} Setup")
        self.root.geometry("620x560")
        self.root.resizable(False, False)
        self.root.configure(bg=A["win_bg"])
        self.root.protocol("WM_DELETE_WINDOW", self._cancel)

        # Window icon
        try:
            ico = Image.open(os.path.join(self.src_dir, "PTMusic.png"))
            self._ico = ImageTk.PhotoImage(ico)
            self.root.iconphoto(True, self._ico)
        except Exception:
            pass

        self._pages = []
        self._cur   = 0
        self._build()
        self.root.after(50, self._drain_events)
        self.root.mainloop()

    # ── SHELL ─────────────────────────────────────────────────────────────
    def _build(self, page=0):
        # Title bar
        tb = tk.Canvas(self.root, height=60, bg=A["title_bar"], highlightthickness=0)
        tb.pack(fill="x")
        tb.create_rectangle(0, 0, 1000, 30,  fill=A["title_bar"],  outline="")
        tb.create_rectangle(0, 30, 1000, 60, fill=A["title_bar2"], outline="")
        tb.create_line(0, 0, 1000, 0, fill=A["border_glow"])

        # Logo + title in titlebar
        try:
            raw = Image.open(os.path.join(self.src_dir, "PTMusic.png")).resize((36, 36), Image.LANCZOS)
            self._tb_img = ImageTk.PhotoImage(raw)
            tb.create_image(16, 30, image=self._tb_img, anchor="w")
            tb.create_text(60, 22, text="PTMusic", fill=A["accent_bright"],
                           font=("Segoe UI", 14, "bold"), anchor="w")
        except Exception:
            tb.create_text(16, 22, text="PTMusic", fill=A["accent_bright"],
                           font=("Segoe UI", 14, "bold"), anchor="w")

        tb.create_text(60, 42, text=t("setup_subtitle", self._lang, v=APP_VERSION),
                       fill=A["text_dim"], font=FONT_SMALL, anchor="w")
        tk.Frame(self.root, bg=A["tb_border"], height=1).pack(fill="x")

        # Step indicator strip
        self.step_canvas = tk.Canvas(self.root, height=32, bg=A["glass_dark"],
                                      highlightthickness=0)
        self.step_canvas.pack(fill="x")
        tk.Frame(self.root, bg=A["border"], height=1).pack(fill="x")

        # Page content area
        self.page_frame = tk.Frame(self.root, bg=A["glass"])
        self.page_frame.pack(fill="both", expand=True)

        # Bottom nav bar
        tk.Frame(self.root, bg=A["border"], height=1).pack(fill="x")
        nav = tk.Frame(self.root, bg=A["glass_dark"])
        nav.pack(fill="x")

        self.cancel_btn = AeroBtn(nav, text=t("btn_cancel", self._lang), icon="✖",
                                   cmd=self._cancel, danger=True)
        self.cancel_btn.pack(side="left", padx=12, pady=10)

        self.next_btn = AeroBtn(nav, text=t("btn_next", self._lang), cmd=self._next, w=110)
        self.next_btn.pack(side="right", padx=12, pady=10)

        self.back_btn = AeroBtn(nav, text=t("btn_back", self._lang), cmd=self._back, w=90)
        self.back_btn.pack(side="right", padx=4, pady=10)

        # Build pages
        self._pages = [
            self._page_welcome,
            self._page_language,
            self._page_options,
            self._page_directory,
            self._page_install,
            self._page_done,
        ]
        self._page_frames = []
        for i, builder in enumerate(self._pages):
            f = tk.Frame(self.page_frame, bg=A["glass"])
            builder(f)
            self._page_frames.append(f)

        self._show_page(page)

    def _draw_steps(self, current):
        c = self.step_canvas
        c.delete("all")
        steps = t("steps", self._lang)
        w = 580
        sw = w // len(steps)
        for i, name in enumerate(steps):
            x = i * sw + sw // 2
            if i < current:
                col = A["green"]
            elif i == current:
                col = A["accent_bright"]
            else:
                col = A["text_dim"]
            c.create_text(x, 16, text=name, fill=col,
                          font=FONT_LABEL if i != current else ("Segoe UI", 7, "bold"))
            if i == current:
                c.create_line(i*sw+8, 28, (i+1)*sw-8, 28,
                              fill=A["accent"], width=2)

    def _show_page(self, idx):
        for f in self._page_frames:
            f.pack_forget()
        self._page_frames[idx].pack(fill="both", expand=True)
        self._cur = idx
        self._draw_steps(idx)
        # Button states
        self.back_btn.config(fg=A["text_dim"] if idx == 0 else A["text"])
        self.back_btn.set_enabled(idx > 0 and not self._installing)
        self.next_btn.set_enabled(not self._installing)
        self.cancel_btn.set_enabled(not self._installing)
        last = len(self._pages) - 1
        if idx == last:
            self.next_btn.config(text=t("btn_close", self._lang), fg=A["green"])
            self.next_btn.cmd = self._finish
            self.back_btn.config(fg=A["text_dim"])
            self.back_btn.set_enabled(False)
        elif idx == last - 1:
            self.next_btn.config(text=t("btn_install", self._lang), fg=A["accent_bright"])
            self.next_btn.cmd = self._run_install
        else:
            self.next_btn.config(text=t("btn_next", self._lang), fg=A["text"])
            self.next_btn.cmd = self._next

    def _next(self):
        if self._cur < len(self._pages) - 1:
            self._show_page(self._cur + 1)

    def _back(self):
        if not self._installing and self._cur > 0:
            self._show_page(self._cur - 1)

    def _cancel(self):
        if self._installing:
            return
        if messagebox.askyesno(t("cancel_title", self._lang),
                                t("cancel_msg", self._lang),
                                parent=self.root):
            self.root.destroy()

    def _language_changed(self, *_):
        """Refresh visible copy after a language selection without stacking traces."""
        chosen = self.lang_var.get()
        if chosen == self._lang or self._rebuild_pending:
            return
        self._lang = chosen
        self._rebuild_pending = True
        self.root.after_idle(self._rebuild_for_language)

    def _rebuild_for_language(self):
        page = self._cur
        self._rebuild_pending = False
        for widget in self.root.winfo_children():
            widget.destroy()
        self._build(page)

    def _emit(self, kind, *values):
        """Send work-thread updates to the Tk main thread."""
        self._events.put((kind, values))

    def _drain_events(self):
        try:
            while True:
                kind, values = self._events.get_nowait()
                if kind == "log":
                    self._append_log(values[0])
                elif kind == "status":
                    self.install_status.config(text=values[0], fg=values[1])
                elif kind == "progress":
                    self._set_progress(values[0])
                elif kind == "complete":
                    self._install_done()
                elif kind == "error":
                    self._install_failed(values[0])
        except queue.Empty:
            pass
        try:
            self.root.after(50, self._drain_events)
        except tk.TclError:
            pass

    # ── PAGE HELPERS ──────────────────────────────────────────────────────
    def _header(self, parent, title, subtitle=""):
        hdr = tk.Frame(parent, bg=A["glass_mid"])
        hdr.pack(fill="x")
        tk.Label(hdr, text=title, bg=A["glass_mid"], fg=A["accent_bright"],
                 font=FONT_BIG, anchor="w").pack(anchor="w", padx=20, pady=(14,0))
        if subtitle:
            tk.Label(hdr, text=subtitle, bg=A["glass_mid"], fg=A["text_dim"],
                     font=FONT_SMALL, anchor="w").pack(anchor="w", padx=20, pady=(0,10))
        tk.Frame(parent, bg=A["border"], height=1).pack(fill="x")

    def _row(self, parent, label, widget_fn):
        r = tk.Frame(parent, bg=A["glass"]); r.pack(fill="x", padx=24, pady=6)
        tk.Label(r, text=label, bg=A["glass"], fg=A["text"],
                 font=FONT_UI, width=22, anchor="w").pack(side="left")
        widget_fn(r)
        return r

    # ── PAGE 0: WELCOME ───────────────────────────────────────────────────
    def _page_welcome(self, f):
        self._header(f, t("welcome_title", self._lang),
                     t("welcome_sub", self._lang, v=APP_VERSION))
        body = tk.Frame(f, bg=A["glass"]); body.pack(fill="both", expand=True, padx=24, pady=20)

        # Logo
        try:
            raw = Image.open(os.path.join(self.src_dir, "PTMusic.png")).resize((80, 80), Image.LANCZOS)
            self._welcome_img = ImageTk.PhotoImage(raw)
            tk.Label(body, image=self._welcome_img, bg=A["glass"]).pack(pady=(0,12))
        except Exception:
            tk.Label(body, text="🎵", bg=A["glass"], fg=A["accent_bright"],
                     font=("Segoe UI", 40)).pack(pady=(0,12))

        tk.Label(body, text="PTMusic", bg=A["glass"], fg=A["accent_bright"],
                 font=("Segoe UI Light", 20)).pack()
        tk.Label(body, text=f"Version {APP_VERSION}  ·  Phoni Technology  ·  2026",
                 bg=A["glass"], fg=A["text_dim"], font=FONT_SMALL).pack(pady=(4,16))
        tk.Frame(body, bg=A["border"], height=1).pack(fill="x")
        tk.Label(body,
                 text=t("welcome_body", self._lang),
                 bg=A["glass"], fg=A["text_dim"], font=FONT_SMALL,
                 justify="center").pack(pady=14)

    # ── PAGE 1: LANGUAGE ──────────────────────────────────────────────────
    def _page_language(self, f):
        self._header(f, t("lang_title", self._lang), t("lang_sub", self._lang))
        body = tk.Frame(f, bg=A["glass"]); body.pack(fill="both", expand=True, padx=24, pady=20)

        tk.Label(body, text="Installer and application language:",
                 bg=A["glass"], fg=A["text"], font=FONT_UI).pack(anchor="w", pady=(0,10))

        for lang in LANGUAGES:
            rb = tk.Radiobutton(body, text=lang, variable=self.lang_var, value=lang,
                                bg=A["glass"], fg=A["text"],
                                activebackground=A["glass"], activeforeground=A["accent"],
                                selectcolor=A["glass_dark"], font=FONT_UI)
            rb.pack(anchor="w", padx=20, pady=3)

        tk.Frame(body, bg=A["border"], height=1).pack(fill="x", pady=16)
        tk.Label(body, text=t("lang_more", self._lang),
                 bg=A["glass"], fg=A["text_dim"], font=FONT_SMALL).pack(anchor="w")

    # ── PAGE 2: OPTIONS ───────────────────────────────────────────────────
    def _page_options(self, f):
        self._header(f, t("options_title", self._lang), t("options_sub", self._lang))
        body = tk.Frame(f, bg=A["glass"]); body.pack(fill="both", expand=True, padx=24, pady=12)

        # Theme
        tk.Label(body, text=t("theme_label", self._lang), bg=A["glass"],
                 fg=A["text"], font=FONT_UI).pack(anchor="w", pady=(0,4))
        theme_frame = tk.Frame(body, bg=A["glass"]); theme_frame.pack(fill="x", padx=12, pady=(0,8))
        for i, theme in enumerate(PUBLIC_THEMES):
            rb = tk.Radiobutton(theme_frame, text=theme, variable=self.theme_var,
                                value=theme, bg=A["glass"], fg=A["text"],
                                activebackground=A["glass"], activeforeground=A["accent"],
                                selectcolor=A["glass_dark"], font=FONT_UI)
            rb.grid(row=i//2, column=i%2, sticky="w", padx=16, pady=2)

        tk.Frame(body, bg=A["border"], height=1).pack(fill="x", pady=10)

        # Shortcuts
        tk.Label(body, text=t("shortcuts_label", self._lang), bg=A["glass"],
                 fg=A["text"], font=FONT_UI).pack(anchor="w", pady=(0,4))
        for var, label in [(self.desktop_var,   t("desktop_sc",   self._lang)),
                           (self.startmenu_var, t("startmenu_sc", self._lang))]:
            tk.Checkbutton(body, text=label, variable=var,
                           bg=A["glass"], fg=A["text"],
                           activebackground=A["glass"], activeforeground=A["accent"],
                           selectcolor=A["glass_dark"],
                           font=FONT_UI).pack(anchor="w", padx=12, pady=2)

        tk.Frame(body, bg=A["border"], height=1).pack(fill="x", pady=10)

        # Behaviour
        tk.Label(body, text=t("behaviour_label", self._lang), bg=A["glass"],
                 fg=A["text"], font=FONT_UI).pack(anchor="w", pady=(0,4))
        for var, label in [(self.scan_var,  t("scan_label",  self._lang)),
                           (self.notif_var, t("notif_label", self._lang))]:
            tk.Checkbutton(body, text=label, variable=var,
                           bg=A["glass"], fg=A["text"],
                           activebackground=A["glass"], activeforeground=A["accent"],
                           selectcolor=A["glass_dark"],
                           font=FONT_UI).pack(anchor="w", padx=12, pady=2)

    # ── PAGE 3: DIRECTORY ─────────────────────────────────────────────────
    def _page_directory(self, f):
        self._header(f, t("dir_title", self._lang), t("dir_sub", self._lang))
        body = tk.Frame(f, bg=A["glass"]); body.pack(fill="both", expand=True, padx=24, pady=20)

        tk.Label(body, text=t("dir_label", self._lang), bg=A["glass"],
                 fg=A["text"], font=FONT_UI).pack(anchor="w", pady=(0,6))

        dir_row = tk.Frame(body, bg=A["glass"]); dir_row.pack(fill="x")
        ef = tk.Frame(dir_row, bg=A["border"], padx=1, pady=1)
        ef.pack(side="left", fill="x", expand=True)
        tk.Entry(ef, textvariable=self.install_dir, bg=A["glass_mid"], fg=A["text"],
                 insertbackground=A["accent_hot"], relief="flat",
                 font=FONT_MONO).pack(fill="x", ipady=4)
        AeroBtn(dir_row, text=t("browse", self._lang), cmd=self._browse, w=90).pack(side="left", padx=(8,0))

        tk.Frame(body, bg=A["border"], height=1).pack(fill="x", pady=16)

        # Space info
        try:
            total, used, free = shutil.disk_usage(Path(self.install_dir.get()).anchor)
            free_mb = free // (1024*1024)
            tk.Label(body, text=t("free_space", self._lang, n=f"{free_mb:,}"),
                     bg=A["glass"], fg=A["text_dim"], font=FONT_SMALL).pack(anchor="w")
        except Exception:
            pass

        tk.Label(body, text=t("req_space", self._lang),
                 bg=A["glass"], fg=A["text_dim"], font=FONT_SMALL).pack(anchor="w", pady=2)
        tk.Label(body,
                 text=("PTMusic installs for the current Windows user. "
                       "No administrator rights are required."),
                 bg=A["glass"], fg=A["text_dim"], font=FONT_SMALL,
                 wraplength=520, justify="left").pack(anchor="w", pady=(14, 0))

    def _browse(self):
        path = filedialog.askdirectory(title="Choose Install Location",
                                        initialdir=self.install_dir.get(),
                                        parent=self.root)
        if path:
            self.install_dir.set(path)

    # ── PAGE 4: INSTALLING ────────────────────────────────────────────────
    def _page_install(self, f):
        self._header(f, t("install_title", self._lang), t("install_sub", self._lang))
        body = tk.Frame(f, bg=A["glass"]); body.pack(fill="both", expand=True, padx=24, pady=20)

        self.install_status = tk.Label(body, text=t("install_ready", self._lang),
                                        bg=A["glass"], fg=A["text"], font=FONT_UI)
        self.install_status.pack(anchor="w", pady=(0,10))

        # Progress bar
        prog_frame = tk.Frame(body, bg=A["border"], padx=1, pady=1)
        prog_frame.pack(fill="x")
        self.prog_canvas = tk.Canvas(prog_frame, height=20, bg=A["prog_bg"],
                                      highlightthickness=0)
        self.prog_canvas.pack(fill="x")

        self.install_log = tk.Text(body, height=10, bg=A["glass_dark"], fg=A["text_dim"],
                                    font=FONT_MONO, relief="flat", state="disabled",
                                    wrap="word", highlightthickness=0)
        self.install_log.pack(fill="both", expand=True, pady=(12,0))

    def _log(self, msg):
        self._emit("log", msg)

    def _append_log(self, msg):
        self.install_log.config(state="normal")
        self.install_log.insert("end", msg + "\n")
        self.install_log.see("end")
        self.install_log.config(state="disabled")

    def _set_progress(self, pct):
        self.prog_canvas.delete("all")
        w = self.prog_canvas.winfo_width() or 530
        fw = int(w * pct / 100)
        self.prog_canvas.create_rectangle(0, 0, w, 20, fill=A["prog_bg"], outline="")
        if fw > 0:
            self.prog_canvas.create_rectangle(0, 0, fw, 10,   fill=A["prog_bright"], outline="")
            self.prog_canvas.create_rectangle(0, 10, fw, 20,  fill=A["prog_fill"],   outline="")
        self.root.update_idletasks()

    def _run_install(self):
        if self._installing:
            return
        error = self._validate_destination()
        if error:
            messagebox.showerror(APP_NAME, error, parent=self.root)
            return
        # Tk variables belong to the UI thread. Snapshot selections before the
        # worker starts so the installer never reads Tk state off-thread.
        self._install_plan = {
            "dest": self.install_dir.get().strip(),
            "theme": self.theme_var.get(),
            "language": self._lang,
            "desktop_shortcut": self.desktop_var.get(),
            "startmenu_shortcut": self.startmenu_var.get(),
            "scan_on_startup": self.scan_var.get(),
            "notifications": self.notif_var.get(),
        }
        self._installing = True
        self._show_page(4)
        self.next_btn.config(text="Installing…", fg=A["text_dim"])
        self.next_btn.set_enabled(False)
        self.back_btn.set_enabled(False)
        self.cancel_btn.set_enabled(False)
        threading.Thread(target=self._do_install, daemon=True).start()

    def _validate_destination(self):
        """Catch common target mistakes before the worker begins writing files."""
        raw = self.install_dir.get().strip()
        if not raw:
            return "Choose an installation folder."
        dest = Path(raw).expanduser()
        if not dest.is_absolute() or dest == Path(dest.anchor):
            return "Choose a folder, not a drive root."
        try:
            disk_root = dest.anchor or str(dest.parent)
            free = shutil.disk_usage(disk_root).free
            required = self._payload_size() + 30 * 1024 * 1024
            if free < required:
                return "There is not enough free space at the selected location."
        except OSError:
            pass
        return None

    def _payload_size(self):
        total = 0
        for path in Path(self.src_dir).rglob("*"):
            if path.is_file():
                try:
                    total += path.stat().st_size
                except OSError:
                    pass
        return total

    def _do_install(self):
        self._example_music_dir = None
        try:
            dest = self._install_plan["dest"]
            steps = [
                (t("installing", self._lang)+" (1/8)",  10, self._step_mkdir,     dest),
                (t("installing", self._lang)+" (2/8)",  25, self._step_copy_exe,  dest),
                (t("installing", self._lang)+" (3/8)",  40, self._step_copy_assets, dest),
                (t("installing", self._lang)+" (4/8)",  55, self._step_copy_example_music, dest),
                (t("installing", self._lang)+" (5/8)",  68, self._step_write_cfg, dest),
                (t("installing", self._lang)+" (6/8)",  78, self._step_shortcuts, dest),
                (t("installing", self._lang)+" (7/8)",  88, self._step_copy_uninstaller, dest),
                (t("installing", self._lang)+" (8/8)",  96, self._step_registry,  dest),
                (t("complete", self._lang),             100, lambda d: None,       dest),
            ]
            for msg, pct, fn, arg in steps:
                self._emit("status", msg, A["text"])
                self._emit("progress", pct)
                self._log(msg)
                fn(arg)

            self._log(t("log_done", self._lang))
            self._emit("complete")
        except Exception as e:
            self._emit("error", str(e))

    def _step_mkdir(self, dest):
        os.makedirs(dest, exist_ok=True)
        self._log(t("log_created", self._lang, path=dest))

    def _step_copy_exe(self, dest):
        exe_src = os.path.join(self.src_dir, APP_EXE)
        if not os.path.exists(exe_src):
            raise FileNotFoundError(t("err_no_exe", self._lang, exe=APP_EXE, path=exe_src))
        shutil.copy2(exe_src, os.path.join(dest, APP_EXE))
        self._log(t("log_copied", self._lang, f=APP_EXE))

    def _step_copy_assets(self, dest):
        for fname in ("PTMusic.png", "PTMusic.ico", "Montserrat-SemiBold.ttf"):
            src = os.path.join(self.src_dir, fname)
            if os.path.exists(src):
                shutil.copy2(src, os.path.join(dest, fname))
                self._log(t("log_copied", self._lang, f=fname))

    def _step_copy_example_music(self, dest):
        """Copy bundled example tracks into the install dir's ExampleMusic folder."""
        src_dir = os.path.join(self.src_dir, "examplemusic")
        if not os.path.exists(src_dir):
            self._log("  No example music bundled — skipping.")
            self._example_music_dir = None
            return
        out_dir = os.path.join(dest, "ExampleMusic")
        try:
            os.makedirs(out_dir, exist_ok=True)
            count = 0
            for fname in os.listdir(src_dir):
                s = os.path.join(src_dir, fname)
                if os.path.isfile(s):
                    shutil.copy2(s, os.path.join(out_dir, fname))
                    count += 1
            self._example_music_dir = out_dir if count else None
            self._log(f"  Copied {count} example track(s) to ExampleMusic")
        except Exception as e:
            self._example_music_dir = None
            self._log(f"  Warning: Could not copy example music ({e})")

    def _step_write_cfg(self, dest):
        # Never overwrite settings during an upgrade. In particular, this avoids
        # wiping a user's library, language, or playback preferences.
        cfg_path = Path(CONFIG_PATH)
        if cfg_path.exists():
            self._log("  Existing PTMusic settings kept")
            return

        # Write first-run settings for this Windows user.
        cfg = {
            "theme":            self._install_plan["theme"],
            "font_size":        9,
            "show_path_col":    True,
            "confirm_clear":    True,
            "scan_on_startup":  self._install_plan["scan_on_startup"],
            "tick_interval_ms": 400,
            "crossfade_ms":     0,
            "notifications":    self._install_plan["notifications"],
            "win_geometry":     "1180x760",
            "win_position":     "",
            "language":         self._install_plan["language"],
        }
        # If example music was bundled, tell PTMusic to auto-scan it on first launch
        if getattr(self, "_example_music_dir", None):
            cfg["first_run_scan_folder"] = self._example_music_dir
        with cfg_path.open("w", encoding="utf-8") as f:
            json.dump(cfg, f, indent=2)
        self._log(t("log_cfg", self._lang, path=cfg_path))

    def _step_shortcuts(self, dest):
        exe_path = os.path.join(dest, APP_EXE)
        ico_path = os.path.join(dest, "PTMusic.ico")

        if self._install_plan["desktop_shortcut"]:
            self._create_shortcut(
                os.path.join(os.path.expanduser("~"), "Desktop", "PTMusic.lnk"),
                exe_path, ico_path)
            self._log(t("log_desktop", self._lang))

        if self._install_plan["startmenu_shortcut"]:
            sm_dir = os.path.join(os.environ.get("APPDATA", ""),
                                  "Microsoft", "Windows", "Start Menu",
                                  "Programs", "Phoni Technology")
            os.makedirs(sm_dir, exist_ok=True)
            self._create_shortcut(
                os.path.join(sm_dir, "PTMusic.lnk"),
                exe_path, ico_path)
            self._log(t("log_startmenu", self._lang))

    def _step_copy_uninstaller(self, dest):
        """Install a self-contained uninstaller when running from a built setup EXE."""
        if not getattr(sys, "frozen", False):
            self._log("  Development run: uninstaller executable not created")
            return
        source = Path(sys.executable)
        target = Path(dest) / UNINSTALL_EXE
        shutil.copy2(source, target)
        self._log("  Created the uninstaller")

    def _create_shortcut(self, lnk_path, target, icon=""):
        try:
            import win32com.client
            shell = win32com.client.Dispatch("WScript.Shell")
            sc = shell.CreateShortCut(lnk_path)
            sc.Targetpath = target
            sc.IconLocation = icon
            sc.WorkingDirectory = os.path.dirname(target)
            sc.save()
        except ImportError:
            # Fallback: PowerShell
            ps = (
                f'$s=(New-Object -COM WScript.Shell).CreateShortcut("{lnk_path}");'
                f'$s.TargetPath="{target}";'
                f'$s.IconLocation="{icon}";'
                f'$s.WorkingDirectory="{os.path.dirname(target)}";'
                f'$s.Save()'
            )
            subprocess.run(
                ["powershell", "-WindowStyle", "Hidden", "-Command", ps],
                check=True, capture_output=True)

    def _step_registry(self, dest):
        try:
            exe_path = os.path.join(dest, APP_EXE)
            ico_path = os.path.join(dest, "PTMusic.ico")
            uninstaller = os.path.join(dest, UNINSTALL_EXE)
            key = winreg.CreateKeyEx(winreg.HKEY_CURRENT_USER, REG_KEY, 0,
                                     winreg.KEY_WRITE)
            winreg.SetValueEx(key, "DisplayName",     0, winreg.REG_SZ, APP_NAME)
            winreg.SetValueEx(key, "DisplayVersion",  0, winreg.REG_SZ, APP_VERSION)
            winreg.SetValueEx(key, "Publisher",       0, winreg.REG_SZ, APP_PUBLISHER)
            winreg.SetValueEx(key, "URLInfoAbout",    0, winreg.REG_SZ, APP_URL)
            winreg.SetValueEx(key, "InstallLocation", 0, winreg.REG_SZ, dest)
            winreg.SetValueEx(key, "DisplayIcon",     0, winreg.REG_SZ, ico_path)
            winreg.SetValueEx(key, "UninstallString", 0, winreg.REG_SZ,
                              f'"{uninstaller}" --uninstall --install-dir "{dest}"')
            winreg.SetValueEx(key, "NoModify",        0, winreg.REG_DWORD, 1)
            winreg.SetValueEx(key, "NoRepair",        0, winreg.REG_DWORD, 1)
            winreg.CloseKey(key)
            self._log(t("log_registry", self._lang))
        except Exception as e:
            self._log(t("log_reg_warn", self._lang, e=e))

        # Register .ptm file association so double-click opens PTMusic
        try:
            exe_path = os.path.join(dest, APP_EXE)
            ico_path = os.path.join(dest, "PTMusic.ico")

            # Progid: PTMusic.Track
            progid_key = winreg.CreateKeyEx(winreg.HKEY_CURRENT_USER,
                                            CLASSES_KEY + r"\PTMusic.Track", 0, winreg.KEY_WRITE)
            winreg.SetValueEx(progid_key, "", 0, winreg.REG_SZ, "PTMusic Track")
            winreg.CloseKey(progid_key)

            icon_key = winreg.CreateKeyEx(winreg.HKEY_CURRENT_USER,
                                          CLASSES_KEY + r"\PTMusic.Track\DefaultIcon", 0, winreg.KEY_WRITE)
            winreg.SetValueEx(icon_key, "", 0, winreg.REG_SZ, ico_path)
            winreg.CloseKey(icon_key)

            cmd_key = winreg.CreateKeyEx(winreg.HKEY_CURRENT_USER,
                                         CLASSES_KEY + r"\PTMusic.Track\shell\open\command", 0, winreg.KEY_WRITE)
            winreg.SetValueEx(cmd_key, "", 0, winreg.REG_SZ, f'"{exe_path}" "%1"')
            winreg.CloseKey(cmd_key)

            # Associate .ptm extension with the progid
            ext_key = winreg.CreateKeyEx(winreg.HKEY_CURRENT_USER,
                                         CLASSES_KEY + r"\.ptm", 0, winreg.KEY_WRITE)
            winreg.SetValueEx(ext_key, "", 0, winreg.REG_SZ, "PTMusic.Track")
            winreg.CloseKey(ext_key)

            # Notify Windows Explorer of the new file association
            import ctypes
            ctypes.windll.shell32.SHChangeNotify(0x08000000, 0x0000, None, None)

            self._log("  .ptm file association registered")
        except Exception as e:
            self._log(f"  Warning: Could not register .ptm association ({e})")

    def _install_done(self):
        self._installing = False
        self.install_status.config(text=t("complete", self._lang), fg=A["green"])
        self._show_page(5)

    def _install_failed(self, error):
        self._installing = False
        self._append_log(t("log_error", self._lang, e=error))
        self.install_status.config(text=t("install_fail", self._lang), fg=A["danger"])
        self.next_btn.config(text=t("btn_close", self._lang), fg=A["danger"])
        self.next_btn.cmd = self.root.destroy
        self.next_btn.set_enabled(True)

    # ── PAGE 5: DONE ──────────────────────────────────────────────────────
    def _page_done(self, f):
        self._header(f, t("install_done_t", self._lang), t("install_done_s", self._lang))
        body = tk.Frame(f, bg=A["glass"]); body.pack(fill="both", expand=True, padx=24, pady=20)

        tk.Label(body, text="✔", bg=A["glass"], fg=A["green"],
                 font=("Segoe UI", 48)).pack(pady=(0,8))
        tk.Label(body, text=t("install_done_b", self._lang, v=APP_VERSION),
                 bg=A["glass"], fg=A["accent_bright"],
                 font=("Segoe UI Light", 16)).pack()
        tk.Label(body, text=t("publisher", self._lang),
                 bg=A["glass"], fg=A["text_dim"], font=FONT_SMALL).pack(pady=(4,20))
        tk.Frame(body, bg=A["border"], height=1).pack(fill="x")

        self.launch_var = tk.BooleanVar(value=True)
        tk.Checkbutton(body, text=t("launch_now", self._lang), variable=self.launch_var,
                       bg=A["glass"], fg=A["text"],
                       activebackground=A["glass"], activeforeground=A["accent"],
                       selectcolor=A["glass_dark"],
                       font=FONT_UI).pack(anchor="w", pady=12)

        # Override close to optionally launch
        self.next_btn.cmd = self._finish

    def _finish(self):
        if self.launch_var.get():
            exe = os.path.join(self.install_dir.get(), APP_EXE)
            if os.path.exists(exe):
                subprocess.Popen([exe])
        self.root.destroy()


# ══════════════════════════════════════════════════════════════════════════
def _argument_value(name):
    """Read a simple command-line value without adding a runtime dependency."""
    try:
        return sys.argv[sys.argv.index(name) + 1]
    except (ValueError, IndexError):
        return None


def _remove_registry_entries():
    try:
        winreg.DeleteKey(winreg.HKEY_CURRENT_USER, REG_KEY)
    except FileNotFoundError:
        pass
    except OSError:
        pass

    # Remove only PTMusic-owned classes. The extension itself is only removed
    # when it still points at PTMusic, so another app's later choice survives.
    try:
        ext_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, CLASSES_KEY + r"\.ptm")
        current, _ = winreg.QueryValueEx(ext_key, "")
        winreg.CloseKey(ext_key)
        if current == "PTMusic.Track":
            winreg.DeleteKey(winreg.HKEY_CURRENT_USER, CLASSES_KEY + r"\.ptm")
    except OSError:
        pass
    for suffix in (r"\PTMusic.Track\shell\open\command",
                   r"\PTMusic.Track\shell\open",
                   r"\PTMusic.Track\shell",
                   r"\PTMusic.Track\DefaultIcon",
                   r"\PTMusic.Track"):
        try:
            winreg.DeleteKey(winreg.HKEY_CURRENT_USER, CLASSES_KEY + suffix)
        except OSError:
            pass


def _defer_self_delete(executable, install_dir):
    """Windows cannot delete a running EXE, so let a tiny detached command do it."""
    command = (
        f'ping 127.0.0.1 -n 3 > nul & del /f /q "{executable}" '
        f'& rmdir "{install_dir}"'
    )
    flags = getattr(subprocess, "CREATE_NO_WINDOW", 0)
    subprocess.Popen(["cmd.exe", "/c", command],
                     creationflags=flags, close_fds=True)


def run_uninstaller(install_dir):
    """Remove files installed by PTMusic while retaining profile-based settings."""
    destination = Path(install_dir).resolve()
    app_path = destination / APP_EXE
    if not app_path.is_file():
        messagebox.showerror(APP_NAME, "PTMusic was not found in this installation folder.")
        return

    if not messagebox.askyesno(
        "Uninstall PTMusic",
        "Remove PTMusic from this computer?\n\nYour music and PTMusic settings will be kept.",
    ):
        return

    try:
        for filename in (APP_EXE, "PTMusic.png", "PTMusic.ico", "Montserrat-SemiBold.ttf"):
            (destination / filename).unlink(missing_ok=True)

        # Remove the bundled samples only when they still match files carried by
        # this installer; unrelated music in the install directory is left alone.
        bundled_music = Path(_source_dir()) / "examplemusic"
        installed_music = destination / "ExampleMusic"
        if bundled_music.is_dir() and installed_music.is_dir():
            for source in bundled_music.iterdir():
                if source.is_file():
                    (installed_music / source.name).unlink(missing_ok=True)
            try:
                installed_music.rmdir()
            except OSError:
                pass

        _remove_registry_entries()
        desktop_shortcut = Path.home() / "Desktop" / "PTMusic.lnk"
        start_shortcut = (Path(os.environ.get("APPDATA", "")) / "Microsoft" / "Windows" /
                          "Start Menu" / "Programs" / "Phoni Technology" / "PTMusic.lnk")
        desktop_shortcut.unlink(missing_ok=True)
        start_shortcut.unlink(missing_ok=True)
        (destination / MANIFEST_NAME).unlink(missing_ok=True)
        _defer_self_delete(Path(sys.executable), destination)
        messagebox.showinfo("PTMusic", "PTMusic has been removed. Your settings were kept.")
    except OSError as error:
        messagebox.showerror("PTMusic", f"PTMusic could not be fully removed:\n{error}")


def _source_dir():
    return sys._MEIPASS if getattr(sys, "_MEIPASS", None) else os.path.dirname(os.path.abspath(__file__))


if __name__ == "__main__":
    if sys.platform != "win32":
        print("PTMusic Installer is for Windows only.")
        sys.exit(1)
    if "--uninstall" in sys.argv:
        root = tk.Tk()
        root.withdraw()
        run_uninstaller(_argument_value("--install-dir") or DEFAULT_DIR)
        root.destroy()
    else:
        Installer()
