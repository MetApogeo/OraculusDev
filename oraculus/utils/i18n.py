import json
import os
import locale

_translations = {}
_current_lang = "en"

def detect_system_language() -> str:
    try:
        sys_lang, _ = locale.getdefaultlocale()
        if sys_lang:
            lang = sys_lang.split("_")[0].lower()
            if lang in ("es", "en", "fr"):
                return lang
    except Exception:
        pass
    return "en"

def obtener_idioma_configurado() -> str:
    config_dir = os.path.expanduser("~/.oraculus")
    config_path = os.path.join(config_dir, "config.json")
    if os.path.exists(config_path):
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                cfg = json.load(f)
                lang = cfg.get("lang")
                if lang in ("es", "en", "fr"):
                    return lang
        except Exception:
            pass
    return None

def cambiar_idioma_configurado(lang: str) -> None:
    global _translations, _current_lang
    if lang not in ("es", "en", "fr"):
        raise ValueError(f"Invalid language: {lang}")
    
    config_dir = os.path.expanduser("~/.oraculus")
    os.makedirs(config_dir, exist_ok=True)
    config_path = os.path.join(config_dir, "config.json")
    
    try:
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump({"lang": lang}, f, indent=2, ensure_ascii=False)
    except Exception:
        pass
        
    _current_lang = lang
    # Recargar traducciones en memoria
    _translations = {}
    inicializar_i18n()

def inicializar_i18n() -> None:
    global _translations, _current_lang
    lang = obtener_idioma_configurado()
    if not lang:
        lang = detect_system_language()
        
    _current_lang = lang
    
    locales_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "locales")
    json_path = os.path.join(locales_dir, f"{lang}.json")
    
    if not os.path.exists(json_path):
        json_path = os.path.join(locales_dir, "en.json")
        _current_lang = "en"
        
    try:
        with open(json_path, "r", encoding="utf-8") as f:
            _translations = json.load(f)
    except Exception:
        _translations = {}

def t(seccion: str, clave: str) -> str:
    global _translations
    if not _translations:
        inicializar_i18n()
    return _translations.get(seccion, {}).get(clave, f"[MISSING: {seccion}.{clave}]")

def t_dict(seccion: str) -> dict:
    global _translations
    if not _translations:
        inicializar_i18n()
    return _translations.get(seccion, {})

def obtener_idioma_actual() -> str:
    global _translations
    if not _translations:
        inicializar_i18n()
    return _current_lang
