"""
Descargador profesional de YouTube - Video o MP3
Multiplataforma: Windows 11 / Fedora 44
Autor: (tu nombre)
Requiere: yt-dlp, FFmpeg
"""

import yt_dlp
import os
import sys
import re
import time
import logging
import platform
import subprocess
import shutil
import json
from pathlib import Path
from datetime import datetime


# ═══════════════════════════════════════════════════════════════
#  CONFIGURACIÓN GENERAL
# ═══════════════════════════════════════════════════════════════

CONFIG = {
    "carpeta_base": "./descargas",
    "subcarpeta_video": "videos",
    "subcarpeta_audio": "audio",
    "carpeta_archivo": "./.historial",
    "archivo_log": "errores.log",
    "bitrate_audio": "192",
    "reintentos": 5,
    "timeout": 30,
    "usar_cookies": True,
    "navegador_cookies": None,
    "js_runtime": None,
    "crear_icono": True,
    # === NUEVAS OPCIONES ===
    "notificar_al_terminar": True,        # 👈 Notificación de escritorio
    "normalizar_audio": True,             # 👈 Normalización de volumen
    "lufs_objetivo": -16,                 # Estándar YouTube/Spotify
    "true_peak": -1.5,                    # Margen de seguridad
    "lra": 11,                            # Rango dinámico
}


# ═══════════════════════════════════════════════════════════════
#  LOGGING
# ═══════════════════════════════════════════════════════════════

logging.basicConfig(
    filename=CONFIG["archivo_log"],
    level=logging.WARNING,
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    encoding="utf-8",
)


# ═══════════════════════════════════════════════════════════════
#  DETECCIÓN DE SO
# ═══════════════════════════════════════════════════════════════

def detectar_so():
    sistema = platform.system()
    if sistema == "Windows":
        return "windows"
    elif sistema == "Linux":
        try:
            with open("/etc/os-release") as f:
                contenido = f.read().lower()
                if "fedora" in contenido:
                    return "fedora"
                elif "ubuntu" in contenido or "debian" in contenido:
                    return "debian"
                else:
                    return "linux"
        except FileNotFoundError:
            return "linux"
    return sistema.lower()


SO = detectar_so()


# ═══════════════════════════════════════════════════════════════
#  DETECCIÓN DE NAVEGADOR
# ═══════════════════════════════════════════════════════════════

def detectar_navegador():
    if CONFIG["navegador_cookies"]:
        return CONFIG["navegador_cookies"]

    candidatos = ["firefox", "chrome", "edge", "brave", "chromium", "opera"]

    if SO == "windows":
        rutas = {
            "firefox": [os.path.expandvars(r"%APPDATA%\Mozilla\Firefox\Profiles")],
            "chrome": [os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\User Data")],
            "edge": [os.path.expandvars(r"%LOCALAPPDATA%\Microsoft\Edge\User Data")],
            "brave": [os.path.expandvars(r"%LOCALAPPDATA%\BraveSoftware\Brave-Browser\User Data")],
        }
        for nav in candidatos:
            if nav in rutas:
                for ruta in rutas[nav]:
                    if os.path.exists(ruta):
                        return nav
    elif SO in ("fedora", "debian", "linux"):
        rutas = {
            "firefox": [os.path.expanduser("~/.mozilla/firefox")],
            "chrome": [os.path.expanduser("~/.config/google-chrome")],
            "chromium": [os.path.expanduser("~/.config/chromium")],
            "brave": [os.path.expanduser("~/.config/BraveSoftware/Brave-Browser")],
        }
        for nav in candidatos:
            if nav in rutas:
                for ruta in rutas[nav]:
                    if os.path.exists(ruta):
                        return nav
    return "firefox"


NAVEGADOR = detectar_navegador()


# ═══════════════════════════════════════════════════════════════
#  DETECCIÓN DE RUNTIME JS
# ═══════════════════════════════════════════════════════════════

def detectar_runtime_js():
    if CONFIG["js_runtime"]:
        return CONFIG["js_runtime"]
    for rt in ["deno", "node", "bun"]:
        if shutil.which(rt):
            return rt
    return None


# ═══════════════════════════════════════════════════════════════
#  === NOTIFICACIÓN DE ESCRITORIO ===
# ═══════════════════════════════════════════════════════════════

def notificar(titulo: str, mensaje: str):
    """
    Envía una notificación de escritorio según el SO.
    - Windows: PowerShell Toast Notification
    - Linux: notify-send
    """
    if not CONFIG["notificar_al_terminar"]:
        return

    try:
        if SO == "windows":
            # Toast notification via PowerShell (sin dependencias externas)
            ps_script = f'''
$ErrorActionPreference = 'Stop'
[Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime] | Out-Null
$xml = New-Object Windows.Data.Xml.Dom.XmlDocument
$xml.LoadXml(@'
<toast>
  <visual>
    <binding template="ToastGeneric">
      <text>{titulo}</text>
      <text>{mensaje}</text>
    </binding>
  </visual>
</toast>
'@)
$toast = New-Object Windows.UI.Notifications.ToastNotification $xml
$appid = '{{1AC14E77-02E7-4E5D-B744-2EB1AE5198B7}}\\WindowsPowerShell\\v1.0\\powershell.exe'
[Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier($appid).Show($toast)
'''
            subprocess.run(
                ["powershell", "-Command", ps_script],
                capture_output=True, text=True, timeout=15
            )
            print(f"   🔔 Notificación enviada")

        elif SO in ("fedora", "debian", "linux"):
            # notify-send para Linux (Fedora 44 incluido)
            subprocess.run(
                ["notify-send", "-a", "Descargador YouTube", "-i", "download", titulo, mensaje],
                capture_output=True, timeout=5
            )
            print(f"   🔔 Notificación enviada")

    except Exception as e:
        logging.warning(f"No se pudo enviar notificación: {e}")


# ═══════════════════════════════════════════════════════════════
#  === NORMALIZACIÓN DE VOLUMEN ===
# ═══════════════════════════════════════════════════════════════

def normalizar_audio(ruta_archivo: str) -> bool:
    """
    Normaliza el volumen usando FFmpeg loudnorm (双通道 / dual-pass).
    
    Método dual-pass:
    1. Primera pasada: mide los valores reales del audio.
    2. Segunda pasada: aplica corrección con valores medidos (lineal).
    
    Estándares:
    - -16 LUFS para YouTube/Spotify
    - -1.5 dB True Peak (margen de seguridad)
    - LRA 11 dB (rango dinámico natural)
    """
    if not CONFIG["normalizar_audio"]:
        return False

    ruta = Path(ruta_archivo)
    if not ruta.exists():
        return False

    # Solo normalizar si es MP3 (u otro formato de audio)
    if ruta.suffix.lower() not in (".mp3", ".m4a", ".opus", ".aac", ".wav", ".flac"):
        return False

    print(f"   🎚️  Normalizando volumen (dual-pass LUFS)...")

    # Valores objetivo
    I = CONFIG["lufs_objetivo"]
    TP = CONFIG["true_peak"]
    LRA = CONFIG["lra"]

    # Archivo temporal para la primera pasada
    archivo_temp = ruta.parent / f"{ruta.stem}_normalizado{ruta.suffix}"

    try:
        # === PRIMERA PASADA: Medir ===
        cmd_medicion = [
            "ffmpeg", "-i", str(ruta),
            "-af", f"loudnorm=I={I}:TP={TP}:LRA={LRA}:print_format=json",
            "-f", "null", "-"
        ]
        resultado = subprocess.run(
            cmd_medicion,
            capture_output=True, text=True, timeout=120
        )

        # Extraer JSON de la salida (FFmpeg lo envía a stderr)
        salida = resultado.stderr
        # Buscar el bloque JSON
        match = re.search(r'\{[^{}]*"input_i"[^{}]*\}', salida, re.DOTALL)
        if not match:
            print(f"   ⚠️  No se pudieron medir los valores de loudness")
            return False

        datos = json.loads(match.group())

        measured_I = datos.get("input_i", "0")
        measured_TP = datos.get("input_tp", "0")
        measured_LRA = datos.get("input_lra", "0")
        measured_thresh = datos.get("input_thresh", "0")
        offset = datos.get("target_offset", "0")

        # === SEGUNDA PASADA: Aplicar corrección ===
        cmd_normalizar = [
            "ffmpeg", "-y",
            "-i", str(ruta),
            "-af", (
                f"loudnorm=I={I}:TP={TP}:LRA={LRA}:"
                f"measured_I={measured_I}:measured_TP={measured_TP}:"
                f"measured_LRA={measured_LRA}:measured_thresh={measured_thresh}:"
                f"offset={offset}:linear=true"
            ),
            "-ar", "48000",
            str(archivo_temp)
        ]

        subprocess.run(
            cmd_normalizar,
            capture_output=True, timeout=180
        )

        if archivo_temp.exists():
            # Reemplazar el archivo original
            archivo_temp.replace(ruta)
            print(f"   ✅ Volumen normalizado ({I} LUFS)")
            return True
        else:
            print(f"   ⚠️  Error en la segunda pasada")
            return False

    except Exception as e:
        print(f"   ⚠️  Error normalizando: {e}")
        logging.warning(f"Error normalizando {ruta.name}: {e}")
        return False
    finally:
        # Limpiar temporal si quedó
        if archivo_temp.exists():
            archivo_temp.unlink(missing_ok=True)


# ═══════════════════════════════════════════════════════════════
#  BARRA DE PROGRESO
# ═══════════════════════════════════════════════════════════════

def _fmt_bytes(b):
    if b is None:
        return "?"
    for unidad in ["B", "KB", "MB", "GB"]:
        if b < 1024:
            return f"{b:.2f}{unidad}"
        b /= 1024
    return f"{b:.2f}TB"


def _fmt_tiempo(seg):
    if seg is None:
        return "--:--"
    seg = int(seg)
    if seg >= 3600:
        return f"{seg//3600}:{(seg%3600)//60:02d}:{seg%60:02d}"
    return f"{seg//60:02d}:{seg%60:02d}"


class ProgresoYDL:
    def __init__(self):
        self.ultimo_print = 0

    def hook(self, d):
        if d["status"] == "downloading":
            ahora = time.time()
            if ahora - self.ultimo_print < 0.2:
                return
            self.ultimo_print = ahora

            descargado = d.get("downloaded_bytes", 0)
            total = d.get("total_bytes") or d.get("total_bytes_estimate")
            velocidad = d.get("speed") or 0
            eta = d.get("eta")

            if total:
                pct = descargado / total * 100
                barra_len = 25
                llenos = int(pct / 100 * barra_len)
                barra = "█" * llenos + "░" * (barra_len - llenos)
                sys.stdout.write(
                    f"\r   [{barra}] {pct:5.1f}%  "
                    f"{_fmt_bytes(descargado)}/{_fmt_bytes(total)}  "
                    f"⚡{_fmt_bytes(velocidad)}/s  "
                    f"⏱ {_fmt_tiempo(eta)}"
                )
                sys.stdout.flush()

        elif d["status"] == "finished":
            sys.stdout.write("\r" + " " * 90 + "\r")
            sys.stdout.flush()
            print(f"   ✔ {Path(d['filename']).name}")


# ═══════════════════════════════════════════════════════════════
#  DESCARGA PRINCIPAL (con normalización y notificación)
# ═══════════════════════════════════════════════════════════════

def descargar_media(url: str, tipo: str, calidad: str = "mejor",
                    carpeta_salida: str = None, solo_video: bool = False):
    base = Path(carpeta_salida or CONFIG["carpeta_base"])
    if tipo == "video":
        carpeta = base / CONFIG["subcarpeta_video"]
    else:
        carpeta = base / CONFIG["subcarpeta_audio"]
    carpeta.mkdir(parents=True, exist_ok=True)

    carpeta_archivo = Path(CONFIG["carpeta_archivo"])
    carpeta_archivo.mkdir(parents=True, exist_ok=True)
    archivo_historial = str(carpeta_archivo / f"descargados_{tipo}.txt")

    outtmpl = str(carpeta / "%(title)s.%(ext)s")

    opts_comunes = {
        "outtmpl": outtmpl,
        "quiet": True,
        "no_warnings": True,
        "ignoreerrors": True,
        "noplaylist": solo_video,
        "retries": CONFIG["reintentos"],
        "fragment_retries": CONFIG["reintentos"],
        "socket_timeout": CONFIG["timeout"],
        "download_archive": archivo_historial,
        "windowsfilenames": True,
        "trim_file_name": 180,
        "progress_hooks": [ProgresoYDL().hook],
        "noprogress": False,
    }

    runtime = detectar_runtime_js()
    if runtime:
        opts_comunes["js_runtimes"] = {runtime: {}}

    if CONFIG["usar_cookies"] and NAVEGADOR:
        opts_comunes["cookiesfrombrowser"] = (NAVEGADOR,)
        print(f"   🍪 Cookies de: {NAVEGADOR}")

    if tipo == "audio":
        formato_audio = calidad if calidad in ["mp3", "m4a", "opus", "aac", "flac", "wav"] else "mp3"
        ydl_opts = {
            **opts_comunes,
            "format": "bestaudio/best",
            "postprocessors": [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": formato_audio,
                    "preferredquality": CONFIG["bitrate_audio"],
                },
                {"key": "FFmpegMetadata", "add_metadata": True},
            ],
        }
        print(f"🎵 Audio ({formato_audio.upper()} @ {CONFIG['bitrate_audio']} kbps) → {carpeta.name}/")

    else:
        calidad_map = {
            "mejor": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
            "1080p": "bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/best[height<=1080][ext=mp4]/best",
            "720p":  "bestvideo[height<=720][ext=mp4]+bestaudio[ext=m4a]/best[height<=720][ext=mp4]/best",
            "480p":  "bestvideo[height<=480][ext=mp4]+bestaudio[ext=m4a]/best[height<=480][ext=mp4]/best",
            "360p":  "bestvideo[height<=360][ext=mp4]+bestaudio[ext=m4a]/best[height<=360][ext=mp4]/best",
            "peor":  "worstvideo[ext=mp4]+worstaudio[ext=m4a]/worst[ext=mp4]/worst",
        }
        ydl_opts = {
            **opts_comunes,
            "format": calidad_map.get(calidad, calidad_map["mejor"]),
            "merge_output_format": "mp4",
        }
        print(f"🎬 Video ({calidad}) → {carpeta.name}/")

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        # === POST-PROCESAMIENTO: Normalizar audios ===
        if tipo == "audio" and CONFIG["normalizar_audio"]:
            # Buscar archivos recién descargados en la carpeta
            for archivo in carpeta.glob(f"*.{formato_audio}"):
                # Normalizar solo si se modificó en los últimos 5 minutos
                if time.time() - archivo.stat().st_mtime < 300:
                    normalizar_audio(str(archivo))

        print("\n✅ Completado.")
        return 0

    except KeyboardInterrupt:
        print("\n\n⏹️  Cancelado.")
        return 1
    except Exception as e:
        print(f"\n❌ Error: {e}")
        logging.error(f"Error descargando {url}: {e}")
        return 1


# ═══════════════════════════════════════════════════════════════
#  CREAR ICONO EN ESCRITORIO
# ═══════════════════════════════════════════════════════════════

def crear_icono_escritorio():
    script_path = Path(sys.argv[0]).resolve()
    python_exe = sys.executable

    if SO == "windows":
        crear_icono_windows(script_path, python_exe)
    elif SO in ("fedora", "debian", "linux"):
        crear_icono_linux(script_path, python_exe)


def crear_icono_windows(script_path: Path, python_exe: str):
    try:
        import win32com.client
    except ImportError:
        print("⚠️  pywin32 no instalado. Instala con: pip install pywin32")
        return

    try:
        try:
            import winshell
            desktop = Path(winshell.desktop())
        except ImportError:
            desktop = Path(os.path.expanduser("~/Desktop"))
            if not desktop.exists():
                desktop = Path(os.path.expandvars(r"%USERPROFILE%\Desktop"))

        if not desktop.exists():
            print(f"⚠️  No se encontró el escritorio: {desktop}")
            return

        shortcut_path = desktop / "Descargador YouTube.lnk"
        shell = win32com.client.Dispatch("WScript.Shell")
        shortcut = shell.CreateShortCut(str(shortcut_path))
        shortcut.TargetPath = python_exe
        shortcut.Arguments = f'"{script_path}"'
        shortcut.WorkingDirectory = str(script_path.parent)
        shortcut.Description = "Descargador de YouTube (Video/MP3)"
        shortcut.Save()
        print(f"✅ Icono creado en: {shortcut_path}")

    except Exception as e:
        print(f"⚠️  No se pudo crear el icono: {e}")


def crear_icono_linux(script_path: Path, python_exe: str):
    try:
        desktop_dir = Path.home() / "Desktop"
        if not desktop_dir.exists():
            desktop_dir = Path.home() / "Escritorio"
            if not desktop_dir.exists():
                desktop_dir = Path.home() / "Desktop"
                desktop_dir.mkdir(parents=True, exist_ok=True)

        wrapper = script_path.parent / f"{script_path.stem}_launcher.sh"
        wrapper.write_text(
            f'#!/bin/bash\n'
            f'cd "{script_path.parent}"\n'
            f'"{python_exe}" "{script_path}"\n'
            f'read -p "Presiona ENTER para cerrar..."\n'
        )
        wrapper.chmod(0o755)

        desktop_file = desktop_dir / "descargador-youtube.desktop"
        contenido = f"""[Desktop Entry]
Version=1.0
Type=Application
Name=Descargador YouTube
Comment=Descarga videos o MP3 de YouTube
Exec={wrapper}
Icon=applications-multimedia
Terminal=true
Categories=AudioVideo;Utility;
StartupNotify=true
"""
        desktop_file.write_text(contenido)
        desktop_file.chmod(0o755)

        menu_dir = Path.home() / ".local" / "share" / "applications"
        menu_dir.mkdir(parents=True, exist_ok=True)
        menu_file = menu_dir / "descargador-youtube.desktop"
        menu_file.write_text(contenido)
        menu_file.chmod(0o644)

        try:
            subprocess.run(["update-desktop-database", str(menu_dir)],
                           capture_output=True, timeout=5)
        except Exception:
            pass

        print(f"✅ Icono creado en: {desktop_file}")
        print(f"✅ Entrada de menú en: {menu_file}")

    except Exception as e:
        print(f"⚠️  No se pudo crear el icono: {e}")


# ═══════════════════════════════════════════════════════════════
#  INTERFAZ INTERACTIVA
# ═══════════════════════════════════════════════════════════════

def pedir_urls():
    print("\n🔗 Introduce URL(s). Una por línea. Línea vacía para terminar:")
    urls = []
    while True:
        u = input("   > ").strip()
        if not u:
            break
        urls.append(u)
    return urls


def main():
    print("=" * 60)
    print("  📥  DESCARGADOR DE YOUTUBE - Video o MP3 (PRO)")
    print("=" * 60)
    print(f"  SO                : {SO.upper()}")
    print(f"  Navegador cookies : {NAVEGADOR}")
    print(f"  Normalizar audio  : {'✅ Activado' if CONFIG['normalizar_audio'] else '❌ Desactivado'} ({CONFIG['lufs_objetivo']} LUFS)")
    print(f"  Notificaciones    : {'✅ Activadas' if CONFIG['notificar_al_terminar'] else '❌ Desactivadas'}")
    print(f"  Carpeta base      : {CONFIG['carpeta_base']}")
    print(f"    ├─ Videos       : {CONFIG['subcarpeta_video']}/")
    print(f"    └─ Audio        : {CONFIG['subcarpeta_audio']}/")
    print("=" * 60)

    if CONFIG["crear_icono"]:
        if SO == "windows":
            posible_icono = Path(os.path.expanduser("~/Desktop")) / "Descargador YouTube.lnk"
        else:
            posible_icono = Path.home() / "Desktop" / "descargador-youtube.desktop"
            if not posible_icono.exists():
                posible_icono = Path.home() / "Escritorio" / "descargador-youtube.desktop"

        if not posible_icono.exists():
            resp = input("\n¿Crear icono en el escritorio? (s/N): ").strip().lower()
            if resp == "s":
                crear_icono_escritorio()

    urls = pedir_urls()
    if not urls:
        print("❌ No se introdujo ninguna URL. Saliendo.")
        return

    alguna_playlist = any(("list=" in u) or ("/playlist" in u) for u in urls)
    solo_video = False
    if alguna_playlist:
        print("\n⚠️  Detectada al menos una URL de PLAYLIST.")
        print("  1. Descargar TODA la playlist")
        print("  2. Descargar SOLO el video (ignorar listas)")
        resp = input("Elige (1/2) [por defecto 1]: ").strip()
        solo_video = (resp == "2")

    print("\n¿Qué deseas descargar?")
    print("  1. Video (MP4)")
    print("  2. Solo Audio (MP3)")
    opcion = input("Elige (1/2): ").strip()

    if opcion == "2":
        tipo = "audio"
        print("\n🎵 Formato de audio:")
        print("  1. MP3 (recomendado)")
        print("  2. M4A")
        print("  3. Opus")
        fmt = input("Elige (1/2/3) [por defecto MP3]: ").strip()
        calidad = {"1": "mp3", "2": "m4a", "3": "opus"}.get(fmt, "mp3")
    else:
        tipo = "video"
        print("\n📺 Calidad de video:")
        print("  1. Mejor disponible")
        print("  2. 1080p")
        print("  3. 720p")
        print("  4. 480p")
        print("  5. 360p")
        cal = input("Elige (1-5) [por defecto Mejor]: ").strip()
        calidad = {"1": "mejor", "2": "1080p", "3": "720p",
                   "4": "480p", "5": "360p"}.get(cal, "mejor")

    carpeta = input(f"\n📁 Carpeta base [{CONFIG['carpeta_base']}]: ").strip()
    carpeta = carpeta or CONFIG["carpeta_base"]

    print("\n" + "─" * 60)
    print(f"  URLs   : {len(urls)}")
    print(f"  Tipo   : {tipo}")
    print(f"  Calidad: {calidad}")
    print(f"  Carpeta: {carpeta}")
    print("─" * 60 + "\n")

    inicio = datetime.now()
    for i, url in enumerate(urls, 1):
        print(f"\n▶ [{i}/{len(urls)}] {url}")
        descargar_media(url, tipo, calidad, carpeta, solo_video)

    fin = datetime.now()

    # === NOTIFICACIÓN FINAL ===
    total_seg = (fin - inicio).total_seconds()
    notificar(
        "Descarga completada ✅",
        f"{len(urls)} archivo(s) en {total_seg:.1f}s → {Path(carpeta).resolve()}"
    )

    print(f"\n🏁 Terminado en {total_seg:.1f}s")
    print(f"📁 Archivos en: {Path(carpeta).resolve()}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⏹️  Cancelado por el usuario.")