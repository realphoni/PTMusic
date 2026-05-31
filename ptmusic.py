"""
PTMusic
Phoni Technology 2026
"""

import os
import json
import threading
import platform
import random
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from pathlib import Path

try:
    import pygame
    pygame.mixer.init()
    PYGAME_AVAILABLE = True
except ImportError:
    PYGAME_AVAILABLE = False

try:
    from mutagen import File as MutagenFile
    MUTAGEN_AVAILABLE = True
except ImportError:
    MUTAGEN_AVAILABLE = False


A = {
    "win_bg":        "#6f8fb1",
    "glass_dark":    "#d7e7f7",
    "glass":         "#edf5fc",
    "glass_mid":     "#c8def2",
    "glass_light":   "#f5fbff",
    "glass_lighter": "#ffffff",
    "border":        "#7aa7d9",
    "border_glow":   "#bfe2ff",
    "accent":        "#3b8edb",
    "accent_bright": "#0b5cad",
    "accent_hot":    "#1f7de2",
    "title_bar":     "#5d89c9",
    "title_bar2":    "#8fb7ea",
    "tb_border":     "#4f79b7",
    "btn":           "#eaf3fc",
    "btn_top":       "#ffffff",
    "btn_hover":     "#d9ecff",
    "btn_press":     "#bdd9f5",
    "btn_border":    "#7aa7d9",
    "text":          "#1d3557",
    "text_dim":      "#56708f",
    "text_bright":   "#003b73",
    "sel":           "#cfe8ff",
    "sel_border":    "#3399ff",
    "prog_bg":       "#c7dff5",
    "prog_fill":     "#3a95e8",
    "prog_bright":   "#7bc3ff",
    "danger":        "#c03a3a",
    "danger_hover":  "#e04848",
    "green":         "#2fa34f",
    "sidebar":       "#dce9f7",
    "sidebar_sect":  "#c7dbf2",
    "row_alt":       "#eef6fd",
}

# ── FONT LOADER ───────────────────────────────────────────────────────────
def _find_montserrat_ttf():
    """Return path to Montserrat TTF if it exists next to script/exe, else None."""
    try:
        import sys as _fs, os as _fo
        base = getattr(_fs, "_MEIPASS", _fo.path.dirname(_fo.path.abspath(__file__)))
        for name in ("Montserrat-SemiBold.ttf", "Montserrat-Bold.ttf", "Montserrat.ttf"):
            p = _fo.path.join(base, name)
            if _fo.path.exists(p):
                return p
    except Exception:
        pass
    return None

_MONT_TTF = _find_montserrat_ttf()   # TTF path or None

# Fonts default to Segoe UI; switched to Montserrat after Tk init (see _init_fonts)
FONT_UI     = ("Segoe UI", 9)
FONT_BOLD   = ("Segoe UI", 9,  "bold")
FONT_SMALL  = ("Segoe UI", 8)
FONT_LABEL  = ("Segoe UI", 7,  "bold")
FONT_MONO   = ("Consolas", 9)
FONT_TITLE  = ("Segoe UI", 10, "bold")
FONT_NOW    = ("Segoe UI", 13)
FONT_NOW_SM = ("Segoe UI", 8)

def _init_fonts():
    """Call AFTER tk.Tk() is created. Loads Montserrat and updates all FONT_* globals."""
    global FONT_UI, FONT_BOLD, FONT_SMALL, FONT_LABEL, FONT_TITLE, FONT_NOW, FONT_NOW_SM
    if not _MONT_TTF:
        return  # no TTF found, keep Segoe UI
    try:
        import tkinter.font as tkfont
        # Register the TTF with Tk via the font file
        # Tk 8.6+ supports loading font files directly
        fam = None
        try:
            # Try Tk's built-in font loading (works on Tk 8.6+)
            tmp = tkfont.Font(file=_MONT_TTF)
            fam = tmp.actual()["family"]
            tmp.delete()
        except Exception:
            pass

        if not fam:
            # Fallback: use ctypes to register with GDI then let Tk pick it up
            try:
                import ctypes
                ctypes.windll.gdi32.AddFontResourceExW(_MONT_TTF, 0x10, 0)
                # Tell Tk to refresh its font list
                import subprocess
                subprocess.Popen(["FSSYNC"], shell=True, stderr=subprocess.DEVNULL)
            except Exception:
                pass
            fam = "Montserrat SemiBold"

        FONT_UI     = (fam, 9)
        FONT_BOLD   = (fam, 9,  "bold")
        FONT_SMALL  = (fam, 8)
        FONT_LABEL  = (fam, 7,  "bold")
        FONT_TITLE  = (fam, 10, "bold")
        FONT_NOW    = (fam, 13)
        FONT_NOW_SM = (fam, 8)
    except Exception:
        pass  # silently keep Segoe UI on any error


# ── THEMES ────────────────────────────────────────────────────────────────
THEMES = {
    "Aero Light": {
        "win_bg":"#6f8fb1","glass_dark":"#d7e7f7","glass":"#edf5fc",
        "glass_mid":"#c8def2","glass_light":"#f5fbff","glass_lighter":"#ffffff",
        "border":"#7aa7d9","border_glow":"#bfe2ff","accent":"#3b8edb",
        "accent_bright":"#0b5cad","accent_hot":"#1f7de2",
        "title_bar":"#5d89c9","title_bar2":"#8fb7ea","tb_border":"#4f79b7",
        "btn":"#eaf3fc","btn_top":"#ffffff","btn_hover":"#d9ecff",
        "btn_press":"#bdd9f5","btn_border":"#7aa7d9",
        "text":"#1d3557","text_dim":"#56708f","text_bright":"#003b73",
        "sel":"#cfe8ff","sel_border":"#3399ff",
        "prog_bg":"#c7dff5","prog_fill":"#3a95e8","prog_bright":"#7bc3ff",
        "danger":"#c03a3a","danger_hover":"#e04848","green":"#2fa34f",
        "sidebar":"#dce9f7","sidebar_sect":"#c7dbf2","row_alt":"#eef6fd",
    },
    "Aero Dark": {
        "win_bg":"#0a1628","glass_dark":"#0d1f3c","glass":"#132840",
        "glass_mid":"#1a3a58","glass_light":"#224d72","glass_lighter":"#2d6494",
        "border":"#1e5a8a","border_glow":"#2e87cc","accent":"#3ea6e0",
        "accent_bright":"#7fd4ff","accent_hot":"#00aaff",
        "title_bar":"#0f2340","title_bar2":"#162e50","tb_border":"#1a4a7a",
        "btn":"#163352","btn_top":"#1e4570","btn_hover":"#1f4d7a",
        "btn_press":"#0c1f33","btn_border":"#2a6aaa",
        "text":"#ddeeff","text_dim":"#6a9cbb","text_bright":"#b8dff5",
        "sel":"#164872","sel_border":"#3ab0ff",
        "prog_bg":"#081828","prog_fill":"#1a8fd1","prog_bright":"#4dc8ff",
        "danger":"#c0304a","danger_hover":"#e03050","green":"#00e080",
        "sidebar":"#0e2238","sidebar_sect":"#0a1a2c","row_alt":"#0f2235",
    },


    "Mint": {
        "win_bg":"#e8f5e9","glass_dark":"#c8e6c9","glass":"#f1f8f1",
        "glass_mid":"#dcedc8","glass_light":"#f9fbe7","glass_lighter":"#ffffff",
        "border":"#81c784","border_glow":"#a5d6a7","accent":"#388e3c",
        "accent_bright":"#2e7d32","accent_hot":"#43a047",
        "title_bar":"#388e3c","title_bar2":"#43a047","tb_border":"#2e7d32",
        "btn":"#f1f8f1","btn_top":"#ffffff","btn_hover":"#dcedc8",
        "btn_press":"#c8e6c9","btn_border":"#81c784",
        "text":"#1b5e20","text_dim":"#558b2f","text_bright":"#003300",
        "sel":"#c8e6c9","sel_border":"#43a047",
        "prog_bg":"#c8e6c9","prog_fill":"#388e3c","prog_bright":"#81c784",
        "danger":"#c62828","danger_hover":"#e53935","green":"#00695c",
        "sidebar":"#dcedc8","sidebar_sect":"#c8e6c9","row_alt":"#f1f8e9",
    },
    # ── SECRET: unlocked by typing "MORE THEMES PLS" ──────────────────────
    "Royale Noir": {
        "win_bg":"#0e0414","glass_dark":"#160b24","glass":"#1e1030",
        "glass_mid":"#2a1545","glass_light":"#38206a","glass_lighter":"#4a2d80",
        "border":"#5c2d8a","border_glow":"#9b4dca","accent":"#b06ee8",
        "accent_bright":"#d4a0ff","accent_hot":"#c060ff",
        "title_bar":"#12091e","title_bar2":"#1e0f30","tb_border":"#5c2d8a",
        "btn":"#1e1030","btn_top":"#2a1545","btn_hover":"#2a1545",
        "btn_press":"#0e0414","btn_border":"#5c2d8a",
        "text":"#ecdcff","text_dim":"#9966cc","text_bright":"#f0d0ff",
        "sel":"#3d1a6e","sel_border":"#b06ee8",
        "prog_bg":"#0e0414","prog_fill":"#7b2fbe","prog_bright":"#b06ee8",
        "danger":"#cc2255","danger_hover":"#ee3366","green":"#44cc88",
        "sidebar":"#160b24","sidebar_sect":"#0e0414","row_alt":"#1a0d2e",
    },
}

# Names shown in the settings dropdown (Royale Noir is hidden until unlocked)
PUBLIC_THEMES = ["Aero Light", "Aero Dark", "Mint"]

# ── CONFIG ─────────────────────────────────────────────────────────────────
import sys as _cfg_sys, os as _cfg_os
_cfg_base = getattr(_cfg_sys, "_MEIPASS",
                    _cfg_os.path.dirname(_cfg_os.path.abspath(__file__)))
CONFIG_PATH = _cfg_os.path.join(
    _cfg_os.path.expanduser("~"), ".ptmusic_config.json")

DEFAULTS = {
    "theme":            "Aero Light",
    "font_size":        9,
    "show_path_col":    True,
    "confirm_clear":    True,
    "scan_on_startup":  True,
    "tick_interval_ms": 400,
    "crossfade_ms":     0,
}

def load_config():
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        # Fill in any missing keys with defaults
        for k, v in DEFAULTS.items():
            data.setdefault(k, v)
        return data
    except Exception:
        return dict(DEFAULTS)

def save_config(cfg: dict):
    try:
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(cfg, f, indent=2)
    except Exception:
        pass

SUPPORTED_EXT = {'.mp3', '.wav', '.mid', '.midi', '.m4a', '.flac', '.wma'}

def get_all_drives():
    sys = platform.system()
    if sys == "Windows":
        import string, ctypes
        mask = ctypes.windll.kernel32.GetLogicalDrives()
        drives = []
        for l in string.ascii_uppercase:
            if mask & 1: drives.append(f"{l}:\\")
            mask >>= 1
        return drives or ["C:\\"]
    elif sys == "Darwin":
        vols = list(Path("/Volumes").iterdir()) if Path("/Volumes").exists() else []
        return [str(v) for v in vols if v.is_dir()] or [str(Path.home())]
    else:
        drives = ["/"]
        for mp in ["/media", "/mnt", "/run/media"]:
            p = Path(mp)
            if p.exists():
                for s in p.iterdir():
                    if s.is_dir(): drives.append(str(s))
        return drives


def scan_paths(paths, callback=None, stop_event=None):
    SKIP = {'$Recycle.Bin','System Volume Information','Windows',
            'Program Files','Program Files (x86)','ProgramData',
            'AppData','Recovery','.git'}
    for root_path in paths:
        for root, dirs, files in os.walk(root_path, followlinks=False):
            dirs[:] = [d for d in dirs
                       if not d.startswith('.') and d not in SKIP]
            if stop_event and stop_event.is_set():
                return
            for fname in files:
                ext = Path(fname).suffix.lower()
                if ext in SUPPORTED_EXT:
                    full = os.path.join(root, fname)
                    try:    size = os.path.getsize(full)
                    except: size = 0
                    info = {
                        "path":   full,
                        "title":  Path(fname).stem,
                        "artist": "—", "album": "—",
                        "dur":    "—", "dur_sec": 0,
                        "ext":    ext.lstrip('.').upper(),
                        "size":   size,
                    }
                    if MUTAGEN_AVAILABLE:
                        _meta(info)
                    if callback:
                        callback(info)


def _meta(info):
    try:
        audio = MutagenFile(info["path"], easy=True)
        if not audio: return
        if audio.tags:
            t = audio.tags
            info["title"]  = str(t.get("title",  [info["title"]])[0])
            info["artist"] = str(t.get("artist", ["—"])[0])
            info["album"]  = str(t.get("album",  ["—"])[0])
        if hasattr(audio, 'info') and hasattr(audio.info, 'length'):
            s = int(audio.info.length)
            info["dur"] = f"{s//60}:{s%60:02d}"
            info["dur_sec"] = s
    except: pass


def fmt_size(b):
    if b < 1024:    return f"{b} B"
    if b < 1048576: return f"{b/1024:.1f} KB"
    return f"{b/1048576:.1f} MB"


class AeroBtn(tk.Label):
    """Aero-style button using tk.Label — no Canvas, no Tcl race conditions."""
    def __init__(self, parent, text="", icon="", cmd=None,
                 w=88, h=26, danger=False, bg_override=None, **kw):
        # strip kwargs that don't apply to Label
        kw.pop('square', None)
        self._bg = bg_override or A["win_bg"]
        self.cmd    = cmd
        self.text   = text
        self.icon   = icon
        self.danger = danger
        self._w = w; self._h = h
        self._hov = False; self._press = False

        lbl = (icon + (" " if icon and text else "") + text)
        super().__init__(parent, text=lbl, font=FONT_UI,
                         bg=A["btn"], fg=A["text"],
                         relief="flat", bd=0,
                         padx=8, pady=3,
                         cursor="hand2", **kw)
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
        if self.cmd: self.cmd()

    def _refresh(self):
        if self._press:
            bg = A["btn_press"]; fg = A["text_dim"]
        elif self._hov:
            bg = A["btn_hover"]; fg = A["accent_bright"]
        else:
            bg = A["btn"];       fg = A["text"]
        if self.danger:
            fg = A["danger_hover"] if self._hov else A["danger"]
        self.config(bg=bg, fg=fg,
                    highlightbackground=A["btn_border"],
                    highlightthickness=1)

    def _draw(self):
        """Called by playback code to update icon/text after init."""
        lbl = (self.icon + (" " if self.icon and self.text else "") + self.text)
        self.config(text=lbl)
        self._refresh()


class GlassPanel(tk.Frame):
    def __init__(self, parent, **kw):
        kw.setdefault("bg", A["glass"])
        kw.setdefault("highlightthickness", 1)
        kw.setdefault("highlightbackground", A["border"])
        super().__init__(parent, **kw)


class FolderList(tk.Frame):
    def __init__(self, parent, on_change=None, **kw):
        kw.setdefault("bg", A["sidebar"])
        super().__init__(parent, **kw)
        self.on_change = on_change
        self.folders: list[str] = []
        self._build()

    def _build(self):
        # Listbox with scrollbar
        box_frame = tk.Frame(self, bg=A["glass_dark"],
                             highlightthickness=1,
                             highlightbackground=A["border"])
        box_frame.pack(fill="both", expand=True, padx=0, pady=0)

        self.lb = tk.Listbox(box_frame,
                             bg=A["glass_dark"], fg=A["text"],
                             selectbackground=A["sel"],
                             selectforeground=A["accent_bright"],
                             activestyle="none",
                             font=FONT_SMALL, relief="flat",
                             highlightthickness=0, bd=0,
                             height=6)
        vsb = ttk.Scrollbar(box_frame, orient="vertical", command=self.lb.yview)
        self.lb.configure(yscrollcommand=vsb.set)
        self.lb.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")

        # Buttons
        btns = tk.Frame(self, bg=A["sidebar"])
        btns.pack(fill="x", pady=(3,0))
        AeroBtn(btns, icon="＋", text="Add Folder",
                cmd=self._add, w=120, h=24,
                bg_override=A["sidebar"]).pack(side="left", padx=(0,3))
        AeroBtn(btns, icon="−", text="Remove",
                cmd=self._remove, w=88, h=24, danger=True,
                bg_override=A["sidebar"]).pack(side="left")

    def _add(self):
        path = filedialog.askdirectory(title="Select Folder to Scan")
        if path and path not in self.folders:
            self.folders.append(path)
            self.lb.insert("end", path)
            if self.on_change: self.on_change()

    def _remove(self):
        sel = self.lb.curselection()
        if not sel: return
        idx = sel[0]
        self.folders.pop(idx)
        self.lb.delete(idx)
        if self.on_change: self.on_change()

    def get_folders(self): return list(self.folders)

    def set_placeholder(self):
        self.lb.delete(0, "end")
        self.lb.insert("end", "  (all drives)")



class SettingsWindow:
    """Modal settings dialog with tabs for Appearance, Playback, Library."""
    def __init__(self, app):
        self.app = app
        self.cfg = dict(app.cfg)  # working copy

        win = tk.Toplevel(app.root)
        win.title("PTMusic Settings")
        win.geometry("520x440")
        win.resizable(False, False)
        win.configure(bg=A["glass"])
        win.grab_set()
        win.transient(app.root)
        self.win = win

        # Centre over parent
        app.root.update_idletasks()
        px = app.root.winfo_x() + app.root.winfo_width()//2 - 260
        py = app.root.winfo_y() + app.root.winfo_height()//2 - 220
        win.geometry(f"+{px}+{py}")

        self._build()

    def _build(self):
        win = self.win

        # Title bar strip
        hdr = tk.Frame(win, bg=A["title_bar"], height=36)
        hdr.pack(fill="x")
        hdr.pack_propagate(False)
        tk.Label(hdr, text="⚙  Settings", bg=A["title_bar"],
                 fg=A["accent_bright"], font=FONT_TITLE).pack(side="left", padx=12, pady=6)
        tk.Frame(win, bg=A["tb_border"], height=1).pack(fill="x")

        # Tab bar
        tab_bar = tk.Frame(win, bg=A["glass_dark"])
        tab_bar.pack(fill="x")
        tk.Frame(win, bg=A["border"], height=1).pack(fill="x")

        # Content area
        self.content = tk.Frame(win, bg=A["glass"])
        self.content.pack(fill="both", expand=True, padx=12, pady=8)

        # Bottom buttons
        tk.Frame(win, bg=A["border"], height=1).pack(fill="x")
        btn_bar = tk.Frame(win, bg=A["glass_dark"])
        btn_bar.pack(fill="x", padx=10, pady=6)
        AeroBtn(btn_bar, text="Apply & Close", icon="✔",
                cmd=self._apply, w=130, h=26,
                bg_override=A["glass_dark"]).pack(side="right", padx=(4,0))
        AeroBtn(btn_bar, text="Cancel", icon="✖",
                cmd=self.win.destroy, w=80, h=26, danger=True,
                bg_override=A["glass_dark"]).pack(side="right")
        AeroBtn(btn_bar, text="Reset Defaults", icon="↺",
                cmd=self._reset, w=120, h=26,
                bg_override=A["glass_dark"]).pack(side="left")

        # Build tabs
        self.tab_btns = {}
        self.tabs = {}
        for name in ("Appearance", "Playback", "Library", "About"):
            btn = tk.Label(tab_bar, text=name, font=FONT_UI,
                           bg=A["glass_dark"], fg=A["text_dim"],
                           padx=14, pady=6, cursor="hand2")
            btn.pack(side="left")
            btn.bind("<Button-1>", lambda e, n=name: self._show_tab(n))
            self.tab_btns[name] = btn

            frame = tk.Frame(self.content, bg=A["glass"])
            self.tabs[name] = frame

        self._build_appearance()
        self._build_playback()
        self._build_library_tab()
        self._build_about()
        self._show_tab("Appearance")

    def _show_tab(self, name):
        for n, f in self.tabs.items():
            f.pack_forget()
        for n, b in self.tab_btns.items():
            b.config(bg=A["glass_dark"], fg=A["text_dim"])
        self.tabs[name].pack(fill="both", expand=True)
        self.tab_btns[name].config(bg=A["glass_mid"], fg=A["accent_bright"])

    # ── APPEARANCE TAB ──────────────────────────────────────────
    def _build_appearance(self):
        f = self.tabs["Appearance"]

        def row(label):
            r = tk.Frame(f, bg=A["glass"])
            r.pack(fill="x", pady=5)
            tk.Label(r, text=label, bg=A["glass"], fg=A["text"],
                     font=FONT_UI, width=18, anchor="w").pack(side="left")
            return r

        # Theme picker
        r = row("Theme:")
        self.theme_var = tk.StringVar(value=self.cfg["theme"])
        # Show public themes + Royale Noir only if already unlocked
        visible = list(PUBLIC_THEMES)
        if self.cfg.get("theme") == "Royale Noir" or self.cfg.get("royale_noir_unlocked"):
            visible.append("Royale Noir")
        theme_names = visible
        om = ttk.OptionMenu(r, self.theme_var, self.cfg["theme"], *theme_names,
                            command=self._preview_theme)
        om.config(width=20)
        om.pack(side="left", padx=4)

        # Theme preview swatch row
        self.swatch_frame = tk.Frame(f, bg=A["glass"])
        self.swatch_frame.pack(fill="x", pady=(0,8))
        self._draw_swatches(self.cfg["theme"])

        tk.Frame(f, bg=A["border"], height=1).pack(fill="x", pady=4)

        # Font size
        r = row("Font size:")
        self.font_var = tk.IntVar(value=self.cfg["font_size"])
        for size in (8, 9, 10, 11, 12):
            tk.Radiobutton(r, text=str(size), variable=self.font_var, value=size,
                           bg=A["glass"], fg=A["text"],
                           activebackground=A["glass"],
                           selectcolor=A["glass_dark"],
                           font=FONT_SMALL).pack(side="left", padx=3)

        tk.Frame(f, bg=A["border"], height=1).pack(fill="x", pady=4)

        # Show/hide columns
        r = row("Show path column:")
        self.path_col_var = tk.BooleanVar(value=self.cfg["show_path_col"])
        tk.Checkbutton(r, variable=self.path_col_var,
                       bg=A["glass"], activebackground=A["glass"],
                       selectcolor=A["glass_dark"]).pack(side="left")

    def _draw_swatches(self, theme_name):
        for w in self.swatch_frame.winfo_children():
            w.destroy()
        palette = THEMES.get(theme_name, {})
        swatch_keys = ["win_bg","glass","accent","accent_bright",
                       "btn","text","prog_fill","danger","green","sidebar"]
        tk.Label(self.swatch_frame, text="Preview:", bg=A["glass"],
                 fg=A["text_dim"], font=FONT_SMALL).pack(side="left", padx=(0,6))
        for key in swatch_keys:
            col = palette.get(key, "#888888")
            tk.Label(self.swatch_frame, bg=col, width=3,
                     relief="solid", bd=1).pack(side="left", padx=1, pady=4)

    def _preview_theme(self, name):
        self._draw_swatches(name)

    # ── PLAYBACK TAB ────────────────────────────────────────────
    def _build_playback(self):
        f = self.tabs["Playback"]

        def row(label):
            r = tk.Frame(f, bg=A["glass"])
            r.pack(fill="x", pady=6)
            tk.Label(r, text=label, bg=A["glass"], fg=A["text"],
                     font=FONT_UI, width=22, anchor="w").pack(side="left")
            return r

        r = row("Progress update (ms):")
        self.tick_var = tk.IntVar(value=self.cfg["tick_interval_ms"])
        tk.Scale(r, variable=self.tick_var, from_=100, to=1000,
                 orient="horizontal", length=200, resolution=50,
                 bg=A["glass"], fg=A["text"],
                 troughcolor=A["prog_bg"],
                 highlightthickness=0,
                 activebackground=A["accent_hot"]
                 ).pack(side="left", padx=4)
        lbl = tk.Label(r, textvariable=self.tick_var, bg=A["glass"],
                       fg=A["text_dim"], font=FONT_MONO, width=5)
        lbl.pack(side="left")

        tk.Frame(f, bg=A["border"], height=1).pack(fill="x", pady=4)

        r = row("Crossfade (ms):")
        self.xfade_var = tk.IntVar(value=self.cfg["crossfade_ms"])
        tk.Scale(r, variable=self.xfade_var, from_=0, to=5000,
                 orient="horizontal", length=200, resolution=100,
                 bg=A["glass"], fg=A["text"],
                 troughcolor=A["prog_bg"],
                 highlightthickness=0,
                 activebackground=A["accent_hot"]
                 ).pack(side="left", padx=4)
        tk.Label(r, textvariable=self.xfade_var, bg=A["glass"],
                 fg=A["text_dim"], font=FONT_MONO, width=5).pack(side="left")
        tk.Label(r, text="(0 = off)", bg=A["glass"],
                 fg=A["text_dim"], font=FONT_SMALL).pack(side="left", padx=4)

        tk.Frame(f, bg=A["border"], height=1).pack(fill="x", pady=4)

        r = row("Scan on startup:")
        self.startup_var = tk.BooleanVar(value=self.cfg["scan_on_startup"])
        tk.Checkbutton(r, variable=self.startup_var,
                       bg=A["glass"], activebackground=A["glass"],
                       selectcolor=A["glass_dark"]).pack(side="left")

    # ── LIBRARY TAB ─────────────────────────────────────────────
    def _build_library_tab(self):
        f = self.tabs["Library"]

        def row(label):
            r = tk.Frame(f, bg=A["glass"])
            r.pack(fill="x", pady=6)
            tk.Label(r, text=label, bg=A["glass"], fg=A["text"],
                     font=FONT_UI, width=22, anchor="w").pack(side="left")
            return r

        r = row("Confirm before clearing:")
        self.confirm_var = tk.BooleanVar(value=self.cfg["confirm_clear"])
        tk.Checkbutton(r, variable=self.confirm_var,
                       bg=A["glass"], activebackground=A["glass"],
                       selectcolor=A["glass_dark"]).pack(side="left")

        tk.Frame(f, bg=A["border"], height=1).pack(fill="x", pady=4)

        r = row("Config file location:")
        tk.Label(r, text=CONFIG_PATH, bg=A["glass"], fg=A["text_dim"],
                 font=FONT_SMALL, wraplength=320, justify="left"
                 ).pack(side="left", padx=4)

        tk.Frame(f, bg=A["border"], height=1).pack(fill="x", pady=4)

        AeroBtn(f, text="Open config folder", icon="📁",
                cmd=self._open_cfg_folder, w=160, h=26,
                bg_override=A["glass"]).pack(anchor="w", pady=4)

    def _open_cfg_folder(self):
        import subprocess, sys
        folder = os.path.dirname(CONFIG_PATH)
        if sys.platform == "win32":
            subprocess.Popen(["explorer", folder])
        elif sys.platform == "darwin":
            subprocess.Popen(["open", folder])
        else:
            subprocess.Popen(["xdg-open", folder])

    # ── ABOUT TAB ───────────────────────────────────────────────
    def _build_about(self):
        f = self.tabs["About"]
        tk.Label(f, text="PTMusic", bg=A["glass"],
                 fg=A["accent_bright"], font=("Segoe UI Light", 22)).pack(pady=(20,4))
        tk.Label(f, text="Version 26.6.0", bg=A["glass"],
                 fg=A["text_dim"], font=FONT_UI).pack()
        tk.Label(f, text="Phoni Technology  ·  2026", bg=A["glass"],
                 fg=A["text_dim"], font=FONT_SMALL).pack(pady=(2,16))
        tk.Frame(f, bg=A["border"], height=1).pack(fill="x")
        tk.Label(f,
                 text="Supports MP3 · FLAC · WAV · M4A · MIDI · WMA\n"
                      "Built with Python, Tkinter, pygame, mutagen, Pillow",
                 bg=A["glass"], fg=A["text_dim"],
                 font=FONT_SMALL, justify="center").pack(pady=12)

    # ── APPLY ────────────────────────────────────────────────────
    def _apply(self):
        self.cfg["theme"]            = self.theme_var.get()
        self.cfg["font_size"]        = self.font_var.get()
        self.cfg["show_path_col"]    = self.path_col_var.get()
        self.cfg["tick_interval_ms"] = self.tick_var.get()
        self.cfg["crossfade_ms"]     = self.xfade_var.get()
        self.cfg["scan_on_startup"]  = self.startup_var.get()
        self.cfg["confirm_clear"]    = self.confirm_var.get()

        save_config(self.cfg)
        self.app.cfg = self.cfg

        # Apply theme palette to global A dict
        PhoniPlayer._apply_theme(self.cfg["theme"])

        # Rebuild UI (also repopulates tree)
        self.app._rebuild_ui()

        # Post-rebuild: show/hide path column on the NEW tree widget
        try:
            if self.cfg["show_path_col"]:
                self.app.tree.column("path", width=260, minwidth=36)
            else:
                self.app.tree.column("path", width=0, minwidth=0, stretch=False)
        except Exception:
            pass

        # Destroy settings window AFTER rebuild so parent ref stays valid
        self.win.destroy()

    def _reset(self):
        if messagebox.askyesno("Reset", "Reset all settings to defaults?",
                               parent=self.win):
            self.cfg = dict(DEFAULTS)
            save_config(self.cfg)
            self.app.cfg = self.cfg
            PhoniPlayer._apply_theme(self.cfg["theme"])
            self.app._rebuild_ui()
            self.win.destroy()



class EasterEggWindow:
    """Secret easter egg — triggered by clicking the logo 7 times."""
    def __init__(self, root):
        win = tk.Toplevel(root)
        win.title("???")
        win.geometry("400x320")
        win.resizable(False, False)
        win.configure(bg="#0a0a0a")
        win.grab_set()
        win.transient(root)

        root.update_idletasks()
        px = root.winfo_x() + root.winfo_width()//2 - 200
        py = root.winfo_y() + root.winfo_height()//2 - 160
        win.geometry(f"+{px}+{py}")

        self.win = win
        self.root = root
        self._frame = 0
        self._colors = ["#ff0000","#ff7700","#ffff00","#00ff00",
                        "#0000ff","#8b00ff","#ff00ff"]
        self._build()
        self._animate()

    def _build(self):
        win = self.win

        self.title_lbl = tk.Label(win, text="🎵 PHONI TECHNOLOGY 🎵",
                                   bg="#0a0a0a", fg="#ff0000",
                                   font=("Segoe UI", 13, "bold"))
        self.title_lbl.pack(pady=(24, 4))

        self.sub_lbl = tk.Label(win,
            text="wassup homie!\n\nwelcome to sneak peak area. here, if theres a minor update like 26.6.1,\n\nu might see a sneak peak here!\ncome back later, no sneak yet.",
            bg="#0a0a0a", fg="#cccccc",
            font=("Segoe UI", 9), justify="center")
        self.sub_lbl.pack(pady=8)

        self.note_lbl = tk.Label(win, text="♪  ♫  ♩  ♬  ♭",
                                  bg="#0a0a0a", fg="#ffffff",
                                  font=("Segoe UI", 18))
        self.note_lbl.pack(pady=8)

        tk.Button(win, text="come back later blud",
                  command=win.destroy,
                  bg="#1a1a1a", fg="#aaaaaa",
                  relief="flat", font=("Segoe UI", 9),
                  activebackground="#333333",
                  activeforeground="#ffffff",
                  padx=12, pady=4).pack(pady=16)

    def _animate(self):
        try:
            col = self._colors[self._frame % len(self._colors)]
            self.title_lbl.config(fg=col)
            notes = ["♪  ♫  ♩  ♬  ♭", "♫  ♩  ♬  ♭  ♪",
                     "♩  ♬  ♭  ♪  ♫", "♬  ♭  ♪  ♫  ♩", "♭  ♪  ♫  ♩  ♬"]
            self.note_lbl.config(text=notes[self._frame % len(notes)])
            self._frame += 1
            self.win.after(150, self._animate)
        except Exception:
            pass


class PhoniPlayer:
    def __init__(self):
        # Load config and apply theme before building UI
        self.cfg = load_config()
        self._apply_theme(self.cfg["theme"], rebuild=False)

        self.root = tk.Tk()
        _init_fonts()  # load Montserrat into Tk now that a display exists
        self.root.title("PTMusic")
        self.root.geometry("1180x760")
        self.root.minsize(860, 580)
        self.root.configure(bg=A["win_bg"])

        # Taskbar / window icon
        import sys as _sys2, os as _os2
        _base2 = getattr(_sys2, "_MEIPASS", _os2.path.dirname(_os2.path.abspath(__file__)))
        _icon_path2 = _os2.path.join(_base2, "PTMusic.png")
        try:
            from PIL import Image, ImageTk
            self._wm_icon = ImageTk.PhotoImage(Image.open(_icon_path2))
            self.root.iconphoto(True, self._wm_icon)
        except Exception:
            pass

        self.library:  list[dict] = []
        self.filtered: list[dict] = []
        self.cur_idx   = -1
        self.playing   = False
        self.paused    = False
        self.scan_stop = threading.Event()
        self.scan_th:  threading.Thread | None = None
        self.prog_after = None
        self._tlen        = 0
        self._seek_offset = 0.0  # seconds seeked to; get_pos() resets on seek
        self._vol   = 0.8
        self._use_folders = False   # False = scan all drives
        self._logo_clicks = 0       # easter egg counter
        self._konami_buf  = ""      # easter egg: type "phoni" or "MORE THEMES PLS"

        self._build()
        self._style()
        self.root.after(250, self._startup_dialog if self.cfg.get("scan_on_startup", True) else lambda: None)
        self.root.mainloop()


    @staticmethod
    def _apply_theme(theme_name: str, rebuild: bool = True):
        """Apply a theme palette to the global A dict."""
        palette = THEMES.get(theme_name, THEMES["Aero Light"])
        A.update(palette)

    def _open_settings(self):
        SettingsWindow(self)

    def _rebuild_ui(self):
        """Destroy and recreate all widgets, then repopulate library."""
        # Stop any active scan/playback tick first
        if self.prog_after:
            try: self.root.after_cancel(self.prog_after)
            except: pass
            self.prog_after = None

        for w in self.root.winfo_children():
            try: w.destroy()
            except: pass

        self.root.configure(bg=A["win_bg"])
        self._build()
        self._style()

        # Re-apply ttk style with a unique style name to bust the cache
        self._style()

        # Repopulate tree from in-memory library
        try:
            self.tree.delete(*self.tree.get_children())
            for info in (self.filtered if self.filtered else self.library):
                self.tree.insert("", "end", iid=info["path"],
                                 values=(info["title"], info["artist"],
                                         info["album"], info["dur"],
                                         info["ext"], fmt_size(info["size"]),
                                         info["path"]))
            self.lib_count.config(text=f"({len(self.filtered or self.library)} tracks)")
            self._upd_stats()
        except Exception:
            pass

    def _build(self):
        self._build_titlebar()
        self._build_toolbar()

        body = tk.Frame(self.root, bg=A["win_bg"])
        body.pack(fill="both", expand=True, padx=5, pady=3)

        self._build_sidebar(body)

        right = tk.Frame(body, bg=A["win_bg"])
        right.pack(side="left", fill="both", expand=True, padx=(4,0))
        self._build_library(right)
        self._build_player(right)

        self._build_statusbar()

    def _build_titlebar(self):
        tb = tk.Canvas(self.root, height=36, bg=A["title_bar"],
                       highlightthickness=0)
        tb.pack(fill="x")

        # Gradient-like: two horizontal bands
        tb.create_rectangle(0, 0, 2000, 18,  fill=A["title_bar"],  outline="")
        tb.create_rectangle(0, 18, 2000, 36, fill=A["title_bar2"], outline="")

        # Thin glow line at top
        tb.create_line(0, 0, 2000, 0, fill=A["border_glow"])

        # Logo + title (no chrome buttons)
        import sys as _sys, os as _os
        _base = getattr(_sys, "_MEIPASS", _os.path.dirname(_os.path.abspath(__file__)))
        _icon_path = _os.path.join(_base, "PTMusic.png")
        try:
            from PIL import Image, ImageTk
            _raw = Image.open(_icon_path).resize((24, 24), Image.LANCZOS)
            self._title_img = ImageTk.PhotoImage(_raw)
            tb.create_image(10, 18, image=self._title_img, anchor="w")
            tb.create_text(40, 18, text="PTMusic",
                           fill=A["accent_bright"], font=FONT_TITLE, anchor="w")
        except Exception:
            tb.create_text(12, 18, text="PTMusic",
                           fill=A["accent_bright"], font=FONT_TITLE, anchor="w")

        # Bottom border glow
        sep = tk.Frame(self.root, bg=A["tb_border"], height=1)
        sep.pack(fill="x")

        # Easter egg: click the logo 7 times
        tb.bind("<Button-1>", self._logo_click)
        # Easter egg: type "phoni" or "MORE THEMES PLS" anywhere
        self.root.bind_all("<Key>", self._konami)

    def _logo_click(self, e=None):
        self._logo_clicks += 1
        if self._logo_clicks >= 7:
            self._logo_clicks = 0
            EasterEggWindow(self.root)

    def _konami(self, e):
        ch = e.char
        if not ch: return
        self._konami_buf = (self._konami_buf + ch)[-15:]
        # Easter egg 1: type "phoni"
        if self._konami_buf.lower().endswith("phoni"):
            self._konami_buf = ""
            EasterEggWindow(self.root)
        # Easter egg 2: type "MORE THEMES PLS" (case-sensitive) → unlock Royale Noir
        elif self._konami_buf.endswith("MORE THEMES PLS"):
            self._konami_buf = ""
            self.cfg["royale_noir_unlocked"] = True
            save_config(self.cfg)
            PhoniPlayer._apply_theme("Royale Noir")
            self.cfg["theme"] = "Royale Noir"
            save_config(self.cfg)
            self._rebuild_ui()
            messagebox.showinfo(
                "👑 Royale Noir Unlocked",
                "You found the secret theme!\n\nRoyale Noir is now available in Settings.",
                parent=self.root)

    def _build_toolbar(self):
        bar = tk.Frame(self.root, bg=A["glass_dark"], height=36)
        bar.pack(fill="x")
        bar.pack_propagate(False)

        self.scan_btn = AeroBtn(bar, icon="🔍", text="Scan All Drives",
                                cmd=self._start_scan_all, w=140, h=26,
                                bg_override=A["glass_dark"])
        self.scan_btn.pack(side="left", padx=(8,3), pady=5)

        self.folder_btn = AeroBtn(bar, icon="📂", text="Scan Folders",
                                  cmd=self._start_scan_folders, w=130, h=26,
                                  bg_override=A["glass_dark"])
        self.folder_btn.pack(side="left", padx=3, pady=5)

        self.stop_scan_btn = AeroBtn(bar, icon="⏹", text="Stop",
                                     cmd=self._stop_scan, w=70, h=26,
                                     danger=True, bg_override=A["glass_dark"])
        # stop_scan_btn is hidden until a scan starts

        tk.Frame(bar, bg=A["border"], width=1).pack(side="left", fill="y",
                                                     padx=8, pady=6)

        AeroBtn(bar, icon="🗑", text="Clear",
                cmd=self._clear_library, w=78, h=26,
                danger=True, bg_override=A["glass_dark"]
                ).pack(side="left", padx=3, pady=5)

        tk.Frame(bar, bg=A["border"], width=1).pack(side="right", fill="y",
                                                      padx=4, pady=6)
        AeroBtn(bar, icon="⚙", text="Settings",
                cmd=self._open_settings, w=90, h=26,
                bg_override=A["glass_dark"]).pack(side="right", padx=(0,4), pady=5)

        # Search on the right
        tk.Label(bar, text="Search:", bg=A["glass_dark"],
                 fg=A["text_dim"], font=FONT_SMALL).pack(side="right", padx=(0,6))
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", lambda *_: self._filter())
        ef = tk.Frame(bar, bg=A["border_glow"], padx=1, pady=1)
        ef.pack(side="right", padx=(0,8), pady=6)
        tk.Entry(ef, textvariable=self.search_var,
                 bg=A["glass_mid"], fg=A["text"],
                 insertbackground=A["accent_hot"],
                 relief="flat", font=FONT_UI, width=22
                 ).pack(ipady=3)

        tk.Frame(bar, bg=A["border"], height=1).pack(side="bottom", fill="x")

    def _build_sidebar(self, parent):
        sb = tk.Frame(parent, bg=A["sidebar"], width=210,
                      highlightthickness=1,
                      highlightbackground=A["border"])
        sb.pack(side="left", fill="y", pady=0)
        sb.pack_propagate(False)

        def sec(text):
            f = tk.Frame(sb, bg=A["sidebar_sect"])
            f.pack(fill="x")
            tk.Label(f, text=text, bg=A["sidebar_sect"],
                     fg=A["text_dim"], font=FONT_LABEL,
                     anchor="w").pack(fill="x", padx=8, pady=(5,3))
            tk.Frame(sb, bg=A["border"], height=1).pack(fill="x")

        sec("SCAN SOURCE")
        src_frame = tk.Frame(sb, bg=A["sidebar"])
        src_frame.pack(fill="x", padx=8, pady=6)

        self.src_var = tk.StringVar(value="drives")
        for val, lbl in [("drives","All Drives"), ("folders","Selected Folders")]:
            rb = tk.Radiobutton(src_frame, text=lbl, variable=self.src_var,
                                value=val, command=self._toggle_src,
                                bg=A["sidebar"], fg=A["text"],
                                activebackground=A["sidebar"],
                                activeforeground=A["accent"],
                                selectcolor=A["glass_dark"],
                                font=FONT_SMALL, anchor="w")
            rb.pack(anchor="w")

        # Folder list
        self.folder_list = FolderList(sb, on_change=None)
        self.folder_list.pack(fill="x", padx=8, pady=(0,6))
        self.folder_list.set_placeholder()

        tk.Frame(sb, bg=A["border"], height=1).pack(fill="x")

        sec("FORMATS")
        fmt_frame = tk.Frame(sb, bg=A["sidebar"])
        fmt_frame.pack(fill="x", padx=8, pady=6)

        self.fmt_vars: dict[str, tk.BooleanVar] = {}
        fmts = [("MP3","#3399ff"), ("FLAC","#33ddaa"), ("WAV","#ffaa33"),
                ("M4A","#aa66ff"), ("MIDI","#ff6688"), ("WMA","#66ccdd")]
        for ext, _ in fmts:
            v = tk.BooleanVar(value=True)
            self.fmt_vars[ext] = v
            row = tk.Frame(fmt_frame, bg=A["sidebar"])
            row.pack(fill="x", pady=1)
            tk.Checkbutton(row, text=ext, variable=v,
                           command=self._filter,
                           bg=A["sidebar"], fg=A["text"],
                           activebackground=A["sidebar"],
                           activeforeground=A["accent"],
                           selectcolor=A["glass_dark"],
                           font=FONT_SMALL, anchor="w",
                           ).pack(side="left")

        tk.Frame(sb, bg=A["border"], height=1).pack(fill="x")

        sec("LIBRARY INFO")
        self.stats_lbl = tk.Label(sb, text="No files loaded",
                                   bg=A["sidebar"], fg=A["text_dim"],
                                   font=FONT_SMALL, justify="left",
                                   anchor="nw", wraplength=190)
        self.stats_lbl.pack(anchor="w", padx=8, pady=6)

    def _build_library(self, parent):
        lf = GlassPanel(parent)
        lf.pack(fill="both", expand=True, pady=(0,3))

        hdr = tk.Frame(lf, bg=A["glass"])
        hdr.pack(fill="x", padx=6, pady=(5,3))
        tk.Label(hdr, text="LIBRARY", bg=A["glass"],
                 fg=A["accent_bright"], font=FONT_BOLD).pack(side="left")
        self.lib_count = tk.Label(hdr, text="",
                                   bg=A["glass"], fg=A["text_dim"],
                                   font=FONT_SMALL)
        self.lib_count.pack(side="left", padx=8)

        # Treeview wrapper
        tv_frame = tk.Frame(lf, bg=A["glass"])
        tv_frame.pack(fill="both", expand=True, padx=4, pady=(0,4))

        cols = ("title","artist","album","dur","ext","size","path")
        self.tree = ttk.Treeview(tv_frame, columns=cols,
                                  show="headings", selectmode="browse")
        hdrs = [("title","Title",210),("artist","Artist",140),
                ("album","Album",120),("dur","Dur.",58),
                ("ext","Fmt",52),("size","Size",65),("path","Path",260)]
        for col, lbl, w in hdrs:
            self.tree.heading(col, text=lbl,
                              command=lambda c=col: self._sort(c))
            self.tree.column(col, width=w, minwidth=36, stretch=(col=="title"))

        vsb = ttk.Scrollbar(tv_frame, orient="vertical",   command=self.tree.yview)
        hsb = ttk.Scrollbar(tv_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        hsb.pack(side="bottom", fill="x")
        vsb.pack(side="right",  fill="y")
        self.tree.pack(fill="both", expand=True)

        self.tree.bind("<Double-1>", self._dbl_click)
        self.tree.bind("<Return>",   self._dbl_click)

    def _build_player(self, parent):
        pf = GlassPanel(parent, height=140)
        pf.pack(fill="x")
        pf.pack_propagate(False)

        np = tk.Frame(pf, bg=A["glass"])
        np.pack(fill="x", padx=12, pady=(8,0))

        # YOOOOOOOOOOOO ITS AN ANIMATED DOT :OOOOOOOOOOOOOO
        self.dot = tk.Label(np, text="◉", bg=A["glass"],
                            fg=A["text_dim"], font=("Segoe UI", 12))
        self.dot.pack(side="left", padx=(0,6))

        info_col = tk.Frame(np, bg=A["glass"])
        info_col.pack(side="left", fill="x", expand=True)
        self.now_title = tk.Label(info_col, text="No track selected",
                                   bg=A["glass"], fg=A["accent_bright"],
                                   font=FONT_NOW, anchor="w")
        self.now_title.pack(anchor="w")
        self.now_sub = tk.Label(info_col, text="",
                                 bg=A["glass"], fg=A["text_dim"],
                                 font=FONT_NOW_SM, anchor="w")
        self.now_sub.pack(anchor="w")

        pg = tk.Frame(pf, bg=A["glass"])
        pg.pack(fill="x", padx=12, pady=(4,2))

        self.time_lbl = tk.Label(pg, text="0:00", width=5,
                                  bg=A["glass"], fg=A["text_dim"], font=FONT_MONO)
        self.time_lbl.pack(side="left")

        self.prog = tk.Canvas(pg, height=14, bg=A["prog_bg"],
                              highlightthickness=1,
                              highlightbackground=A["border"])
        self.prog.pack(side="left", fill="x", expand=True, padx=6)
        self.prog.bind("<Button-1>", self._seek)

        self.dur_lbl = tk.Label(pg, text="0:00", width=5,
                                 bg=A["glass"], fg=A["text_dim"], font=FONT_MONO)
        self.dur_lbl.pack(side="left")

        ctrl = tk.Frame(pf, bg=A["glass"])
        ctrl.pack(pady=5)

        self.btn_prev = AeroBtn(ctrl, icon="⏮", cmd=self._prev, w=44, h=32, bg_override=A["glass"])
        self.btn_play = AeroBtn(ctrl, icon="▶", cmd=self._playpause, w=56, h=36, bg_override=A["glass"])
        self.btn_stop = AeroBtn(ctrl, icon="⏹", cmd=self._stop, w=44, h=32, danger=True, bg_override=A["glass"])
        self.btn_next = AeroBtn(ctrl, icon="⏭", cmd=self._next, w=44, h=32, bg_override=A["glass"])
        self.btn_shuf = AeroBtn(ctrl, icon="🔀", cmd=self._shuffle, w=44, h=28, bg_override=A["glass"])
        self.btn_rep  = AeroBtn(ctrl, icon="🔁", cmd=self._toggle_repeat, w=44, h=28, bg_override=A["glass"])

        for b in (self.btn_prev, self.btn_play, self.btn_stop,
                  self.btn_next, self.btn_shuf, self.btn_rep):
            b.pack(side="left", padx=2)

        # Volume
        vf = tk.Frame(ctrl, bg=A["glass"])
        vf.pack(side="left", padx=(14,0))
        tk.Label(vf, text="🔊", bg=A["glass"], fg=A["text_dim"],
                 font=("Segoe UI", 9)).pack(side="left")
        self.vol_scale = tk.Scale(vf, from_=0, to=100, orient="horizontal",
                                   length=100, showvalue=False,
                                   bg=A["glass"], fg=A["text"],
                                   troughcolor=A["prog_bg"],
                                   activebackground=A["accent_hot"],
                                   highlightthickness=0, bd=0,
                                   command=self._set_vol)
        self.vol_scale.set(int(self._vol * 100))
        self.vol_scale.pack(side="left")

        self._repeat = False

    def _build_statusbar(self):
        sb = tk.Frame(self.root, bg=A["glass_dark"], height=22)
        sb.pack(fill="x", side="bottom")
        sb.pack_propagate(False)
        tk.Frame(sb, bg=A["tb_border"], height=1).pack(fill="x", side="top")
        self.status_var = tk.StringVar(value="Ready")
        tk.Label(sb, textvariable=self.status_var,
                 bg=A["glass_dark"], fg=A["text_dim"],
                 font=FONT_SMALL, anchor="w").pack(side="left", padx=8)
        self.ind_lbl = tk.Label(sb, text="◉ STOPPED",
                                 bg=A["glass_dark"], fg=A["text_dim"],
                                 font=FONT_LABEL)
        self.ind_lbl.pack(side="right", padx=8)

    def _style(self):
        s = ttk.Style()
        # Re-apply clam fresh; configure forces widget refresh even on repeat calls
        try: s.theme_use("clam")
        except Exception: pass
        s.configure("Treeview",
                     background=A["glass"],
                     foreground=A["text"],
                     fieldbackground=A["glass"],
                     rowheight=24, font=FONT_SMALL, borderwidth=0)
        s.configure("Treeview.Heading",
                     background=A["glass_mid"],
                     foreground=A["accent_bright"],
                     font=FONT_LABEL, relief="flat")
        s.map("Treeview",
              background=[("selected", A["sel"])],
              foreground=[("selected", A["accent_bright"])])
        s.configure("Vertical.TScrollbar",
                     background=A["glass_mid"],
                     troughcolor=A["prog_bg"],
                     bordercolor=A["border"],
                     arrowcolor=A["text_dim"], borderwidth=0)
        s.configure("Horizontal.TScrollbar",
                     background=A["glass_mid"],
                     troughcolor=A["prog_bg"],
                     bordercolor=A["border"],
                     arrowcolor=A["text_dim"], borderwidth=0)

    def _toggle_src(self):
        self._use_folders = (self.src_var.get() == "folders")
        if self._use_folders:
            self.folder_list.set_placeholder()
            # Clear placeholder and let user add
            self.folder_list.lb.delete(0, "end")
        else:
            self.folder_list.set_placeholder()

    def _startup_dialog(self):
        if messagebox.askyesno("Welcome",
                                "Welcome to PTMusic!\n\n"
                                "Would you like to scan all drives?\n"
                                "You can also scan specific drives later.",
                                parent=self.root):
            self._start_scan_all()

    def _start_scan_all(self):
        self.src_var.set("drives")
        self._use_folders = False
        self.folder_list.set_placeholder()
        self._run_scan(get_all_drives())

    def _start_scan_folders(self):
        self.src_var.set("folders")
        self._use_folders = True
        folders = self.folder_list.get_folders()
        if not folders:
            # Ask to pick one now
            path = filedialog.askdirectory(title="Select Folder to Scan")
            if not path: return
            self.folder_list.folders.append(path)
            self.folder_list.lb.delete(0, "end")
            self.folder_list.lb.insert("end", path)
            folders = [path]
        self._run_scan(folders)

    def _run_scan(self, paths: list):
        if self.scan_th and self.scan_th.is_alive():
            self.scan_stop.set()
            self.scan_th.join(timeout=2)
        self.scan_stop.clear()
        self._clear_library(confirm=False)

        self.status_var.set(f"Scanning {len(paths)} location(s)…")
        self.stop_scan_btn.pack(side="left", padx=3, pady=5)

        def run():
            scan_paths(paths,
                       callback=self._on_found,
                       stop_event=self.scan_stop)
            self.root.after(0, self._scan_done)

        self.scan_th = threading.Thread(target=run, daemon=True)
        self.scan_th.start()

    def _stop_scan(self):
        self.scan_stop.set()

    def _on_found(self, info):
        self.library.append(info)
        self.root.after(0, lambda i=info: self._add_row(i))
        n = len(self.library)
        if n % 20 == 0:
            self.root.after(0, lambda x=n:
                self.status_var.set(f"Found {x} tracks…"))

    def _add_row(self, info):
        if self.tree.exists(info["path"]): return
        self.tree.insert("", "end", iid=info["path"],
                          values=(info["title"], info["artist"], info["album"],
                                  info["dur"], info["ext"],
                                  fmt_size(info["size"]), info["path"]))
        self._upd_stats()

    def _scan_done(self):
        n = len(self.library)
        self.status_var.set(f"Scan complete — {n} track{'s' if n!=1 else ''} found")
        self.stop_scan_btn.pack_forget()
        self._upd_stats()
        self._filter()

    def _clear_library(self, confirm=True):
        if confirm and self.cfg.get("confirm_clear", True) and not messagebox.askyesno("Clear Library",
                                                "Remove all tracks?",
                                                parent=self.root):
            return
        self._stop()
        self.library.clear()
        self.filtered.clear()
        self.tree.delete(*self.tree.get_children())
        self._upd_stats()
        self.status_var.set("Library cleared")

    def _filter(self, *_):
        q = self.search_var.get().lower()
        enabled = {k for k, v in self.fmt_vars.items() if v.get()}
        if "MIDI" in enabled: enabled.add("MID")

        self.filtered = [
            t for t in self.library
            if t["ext"] in enabled and (
                not q or q in t["title"].lower()
                       or q in t["artist"].lower()
                       or q in t["album"].lower()
                       or q in t["path"].lower())
        ]
        self.tree.delete(*self.tree.get_children())
        for info in self.filtered:
            self.tree.insert("", "end", iid=info["path"],
                              values=(info["title"], info["artist"], info["album"],
                                      info["dur"], info["ext"],
                                      fmt_size(info["size"]), info["path"]))
        self.lib_count.config(text=f"({len(self.filtered)} tracks)")

    def _sort(self, col):
        items = [(self.tree.set(k, col), k) for k in self.tree.get_children()]
        items.sort(key=lambda x: x[0].lower())
        for i, (_, k) in enumerate(items): self.tree.move(k, "", i)

    def _upd_stats(self):
        n = len(self.library)
        fmts: dict[str, int] = {}
        for t in self.library: fmts[t["ext"]] = fmts.get(t["ext"],0)+1
        lines = [f"{n} track{'s' if n!=1 else ''}"]
        for k, v in sorted(fmts.items()): lines.append(f"  {k}: {v}")
        self.stats_lbl.config(text="\n".join(lines) if n else "No files loaded")
        self.lib_count.config(text=f"({len(self.filtered or self.library)} tracks)")

    def _dbl_click(self, e=None):
        sel = self.tree.selection()
        if not sel: return
        path = sel[0]
        self.filtered = [t for t in self.library if self.tree.exists(t["path"])]
        try:
            self.cur_idx = next(i for i,t in enumerate(self.filtered)
                                if t["path"] == path)
        except StopIteration: return
        self._play(self.filtered[self.cur_idx])

    def _play(self, info):
        if not PYGAME_AVAILABLE:
            messagebox.showerror("pygame missing",
                                  "pip install pygame", parent=self.root)
            return
        if not os.path.exists(info["path"]):
            self.status_var.set(f"Missing: {info['path']}"); return
        try:
            pygame.mixer.music.load(info["path"])
            pygame.mixer.music.set_volume(self._vol)
            pygame.mixer.music.play()
            self.playing = True; self.paused = False
            self._seek_offset = 0.0
        except Exception as e:
            self.status_var.set(f"Error: {e}"); return

        self._tlen = 0
        if MUTAGEN_AVAILABLE:
            try:
                a = MutagenFile(info["path"])
                if a and hasattr(a.info,'length'):
                    self._tlen = a.info.length
            except: pass

        self.now_title.config(text=info["title"])
        self.now_sub.config(text=f"{info['artist']}  ·  {info['album']}  ·  {info['ext']}")
        self.dur_lbl.config(text=info["dur"] if info["dur"]!="—" else "—")
        self.btn_play.icon = "⏸"; self.btn_play._draw()
        self.dot.config(fg=A["green"])
        self.ind_lbl.config(text="◉ PLAYING", fg=A["green"])
        self.status_var.set(f"Playing: {info['title']}")
        if self.tree.exists(info["path"]):
            self.tree.selection_set(info["path"])
            self.tree.see(info["path"])
        self._tick()

    def _tick(self):
        if self.prog_after: self.root.after_cancel(self.prog_after)
        if not (PYGAME_AVAILABLE and self.playing and not self.paused):
            return
        raw = pygame.mixer.music.get_pos() / 1000.0
        if raw < 0:
            self._track_ended(); return
        pos = self._seek_offset + raw   # real playback position

        m, s = int(pos//60), int(pos%60)
        self.time_lbl.config(text=f"{m}:{s:02d}")

        W = self.prog.winfo_width()
        H = self.prog.winfo_height()
        self.prog.delete("all")
        if self._tlen > 0 and W > 0:
            frac = min(pos/self._tlen, 1.0)
            fw = int(frac * W)
            # Trough
            self.prog.create_rectangle(0,0,W,H, fill=A["prog_bg"], outline="")
            # Fill gradient (two bands)
            if fw > 0:
                mid = H//2
                self.prog.create_rectangle(0,0,fw,mid,   fill=A["prog_bright"], outline="")
                self.prog.create_rectangle(0,mid,fw,H,    fill=A["prog_fill"],   outline="")
                # Gloss stipple
                self.prog.create_rectangle(0,0,fw,mid,
                    fill="#ffffff", outline="", stipple="gray12")
            # Knob
            kx = fw
            self.prog.create_oval(kx-6,1,kx+6,H-1,
                fill=A["accent_bright"], outline=A["accent_hot"])
            self.prog.create_oval(kx-3,H//2-3,kx+3,H//2+3,
                fill=A["glass"], outline="")

        self.prog_after = self.root.after(400, self._tick)

    def _track_ended(self):
        if self._repeat and self.cur_idx >= 0:
            self._play(self.filtered[self.cur_idx])
        else:
            self._next()

    def _seek(self, e):
        if not (PYGAME_AVAILABLE and self.playing): return
        W = self.prog.winfo_width()
        if W <= 0 or self._tlen <= 0: return
        target = max(0.0, min(e.x / W * self._tlen, self._tlen))
        try:
            # set_pos() is unreliable for MP3 in pygame — play(start=) is more robust
            pygame.mixer.music.play(start=target)
            self._seek_offset = target
        except Exception:
            try:
                pygame.mixer.music.set_pos(target)
                self._seek_offset = target
            except Exception:
                pass

    def _playpause(self):
        if not PYGAME_AVAILABLE: return
        if not self.playing:
            sel = self.tree.selection()
            if sel: self._dbl_click()
            return
        if self.paused:
            pygame.mixer.music.unpause()
            self.paused = False
            self.btn_play.icon = "⏸"; self.btn_play._draw()
            self.dot.config(fg=A["green"])
            self.ind_lbl.config(text="◉ PLAYING", fg=A["green"])
            self._tick()
        else:
            pygame.mixer.music.pause()
            self.paused = True
            self.btn_play.icon = "▶"; self.btn_play._draw()
            self.dot.config(fg=A["accent"])
            self.ind_lbl.config(text="❚❚ PAUSED", fg=A["accent"])
            self.status_var.set("Paused")

    def _stop(self):
        if PYGAME_AVAILABLE: pygame.mixer.music.stop()
        self.playing = False; self.paused = False
        self.btn_play.icon = "▶"; self.btn_play._draw()
        self.dot.config(fg=A["text_dim"])
        self.ind_lbl.config(text="◉ STOPPED", fg=A["text_dim"])
        self.now_title.config(text="No track selected")
        self.now_sub.config(text="")
        self.time_lbl.config(text="0:00")
        self.prog.delete("all")
        self.status_var.set("Stopped")

    def _next(self):
        if not self.filtered: return
        self.cur_idx = (self.cur_idx + 1) % len(self.filtered)
        self._play(self.filtered[self.cur_idx])

    def _prev(self):
        if not self.filtered: return
        self.cur_idx = (self.cur_idx - 1) % len(self.filtered)
        self._play(self.filtered[self.cur_idx])

    def _shuffle(self):
        if self.filtered:
            random.shuffle(self.filtered)
            self.tree.delete(*self.tree.get_children())
            for info in self.filtered:
                self.tree.insert("", "end", iid=info["path"],
                                  values=(info["title"], info["artist"], info["album"],
                                          info["dur"], info["ext"],
                                          fmt_size(info["size"]), info["path"]))
            self.status_var.set("Library shuffled")

    def _toggle_repeat(self):
        self._repeat = not self._repeat
        self.btn_rep.text = "🔁" if not self._repeat else ""
        self.btn_rep.icon = "🔁"
        col = A["accent_hot"] if self._repeat else A["btn_border"]
        self.btn_rep.danger = False
        # Visually indicate repeat is on by changing border color
        self.status_var.set("Repeat: " + ("ON" if self._repeat else "OFF"))

    def _set_vol(self, val):
        self._vol = int(val)/100.0
        if PYGAME_AVAILABLE: pygame.mixer.music.set_volume(self._vol)


if __name__ == "__main__":
    import traceback, sys, os

    log_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "phoni_crash.log")

    class Tee:
        """Safe stream tee — works even when stdout/stderr are None (windowed exe)."""
        def __init__(self, stream, logfile):
            self._s = stream  # may be None under PyInstaller --windowed
            self._f = logfile
        def write(self, data):
            if self._s is not None:
                try: self._s.write(data)
                except Exception: pass
            try: self._f.write(data); self._f.flush()
            except Exception: pass
        def flush(self):
            if self._s is not None:
                try: self._s.flush()
                except Exception: pass

    with open(log_path, "w", encoding="utf-8") as lf:
        sys.stdout = Tee(sys.__stdout__, lf)
        sys.stderr = Tee(sys.__stderr__, lf)
        print("PTMusic starting")
        print("Python", sys.version)
        print("pygame  :", PYGAME_AVAILABLE)
        print("mutagen :", MUTAGEN_AVAILABLE)
        print("-" * 60)
        if not PYGAME_AVAILABLE:
            print("WARNING: pip install pygame")
        if not MUTAGEN_AVAILABLE:
            print("WARNING: pip install mutagen")
        try:
            PhoniPlayer()
        except Exception:
            print("\n=== CRASH ===")
            traceback.print_exc()
            print("=============")
            input("\nPress Enter to exit...")
        finally:
            sys.stdout = sys.__stdout__
            sys.stderr = sys.__stderr__
            print("Log saved to:", log_path)
