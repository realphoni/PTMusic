"""
PTMusic
Phoni Technology 2026
"""

import os
import sys
import json
import shutil
import threading
import platform
import random
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from pathlib import Path
from collections import deque

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

try:
    from PIL import Image, ImageTk
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

try:
    import pystray
    PYSTRAY_AVAILABLE = True
except ImportError:
    PYSTRAY_AVAILABLE = False


A = {
    "win_bg":        "#dceaf6",
    "glass_dark":    "#e5f0fa",
    "glass":         "#f8fbff",
    "glass_mid":     "#c8def2",
    "glass_light":   "#f5fbff",
    "glass_lighter": "#ffffff",
    "border":        "#7aa7d9",
    "border_glow":   "#bfe2ff",
    "accent":        "#2468a8",
    "accent_bright": "#0b5cad",
    "accent_hot":    "#1f7de2",
    "title_bar":     "#365f94",
    "title_bar2":    "#456f9f",
    "title_text":    "#ffffff",
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
    "sidebar":       "#e5f0fa",
    "sidebar_sect":  "#d5e5f4",
    "row_alt":       "#f2f8fd",
}

# ── FONT LOADER ───────────────────────────────────────────────────────────
def _find_montserrat_ttf():
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

_MONT_TTF = _find_montserrat_ttf()

FONT_UI     = ("Segoe UI", 9)
FONT_BOLD   = ("Segoe UI", 9,  "bold")
FONT_SMALL  = ("Segoe UI", 8)
FONT_LABEL  = ("Segoe UI", 7,  "bold")
FONT_MONO   = ("Consolas", 9)
FONT_TITLE  = ("Segoe UI", 10, "bold")
FONT_NOW    = ("Segoe UI", 13)
FONT_NOW_SM = ("Segoe UI", 8)

def _init_fonts():
    global FONT_UI, FONT_BOLD, FONT_SMALL, FONT_LABEL, FONT_TITLE, FONT_NOW, FONT_NOW_SM
    if not _MONT_TTF:
        return
    try:
        import tkinter.font as tkfont
        fam = None
        try:
            tmp = tkfont.Font(file=_MONT_TTF)
            fam = tmp.actual()["family"]
            tmp.delete()
        except Exception:
            pass
        if not fam:
            try:
                import ctypes
                ctypes.windll.gdi32.AddFontResourceExW(_MONT_TTF, 0x10, 0)
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
        pass

# ── TRANSLATIONS ──────────────────────────────────────────────────────────
_STRINGS = {
    "English": {
        # Toolbar
        "scan_all":         "Scan All Drives",
        "scan_folders":     "Scan Folders",
        "stop":             "Stop",
        "clear":            "Clear",
        "settings":         "Settings",
        "mini":             "Mini",
        "queue":            "Queue",
        "search":           "Search:",
        # Sidebar sections
        "scan_source":      "SCAN SOURCE",
        "all_drives":       "All Drives",
        "sel_folders":      "Selected Folders",
        "formats":          "FORMATS",
        "recently_played":  "RECENTLY PLAYED",
        "nothing_yet":      "Nothing yet",
        "library_info":     "LIBRARY INFO",
        "no_files":         "No files loaded",
        # Library
        "library":          "LIBRARY",
        "add_folder":       "Add Folder",
        "remove":           "Remove",
        "queue_btn":        "+ Queue",
        "col_title":        "Title",
        "col_artist":       "Artist",
        "col_album":        "Album",
        "col_dur":          "Dur.",
        "col_fmt":          "Fmt",
        "col_size":         "Size",
        "col_path":         "Path",
        "albums_tab":       "Albums",
        "library_tab":      "Library",
        "search_albums":    "Search albums:",
        "sort":             "Sort:",
        "sort_name":        "Name",
        "sort_artist":      "Artist",
        "sort_tracks":      "Tracks",
        "no_albums":        "No albums found.\nScan your music library first.",
        # Player
        "no_track":         "No track selected",
        # Context menu
        "ctx_play":         "▶  Play Now",
        "ctx_queue":        "+ Add to Queue",
        "ctx_next":         "⏭  Play Next",
        "ctx_copy":         "📋 Copy Path",
        # Status
        "ready":            "Ready",
        "stopped":          "◉ STOPPED",
        "playing":          "◉ PLAYING",
        "paused":           "❚❚ PAUSED",
        "repeat_on":        "Repeat: ON",
        "repeat_off":       "Repeat: OFF",
        "shuffled":         "Library shuffled",
        "cleared":          "Library cleared",
        "muted":            "Muted",
        "unmuted":          "Unmuted — Volume: {}%",
        "volume":           "Volume: {}%",
        "scan_complete":    "Scan complete — {} track{} found",
        "found_tracks":     "Found {} tracks…",
        "scanning":         "Scanning {} location(s)…",
        "playing_status":   "Playing: {}",
        "copied":           "Copied: {}",
        "added_queue":      "Added to queue: {}",
        "playing_next":     "Playing next: {}",
        # Settings
        "settings_title":   "PTMusic Settings",
        "appearance":       "Appearance",
        "playback":         "Playback",
        "lib_tab":          "Library",
        "about":            "About",
        "apply_close":      "Apply & Close",
        "cancel":           "Cancel",
        "reset_defaults":   "Reset Defaults",
        "theme":            "Theme:",
        "preview":          "Preview:",
        "font_size":        "Font size:",
        "show_path_col":    "Show path column:",
        "tick_ms":          "Progress update (ms):",
        "crossfade_ms":     "Crossfade (ms):",
        "off":              "(0 = off)",
        "scan_startup":     "Scan on startup:",
        "notifications":    "Track notifications:",
        "notif_hint":       "(requires winotify, plyer, or win10toast)",
        "language":         "Language / Sprache:",
        "lang_restart":     "(restart to apply)",
        "confirm_clear":    "Confirm before clearing:",
        "cfg_location":     "Config file location:",
        "open_cfg_folder":  "Open config folder",
        "reset_confirm":    "Reset all settings to defaults?",
        "reset_title":      "Reset",
        # About
        "version":          "Version 26.9.3",
        "publisher":        "Phoni Technology  ·  2026",
        "supports":         "Supports MP3 · FLAC · WAV · M4A · MIDI · WMA\nBuilt with Python, Tkinter, pygame, mutagen, Pillow",
        "shortcuts_title":  "Keyboard Shortcuts",
        "shortcuts_text":   "Space  Play / Pause        N  Next track\nP  Previous track          S  Stop\n←/→  Skip ±5s              Shift+←/→  Skip ±30s\n↑/↓  Volume ±5%            M  Mute toggle\nR  Repeat toggle           H  Shuffle      Q  Add to queue",
        # Dialogs
        "welcome_title":    "Welcome",
        "welcome_msg":      "Welcome to PTMusic!\n\nWould you like to scan all drives?\nYou can also scan specific folders later.",
        "clear_title":      "Clear Library",
        "clear_msg":        "Remove all tracks?",
        "missing_file":     "File Missing",
        "missing_msg":      "Cannot find:\n{}",
        "queue_title":      "▶  Play Queue",
        "play_next_btn":    "Play Next",
        "move_up":          "Move Up",
        "move_down":        "Move Down",
        "remove_btn":       "Remove",
        "clear_btn":        "Clear",
        "tracks_found":     "{} track{} found",
        "tracks_label":     "{} track{}",
    },
    "Deutsch": {
        "scan_all":         "Alle Laufwerke scannen",
        "scan_folders":     "Ordner scannen",
        "stop":             "Stopp",
        "clear":            "Leeren",
        "settings":         "Einstellungen",
        "mini":             "Mini",
        "queue":            "Warteschlange",
        "search":           "Suche:",
        "scan_source":      "SCAN-QUELLE",
        "all_drives":       "Alle Laufwerke",
        "sel_folders":      "Ausgewählte Ordner",
        "formats":          "FORMATE",
        "recently_played":  "ZULETZT GESPIELT",
        "nothing_yet":      "Noch nichts gespielt",
        "library_info":     "BIBLIOTHEK-INFO",
        "no_files":         "Keine Dateien geladen",
        "library":          "BIBLIOTHEK",
        "add_folder":       "Ordner hinzufügen",
        "remove":           "Entfernen",
        "queue_btn":        "+ Warteschlange",
        "col_title":        "Titel",
        "col_artist":       "Künstler",
        "col_album":        "Album",
        "col_dur":          "Dauer",
        "col_fmt":          "Format",
        "col_size":         "Größe",
        "col_path":         "Pfad",
        "albums_tab":       "Alben",
        "library_tab":      "Bibliothek",
        "search_albums":    "Alben suchen:",
        "sort":             "Sortierung:",
        "sort_name":        "Name",
        "sort_artist":      "Künstler",
        "sort_tracks":      "Titel",
        "no_albums":        "Keine Alben gefunden.\nBibliothek zuerst scannen.",
        "no_track":         "Kein Titel ausgewählt",
        "ctx_play":         "▶  Jetzt abspielen",
        "ctx_queue":        "+ Zur Warteschlange",
        "ctx_next":         "⏭  Als Nächstes",
        "ctx_copy":         "📋 Pfad kopieren",
        "ready":            "Bereit",
        "stopped":          "◉ GESTOPPT",
        "playing":          "◉ SPIELT",
        "paused":           "❚❚ PAUSIERT",
        "repeat_on":        "Wiederholen: AN",
        "repeat_off":       "Wiederholen: AUS",
        "shuffled":         "Bibliothek gemischt",
        "cleared":          "Bibliothek geleert",
        "muted":            "Stummgeschaltet",
        "unmuted":          "Ton an — Lautstärke: {}%",
        "volume":           "Lautstärke: {}%",
        "scan_complete":    "Scan abgeschlossen — {} Titel{} gefunden",
        "found_tracks":     "{} Titel gefunden…",
        "scanning":         "{} Speicherort(e) wird gescannt…",
        "playing_status":   "Spielt: {}",
        "copied":           "Kopiert: {}",
        "added_queue":      "Zur Warteschlange: {}",
        "playing_next":     "Nächster Titel: {}",
        "settings_title":   "PTMusic Einstellungen",
        "appearance":       "Erscheinungsbild",
        "playback":         "Wiedergabe",
        "lib_tab":          "Bibliothek",
        "about":            "Über",
        "apply_close":      "Anwenden & Schließen",
        "cancel":           "Abbrechen",
        "reset_defaults":   "Standard zurücksetzen",
        "theme":            "Design:",
        "preview":          "Vorschau:",
        "font_size":        "Schriftgröße:",
        "show_path_col":    "Pfadspalte anzeigen:",
        "tick_ms":          "Fortschrittsintervall (ms):",
        "crossfade_ms":     "Überblendung (ms):",
        "off":              "(0 = aus)",
        "scan_startup":     "Beim Start scannen:",
        "notifications":    "Titelbenachrichtigungen:",
        "notif_hint":       "(benötigt winotify, plyer oder win10toast)",
        "language":         "Language / Sprache:",
        "lang_restart":     "(Neustart erforderlich)",
        "confirm_clear":    "Vor dem Leeren bestätigen:",
        "cfg_location":     "Konfigurationsdatei:",
        "open_cfg_folder":  "Konfigurationsordner öffnen",
        "reset_confirm":    "Alle Einstellungen zurücksetzen?",
        "reset_title":      "Zurücksetzen",
        "version":          "Version 26.9.3",
        "publisher":        "Phoni Technology  ·  2026",
        "supports":         "Unterstützt MP3 · FLAC · WAV · M4A · MIDI · WMA\nErstellt mit Python, Tkinter, pygame, mutagen, Pillow",
        "shortcuts_title":  "Tastenkürzel",
        "shortcuts_text":   "Leertaste  Abspielen/Pause   N  Nächster Titel\nP  Vorheriger Titel          S  Stopp\n←/→  Überspringen ±5s       Shift+←/→  ±30s\n↑/↓  Lautstärke ±5%         M  Stummschalten\nR  Wiederholen               H  Mischen    Q  Warteschlange",
        "welcome_title":    "Willkommen",
        "welcome_msg":      "Willkommen bei PTMusic!\n\nMöchten Sie alle Laufwerke scannen?\nSie können auch später bestimmte Ordner scannen.",
        "clear_title":      "Bibliothek leeren",
        "clear_msg":        "Alle Titel entfernen?",
        "missing_file":     "Datei fehlt",
        "missing_msg":      "Nicht gefunden:\n{}",
        "queue_title":      "▶  Warteschlange",
        "play_next_btn":    "Als Nächstes",
        "move_up":          "Nach oben",
        "move_down":        "Nach unten",
        "remove_btn":       "Entfernen",
        "clear_btn":        "Leeren",
        "tracks_found":     "{} Titel{} gefunden",
        "tracks_label":     "{} Titel{}",
    },
}

def _t(key: str, *args) -> str:
    """Return translated string for current language, with optional .format() args."""
    lang = _CURRENT_LANG
    s = _STRINGS.get(lang, _STRINGS["English"]).get(key)
    if s is None:
        s = _STRINGS["English"].get(key, key)
    if args:
        try: s = s.format(*args)
        except Exception: pass
    return s

_CURRENT_LANG = "English"   # updated from config at startup


# ── THEMES ────────────────────────────────────────────────────────────────
THEMES = {
    "Aero Light": {
        "win_bg":"#dceaf6","glass_dark":"#e5f0fa","glass":"#f8fbff",
        "glass_mid":"#c8def2","glass_light":"#f5fbff","glass_lighter":"#ffffff",
        "border":"#7aa7d9","border_glow":"#bfe2ff","accent":"#2468a8",
        "accent_bright":"#0b5cad","accent_hot":"#1f7de2",
        "title_bar":"#365f94","title_bar2":"#456f9f","title_text":"#ffffff","tb_border":"#4f79b7",
        "btn":"#eaf3fc","btn_top":"#ffffff","btn_hover":"#d9ecff",
        "btn_press":"#bdd9f5","btn_border":"#7aa7d9",
        "text":"#1d3557","text_dim":"#56708f","text_bright":"#003b73",
        "sel":"#cfe8ff","sel_border":"#3399ff",
        "prog_bg":"#c7dff5","prog_fill":"#3a95e8","prog_bright":"#7bc3ff",
        "danger":"#c03a3a","danger_hover":"#e04848","green":"#2fa34f",
        "sidebar":"#e5f0fa","sidebar_sect":"#d5e5f4","row_alt":"#f2f8fd",
    },
    "Aero Dark": {
        "win_bg":"#0a1628","glass_dark":"#0d1f3c","glass":"#132840",
        "glass_mid":"#1a3a58","glass_light":"#224d72","glass_lighter":"#2d6494",
        "border":"#1e5a8a","border_glow":"#2e87cc","accent":"#3ea6e0",
        "accent_bright":"#7fd4ff","accent_hot":"#00aaff",
        "title_bar":"#0f2340","title_bar2":"#162e50","title_text":"#ddeeff","tb_border":"#1a4a7a",
        "btn":"#163352","btn_top":"#1e4570","btn_hover":"#1f4d7a",
        "btn_press":"#0c1f33","btn_border":"#2a6aaa",
        "text":"#ddeeff","text_dim":"#6a9cbb","text_bright":"#b8dff5",
        "sel":"#164872","sel_border":"#3ab0ff",
        "prog_bg":"#081828","prog_fill":"#1a8fd1","prog_bright":"#4dc8ff",
        "danger":"#c0304a","danger_hover":"#e03050","green":"#00e080",
        "sidebar":"#0e2238","sidebar_sect":"#0a1a2c","row_alt":"#0f2235",
    },
    "Mint": {
        "win_bg":"#e7f4eb","glass_dark":"#dcefe1","glass":"#f8fcf8",
        "glass_mid":"#d7e9d9","glass_light":"#fbfefb","glass_lighter":"#ffffff",
        "border":"#81c784","border_glow":"#a5d6a7","accent":"#2d7046",
        "accent_bright":"#2e7d32","accent_hot":"#43a047",
        "title_bar":"#276a48","title_bar2":"#2e7651","title_text":"#ffffff","tb_border":"#245e40",
        "btn":"#f1f8f1","btn_top":"#ffffff","btn_hover":"#dcedc8",
        "btn_press":"#c8e6c9","btn_border":"#81c784",
        "text":"#194b34","text_dim":"#416b50","text_bright":"#103c2a",
        "sel":"#c8e6c9","sel_border":"#43a047",
        "prog_bg":"#c8e6c9","prog_fill":"#388e3c","prog_bright":"#81c784",
        "danger":"#c62828","danger_hover":"#e53935","green":"#00695c",
        "sidebar":"#e0f0e3","sidebar_sect":"#cfe4d3","row_alt":"#f2faf3",
    },

    "Cherry": {
        "win_bg":"#1a0a0d","glass_dark":"#2a0d12","glass":"#3a1018",
        "glass_mid":"#4d1520","glass_light":"#661c2a","glass_lighter":"#802235",
        "border":"#8b2030","border_glow":"#cc3348","accent":"#d94060",
        "accent_bright":"#ff7088","accent_hot":"#ff2244",
        "title_bar":"#130809","title_bar2":"#1f0c10","title_text":"#ffe0e5","tb_border":"#8b2030",
        "btn":"#3a1018","btn_top":"#4d1520","btn_hover":"#5c1a25",
        "btn_press":"#0f0608","btn_border":"#8b2030",
        "text":"#ffe0e5","text_dim":"#b06070","text_bright":"#fff0f2",
        "sel":"#5c1a25","sel_border":"#d94060",
        "prog_bg":"#130809","prog_fill":"#b02840","prog_bright":"#e05070",
        "danger":"#ff2244","danger_hover":"#ff4466","green":"#44cc77",
        "sidebar":"#200c10","sidebar_sect":"#150809","row_alt":"#2a0e14",
    },
    "Sand": {
        "win_bg":"#f0e8d8","glass_dark":"#f3e9d6","glass":"#fffaf1",
        "glass_mid":"#ecdfc0","glass_light":"#fefaf0","glass_lighter":"#ffffff",
        "border":"#c8a878","border_glow":"#e8c898","accent":"#7d5933",
        "accent_bright":"#7a5828","accent_hot":"#c09050",
        "title_bar":"#72512e","title_bar2":"#805e35","title_text":"#ffffff","tb_border":"#684a2c",
        "btn":"#fdf6e8","btn_top":"#ffffff","btn_hover":"#ecdfc0",
        "btn_press":"#ddd0a8","btn_border":"#c8a878",
        "text":"#3a2808","text_dim":"#665235","text_bright":"#1e1404",
        "sel":"#e8d8a8","sel_border":"#c09050",
        "prog_bg":"#ddd0a8","prog_fill":"#a07840","prog_bright":"#d0a860",
        "danger":"#b03020","danger_hover":"#d04030","green":"#507030",
        "sidebar":"#f2e7d0","sidebar_sect":"#e7d7b8","row_alt":"#fcf4e5",
    },
    "Ocean Teal": {
        "win_bg":"#091e22","glass_dark":"#0d282d","glass":"#12343a",
        "glass_mid":"#1a4549","glass_light":"#22575a","glass_lighter":"#2e6b6a",
        "border":"#397b78","border_glow":"#63bdb1","accent":"#4fc4b2",
        "accent_bright":"#a3eee0","accent_hot":"#6ce3d0",
        "title_bar":"#0b3035","title_bar2":"#13505a","title_text":"#e4f7f2","tb_border":"#397b78",
        "btn":"#174046","btn_top":"#25575a","btn_hover":"#245b5e",
        "btn_press":"#0b282d","btn_border":"#397b78",
        "text":"#e4f7f2","text_dim":"#a5c7c2","text_bright":"#ffffff",
        "sel":"#24575b","sel_border":"#6ce3d0",
        "prog_bg":"#0a2428","prog_fill":"#3ba999","prog_bright":"#84e2d3",
        "danger":"#f27783","danger_hover":"#ff98a0","green":"#7de0a2",
        "sidebar":"#0e2a30","sidebar_sect":"#0a2428","row_alt":"#153940",
    },
    "Royale Noir": {
        "win_bg":"#0e0414","glass_dark":"#160b24","glass":"#1e1030",
        "glass_mid":"#2a1545","glass_light":"#38206a","glass_lighter":"#4a2d80",
        "border":"#5c2d8a","border_glow":"#9b4dca","accent":"#b06ee8",
        "accent_bright":"#d4a0ff","accent_hot":"#c060ff",
        "title_bar":"#12091e","title_bar2":"#1e0f30","title_text":"#ecdcff","tb_border":"#5c2d8a",
        "btn":"#1e1030","btn_top":"#2a1545","btn_hover":"#2a1545",
        "btn_press":"#0e0414","btn_border":"#5c2d8a",
        "text":"#ecdcff","text_dim":"#9966cc","text_bright":"#f0d0ff",
        "sel":"#3d1a6e","sel_border":"#b06ee8",
        "prog_bg":"#0e0414","prog_fill":"#7b2fbe","prog_bright":"#b06ee8",
        "danger":"#cc2255","danger_hover":"#ee3366","green":"#44cc88",
        "sidebar":"#160b24","sidebar_sect":"#0e0414","row_alt":"#1a0d2e",
    },
}
PUBLIC_THEMES = ["Aero Light", "Aero Dark", "Mint", "Cherry", "Sand", "Ocean Teal"]

# ── CONFIG ─────────────────────────────────────────────────────────────────
import sys as _cfg_sys, os as _cfg_os
_cfg_base = getattr(_cfg_sys, "_MEIPASS",
                    _cfg_os.path.dirname(_cfg_os.path.abspath(__file__)))
CONFIG_PATH = _cfg_os.path.join(
    _cfg_os.path.expanduser("~"), ".ptmusic_config.json")
RECENT_PATH = _cfg_os.path.join(
    _cfg_os.path.expanduser("~"), ".ptmusic_recent.json")

DEFAULTS = {
    "theme":            "Aero Light",
    "font_size":        9,
    "show_path_col":    True,
    "confirm_clear":    True,
    "scan_on_startup":  True,
    "tick_interval_ms": 400,
    "crossfade_ms":     0,
    "notifications":    True,
    "win_geometry":     "1180x760",
    "win_position":     "",
    "language":         "English",
    "minimize_to_tray": True,
}

def load_config():
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        for key in ("discord_rich_presence", "discord_client_id", "discord_large_image"):
            data.pop(key, None)
        for k, v in DEFAULTS.items():
            data.setdefault(k, v)
        return data
    except Exception:
        return dict(DEFAULTS)

def save_config(cfg: dict):
    try:
        cfg = {key: value for key, value in cfg.items()
               if key not in ("discord_rich_presence", "discord_client_id", "discord_large_image")}
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(cfg, f, indent=2)
    except Exception:
        pass

def load_recent() -> list:
    try:
        with open(RECENT_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []

def save_recent(items: list):
    try:
        with open(RECENT_PATH, "w", encoding="utf-8") as f:
            json.dump(items[-50:], f, indent=2)
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

def _get_cover_art(path: str, size: int = 80):
    """Extract embedded cover art from audio file. Returns ImageTk.PhotoImage or None."""
    if not PIL_AVAILABLE or not MUTAGEN_AVAILABLE:
        return None
    try:
        audio = MutagenFile(path)
        if not audio: return None
        img_data = None
        # MP3 / ID3
        if hasattr(audio, 'tags') and audio.tags:
            for tag in audio.tags.values():
                if hasattr(tag, 'data') and hasattr(tag, 'mime'):
                    img_data = tag.data; break
                if hasattr(tag, 'value') and isinstance(getattr(tag,'value',None), bytes):
                    img_data = tag.value; break
        # FLAC
        if not img_data and hasattr(audio, 'pictures') and audio.pictures:
            img_data = audio.pictures[0].data
        # M4A
        if not img_data and hasattr(audio, 'tags') and audio.tags:
            covr = audio.tags.get('covr')
            if covr: img_data = bytes(covr[0])
        if not img_data: return None
        import io
        img = Image.open(io.BytesIO(img_data)).resize((size, size), Image.LANCZOS)
        return ImageTk.PhotoImage(img)
    except Exception:
        return None

def _get_cover_art_bytes(path: str):
    """Extract embedded cover art as raw bytes (for export). Returns bytes or None."""
    if not MUTAGEN_AVAILABLE:
        return None
    try:
        audio = MutagenFile(path)
        if not audio: return None
        if hasattr(audio, 'tags') and audio.tags:
            for tag in audio.tags.values():
                if hasattr(tag, 'data') and hasattr(tag, 'mime'):
                    return tag.data
                if hasattr(tag, 'value') and isinstance(getattr(tag,'value',None), bytes):
                    return tag.value
        if hasattr(audio, 'pictures') and audio.pictures:
            return audio.pictures[0].data
        if hasattr(audio, 'tags') and audio.tags:
            covr = audio.tags.get('covr')
            if covr: return bytes(covr[0])
    except Exception:
        pass
    return None


# ── .PTM FILE FORMAT ─────────────────────────────────────────────────────
# A .ptm file is a ZIP container holding:
#   metadata.json  — title/artist/album/dur/ext + PTMusic marker
#   cover.jpg      — optional embedded cover art
#   audio.<ext>    — the original audio file, unmodified
PTM_EXT = ".ptm"

def export_ptm(info: dict, dest_path: str) -> tuple[bool, str]:
    """Bundle a track's audio + metadata + cover art into a .ptm file.
    Returns (success, message)."""
    import zipfile
    src_path = info["path"]
    if not os.path.exists(src_path):
        return False, f"Source file not found:\n{src_path}"
    try:
        meta = {
            "ptm_version": 1,
            "app":         "PTMusic",
            "title":       info.get("title", "—"),
            "artist":      info.get("artist", "—"),
            "album":       info.get("album", "—"),
            "dur":         info.get("dur", "—"),
            "dur_sec":     info.get("dur_sec", 0),
            "ext":         info.get("ext", Path(src_path).suffix.lstrip(".").upper()),
            "orig_filename": os.path.basename(src_path),
        }
        cover = _get_cover_art_bytes(src_path)

        with zipfile.ZipFile(dest_path, "w", zipfile.ZIP_DEFLATED) as z:
            z.writestr("metadata.json", json.dumps(meta, indent=2, ensure_ascii=False))
            audio_name = "audio" + Path(src_path).suffix.lower()
            z.write(src_path, audio_name)
            if cover:
                z.writestr("cover.img", cover)
        return True, f"Exported to:\n{dest_path}"
    except Exception as e:
        return False, f"Export failed:\n{e}"


def import_ptm(ptm_path: str, extract_dir: str) -> tuple[bool, str, dict]:
    """Extract a .ptm file's audio into extract_dir and return its info dict.
    Returns (success, message, info_dict)."""
    import zipfile
    try:
        with zipfile.ZipFile(ptm_path, "r") as z:
            names = z.namelist()
            meta_name = next((n for n in names if n == "metadata.json"), None)
            audio_name = next((n for n in names if n.startswith("audio.")), None)
            if not meta_name or not audio_name:
                return False, "Not a valid .ptm file (missing metadata or audio).", {}

            meta = json.loads(z.read(meta_name).decode("utf-8"))
            audio_ext = Path(audio_name).suffix

            os.makedirs(extract_dir, exist_ok=True)
            # Build a safe output filename from the original title
            safe_title = "".join(c for c in meta.get("title", "imported")
                                 if c.isalnum() or c in " -_()[]").strip() or "imported"
            out_path = os.path.join(extract_dir, safe_title + audio_ext)
            # Avoid overwriting existing files
            counter = 1
            base_out = out_path
            while os.path.exists(out_path):
                stem = Path(base_out).stem
                out_path = os.path.join(extract_dir, f"{stem} ({counter}){audio_ext}")
                counter += 1

            with z.open(audio_name) as src_f, open(out_path, "wb") as dst_f:
                shutil.copyfileobj(src_f, dst_f)

            info = {
                "path":    out_path,
                "title":   meta.get("title", Path(out_path).stem),
                "artist":  meta.get("artist", "—"),
                "album":   meta.get("album", "—"),
                "dur":     meta.get("dur", "—"),
                "dur_sec": meta.get("dur_sec", 0),
                "ext":     meta.get("ext", audio_ext.lstrip(".").upper()),
                "size":    os.path.getsize(out_path),
            }
            return True, f"Imported: {info['title']}", info
    except zipfile.BadZipFile:
        return False, "Not a valid .ptm file (corrupt or wrong format).", {}
    except Exception as e:
        return False, f"Import failed:\n{e}", {}


def fmt_size(b):
    if b < 1024:    return f"{b} B"
    if b < 1048576: return f"{b/1024:.1f} KB"
    return f"{b/1048576:.1f} MB"

def _notify(title: str, body: str):
    """Windows toast notification — winotify first, then PowerShell fallback."""
    try:
        import sys as _s
        if _s.platform != "win32":
            return

        # ── winotify ──────────────────────────────────────────────────────
        try:
            from winotify import Notification, audio
            import os as _o
            base = getattr(_s, "_MEIPASS", _o.path.dirname(_o.path.abspath(__file__)))
            icon_path = _o.path.abspath(_o.path.join(base, "PTMusic.png"))
            # Use PowerShell's AUMID so Windows doesn't require Start Menu registration
            aumid = ("{1AC14E77-02E7-4E5D-B744-2EB1AE5198B7}"
                     "\\WindowsPowerShell\\v1.0\\powershell.exe")
            toast = Notification(
                app_id=aumid,
                title=title,
                msg=body,
                icon=icon_path if _o.path.exists(icon_path) else "",
                duration="short",
            )
            toast.set_audio(audio.Default, loop=False)
            toast.show()
            return
        except Exception:
            pass

        # ── PowerShell raw fallback ───────────────────────────────────────
        import subprocess
        safe_title = title.replace("'", "").replace('"', "").replace("<", "").replace(">", "")
        safe_body  = body.replace("'",  "").replace('"', "").replace("<", "").replace(">", "")
        xml = (
            '<toast><visual><binding template="ToastGeneric">'
            '<text>' + safe_title + '</text>'
            '<text>' + safe_body  + '</text>'
            '</binding></visual></toast>'
        )
        ps = (
            'Add-Type -AssemblyName System.Runtime.WindowsRuntime;'
            '[void][Windows.UI.Notifications.ToastNotificationManager,Windows.UI.Notifications,ContentType=WindowsRuntime];'
            '[void][Windows.Data.Xml.Dom.XmlDocument,Windows.Data.Xml.Dom.XmlDocument,ContentType=WindowsRuntime];'
            '$xml=New-Object Windows.Data.Xml.Dom.XmlDocument;'
            '$xml.LoadXml(\'' + xml + '\');'
            '$t=[Windows.UI.Notifications.ToastNotification]::new($xml);'
            '$m=[Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier(\'PTMusic\');'
            '$m.Show($t)'
        )
        subprocess.Popen(
            ["powershell", "-WindowStyle", "Hidden", "-NonInteractive", "-Command", ps],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            creationflags=0x08000000
        )
    except Exception:
        pass

# ══════════════════════════════════════════════════════════════════════════
#  WIDGETS
# ══════════════════════════════════════════════════════════════════════════

class AeroBtn(tk.Label):
    def __init__(self, parent, text="", icon="", cmd=None,
                 w=88, h=26, danger=False, bg_override=None, **kw):
        kw.pop('square', None)
        self._bg = bg_override or A["win_bg"]
        self.cmd = cmd; self.text = text; self.icon = icon
        self.danger = danger; self._w = w; self._h = h
        self._hov = False; self._press = False
        lbl = (icon + (" " if icon and text else "") + text)
        super().__init__(parent, text=lbl, font=FONT_UI,
                         bg=A["btn"], fg=A["text"], relief="flat", bd=0,
                         padx=8, pady=3, cursor="hand2", **kw)
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
        if self._press:   bg = A["btn_press"]; fg = A["text_dim"]
        elif self._hov:   bg = A["btn_hover"]; fg = A["accent_bright"]
        else:             bg = A["btn"];       fg = A["text"]
        if self.danger:   fg = A["danger_hover"] if self._hov else A["danger"]
        self.config(bg=bg, fg=fg,
                    highlightbackground=A["btn_border"], highlightthickness=1)

    def _draw(self):
        lbl = (self.icon + (" " if self.icon and self.text else "") + self.text)
        self.config(text=lbl); self._refresh()


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
        box_frame = tk.Frame(self, bg=A["glass_dark"],
                             highlightthickness=1, highlightbackground=A["border"])
        box_frame.pack(fill="both", expand=True)
        self.lb = tk.Listbox(box_frame, bg=A["glass_dark"], fg=A["text"],
                             selectbackground=A["sel"], selectforeground=A["accent_bright"],
                             activestyle="none", font=FONT_SMALL, relief="flat",
                             highlightthickness=0, bd=0, height=6)
        vsb = ttk.Scrollbar(box_frame, orient="vertical", command=self.lb.yview)
        self.lb.configure(yscrollcommand=vsb.set)
        self.lb.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")
        btns = tk.Frame(self, bg=A["sidebar"])
        btns.pack(fill="x", pady=(3,0))
        AeroBtn(btns, icon="＋", text="Add Folder", cmd=self._add,
                w=120, h=24, bg_override=A["sidebar"]).pack(side="left", padx=(0,3))
        AeroBtn(btns, icon="−", text="Remove", cmd=self._remove,
                w=88, h=24, danger=True, bg_override=A["sidebar"]).pack(side="left")

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
        self.folders.pop(idx); self.lb.delete(idx)
        if self.on_change: self.on_change()

    def get_folders(self): return list(self.folders)

    def set_placeholder(self):
        self.lb.delete(0, "end")
        self.lb.insert("end", "  (all drives)")



# ══════════════════════════════════════════════════════════════════════════
#  ALBUMS VIEW
# ══════════════════════════════════════════════════════════════════════════

class AlbumsView(tk.Frame):
    """Scrollable grid of album cards, each showing art, title, artist, track count."""
    CARD_W = 130
    CARD_H = 160

    def __init__(self, parent, app, **kw):
        kw.setdefault("bg", A["glass"])
        super().__init__(parent, **kw)
        self.app = app
        self._art_cache = {}   # (album, artist) -> PhotoImage | None
        self._cards = []
        self._albums = []      # list of dicts
        self._build()

    def _build(self):
        # Search + sort bar
        top = tk.Frame(self, bg=A["glass_mid"])
        top.pack(fill="x", padx=0, pady=0)
        tk.Label(top, text=_t("search_albums"), bg=A["glass_mid"],
                 fg=A["text"], font=FONT_SMALL).pack(side="left", padx=(8,4), pady=6)
        self._search_var = tk.StringVar()
        self._search_var.trace_add("write", lambda *_: self.refresh(self.app.library))
        ef = tk.Frame(top, bg=A["border"], padx=1, pady=1)
        ef.pack(side="left", pady=6)
        tk.Entry(ef, textvariable=self._search_var, bg=A["glass"], fg=A["text"],
                 insertbackground=A["accent_hot"], relief="flat",
                 font=FONT_SMALL, width=18).pack(ipady=2)

        tk.Label(top, text=_t("sort"), bg=A["glass_mid"],
                 fg=A["text_dim"], font=FONT_SMALL).pack(side="left", padx=(12,4))
        self._sort_var = tk.StringVar(value="Name")   # fixed internal key
        for key, label in (("Name", _t("sort_name")),
                           ("Artist", _t("sort_artist")),
                           ("Tracks", _t("sort_tracks"))):
            tk.Radiobutton(top, text=label, variable=self._sort_var, value=key,
                           command=lambda: self.refresh(self.app.library),
                           bg=A["glass_mid"], fg=A["text"],
                           activebackground=A["glass_mid"],
                           selectcolor=A["glass_dark"],
                           font=FONT_SMALL).pack(side="left", padx=2)

        tk.Frame(self, bg=A["border"], height=1).pack(fill="x")

        # Scrollable canvas for cards
        self._canvas = tk.Canvas(self, bg=A["glass"], highlightthickness=0)
        vsb = ttk.Scrollbar(self, orient="vertical", command=self._canvas.yview)
        self._canvas.configure(yscrollcommand=vsb.set)
        vsb.pack(side="right", fill="y")
        self._canvas.pack(fill="both", expand=True)

        self._inner = tk.Frame(self._canvas, bg=A["glass"])
        self._canvas_win = self._canvas.create_window((0, 0), window=self._inner, anchor="nw")

        self._inner.bind("<Configure>", lambda e: self._canvas.configure(
            scrollregion=self._canvas.bbox("all")))
        self._canvas.bind("<Configure>", self._on_canvas_resize)
        self._canvas.bind("<MouseWheel>", lambda e: self._canvas.yview_scroll(
            -1 if e.delta > 0 else 1, "units"))

        tk.Label(self._inner, text="Scan your music library to see albums here.",
                 bg=A["glass"], fg=A["text_dim"], font=FONT_SMALL).pack(pady=40)

    def _on_canvas_resize(self, e):
        self._canvas.itemconfig(self._canvas_win, width=e.width)

    def refresh(self, library):
        """Rebuild the album grid from the library list."""
        # Group tracks by (album, artist)
        groups = {}
        for t in library:
            key = (t["album"], t["artist"])
            if key not in groups:
                groups[key] = {"album": t["album"], "artist": t["artist"],
                               "tracks": [], "path": t["path"]}
            groups[key]["tracks"].append(t)

        q = self._search_var.get().lower()
        albums = [v for v in groups.values()
                  if not q or q in v["album"].lower() or q in v["artist"].lower()]

        sort_key = self._sort_var.get()
        if sort_key == "Name":
            albums.sort(key=lambda a: a["album"].lower())
        elif sort_key == "Artist":
            albums.sort(key=lambda a: a["artist"].lower())
        else:
            albums.sort(key=lambda a: len(a["tracks"]), reverse=True)

        self._albums = albums
        self._redraw()

    def _redraw(self):
        for w in self._inner.winfo_children():
            w.destroy()
        self._art_cache.clear()

        if not self._albums:
            tk.Label(self._inner, text=_t("no_albums"),
                     bg=A["glass"], fg=A["text_dim"],
                     font=FONT_SMALL, justify="center").pack(pady=40)
            return

        # Work out how many columns fit
        canvas_w = self._canvas.winfo_width() or 800
        cols = max(1, canvas_w // (self.CARD_W + 8))

        for i, album in enumerate(self._albums):
            col = i % cols
            row = i // cols
            self._make_card(self._inner, album, row, col)

    def _make_card(self, parent, album, row, col):
        card = tk.Frame(parent, bg=A["glass_mid"],
                        width=self.CARD_W, height=self.CARD_H,
                        highlightthickness=1, highlightbackground=A["border"],
                        cursor="hand2")
        card.grid(row=row, column=col, padx=5, pady=5, sticky="nw")
        card.pack_propagate(False)
        card.bind("<Button-1>", lambda e, a=album: self._play_album(a))

        # Art
        art_lbl = tk.Label(card, bg=A["glass_dark"], width=self.CARD_W,
                            height=90, relief="flat")
        art_lbl.pack(fill="x")
        art_lbl.bind("<Button-1>", lambda e, a=album: self._play_album(a))

        # Load art in background thread
        key = (album["album"], album["artist"])
        def _load(path=album["path"], lbl=art_lbl, k=key):
            try:
                img = _get_cover_art(path, size=self.CARD_W)
                self._art_cache[k] = img
                if img:
                    lbl.after(0, lambda: lbl.config(image=img, text="", width=self.CARD_W, height=90))
                else:
                    lbl.after(0, lambda: lbl.config(text="♪", font=("Segoe UI", 28),
                                                     fg=A["text_dim"]))
            except Exception:
                pass
        threading.Thread(target=_load, daemon=True).start()

        # Album name
        name = album["album"][:18] + ("…" if len(album["album"]) > 18 else "")
        nl = tk.Label(card, text=name, bg=A["glass_mid"], fg=A["text"],
                      font=FONT_BOLD, anchor="w", wraplength=self.CARD_W-8)
        nl.pack(fill="x", padx=4, pady=(4,0))
        nl.bind("<Button-1>", lambda e, a=album: self._play_album(a))

        # Artist
        artist = album["artist"][:20] + ("…" if len(album["artist"]) > 20 else "")
        al = tk.Label(card, text=artist, bg=A["glass_mid"], fg=A["text_dim"],
                      font=FONT_SMALL, anchor="w")
        al.pack(fill="x", padx=4)
        al.bind("<Button-1>", lambda e, a=album: self._play_album(a))

        # Track count
        n = len(album["tracks"])
        tl = tk.Label(card, text=f"{n} track{'s' if n!=1 else ''}",
                      bg=A["glass_mid"], fg=A["accent_bright"],
                      font=FONT_SMALL, anchor="w")
        tl.pack(fill="x", padx=4)
        tl.bind("<Button-1>", lambda e, a=album: self._play_album(a))

        # Hover highlight
        def _enter(e, c=card): c.config(highlightbackground=A["accent_hot"])
        def _leave(e, c=card): c.config(highlightbackground=A["border"])
        for w in [card, art_lbl, nl, al, tl]:
            w.bind("<Enter>", _enter)
            w.bind("<Leave>", _leave)

    def _play_album(self, album):
        """Queue all tracks in the album and start playing."""
        app = self.app
        tracks = sorted(album["tracks"],
                        key=lambda t: t.get("title", "").lower())
        app.queue.clear()
        for t in tracks:
            app.queue.append(t)
        app._play_from_queue()


# ══════════════════════════════════════════════════════════════════════════
#  SETTINGS WINDOW
# ══════════════════════════════════════════════════════════════════════════

class SettingsWindow:
    def __init__(self, app):
        self.app = app
        self.cfg = dict(app.cfg)
        win = tk.Toplevel(app.root)
        win.title(_t("settings_title"))
        win.geometry("520x440")
        win.resizable(False, False)
        win.configure(bg=A["glass"])
        win.grab_set(); win.transient(app.root)
        self.win = win
        app.root.update_idletasks()
        px = app.root.winfo_x() + app.root.winfo_width()//2 - 260
        py = app.root.winfo_y() + app.root.winfo_height()//2 - 220
        win.geometry(f"+{px}+{py}")
        self._build()

    def _build(self):
        win = self.win
        hdr = tk.Frame(win, bg=A["title_bar"], height=36)
        hdr.pack(fill="x"); hdr.pack_propagate(False)
        tk.Label(hdr, text="⚙  " + _t("settings_title"), bg=A["title_bar"],
                 fg=A["title_text"], font=FONT_TITLE).pack(side="left", padx=12, pady=6)
        tk.Frame(win, bg=A["tb_border"], height=1).pack(fill="x")
        tab_bar = tk.Frame(win, bg=A["glass_dark"])
        tab_bar.pack(fill="x")
        tk.Frame(win, bg=A["border"], height=1).pack(fill="x")
        self.content = tk.Frame(win, bg=A["glass"])
        self.content.pack(fill="both", expand=True, padx=12, pady=8)
        tk.Frame(win, bg=A["border"], height=1).pack(fill="x")
        btn_bar = tk.Frame(win, bg=A["glass_dark"])
        btn_bar.pack(fill="x", padx=10, pady=6)
        AeroBtn(btn_bar, text=_t("apply_close"), icon="✔", cmd=self._apply,
                w=130, h=26, bg_override=A["glass_dark"]).pack(side="right", padx=(4,0))
        AeroBtn(btn_bar, text=_t("cancel"), icon="✖", cmd=self.win.destroy,
                w=80, h=26, danger=True, bg_override=A["glass_dark"]).pack(side="right")
        AeroBtn(btn_bar, text=_t("reset_defaults"), icon="↺", cmd=self._reset,
                w=120, h=26, bg_override=A["glass_dark"]).pack(side="left")
        self.tab_btns = {}; self.tabs = {}
        # Fixed internal keys, translated display labels
        tab_defs = [
            ("Appearance", _t("appearance")),
            ("Playback",   _t("playback")),
            ("Library",    _t("lib_tab")),
            ("About",      _t("about")),
        ]
        for key, label in tab_defs:
            btn = tk.Label(tab_bar, text=label, font=FONT_UI,
                           bg=A["glass_dark"], fg=A["text_dim"],
                           padx=14, pady=6, cursor="hand2")
            btn.pack(side="left")
            btn.bind("<Button-1>", lambda e, n=key: self._show_tab(n))
            self.tab_btns[key] = btn
            self.tabs[key] = tk.Frame(self.content, bg=A["glass"])
        self._build_appearance(); self._build_playback()
        self._build_library_tab(); self._build_about()
        self._show_tab("Appearance")

    def _show_tab(self, name):
        for f in self.tabs.values(): f.pack_forget()
        for n, b in self.tab_btns.items():
            b.config(bg=A["glass_dark"], fg=A["text_dim"])
        self.tabs[name].pack(fill="both", expand=True)
        self.tab_btns[name].config(bg=A["glass_mid"], fg=A["accent_bright"])

    def _build_appearance(self):
        f = self.tabs["Appearance"]
        def row(label):
            r = tk.Frame(f, bg=A["glass"]); r.pack(fill="x", pady=5)
            tk.Label(r, text=label, bg=A["glass"], fg=A["text"],
                     font=FONT_UI, width=18, anchor="w").pack(side="left")
            return r
        r = row(_t("theme"))
        self.theme_var = tk.StringVar(value=self.cfg["theme"])
        visible = list(PUBLIC_THEMES)
        if self.cfg.get("theme") == "Royale Noir" or self.cfg.get("royale_noir_unlocked"):
            visible.append("Royale Noir")
        om = ttk.OptionMenu(r, self.theme_var, self.cfg["theme"], *visible,
                            command=self._preview_theme)
        om.config(width=20); om.pack(side="left", padx=4)
        self.swatch_frame = tk.Frame(f, bg=A["glass"])
        self.swatch_frame.pack(fill="x", pady=(0,8))
        self._draw_swatches(self.cfg["theme"])
        tk.Frame(f, bg=A["border"], height=1).pack(fill="x", pady=4)
        r = row(_t("font_size"))
        self.font_var = tk.IntVar(value=self.cfg["font_size"])
        for size in (8, 9, 10, 11, 12):
            tk.Radiobutton(r, text=str(size), variable=self.font_var, value=size,
                           bg=A["glass"], fg=A["text"], activebackground=A["glass"],
                           selectcolor=A["glass_dark"], font=FONT_SMALL
                           ).pack(side="left", padx=3)
        tk.Frame(f, bg=A["border"], height=1).pack(fill="x", pady=4)
        r = row("Show path column:")
        self.path_col_var = tk.BooleanVar(value=self.cfg["show_path_col"])
        tk.Checkbutton(r, variable=self.path_col_var, bg=A["glass"],
                       activebackground=A["glass"], selectcolor=A["glass_dark"]).pack(side="left")

    def _draw_swatches(self, name):
        for w in self.swatch_frame.winfo_children(): w.destroy()
        palette = THEMES.get(name, {})
        tk.Label(self.swatch_frame, text=_t("preview"), bg=A["glass"],
                 fg=A["text_dim"], font=FONT_SMALL).pack(side="left", padx=(0,6))
        for key in ["win_bg","glass","accent","accent_bright","btn","text",
                    "prog_fill","danger","green","sidebar"]:
            col = palette.get(key, "#888888")
            tk.Label(self.swatch_frame, bg=col, width=3,
                     relief="solid", bd=1).pack(side="left", padx=1, pady=4)

    def _preview_theme(self, name): self._draw_swatches(name)

    def _build_playback(self):
        f = self.tabs["Playback"]
        def row(label):
            r = tk.Frame(f, bg=A["glass"]); r.pack(fill="x", pady=6)
            tk.Label(r, text=label, bg=A["glass"], fg=A["text"],
                     font=FONT_UI, width=22, anchor="w").pack(side="left")
            return r
        r = row(_t("tick_ms"))
        self.tick_var = tk.IntVar(value=self.cfg["tick_interval_ms"])
        tk.Scale(r, variable=self.tick_var, from_=100, to=1000, orient="horizontal",
                 length=200, resolution=50, bg=A["glass"], fg=A["text"],
                 troughcolor=A["prog_bg"], highlightthickness=0,
                 activebackground=A["accent_hot"]).pack(side="left", padx=4)
        tk.Label(r, textvariable=self.tick_var, bg=A["glass"],
                 fg=A["text_dim"], font=FONT_MONO, width=5).pack(side="left")
        tk.Frame(f, bg=A["border"], height=1).pack(fill="x", pady=4)
        r = row(_t("crossfade_ms"))
        self.xfade_var = tk.IntVar(value=self.cfg["crossfade_ms"])
        tk.Scale(r, variable=self.xfade_var, from_=0, to=5000, orient="horizontal",
                 length=200, resolution=100, bg=A["glass"], fg=A["text"],
                 troughcolor=A["prog_bg"], highlightthickness=0,
                 activebackground=A["accent_hot"]).pack(side="left", padx=4)
        tk.Label(r, textvariable=self.xfade_var, bg=A["glass"],
                 fg=A["text_dim"], font=FONT_MONO, width=5).pack(side="left")
        tk.Label(r, text=_t("off"), bg=A["glass"],
                 fg=A["text_dim"], font=FONT_SMALL).pack(side="left", padx=4)
        tk.Frame(f, bg=A["border"], height=1).pack(fill="x", pady=4)
        r = row(_t("scan_startup"))
        self.startup_var = tk.BooleanVar(value=self.cfg["scan_on_startup"])
        tk.Checkbutton(r, variable=self.startup_var, bg=A["glass"],
                       activebackground=A["glass"], selectcolor=A["glass_dark"]).pack(side="left")
        tk.Frame(f, bg=A["border"], height=1).pack(fill="x", pady=4)
        r = row(_t("notifications"))
        self.notif_var = tk.BooleanVar(value=self.cfg.get("notifications", True))
        tk.Checkbutton(r, variable=self.notif_var, bg=A["glass"],
                       activebackground=A["glass"], selectcolor=A["glass_dark"]).pack(side="left")
        tk.Frame(f, bg=A["border"], height=1).pack(fill="x", pady=4)
        r = row("Minimize to tray:")
        self.tray_var = tk.BooleanVar(value=self.cfg.get("minimize_to_tray", True))
        tk.Checkbutton(r, variable=self.tray_var, bg=A["glass"],
                       activebackground=A["glass"], selectcolor=A["glass_dark"]).pack(side="left")
        if not PYSTRAY_AVAILABLE:
            tk.Label(r, text="(requires: pip install pystray)", bg=A["glass"],
                     fg=A["text_dim"], font=FONT_SMALL).pack(side="left", padx=4)
        tk.Frame(f, bg=A["border"], height=1).pack(fill="x", pady=4)
        r = row(_t("language"))
        self.lang_var = tk.StringVar(value=self.cfg.get("language", "English"))
        for lang in ("English", "Deutsch"):
            tk.Radiobutton(r, text=lang, variable=self.lang_var, value=lang,
                           bg=A["glass"], fg=A["text"],
                           activebackground=A["glass"], activeforeground=A["accent"],
                           selectcolor=A["glass_dark"],
                           font=FONT_SMALL).pack(side="left", padx=6)
        tk.Label(r, text=_t("lang_restart"), bg=A["glass"],
                 fg=A["text_dim"], font=FONT_SMALL).pack(side="left", padx=4)

    def _build_library_tab(self):
        f = self.tabs["Library"]
        def row(label):
            r = tk.Frame(f, bg=A["glass"]); r.pack(fill="x", pady=6)
            tk.Label(r, text=label, bg=A["glass"], fg=A["text"],
                     font=FONT_UI, width=22, anchor="w").pack(side="left")
            return r
        r = row(_t("confirm_clear"))
        self.confirm_var = tk.BooleanVar(value=self.cfg["confirm_clear"])
        tk.Checkbutton(r, variable=self.confirm_var, bg=A["glass"],
                       activebackground=A["glass"], selectcolor=A["glass_dark"]).pack(side="left")
        tk.Frame(f, bg=A["border"], height=1).pack(fill="x", pady=4)
        r = row(_t("cfg_location"))
        tk.Label(r, text=CONFIG_PATH, bg=A["glass"], fg=A["text_dim"],
                 font=FONT_SMALL, wraplength=320, justify="left").pack(side="left", padx=4)
        tk.Frame(f, bg=A["border"], height=1).pack(fill="x", pady=4)
        AeroBtn(f, text=_t("open_cfg_folder"), icon="📁",
                cmd=self._open_cfg_folder, w=160, h=26,
                bg_override=A["glass"]).pack(anchor="w", pady=4)

    def _open_cfg_folder(self):
        import subprocess, sys
        folder = os.path.dirname(CONFIG_PATH)
        if sys.platform == "win32": subprocess.Popen(["explorer", folder])
        elif sys.platform == "darwin": subprocess.Popen(["open", folder])
        else: subprocess.Popen(["xdg-open", folder])

    def _build_about(self):
        f = self.tabs["About"]
        tk.Label(f, text="PTMusic", bg=A["glass"],
                 fg=A["accent_bright"], font=("Segoe UI Light", 22)).pack(pady=(20,4))
        tk.Label(f, text=_t("version"), bg=A["glass"],
                 fg=A["text_dim"], font=FONT_UI).pack()
        tk.Label(f, text=_t("publisher"), bg=A["glass"],
                 fg=A["text_dim"], font=FONT_SMALL).pack(pady=(2,16))
        tk.Frame(f, bg=A["border"], height=1).pack(fill="x")
        tk.Label(f, text=_t("supports"),
                 bg=A["glass"], fg=A["text_dim"],
                 font=FONT_SMALL, justify="center").pack(pady=12)
        tk.Frame(f, bg=A["border"], height=1).pack(fill="x")
        shortcuts = (
            _t("shortcuts_text")
        )
        tk.Label(f, text=_t("shortcuts_title"), bg=A["glass"],
                 fg=A["accent_bright"], font=FONT_BOLD).pack(pady=(10,4))
        tk.Label(f, text=shortcuts, bg=A["glass"], fg=A["text_dim"],
                 font=FONT_MONO, justify="left").pack(padx=12)

    def _apply(self):
        self.cfg["theme"]            = self.theme_var.get()
        self.cfg["font_size"]        = self.font_var.get()
        self.cfg["show_path_col"]    = self.path_col_var.get()
        self.cfg["tick_interval_ms"] = self.tick_var.get()
        self.cfg["crossfade_ms"]     = self.xfade_var.get()
        self.cfg["scan_on_startup"]  = self.startup_var.get()
        self.cfg["confirm_clear"]    = self.confirm_var.get()
        self.cfg["notifications"]    = self.notif_var.get()
        self.cfg["minimize_to_tray"] = self.tray_var.get()
        self.cfg["language"]         = self.lang_var.get()
        save_config(self.cfg)
        self.app.cfg = self.cfg
        PhoniPlayer._apply_theme(self.cfg["theme"])
        self.app._rebuild_ui()
        try:
            if self.cfg["show_path_col"]:
                self.app.tree.column("path", width=260, minwidth=36)
            else:
                self.app.tree.column("path", width=0, minwidth=0, stretch=False)
        except Exception: pass
        self.win.destroy()

    def _reset(self):
        if messagebox.askyesno(_t("reset_title"), _t("reset_confirm"), parent=self.win):
            self.cfg = dict(DEFAULTS)
            save_config(self.cfg)
            self.app.cfg = self.cfg
            PhoniPlayer._apply_theme(self.cfg["theme"])
            self.app._rebuild_ui()
            self.win.destroy()


# ══════════════════════════════════════════════════════════════════════════
#  EASTER EGG
# ══════════════════════════════════════════════════════════════════════════

class EasterEggWindow:
    def __init__(self, root):
        win = tk.Toplevel(root)
        win.title("Sneak Peaks"); win.geometry("400x320")
        win.resizable(False, False); win.configure(bg="#0a0a0a")
        win.grab_set(); win.transient(root)
        root.update_idletasks()
        win.geometry(f"+{root.winfo_x()+root.winfo_width()//2-200}"
                     f"+{root.winfo_y()+root.winfo_height()//2-160}")
        self.win = win; self._frame = 0
        self._colors = ["#ff0000","#ff7700","#ffff00","#00ff00",
                        "#0000ff","#8b00ff","#ff00ff"]
        self._build(); self._animate()

    def _build(self):
        self.title_lbl = tk.Label(self.win, text="🎵 PHONI TECHNOLOGY 🎵",
                                   bg="#0a0a0a", fg="#ff0000",
                                   font=("Segoe UI", 13, "bold"))
        self.title_lbl.pack(pady=(24,4))
        tk.Label(self.win,
                 text="hello there!\n\nwelcome here. its cool isnt it?\n"
                      "dont you just miss more themes?",
                 bg="#0a0a0a", fg="#cccccc",
                 font=("Segoe UI", 9), justify="center").pack(pady=8)
        self.note_lbl = tk.Label(self.win, text="♪  ♫  ♩  ♬  ♭",
                                  bg="#0a0a0a", fg="#ffffff", font=("Segoe UI", 18))
        self.note_lbl.pack(pady=8)
        tk.Button(self.win, text="leaved",
                  command=self.win.destroy, bg="#1a1a1a", fg="#aaaaaa",
                  relief="flat", font=("Segoe UI", 9),
                  activebackground="#333333", activeforeground="#ffffff",
                  padx=12, pady=4).pack(pady=16)

    def _animate(self):
        try:
            col = self._colors[self._frame % len(self._colors)]
            self.title_lbl.config(fg=col)
            notes = ["♪  ♫  ♩  ♬  ♭","♫  ♩  ♬  ♭  ♪","♩  ♬  ♭  ♪  ♫",
                     "♬  ♭  ♪  ♫  ♩","♭  ♪  ♫  ♩  ♬"]
            self.note_lbl.config(text=notes[self._frame % len(notes)])
            self._frame += 1
            self.win.after(150, self._animate)
        except Exception: pass


# ══════════════════════════════════════════════════════════════════════════
#  MINI PLAYER
# ══════════════════════════════════════════════════════════════════════════

class MiniPlayer:
    def __init__(self, app):
        self.app = app
        win = tk.Toplevel(app.root)
        win.title("PTMusic Mini")
        win.geometry("420x90")
        win.resizable(False, False)
        win.configure(bg=A["glass_dark"])
        win.attributes("-topmost", True)
        win.overrideredirect(True)   # borderless
        win.transient(app.root)
        self.win = win
        self._drag_x = 0; self._drag_y = 0
        self._art_img = None
        self._build()
        self._update()
        # drag to move
        win.bind("<ButtonPress-1>",   self._drag_start)
        win.bind("<B1-Motion>",        self._drag_move)

    def _drag_start(self, e):
        self._drag_x = e.x_root - self.win.winfo_x()
        self._drag_y = e.y_root - self.win.winfo_y()

    def _drag_move(self, e):
        self.win.geometry(f"+{e.x_root - self._drag_x}+{e.y_root - self._drag_y}")

    def _build(self):
        win = self.win
        # thin colour strip at top
        tk.Frame(win, bg=A["accent"], height=3).pack(fill="x")

        body = tk.Frame(win, bg=A["glass_dark"])
        body.pack(fill="both", expand=True, padx=4, pady=4)

        # Cover art thumbnail
        self.art_lbl = tk.Label(body, bg=A["glass_mid"], width=5,
                                 relief="flat", bd=0)
        self.art_lbl.pack(side="left", padx=(0,6))

        # Track info
        info = tk.Frame(body, bg=A["glass_dark"])
        info.pack(side="left", fill="both", expand=True)
        self.mini_title = tk.Label(info, text="Nothing playing",
                                    bg=A["glass_dark"], fg=A["accent_bright"],
                                    font=FONT_BOLD, anchor="w")
        self.mini_title.pack(fill="x")
        self.mini_sub = tk.Label(info, text="",
                                  bg=A["glass_dark"], fg=A["text_dim"],
                                  font=FONT_SMALL, anchor="w")
        self.mini_sub.pack(fill="x")

        # Mini progress bar
        self.mini_prog = tk.Canvas(info, height=4, bg=A["prog_bg"],
                                    highlightthickness=0)
        self.mini_prog.pack(fill="x", pady=(3,0))

        # Controls
        ctrl = tk.Frame(body, bg=A["glass_dark"])
        ctrl.pack(side="right", padx=(6,0))
        for icon, cmd in [("⏮", self.app._prev),
                           ("⏸" if self.app.playing else "▶", self.app._playpause),
                           ("⏭", self.app._next),
                           ("✖", self._close)]:
            AeroBtn(ctrl, icon=icon, cmd=cmd, w=28, h=28,
                    bg_override=A["glass_dark"],
                    danger=(icon=="✖")).pack(side="left", padx=1)

    def _close(self):
        self.app.mini_player = None
        self.win.destroy()

    def _update(self):
        try:
            app = self.app
            # Title / sub
            title = app.now_title.cget("text") if hasattr(app, 'now_title') else "Nothing playing"
            sub   = app.now_sub.cget("text")   if hasattr(app, 'now_sub')   else ""
            self.mini_title.config(text=title[:45] + ("…" if len(title)>45 else ""))
            self.mini_sub.config(text=sub[:55] + ("…" if len(sub)>55 else ""))

            # Progress bar
            W = self.mini_prog.winfo_width()
            self.mini_prog.delete("all")
            if app._tlen > 0 and W > 0 and PYGAME_AVAILABLE and app.playing:
                raw = pygame.mixer.music.get_pos() / 1000.0
                if raw >= 0:
                    pos = app._seek_offset + raw
                    fw = int(min(pos / app._tlen, 1.0) * W)
                    self.mini_prog.create_rectangle(0,0,W,4, fill=A["prog_bg"], outline="")
                    if fw > 0:
                        self.mini_prog.create_rectangle(0,0,fw,4, fill=A["prog_fill"], outline="")

            # Cover art
            if app.playing and app.cur_idx >= 0 and 0 <= app.cur_idx < len(app.filtered):
                path = app.filtered[app.cur_idx]["path"]
                img = _get_cover_art(path, size=60)
                if img:
                    self._art_img = img
                    self.art_lbl.config(image=img, width=60, height=60)
                else:
                    self.art_lbl.config(image="", text="🎵", font=("Segoe UI",18),
                                         width=3, height=2)
            self.win.after(500, self._update)
        except Exception:
            pass


# ══════════════════════════════════════════════════════════════════════════
#  QUEUE WINDOW
# ══════════════════════════════════════════════════════════════════════════

class QueueWindow:
    def __init__(self, app):
        self.app = app
        win = tk.Toplevel(app.root)
        win.title("Play Queue")
        win.geometry("420x500")
        win.configure(bg=A["glass"])
        win.transient(app.root)
        self.win = win
        app.root.update_idletasks()
        win.geometry(f"+{app.root.winfo_x()+app.root.winfo_width()-440}"
                     f"+{app.root.winfo_y()+60}")
        self._build()
        self._refresh()

    def _build(self):
        hdr = tk.Frame(self.win, bg=A["title_bar"], height=36)
        hdr.pack(fill="x"); hdr.pack_propagate(False)
        tk.Label(hdr, text=_t("queue_title"), bg=A["title_bar"],
                 fg=A["title_text"], font=FONT_TITLE).pack(side="left", padx=12, pady=6)
        tk.Frame(self.win, bg=A["tb_border"], height=1).pack(fill="x")

        # Queue listbox
        lf = GlassPanel(self.win)
        lf.pack(fill="both", expand=True, padx=6, pady=6)
        self.lb = tk.Listbox(lf, bg=A["glass"], fg=A["text"],
                              selectbackground=A["sel"], selectforeground=A["accent_bright"],
                              activestyle="none", font=FONT_SMALL,
                              relief="flat", highlightthickness=0, bd=0)
        vsb = ttk.Scrollbar(lf, orient="vertical", command=self.lb.yview)
        self.lb.configure(yscrollcommand=vsb.set)
        vsb.pack(side="right", fill="y")
        self.lb.pack(fill="both", expand=True, padx=4, pady=4)
        self.lb.bind("<Double-1>", self._play_selected)

        # Buttons
        btn_row = tk.Frame(self.win, bg=A["glass_dark"])
        btn_row.pack(fill="x", padx=6, pady=(0,6))
        AeroBtn(btn_row, icon="▶", text=_t("play_next_btn"), w=100, h=26,
                cmd=self._play_next, bg_override=A["glass_dark"]).pack(side="left", padx=3)
        AeroBtn(btn_row, icon="↑", text=_t("move_up"), w=90, h=26,
                cmd=self._move_up, bg_override=A["glass_dark"]).pack(side="left", padx=3)
        AeroBtn(btn_row, icon="↓", text=_t("move_down"), w=100, h=26,
                cmd=self._move_down, bg_override=A["glass_dark"]).pack(side="left", padx=3)
        AeroBtn(btn_row, icon="✖", text=_t("remove_btn"), w=90, h=26, danger=True,
                cmd=self._remove, bg_override=A["glass_dark"]).pack(side="left", padx=3)
        AeroBtn(btn_row, icon="🗑", text=_t("clear_btn"), w=80, h=26, danger=True,
                cmd=self._clear, bg_override=A["glass_dark"]).pack(side="right", padx=3)

    def _refresh(self):
        self.lb.delete(0, "end")
        for i, info in enumerate(self.app.queue):
            prefix = "▶ " if i == 0 else f"{i+1}. "
            self.lb.insert("end", f"{prefix}{info['title']}  —  {info['artist']}")

    def _play_selected(self, e=None):
        sel = self.lb.curselection()
        if not sel: return
        idx = sel[0]
        info = self.app.queue[idx]
        # Move to front and play
        self.app.queue.rotate(-idx)
        self.app._play_from_queue()
        self._refresh()

    def _play_next(self):
        sel = self.lb.curselection()
        if not sel or len(self.app.queue) == 0: return
        idx = sel[0]
        item = self.app.queue[idx]
        del self.app.queue[idx]
        self.app.queue.appendleft(item)
        self._refresh()

    def _move_up(self):
        sel = self.lb.curselection()
        if not sel or sel[0] == 0: return
        idx = sel[0]
        self.app.queue[idx], self.app.queue[idx-1] = \
            self.app.queue[idx-1], self.app.queue[idx]
        self._refresh(); self.lb.selection_set(idx-1)

    def _move_down(self):
        sel = self.lb.curselection()
        if not sel or sel[0] >= len(self.app.queue)-1: return
        idx = sel[0]
        self.app.queue[idx], self.app.queue[idx+1] = \
            self.app.queue[idx+1], self.app.queue[idx]
        self._refresh(); self.lb.selection_set(idx+1)

    def _remove(self):
        sel = self.lb.curselection()
        if not sel: return
        del self.app.queue[sel[0]]; self._refresh()

    def _clear(self):
        self.app.queue.clear(); self._refresh()


# ══════════════════════════════════════════════════════════════════════════
#  MAIN APP
# ══════════════════════════════════════════════════════════════════════════

class PhoniPlayer:
    def __init__(self, open_ptm_path: str = None):
        self._pending_ptm = open_ptm_path   # .ptm file to import once UI is ready
        self.cfg = load_config()
        global _CURRENT_LANG
        _CURRENT_LANG = self.cfg.get("language", "English")
        self._apply_theme(self.cfg["theme"], rebuild=False)

        self.root = tk.Tk()
        _init_fonts()
        self.root.title("PTMusic")
        # Restore saved window size and position
        saved_geom = self.cfg.get("win_geometry", "1180x760")
        saved_pos  = self.cfg.get("win_position", "")
        if saved_pos:
            self.root.geometry(f"{saved_geom}{saved_pos}")
        else:
            self.root.geometry(saved_geom)
        self.root.minsize(860, 580)
        self.root.configure(bg=A["win_bg"])

        import sys as _sys2, os as _os2
        _base2 = getattr(_sys2, "_MEIPASS", _os2.path.dirname(_os2.path.abspath(__file__)))
        _icon_path2 = _os2.path.join(_base2, "PTMusic.png")
        try:
            self._wm_icon = ImageTk.PhotoImage(Image.open(_icon_path2))
            self.root.iconphoto(True, self._wm_icon)
        except Exception: pass

        self.library:  list[dict] = []
        self.filtered: list[dict] = []
        self.queue:    deque      = deque()   # play queue
        self.recent:   list[dict] = load_recent()  # recently played

        self.cur_idx    = -1
        self.playing    = False
        self.paused     = False
        self.scan_stop  = threading.Event()
        self.scan_th    = None
        self.prog_after = None
        self._tlen      = 0
        self._seek_offset = 0.0
        self._vol       = 0.8
        self._use_folders = False
        self._logo_clicks = 0
        self._konami_buf  = ""
        self._repeat      = False
        self.mini_player  = None
        self.queue_win    = None
        self._cover_cache = {}   # path -> PhotoImage
        self._tray_icon   = None   # pystray.Icon instance, once created
        self._tray_thread = None
        self._current_track = None  # dict of the currently playing track, for tray tooltip

        self._build()
        self._style()
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

        first_run_folder = self.cfg.pop("first_run_scan_folder", None)
        if first_run_folder:
            save_config(self.cfg)   # consume the key so this only runs once

        if self._pending_ptm:
            # A .ptm file was opened via double-click / file association —
            # import it instead of the normal startup scan dialog.
            self.root.after(250, lambda: self._import_ptm_file(self._pending_ptm))
        elif first_run_folder and os.path.exists(first_run_folder):
            # Installer bundled example music — auto-scan it on first launch
            self.root.after(250, lambda: self._scan_first_run_folder(first_run_folder))
        else:
            self.root.after(250, self._startup_dialog if self.cfg.get("scan_on_startup", True) else lambda: None)

        self.root.mainloop()

    # ── THEME ─────────────────────────────────────────────────────────────
    @staticmethod
    def _apply_theme(theme_name, rebuild=True):
        A.update(THEMES.get(theme_name, THEMES["Aero Light"]))

    def _open_settings(self): SettingsWindow(self)

    def _rebuild_ui(self):
        if self.prog_after:
            try: self.root.after_cancel(self.prog_after)
            except: pass
            self.prog_after = None
        for w in self.root.winfo_children():
            try: w.destroy()
            except: pass
        self.root.configure(bg=A["win_bg"])
        self._build(); self._style(); self._style()
        try:
            self.tree.delete(*self.tree.get_children())
            for info in (self.filtered if self.filtered else self.library):
                self.tree.insert("", "end", iid=info["path"],
                                 values=(info["title"], info["artist"], info["album"],
                                         info["dur"], info["ext"],
                                         fmt_size(info["size"]), info["path"]))
            self.lib_count.config(text=f"({len(self.filtered or self.library)} tracks)")
            self._upd_stats()
        except Exception: pass
        try: self.albums_view.refresh(self.library)
        except Exception: pass

    # ── BUILD ─────────────────────────────────────────────────────────────
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
        tb = tk.Canvas(self.root, height=36, bg=A["title_bar"], highlightthickness=0)
        tb.pack(fill="x")
        tb.create_rectangle(0,0,2000,18,  fill=A["title_bar"],  outline="")
        tb.create_rectangle(0,18,2000,36, fill=A["title_bar2"], outline="")
        tb.create_line(0,0,2000,0, fill=A["border_glow"])
        import sys as _sys, os as _os
        _base = getattr(_sys, "_MEIPASS", _os.path.dirname(_os.path.abspath(__file__)))
        _icon_path = _os.path.join(_base, "PTMusic.png")
        try:
            _raw = Image.open(_icon_path).resize((24,24), Image.LANCZOS)
            self._title_img = ImageTk.PhotoImage(_raw)
            tb.create_image(10,18, image=self._title_img, anchor="w")
            tb.create_text(40,18, text="PTMusic", fill=A["title_text"],
                           font=FONT_TITLE, anchor="w")
        except Exception:
            tb.create_text(12,18, text="PTMusic", fill=A["title_text"],
                           font=FONT_TITLE, anchor="w")
        tk.Frame(self.root, bg=A["tb_border"], height=1).pack(fill="x")
        tb.bind("<Button-1>", self._logo_click)
        self.root.bind_all("<Key>", self._konami)
        self._register_shortcuts()

    def _register_shortcuts(self):
        r = self.root
        # Ignore shortcuts when typing in an Entry widget
        def _guard(fn):
            def _wrapped(e):
                if isinstance(e.widget, tk.Entry): return
                fn(e)
            return _wrapped

        r.bind_all("<space>",          _guard(lambda e: self._playpause()))
        r.bind_all("<n>",              _guard(lambda e: self._next()))
        r.bind_all("<p>",              _guard(lambda e: self._prev()))
        r.bind_all("<s>",              _guard(lambda e: self._stop()))
        r.bind_all("<m>",              _guard(lambda e: self._toggle_mute()))
        r.bind_all("<r>",              _guard(lambda e: self._toggle_repeat()))
        r.bind_all("<h>",              _guard(lambda e: self._shuffle()))
        # Skip ±5 seconds
        r.bind_all("<Left>",           _guard(lambda e: self._seek_by(-5)))
        r.bind_all("<Right>",          _guard(lambda e: self._seek_by(5)))
        # Skip ±30 seconds
        r.bind_all("<Shift-Left>",     _guard(lambda e: self._seek_by(-30)))
        r.bind_all("<Shift-Right>",    _guard(lambda e: self._seek_by(30)))
        # Volume ±5%
        r.bind_all("<Up>",             _guard(lambda e: self._change_vol(5)))
        r.bind_all("<Down>",           _guard(lambda e: self._change_vol(-5)))
        # Queue selected
        r.bind_all("<q>",              _guard(lambda e: self._queue_selected()))

    def _logo_click(self, e=None):
        self._logo_clicks += 1
        if self._logo_clicks >= 7:
            self._logo_clicks = 0; EasterEggWindow(self.root)

    def _konami(self, e):
        ch = e.char
        if not ch: return
        self._konami_buf = (self._konami_buf + ch)[-15:]
        if self._konami_buf.lower().endswith("phoni"):
            self._konami_buf = ""; EasterEggWindow(self.root)
        elif self._konami_buf.endswith("MORE THEMES PLS"):
            self._konami_buf = ""
            self.cfg["royale_noir_unlocked"] = True
            self.cfg["theme"] = "Royale Noir"
            save_config(self.cfg)
            PhoniPlayer._apply_theme("Royale Noir")
            self._rebuild_ui()
            messagebox.showinfo("👑 Royale Noir Unlocked",
                                "You found the secret theme!\n\nRoyale Noir is now available in Settings.",
                                parent=self.root)

    def _build_toolbar(self):
        bar = tk.Frame(self.root, bg=A["glass_dark"], height=36)
        bar.pack(fill="x"); bar.pack_propagate(False)

        self.scan_btn = AeroBtn(bar, icon="🔍", text=_t("scan_all"),
                                cmd=self._start_scan_all, w=140, h=26,
                                bg_override=A["glass_dark"])
        self.scan_btn.pack(side="left", padx=(8,3), pady=5)
        AeroBtn(bar, icon="📂", text=_t("scan_folders"),
                cmd=self._start_scan_folders, w=130, h=26,
                bg_override=A["glass_dark"]).pack(side="left", padx=3, pady=5)
        self.stop_scan_btn = AeroBtn(bar, icon="⏹", text=_t("stop"),
                                     cmd=self._stop_scan, w=70, h=26,
                                     danger=True, bg_override=A["glass_dark"])
        tk.Frame(bar, bg=A["border"], width=1).pack(side="left", fill="y", padx=8, pady=6)
        AeroBtn(bar, icon="🗑", text=_t("clear"), cmd=self._clear_library,
                w=78, h=26, danger=True, bg_override=A["glass_dark"]
                ).pack(side="left", padx=3, pady=5)

        # Right side
        tk.Frame(bar, bg=A["border"], width=1).pack(side="right", fill="y", padx=4, pady=6)
        AeroBtn(bar, icon="⚙", text=_t("settings"), cmd=self._open_settings,
                w=90, h=26, bg_override=A["glass_dark"]
                ).pack(side="right", padx=(0,4), pady=5)
        AeroBtn(bar, icon="⬛", text=_t("mini"), cmd=self._open_mini,
                w=70, h=26, bg_override=A["glass_dark"]
                ).pack(side="right", padx=3, pady=5)
        AeroBtn(bar, icon="▶", text=_t("queue"), cmd=self._open_queue,
                w=80, h=26, bg_override=A["glass_dark"]
                ).pack(side="right", padx=3, pady=5)

        tk.Label(bar, text=_t("search"), bg=A["glass_dark"],
                 fg=A["text_dim"], font=FONT_SMALL).pack(side="right", padx=(0,6))
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", lambda *_: self._filter())
        ef = tk.Frame(bar, bg=A["border_glow"], padx=1, pady=1)
        ef.pack(side="right", padx=(0,8), pady=6)
        tk.Entry(ef, textvariable=self.search_var, bg=A["glass_mid"], fg=A["text"],
                 insertbackground=A["accent_hot"], relief="flat",
                 font=FONT_UI, width=22).pack(ipady=3)
        tk.Frame(bar, bg=A["border"], height=1).pack(side="bottom", fill="x")

    def _build_sidebar(self, parent):
        sb = tk.Frame(parent, bg=A["sidebar"], width=210,
                      highlightthickness=1, highlightbackground=A["border"])
        sb.pack(side="left", fill="y"); sb.pack_propagate(False)

        def sec(text):
            f = tk.Frame(sb, bg=A["sidebar_sect"]); f.pack(fill="x")
            tk.Label(f, text=text, bg=A["sidebar_sect"], fg=A["text_dim"],
                     font=FONT_LABEL, anchor="w").pack(fill="x", padx=8, pady=(5,3))
            tk.Frame(sb, bg=A["border"], height=1).pack(fill="x")

        sec(_t("scan_source"))
        src_frame = tk.Frame(sb, bg=A["sidebar"])
        src_frame.pack(fill="x", padx=8, pady=6)
        self.src_var = tk.StringVar(value="drives")
        for val, lbl in [("drives", _t("all_drives")), ("folders", _t("sel_folders"))]:
            tk.Radiobutton(src_frame, text=lbl, variable=self.src_var,
                           value=val, command=self._toggle_src,
                           bg=A["sidebar"], fg=A["text"],
                           activebackground=A["sidebar"], activeforeground=A["accent"],
                           selectcolor=A["glass_dark"], font=FONT_SMALL, anchor="w"
                           ).pack(anchor="w")
        self.folder_list = FolderList(sb, on_change=None)
        self.folder_list.pack(fill="x", padx=8, pady=(0,6))
        self.folder_list.set_placeholder()
        tk.Frame(sb, bg=A["border"], height=1).pack(fill="x")

        sec(_t("formats"))
        fmt_frame = tk.Frame(sb, bg=A["sidebar"])
        fmt_frame.pack(fill="x", padx=8, pady=6)
        self.fmt_vars = {}
        for ext, _ in [("MP3",""), ("FLAC",""), ("WAV",""),
                       ("M4A",""), ("MIDI",""), ("WMA","")]:
            v = tk.BooleanVar(value=True)
            self.fmt_vars[ext] = v
            row = tk.Frame(fmt_frame, bg=A["sidebar"]); row.pack(fill="x", pady=1)
            tk.Checkbutton(row, text=ext, variable=v, command=self._filter,
                           bg=A["sidebar"], fg=A["text"],
                           activebackground=A["sidebar"], activeforeground=A["accent"],
                           selectcolor=A["glass_dark"], font=FONT_SMALL, anchor="w"
                           ).pack(side="left")
        tk.Frame(sb, bg=A["border"], height=1).pack(fill="x")

        # ── RECENTLY PLAYED ────────────────────────────────────────────────
        sec(_t("recently_played"))
        self.recent_frame = tk.Frame(sb, bg=A["sidebar"])
        self.recent_frame.pack(fill="x", padx=4, pady=4)
        self._refresh_recent()
        tk.Frame(sb, bg=A["border"], height=1).pack(fill="x")

        sec(_t("library_info"))
        self.stats_lbl = tk.Label(sb, text=_t("no_files"),
                                   bg=A["sidebar"], fg=A["text_dim"],
                                   font=FONT_SMALL, justify="left",
                                   anchor="nw", wraplength=190)
        self.stats_lbl.pack(anchor="w", padx=8, pady=6)

    def _refresh_recent(self):
        for w in self.recent_frame.winfo_children(): w.destroy()
        if not self.recent:
            tk.Label(self.recent_frame, text=_t("nothing_yet"),
                     bg=A["sidebar"], fg=A["text_dim"],
                     font=FONT_SMALL).pack(anchor="w", padx=4)
            return
        for info in reversed(self.recent[-8:]):
            row = tk.Frame(self.recent_frame, bg=A["sidebar"], cursor="hand2")
            row.pack(fill="x", pady=1)
            title = info["title"][:22] + ("…" if len(info["title"])>22 else "")
            lbl = tk.Label(row, text=f"♪ {title}", bg=A["sidebar"],
                           fg=A["text"], font=FONT_SMALL, anchor="w", cursor="hand2")
            lbl.pack(side="left", padx=4)
            lbl.bind("<Button-1>", lambda e, i=info: self._play_recent(i))
            row.bind("<Button-1>", lambda e, i=info: self._play_recent(i))

    def _play_recent(self, info):
        # Check it still exists on disk
        if not os.path.exists(info["path"]):
            messagebox.showwarning(_t("missing_file"),
                                   _t("missing_msg", info["path"]), parent=self.root)
            return
        # Prefer the full track dict from the library (has album/ext/dur/size);
        # the recent-played entry only stores path/title/artist.
        match = next((t for t in self.library if t["path"] == info["path"]), None)
        if match:
            try:
                self.cur_idx = self.filtered.index(match)
            except ValueError:
                self.filtered = list(self.library)
                self.cur_idx  = self.filtered.index(match)
            self._play(match)
        else:
            # Not in current library (e.g. library not scanned this session) —
            # build a complete dict with sane defaults so _play() never KeyErrors.
            full = {
                "path":   info["path"],
                "title":  info.get("title", Path(info["path"]).stem),
                "artist": info.get("artist", "—"),
                "album":  info.get("album", "—"),
                "dur":    info.get("dur", "—"),
                "dur_sec":info.get("dur_sec", 0),
                "ext":    Path(info["path"]).suffix.lstrip(".").upper(),
                "size":   0,
            }
            self._play(full)

    def _build_library(self, parent):
        lf = GlassPanel(parent)
        lf.pack(fill="both", expand=True, pady=(0,3))

        # ── Tab bar ──────────────────────────────────────────────────────
        tab_bar = tk.Frame(lf, bg=A["glass_dark"])
        tab_bar.pack(fill="x")
        tk.Frame(lf, bg=A["border"], height=1).pack(fill="x")

        self._lib_tab_frames = {}
        self._lib_tab_btns   = {}

        def _show_lib_tab(name):
            for n, f in self._lib_tab_frames.items():
                f.pack_forget()
            for n, b in self._lib_tab_btns.items():
                b.config(bg=A["glass_dark"], fg=A["text_dim"],
                         font=FONT_SMALL, relief="flat", bd=0)
            self._lib_tab_frames[name].pack(fill="both", expand=True)
            self._lib_tab_btns[name].config(bg=A["glass_mid"],
                                             fg=A["accent_bright"],
                                             font=FONT_BOLD)
        self._show_lib_tab = _show_lib_tab

        # Use fixed internal keys, translated display labels
        for key, icon in [("Library", "♩"), ("Albums", "■")]:
            label = _t("library_tab") if key == "Library" else _t("albums_tab")
            btn = tk.Label(tab_bar, text=f"{icon} {label}",
                           bg=A["glass_dark"], fg=A["text_dim"],
                           font=FONT_SMALL, padx=14, pady=6,
                           cursor="hand2", relief="flat", bd=0)
            btn.pack(side="left")
            btn.bind("<Button-1>", lambda e, n=key: _show_lib_tab(n))
            self._lib_tab_btns[key] = btn
            frame = tk.Frame(lf, bg=A["glass"])
            self._lib_tab_frames[key] = frame

        # ── Library tab ───────────────────────────────────────────────────
        lib_frame = self._lib_tab_frames["Library"]
        hdr = tk.Frame(lib_frame, bg=A["glass"]); hdr.pack(fill="x", padx=6, pady=(5,3))
        tk.Label(hdr, text=_t("library"), bg=A["glass"],
                 fg=A["accent_bright"], font=FONT_BOLD).pack(side="left")
        self.lib_count = tk.Label(hdr, text="", bg=A["glass"],
                                   fg=A["text_dim"], font=FONT_SMALL)
        self.lib_count.pack(side="left", padx=8)
        AeroBtn(hdr, icon=_t("queue_btn"), cmd=self._queue_selected, w=90, h=22,
                bg_override=A["glass"]).pack(side="right", padx=4)

        tv_frame = tk.Frame(lib_frame, bg=A["glass"])
        tv_frame.pack(fill="both", expand=True, padx=4, pady=(0,4))
        cols = ("title","artist","album","dur","ext","size","path")
        self.tree = ttk.Treeview(tv_frame, columns=cols, show="headings", selectmode="browse")
        hdrs = [("title", _t("col_title"), 210),("artist", _t("col_artist"), 140),("album", _t("col_album"), 120),
                ("dur", _t("col_dur"), 58),("ext", _t("col_fmt"), 52),("size", _t("col_size"), 65),("path", _t("col_path"), 260)]
        for col, lbl, w in hdrs:
            self.tree.heading(col, text=lbl, command=lambda c=col: self._sort(c))
            self.tree.column(col, width=w, minwidth=36, stretch=(col=="title"))
        vsb = ttk.Scrollbar(tv_frame, orient="vertical",   command=self.tree.yview)
        hsb = ttk.Scrollbar(tv_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        hsb.pack(side="bottom", fill="x")
        vsb.pack(side="right",  fill="y")
        self.tree.pack(fill="both", expand=True)
        self.tree.bind("<Double-1>", self._dbl_click)
        self.tree.bind("<Return>",   self._dbl_click)
        self.ctx = tk.Menu(self.root, tearoff=0, bg=A["glass"], fg=A["text"],
                           activebackground=A["sel"], activeforeground=A["accent_bright"])
        self.ctx.add_command(label=_t("ctx_play"),   command=self._dbl_click)
        self.ctx.add_command(label=_t("ctx_queue"),  command=self._queue_selected)
        self.ctx.add_command(label=_t("ctx_next"),   command=self._queue_next)
        self.ctx.add_separator()
        self.ctx.add_command(label=_t("ctx_copy"),   command=self._copy_path)
        self.ctx.add_command(label="📦 Export as .ptm…", command=self._export_ptm_selected)
        self.tree.bind("<Button-3>", self._show_ctx)

        # ── Albums tab ────────────────────────────────────────────────────
        self.albums_view = AlbumsView(self._lib_tab_frames["Albums"], app=self)
        self.albums_view.pack(fill="both", expand=True)

        _show_lib_tab("Library")

    def _build_player(self, parent):
        pf = GlassPanel(parent, height=160)
        pf.pack(fill="x"); pf.pack_propagate(False)

        # Cover art + now playing row
        np = tk.Frame(pf, bg=A["glass"])
        np.pack(fill="x", padx=12, pady=(8,0))

        # Cover art
        self.cover_lbl = tk.Label(np, bg=A["glass_mid"], width=60, height=60,
                                   relief="flat", bd=0, text="♪",
                                   font=("Segoe UI", 20), fg=A["text_dim"])
        self.cover_lbl.pack(side="left", padx=(0,10))
        self._cover_photo = None

        self.dot = tk.Label(np, text="◉", bg=A["glass"],
                            fg=A["text_dim"], font=("Segoe UI", 12))
        self.dot.pack(side="left", padx=(0,6))
        info_col = tk.Frame(np, bg=A["glass"]); info_col.pack(side="left", fill="x", expand=True)
        self.now_title = tk.Label(info_col, text=_t("no_track"),
                                   bg=A["glass"], fg=A["accent_bright"],
                                   font=FONT_NOW, anchor="w")
        self.now_title.pack(anchor="w")
        self.now_sub = tk.Label(info_col, text="", bg=A["glass"],
                                 fg=A["text_dim"], font=FONT_NOW_SM, anchor="w")
        self.now_sub.pack(anchor="w")

        pg = tk.Frame(pf, bg=A["glass"]); pg.pack(fill="x", padx=12, pady=(4,2))
        self.time_lbl = tk.Label(pg, text="0:00", width=5,
                                  bg=A["glass"], fg=A["text_dim"], font=FONT_MONO)
        self.time_lbl.pack(side="left")
        self.prog = tk.Canvas(pg, height=14, bg=A["prog_bg"],
                              highlightthickness=1, highlightbackground=A["border"])
        self.prog.pack(side="left", fill="x", expand=True, padx=6)
        self.prog.bind("<Button-1>", self._seek)
        self.dur_lbl = tk.Label(pg, text="0:00", width=5,
                                 bg=A["glass"], fg=A["text_dim"], font=FONT_MONO)
        self.dur_lbl.pack(side="left")

        ctrl = tk.Frame(pf, bg=A["glass"]); ctrl.pack(pady=5)
        self.btn_prev = AeroBtn(ctrl, icon="⏮", cmd=self._prev, w=44, h=32, bg_override=A["glass"])
        self.btn_play = AeroBtn(ctrl, icon="▶", cmd=self._playpause, w=56, h=36, bg_override=A["glass"])
        self.btn_stop = AeroBtn(ctrl, icon="⏹", cmd=self._stop, w=44, h=32, danger=True, bg_override=A["glass"])
        self.btn_next = AeroBtn(ctrl, icon="⏭", cmd=self._next, w=44, h=32, bg_override=A["glass"])
        self.btn_shuf = AeroBtn(ctrl, icon="🔀", cmd=self._shuffle, w=44, h=28, bg_override=A["glass"])
        self.btn_rep  = AeroBtn(ctrl, icon="🔁", cmd=self._toggle_repeat, w=44, h=28, bg_override=A["glass"])
        for b in (self.btn_prev, self.btn_play, self.btn_stop,
                  self.btn_next, self.btn_shuf, self.btn_rep):
            b.pack(side="left", padx=2)
        vf = tk.Frame(ctrl, bg=A["glass"]); vf.pack(side="left", padx=(14,0))
        tk.Label(vf, text="🔊", bg=A["glass"], fg=A["text_dim"],
                 font=("Segoe UI",9)).pack(side="left")
        self.vol_scale = tk.Scale(vf, from_=0, to=100, orient="horizontal",
                                   length=100, showvalue=False, bg=A["glass"], fg=A["text"],
                                   troughcolor=A["prog_bg"], activebackground=A["accent_hot"],
                                   highlightthickness=0, bd=0, command=self._set_vol)
        self.vol_scale.set(int(self._vol*100)); self.vol_scale.pack(side="left")

    def _build_statusbar(self):
        sb = tk.Frame(self.root, bg=A["glass_dark"], height=22)
        sb.pack(fill="x", side="bottom"); sb.pack_propagate(False)
        tk.Frame(sb, bg=A["tb_border"], height=1).pack(fill="x", side="top")
        self.status_var = tk.StringVar(value=_t("ready"))
        tk.Label(sb, textvariable=self.status_var, bg=A["glass_dark"],
                 fg=A["text_dim"], font=FONT_SMALL, anchor="w").pack(side="left", padx=8)
        self.ind_lbl = tk.Label(sb, text=_t("stopped"), bg=A["glass_dark"],
                                 fg=A["text_dim"], font=FONT_LABEL)
        self.ind_lbl.pack(side="right", padx=8)

    def _style(self):
        s = ttk.Style()
        try: s.theme_use("clam")
        except: pass
        s.configure("Treeview", background=A["glass"], foreground=A["text"],
                     fieldbackground=A["glass"], rowheight=24, font=FONT_SMALL, borderwidth=0)
        s.configure("Treeview.Heading", background=A["glass_mid"],
                     foreground=A["accent_bright"], font=FONT_LABEL, relief="flat")
        s.map("Treeview", background=[("selected", A["sel"])],
              foreground=[("selected", A["accent_bright"])])
        s.configure("Vertical.TScrollbar", background=A["glass_mid"],
                     troughcolor=A["prog_bg"], bordercolor=A["border"],
                     arrowcolor=A["text_dim"], borderwidth=0)
        s.configure("Horizontal.TScrollbar", background=A["glass_mid"],
                     troughcolor=A["prog_bg"], bordercolor=A["border"],
                     arrowcolor=A["text_dim"], borderwidth=0)

    # ── QUEUE ─────────────────────────────────────────────────────────────
    def _open_queue(self):
        if self.queue_win and self.queue_win.win.winfo_exists():
            self.queue_win.win.lift(); return
        self.queue_win = QueueWindow(self)

    def _queue_selected(self):
        sel = self.tree.selection()
        if not sel: return
        path = sel[0]
        info = next((t for t in self.library if t["path"] == path), None)
        if info:
            self.queue.append(info)
            self.status_var.set(_t("added_queue", info["title"]))
            if self.queue_win and self.queue_win.win.winfo_exists():
                self.queue_win._refresh()

    def _queue_next(self):
        sel = self.tree.selection()
        if not sel: return
        path = sel[0]
        info = next((t for t in self.library if t["path"] == path), None)
        if info:
            self.queue.appendleft(info)
            self.status_var.set(_t("playing_next", info["title"]))
            if self.queue_win and self.queue_win.win.winfo_exists():
                self.queue_win._refresh()

    def _play_from_queue(self):
        if self.queue:
            info = self.queue.popleft()
            self._play(info)
            if self.queue_win and self.queue_win.win.winfo_exists():
                self.queue_win._refresh()

    # ── MINI PLAYER ────────────────────────────────────────────────────────
    def _open_mini(self):
        if self.mini_player and self.mini_player.win.winfo_exists():
            self.mini_player.win.lift(); return
        self.mini_player = MiniPlayer(self)

    # ── CONTEXT MENU ──────────────────────────────────────────────────────
    def _show_ctx(self, e):
        try:
            self.tree.selection_set(self.tree.identify_row(e.y))
            self.ctx.tk_popup(e.x_root, e.y_root)
        finally:
            self.ctx.grab_release()

    def _copy_path(self):
        sel = self.tree.selection()
        if not sel: return
        self.root.clipboard_clear()
        self.root.clipboard_append(sel[0])
        self.status_var.set(_t("copied", sel[0]))

    def _export_ptm_selected(self):
        sel = self.tree.selection()
        if not sel: return
        path = sel[0]
        info = next((t for t in self.library if t["path"] == path), None)
        if not info:
            return
        default_name = "".join(c for c in info["title"]
                               if c.isalnum() or c in " -_()[]").strip() or "track"
        dest = filedialog.asksaveasfilename(
            title="Export as .ptm",
            defaultextension=PTM_EXT,
            initialfile=default_name + PTM_EXT,
            filetypes=[("PTMusic Track", f"*{PTM_EXT}"), ("All Files", "*.*")],
            parent=self.root,
        )
        if not dest:
            return
        self.status_var.set(f"Exporting {info['title']}…")
        self.root.update_idletasks()

        def _do_export():
            ok, msg = export_ptm(info, dest)
            self.root.after(0, lambda: self._export_done(ok, msg, info["title"]))

        threading.Thread(target=_do_export, daemon=True).start()

    def _export_done(self, ok, msg, title):
        if ok:
            self.status_var.set(f"Exported: {title}")
        else:
            self.status_var.set("Export failed")
            messagebox.showerror("Export Failed", msg, parent=self.root)

    def _import_ptm_file(self, ptm_path: str):
        """Import a .ptm file — extracts audio, adds to library, and plays it."""
        if not os.path.exists(ptm_path):
            messagebox.showerror("Import Failed", f"File not found:\n{ptm_path}",
                                 parent=self.root)
            return

        # Extract into a dedicated PTMusic imports folder
        imports_dir = os.path.join(os.path.expanduser("~"), "PTMusic Imports")
        self.status_var.set(f"Importing {os.path.basename(ptm_path)}…")
        self.root.update_idletasks()

        def _do_import():
            ok, msg, info = import_ptm(ptm_path, imports_dir)
            self.root.after(0, lambda: self._import_done(ok, msg, info))

        threading.Thread(target=_do_import, daemon=True).start()

    def _import_done(self, ok, msg, info):
        if not ok:
            self.status_var.set("Import failed")
            messagebox.showerror("Import Failed", msg, parent=self.root)
            return
        # Add to library if not already present
        if not any(t["path"] == info["path"] for t in self.library):
            self.library.append(info)
            self._add_row(info)
            self._upd_stats()
            try: self.albums_view.refresh(self.library)
            except Exception: pass
        self.status_var.set(msg)
        # Play it immediately
        self.filtered = [t for t in self.library if self.tree.exists(t["path"])]
        try:
            self.cur_idx = next(i for i, t in enumerate(self.filtered)
                                if t["path"] == info["path"])
        except StopIteration:
            self.cur_idx = -1
        self._play(info)

    # ── SCAN SOURCE ────────────────────────────────────────────────────────
    def _toggle_src(self):
        self._use_folders = (self.src_var.get() == "folders")
        if not self._use_folders: self.folder_list.set_placeholder()
        else: self.folder_list.lb.delete(0, "end")

    def _save_geometry(self):
        try:
            geo = self.root.geometry()
            if '+' in geo:
                plus = geo.index('+')
                self.cfg["win_geometry"] = geo[:plus]
                self.cfg["win_position"] = geo[plus:]
            else:
                self.cfg["win_geometry"] = geo
                self.cfg["win_position"] = ""
            save_config(self.cfg)
        except Exception:
            pass

    def _on_close(self):
        """Minimize to tray if enabled and available, otherwise exit fully."""
        self._save_geometry()
        if self.cfg.get("minimize_to_tray", True) and PYSTRAY_AVAILABLE:
            self._minimize_to_tray()
        else:
            self._quit_app()

    def _minimize_to_tray(self):
        self.root.withdraw()  # hide window, keep process alive
        if self._tray_icon is None:
            self._start_tray_icon()
        else:
            self._update_tray_menu()

    def _restore_from_tray(self):
        self.root.deiconify()
        self.root.lift()
        self.root.focus_force()

    def _quit_app(self):
        """Fully exit — stop tray icon, stop playback, destroy window."""
        try:
            if PYGAME_AVAILABLE:
                pygame.mixer.music.stop()
        except Exception:
            pass
        if self._tray_icon is not None:
            try:
                self._tray_icon.stop()
            except Exception:
                pass
        try:
            self.root.destroy()
        except Exception:
            pass
        os._exit(0)   # hard-stop any lingering non-daemon threads

    # ── SYSTEM TRAY ──────────────────────────────────────────────────────
    def _tray_image(self):
        """Load PTMusic.png for the tray icon."""
        try:
            base = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
            path = os.path.join(base, "PTMusic.png")
            return Image.open(path)
        except Exception:
            # Fallback: simple generated icon
            img = Image.new("RGBA", (64, 64), (30, 90, 160, 255))
            return img

    def _tray_track_label(self):
        if self._current_track:
            t = self._current_track
            title  = t.get("title", "—")
            artist = t.get("artist", "—")
            state  = "Paused" if self.paused else ("Playing" if self.playing else "Stopped")
            return f"{state}: {title} — {artist}"
        return "PTMusic — Nothing playing"

    def _build_tray_menu(self):
        import pystray
        return pystray.Menu(
            pystray.MenuItem(self._tray_track_label(), None, enabled=False),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Play / Pause", lambda: self.root.after(0, self._playpause)),
            pystray.MenuItem("Next Track",   lambda: self.root.after(0, self._next)),
            pystray.MenuItem("Previous Track", lambda: self.root.after(0, self._prev)),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Show PTMusic", lambda: self.root.after(0, self._restore_from_tray), default=True),
            pystray.MenuItem("Exit", lambda: self.root.after(0, self._quit_app)),
        )

    def _start_tray_icon(self):
        import pystray
        self._tray_icon = pystray.Icon(
            "PTMusic",
            icon=self._tray_image(),
            title=self._tray_track_label(),
            menu=self._build_tray_menu(),
        )
        self._tray_thread = threading.Thread(target=self._tray_icon.run, daemon=True)
        self._tray_thread.start()

    def _update_tray_menu(self):
        """Refresh tray tooltip and menu text (call after track changes)."""
        if self._tray_icon is None:
            return
        try:
            self._tray_icon.title = self._tray_track_label()
            self._tray_icon.menu  = self._build_tray_menu()
        except Exception:
            pass

    def _startup_dialog(self):
        if messagebox.askyesno(_t("welcome_title"),
                                _t("welcome_msg"), parent=self.root):
            self._start_scan_all()

    def _scan_first_run_folder(self, folder: str):
        """Auto-scan a folder bundled by the installer (e.g. example music)
        on first launch, without prompting the user."""
        self.src_var.set("folders"); self._use_folders = True
        self.folder_list.folders = [folder]
        self.folder_list.lb.delete(0, "end")
        self.folder_list.lb.insert("end", folder)
        self.status_var.set(f"Scanning bundled example music…")
        self._run_scan([folder])

    def _start_scan_all(self):
        self.src_var.set("drives"); self._use_folders = False
        self.folder_list.set_placeholder(); self._run_scan(get_all_drives())

    def _start_scan_folders(self):
        self.src_var.set("folders"); self._use_folders = True
        folders = self.folder_list.get_folders()
        if not folders:
            path = filedialog.askdirectory(title="Select Folder to Scan")
            if not path: return
            self.folder_list.folders.append(path)
            self.folder_list.lb.delete(0,"end")
            self.folder_list.lb.insert("end", path)
            folders = [path]
        self._run_scan(folders)

    def _run_scan(self, paths):
        if self.scan_th and self.scan_th.is_alive():
            self.scan_stop.set(); self.scan_th.join(timeout=2)
        self.scan_stop.clear()
        self._clear_library(confirm=False)
        self.status_var.set(_t("scanning", len(paths)))
        self.stop_scan_btn.pack(side="left", padx=3, pady=5)
        def run():
            scan_paths(paths, callback=self._on_found, stop_event=self.scan_stop)
            self.root.after(0, self._scan_done)
        self.scan_th = threading.Thread(target=run, daemon=True)
        self.scan_th.start()

    def _stop_scan(self): self.scan_stop.set()

    def _on_found(self, info):
        self.library.append(info)
        self.root.after(0, lambda i=info: self._add_row(i))
        n = len(self.library)
        if n % 20 == 0:
            self.root.after(0, lambda x=n: self.status_var.set(_t("found_tracks", x)))

    def _add_row(self, info):
        if self.tree.exists(info["path"]): return
        self.tree.insert("", "end", iid=info["path"],
                          values=(info["title"], info["artist"], info["album"],
                                  info["dur"], info["ext"],
                                  fmt_size(info["size"]), info["path"]))
        self._upd_stats()

    def _scan_done(self):
        n = len(self.library)
        self.status_var.set(_t("scan_complete", n, "s" if n!=1 else ""))
        self.stop_scan_btn.pack_forget(); self._upd_stats(); self._filter()
        try: self.albums_view.refresh(self.library)
        except Exception: pass

    def _clear_library(self, confirm=True):
        if confirm and self.cfg.get("confirm_clear", True) and not messagebox.askyesno(
                _t("clear_title"), _t("clear_msg"), parent=self.root):
            return
        self._stop(); self.library.clear(); self.filtered.clear()
        self.tree.delete(*self.tree.get_children())
        self._upd_stats(); self.status_var.set(_t("cleared"))

    def _filter(self, *_):
        q = self.search_var.get().lower()
        enabled = {k for k, v in self.fmt_vars.items() if v.get()}
        if "MIDI" in enabled: enabled.add("MID")
        self.filtered = [
            t for t in self.library
            if t["ext"] in enabled and (
                not q or q in t["title"].lower() or q in t["artist"].lower()
                       or q in t["album"].lower() or q in t["path"].lower())
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
        fmts = {}
        for t in self.library: fmts[t["ext"]] = fmts.get(t["ext"],0)+1
        lines = [_t("tracks_label", n, "s" if n!=1 else "")]
        for k, v in sorted(fmts.items()): lines.append(f"  {k}: {v}")
        self.stats_lbl.config(text="\n".join(lines) if n else "No files loaded")
        self.lib_count.config(text=f"({len(self.filtered or self.library)} tracks)")

    def _dbl_click(self, e=None):
        sel = self.tree.selection()
        if not sel: return
        path = sel[0]
        self.filtered = [t for t in self.library if self.tree.exists(t["path"])]
        try:
            self.cur_idx = next(i for i,t in enumerate(self.filtered) if t["path"]==path)
        except StopIteration: return
        self._play(self.filtered[self.cur_idx])

    def _play(self, info):
        if not PYGAME_AVAILABLE:
            messagebox.showerror("pygame missing", "pip install pygame", parent=self.root)
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
                if a and hasattr(a.info,'length'): self._tlen = a.info.length
            except: pass

        # Cover art
        self._load_cover(info["path"])

        # Recently played — store full info so it plays correctly even
        # before the library has been re-scanned in a future session
        self.recent = [r for r in self.recent if r["path"] != info["path"]]
        self.recent.append({
            "path":   info["path"],
            "title":  info["title"],
            "artist": info["artist"],
            "album":  info.get("album", "—"),
            "dur":    info.get("dur", "—"),
            "ext":    info.get("ext", ""),
        })
        save_recent(self.recent)
        try: self._refresh_recent()
        except: pass

        self.now_title.config(text=info["title"])
        self.now_sub.config(text=f"{info['artist']}  ·  {info['album']}  ·  {info['ext']}")
        self.dur_lbl.config(text=info["dur"] if info["dur"]!="—" else "—")
        self.btn_play.icon = "⏸"; self.btn_play._draw()
        self.dot.config(fg=A["green"])
        self.ind_lbl.config(text=_t("playing"), fg=A["green"])
        self.status_var.set(_t("playing_status", info["title"]))
        if self.tree.exists(info["path"]):
            self.tree.selection_set(info["path"]); self.tree.see(info["path"])
        if self.cfg.get("notifications", True):
            threading.Thread(
                target=_notify,
                args=(info["title"], f"{info['artist']}  ·  {info['album']}"),
                daemon=True).start()
        self._current_track = info
        self._update_tray_menu()
        self._tick()

    def _load_cover(self, path):
        """Load and display cover art for currently playing track."""
        try:
            if path in self._cover_cache:
                img = self._cover_cache[path]
            else:
                img = _get_cover_art(path, size=60)
                self._cover_cache[path] = img
            if img:
                self._cover_photo = img
                self.cover_lbl.config(image=img, text="", width=60, height=60)
            else:
                self._cover_photo = None
                self.cover_lbl.config(image="", text="♪", font=("Segoe UI",20),
                                       fg=A["text_dim"], width=4, height=2)
        except Exception:
            pass

    def _tick(self):
        if self.prog_after: self.root.after_cancel(self.prog_after)
        if not (PYGAME_AVAILABLE and self.playing and not self.paused): return
        raw = pygame.mixer.music.get_pos() / 1000.0
        if raw < 0: self._track_ended(); return
        pos = self._seek_offset + raw
        m, s = int(pos//60), int(pos%60)
        self.time_lbl.config(text=f"{m}:{s:02d}")
        W = self.prog.winfo_width(); H = self.prog.winfo_height()
        self.prog.delete("all")
        if self._tlen > 0 and W > 0:
            frac = min(pos/self._tlen, 1.0); fw = int(frac*W)
            self.prog.create_rectangle(0,0,W,H, fill=A["prog_bg"], outline="")
            if fw > 0:
                mid = H//2
                self.prog.create_rectangle(0,0,fw,mid,   fill=A["prog_bright"], outline="")
                self.prog.create_rectangle(0,mid,fw,H,   fill=A["prog_fill"],   outline="")
                self.prog.create_rectangle(0,0,fw,mid, fill="#ffffff", outline="", stipple="gray12")
            kx = fw
            self.prog.create_oval(kx-6,1,kx+6,H-1, fill=A["accent_bright"], outline=A["accent_hot"])
            self.prog.create_oval(kx-3,H//2-3,kx+3,H//2+3, fill=A["glass"], outline="")
        self.prog_after = self.root.after(400, self._tick)

    def _track_ended(self):
        if self._repeat and self.cur_idx >= 0:
            self._play(self.filtered[self.cur_idx])
        elif self.queue:
            self._play_from_queue()
        else:
            self._next()

    def _seek(self, e):
        if not (PYGAME_AVAILABLE and self.playing): return
        W = self.prog.winfo_width()
        if W <= 0 or self._tlen <= 0: return
        target = max(0.0, min(e.x/W*self._tlen, self._tlen))
        try:
            pygame.mixer.music.play(start=target); self._seek_offset = target
        except:
            try: pygame.mixer.music.set_pos(target); self._seek_offset = target
            except: pass

    def _seek_by(self, seconds: float):
        """Seek forward/backward by N seconds."""
        if not (PYGAME_AVAILABLE and self.playing): return
        raw = pygame.mixer.music.get_pos() / 1000.0
        if raw < 0: return
        target = max(0.0, min(self._seek_offset + raw + seconds, self._tlen or 9999))
        try:
            pygame.mixer.music.play(start=target)
            self._seek_offset = target
        except:
            try:
                pygame.mixer.music.set_pos(target)
                self._seek_offset = target
            except: pass

    def _change_vol(self, delta: int):
        """Change volume by delta percent (-100 to +100)."""
        new_vol = max(0, min(100, int(self._vol * 100) + delta))
        self._vol = new_vol / 100.0
        if PYGAME_AVAILABLE: pygame.mixer.music.set_volume(self._vol)
        try: self.vol_scale.set(new_vol)
        except: pass
        self.status_var.set(_t("volume", new_vol))

    def _toggle_mute(self):
        """Toggle mute on/off, remembering previous volume."""
        if not hasattr(self, '_pre_mute_vol'):
            self._pre_mute_vol = None
        if self._pre_mute_vol is None:
            self._pre_mute_vol = self._vol
            self._change_vol(-100)
            self.status_var.set(_t("muted"))
        else:
            self._vol = self._pre_mute_vol
            self._pre_mute_vol = None
            if PYGAME_AVAILABLE: pygame.mixer.music.set_volume(self._vol)
            try: self.vol_scale.set(int(self._vol * 100))
            except: pass
            self.status_var.set(f"Unmuted — Volume: {int(self._vol*100)}%")

    def _playpause(self):
        if not PYGAME_AVAILABLE: return
        if not self.playing:
            sel = self.tree.selection()
            if sel: self._dbl_click()
            return
        if self.paused:
            pygame.mixer.music.unpause(); self.paused = False
            self.btn_play.icon = "⏸"; self.btn_play._draw()
            self.dot.config(fg=A["green"])
            self.ind_lbl.config(text=_t("playing"), fg=A["green"]); self._tick()
        else:
            pygame.mixer.music.pause(); self.paused = True
            self.btn_play.icon = "▶"; self.btn_play._draw()
            self.dot.config(fg=A["accent"])
            self.ind_lbl.config(text=_t("paused"), fg=A["accent"])
            self.status_var.set(_t("paused"))
        self._update_tray_menu()

    def _stop(self):
        if PYGAME_AVAILABLE: pygame.mixer.music.stop()
        self.playing = False; self.paused = False
        self.btn_play.icon = "▶"; self.btn_play._draw()
        self.dot.config(fg=A["text_dim"])
        self.ind_lbl.config(text=_t("stopped"), fg=A["text_dim"])
        self.now_title.config(text=_t("no_track")); self.now_sub.config(text="")
        self.time_lbl.config(text="0:00"); self.prog.delete("all")
        self.cover_lbl.config(image="", text="♪", font=("Segoe UI",20),
                               fg=A["text_dim"], width=4, height=2)
        self.status_var.set(_t("stopped"))
        self._current_track = None
        self._update_tray_menu()

    def _next(self):
        if self.queue:
            self._play_from_queue(); return
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
            self.status_var.set(_t("shuffled"))

    def _toggle_repeat(self):
        self._repeat = not self._repeat
        self.status_var.set(_t("repeat_on") if self._repeat else _t("repeat_off"))

    def _set_vol(self, val):
        self._vol = int(val)/100.0
        if PYGAME_AVAILABLE: pygame.mixer.music.set_volume(self._vol)


# ══════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    import traceback, sys, os

    log_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "phoni_crash.log")

    class Tee:
        def __init__(self, stream, logfile):
            self._s = stream; self._f = logfile
        def write(self, data):
            if self._s is not None:
                try: self._s.write(data)
                except: pass
            try: self._f.write(data); self._f.flush()
            except: pass
        def flush(self):
            if self._s is not None:
                try: self._s.flush()
                except: pass

    with open(log_path, "w", encoding="utf-8") as lf:
        sys.stdout = Tee(sys.__stdout__, lf)
        sys.stderr = Tee(sys.__stderr__, lf)
        print("PTMusic starting"); print("Python", sys.version)
        print("pygame  :", PYGAME_AVAILABLE)
        print("mutagen :", MUTAGEN_AVAILABLE)
        print("pillow  :", PIL_AVAILABLE)
        print("-" * 60)

        # Check if launched with a .ptm file (double-click / file association)
        ptm_arg = None
        for arg in sys.argv[1:]:
            if arg.lower().endswith(PTM_EXT):
                ptm_arg = arg
                print("Opening .ptm file:", ptm_arg)
                break

        try:
            PhoniPlayer(open_ptm_path=ptm_arg)
        except SystemExit:
            pass  # normal exit
        except Exception:
            print("\n=== CRASH ===")
            traceback.print_exc()
            print("=============")
            # Only pause for input if we actually have a console
            if sys.__stdout__ is not None:
                input("\nPress Enter to exit...")
        finally:
            sys.stdout = sys.__stdout__
            sys.stderr = sys.__stderr__
            print("Log saved to:", log_path)
