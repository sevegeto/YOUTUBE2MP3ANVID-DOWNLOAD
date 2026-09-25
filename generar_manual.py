"""
Generador de manuales PDF para el Descargador de YouTube.
Requiere: pip install reportlab
Genera: Manual_Tecnico.pdf y Manual_Usuario.pdf
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, PageBreak,
    Table, TableStyle
)


# ═══════════════════════════════════════════════════════════════
#  ESTILOS
# ═══════════════════════════════════════════════════════════════

def crear_estilos():
    styles = getSampleStyleSheet()

    styles.add(ParagraphStyle(
        'TituloManual',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1a1a2e'),
        alignment=TA_CENTER,
        spaceAfter=20
    ))
    styles.add(ParagraphStyle(
        'Subtitulo',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=colors.HexColor('#16213e'),
        spaceBefore=15,
        spaceAfter=10
    ))
    styles.add(ParagraphStyle(
        'Seccion',
        parent=styles['Heading3'],
        fontSize=13,
        textColor=colors.HexColor('#0f3460'),
        spaceBefore=12,
        spaceAfter=8
    ))
    styles.add(ParagraphStyle(
        'Cuerpo',
        parent=styles['Normal'],
        fontSize=10.5,
        leading=15,
        alignment=TA_JUSTIFY,
        spaceAfter=8
    ))
    styles.add(ParagraphStyle(
        'Codigo',
        parent=styles['Normal'],
        fontName='Courier',
        fontSize=9,
        leading=12,
        textColor=colors.HexColor('#2d3436'),
        backColor=colors.HexColor('#f5f6fa'),
        borderPadding=6,
        spaceAfter=6
    ))
    styles.add(ParagraphStyle(
        'PiePagina',
        parent=styles['Normal'],
        fontSize=8,
        textColor=colors.HexColor('#888888'),
        alignment=TA_CENTER
    ))
    return styles


# ═══════════════════════════════════════════════════════════════
#  HELPERS
# ═══════════════════════════════════════════════════════════════

def tabla(datos, col_widths, header=True):
    """Crea una tabla estilizada."""
    t = Table(datos, colWidths=col_widths)
    estilo = [
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
        ('FONTSIZE', (0,0), (-1,-1), 9.5),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('GRID', (0,0), (-1,-1), 0.4, colors.HexColor('#cccccc')),
    ]
    if header:
        estilo += [
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#0f3460')),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ]
    t.setStyle(TableStyle(estilo))
    return t


def numeracion_paginas(canvas, doc):
    """Agrega número de página al pie."""
    canvas.saveState()
    canvas.setFont('Helvetica', 8)
    canvas.setFillColor(colors.HexColor('#888888'))
    canvas.drawCentredString(
        A4[0] / 2, 1.2*cm,
        f"Página {doc.page}"
    )
    canvas.restoreState()


# ═══════════════════════════════════════════════════════════════
#  MANUAL TÉCNICO
# ═══════════════════════════════════════════════════════════════

def generar_manual_tecnico(ruta: str):
    doc = SimpleDocTemplate(
        ruta, pagesize=A4,
        leftMargin=2*cm, rightMargin=2*cm,
        topMargin=2*cm, bottomMargin=2*cm,
        title="Manual Técnico - Descargador YouTube Pro",
        author="Sistema de Descarga"
    )
    s = crear_estilos()
    story = []

    # ---------- PORTADA ----------
    story.append(Spacer(1, 4*cm))
    story.append(Paragraph("Manual Técnico", s['TituloManual']))
    story.append(Spacer(1, 1*cm))
    story.append(Paragraph(
        "Descargador de YouTube Pro<br/>"
        "Video &amp; MP3 con Normalización de Audio",
        s['Subtitulo']
    ))
    story.append(Spacer(1, 3*cm))
    story.append(Paragraph(
        "<b>Plataformas:</b> Windows 11 · Fedora 44<br/>"
        "<b>Versión:</b> 3.0<br/>"
        "<b>Fecha:</b> 2026<br/>"
        "<b>Lenguaje:</b> Python 3.10+",
        s['Cuerpo']
    ))
    story.append(PageBreak())

    # ---------- TOC ----------
    story.append(Paragraph("Tabla de Contenidos", s['Subtitulo']))
    toc = [
        ["1.", "Arquitectura del sistema"],
        ["2.", "Requisitos técnicos"],
        ["3.", "Módulos y funciones"],
        ["4.", "Normalización de audio (LUFS)"],
        ["5.", "Sistema de notificaciones"],
        ["6.", "Cookies y autenticación"],
        ["7.", "Gestión de errores y logging"],
        ["8.", "Estructura de archivos"],
    ]
    story.append(tabla([["#", "Sección"]] + toc, [1.5*cm, 13.5*cm]))
    story.append(PageBreak())

    # ---------- 1. ARQUITECTURA ----------
    story.append(Paragraph("1. Arquitectura del Sistema", s['Subtitulo']))
    story.append(Paragraph(
        "El sistema es un script Python monolítico que orquesta componentes externos "
        "(yt-dlp, FFmpeg, PowerShell / notify-send) mediante subprocess. La lógica se "
        "organiza en capas funcionales:",
        s['Cuerpo']
    ))
    capas = [
        ["Capa", "Responsabilidad"],
        ["Interfaz", "Menú interactivo, entrada de URLs, selección de calidad"],
        ["Descarga", "yt-dlp con cookies, reintentos, historial"],
        ["Post-proceso", "FFmpeg: conversión, metadatos, normalización LUFS"],
        ["Notificación", "PowerShell Toast (Win) / notify-send (Linux)"],
        ["Sistema", "Detección de SO, navegador, creación de iconos"],
    ]
    story.append(tabla(capas, [3.5*cm, 11.5*cm]))
    story.append(Spacer(1, 0.5*cm))

    # ---------- 2. REQUISITOS ----------
    story.append(Paragraph("2. Requisitos Técnicos", s['Subtitulo']))
    reqs = [
        ["Componente", "Versión mínima", "Propósito"],
        ["Python", "3.10", "Ejecución del script"],
        ["yt-dlp", "2024.01+", "Extracción y descarga"],
        ["FFmpeg", "6.0", "Conversión, normalización, merge"],
        ["Deno / Node", "Opcional", "Runtime JS para YouTube"],
        ["pywin32", "Opcional (Win)", "Acceso directo .lnk"],
        ["reportlab", "4.0", "Generación de PDFs"],
    ]
    story.append(tabla(reqs, [3.5*cm, 3.5*cm, 8*cm]))
    story.append(PageBreak())

    # ---------- 3. MÓDULOS ----------
    story.append(Paragraph("3. Módulos y Funciones", s['Subtitulo']))

    modulos = [
        ("detectar_so()", "Devuelve 'windows', 'fedora' o 'debian' según /etc/os-release o platform.system()."),
        ("detectar_navegador()", "Busca perfiles de Firefox, Chrome, Edge, Brave o Chromium en rutas típicas."),
        ("detectar_runtime_js()", "Localiza 'deno', 'node' o 'bun' en PATH para habilitar extracción completa de YouTube."),
        ("notificar(titulo, msg)", "Envía Toast en Windows (PowerShell) o notify-send en Linux. No bloqueante."),
        ("normalizar_audio(ruta)", "Ejecuta FFmpeg loudnorm en 2 pasadas para ajustar LUFS objetivo."),
        ("descargar_media(...)", "Función principal: configura yt-dlp, descarga, postprocesa y notifica."),
        ("crear_icono_escritorio()", "Genera .lnk en Windows o .desktop en Fedora."),
    ]
    for nombre, desc in modulos:
        story.append(Paragraph(f"<b>{nombre}</b>", s['Cuerpo']))
        story.append(Paragraph(desc, s['Cuerpo']))
        story.append(Spacer(1, 0.2*cm))

    story.append(PageBreak())

    # ---------- 4. NORMALIZACIÓN LUFS ----------
    story.append(Paragraph("4. Normalización de Audio (LUFS)", s['Subtitulo']))
    story.append(Paragraph(
        "La normalización se realiza con el filtro <b>loudnorm</b> de FFmpeg en modo "
        "<b>dual-pass</b>, que mide primero y aplica después. Esto evita distorsión y "
        "garantiza un volumen consistente entre pistas.",
        s['Cuerpo']
    ))
    lufs = [
        ["Parámetro", "Valor", "Descripción"],
        ["I (Integrated)", "-16 LUFS", "Estándar YouTube / Spotify / Apple Music"],
        ["TP (True Peak)", "-1.5 dB", "Margen para evitar clipping en DACs"],
        ["LRA", "11 dB", "Rango dinámico; 11 dB es natural para voz/música"],
        ["Sample rate", "48000 Hz", "Estándar de audio profesional"],
    ]
    story.append(tabla(lufs, [4*cm, 3*cm, 8*cm]))
    story.append(Spacer(1, 0.4*cm))
    story.append(Paragraph(
        "<b>Primera pasada:</b> mide input_i, input_tp, input_lra, input_thresh y target_offset. "
        "FFmpeg emite estos valores como JSON en stderr.<br/>"
        "<b>Segunda pasada:</b> aplica loudnorm con los valores medidos y <i>linear=true</i> para "
        "corrección lineal sin compresión adicional.",
        s['Cuerpo']
    ))

    # ---------- 5. NOTIFICACIONES ----------
    story.append(Paragraph("5. Sistema de Notificaciones", s['Subtitulo']))
    notif = [
        ["SO", "Mecanismo", "Comando"],
        ["Windows 11", "Toast nativo", "powershell -Command [ToastNotificationManager]"],
        ["Fedora 44", "libnotify", "notify-send -a 'Descargador' -i download <título> <msg>"],
    ]
    story.append(tabla(notif, [3*cm, 3.5*cm, 8.5*cm]))
    story.append(Spacer(1, 0.4*cm))
    story.append(Paragraph(
        "Las notificaciones se envían al finalizar toda la cola de descargas con el "
        "número de archivos y el tiempo total. Si falla, se registra en el log sin "
        "interrumpir el flujo principal.",
        s['Cuerpo']
    ))

    # ---------- 6. COOKIES ----------
    story.append(Paragraph("6. Cookies y Autenticación", s['Subtitulo']))
    story.append(Paragraph(
        "El script extrae cookies del navegador automáticamente mediante "
        "<i>cookiesfrombrowser</i> de yt-dlp. El orden de preferencia es: "
        "firefox → chrome → edge → brave → chromium → opera.",
        s['Cuerpo']
    ))
    story.append(Paragraph(
        "<b>Nota importante:</b> Chrome 127+ introdujo cifrado App-Bound que puede impedir "
        "la lectura de cookies desde procesos externos. Se recomienda Firefox o cerrar Chrome "
        "antes de ejecutar el script.",
        s['Cuerpo']
    ))

    # ---------- 7. ERRORES ----------
    story.append(Paragraph("7. Gestión de Errores y Logging", s['Subtitulo']))
    story.append(Paragraph(
        "El módulo <i>logging</i> escribe en <b>errores.log</b> con formato: "
        "<i>fecha | nivel | mensaje</i>. Solo se registran WARNING y ERROR para no "
        "saturar el archivo. Los errores de descarga individuales no detienen la cola "
        "gracias a <i>ignoreerrors=True</i>.",
        s['Cuerpo']
    ))

    # ---------- 8. ESTRUCTURA ----------
    story.append(Paragraph("8. Estructura de Archivos", s['Subtitulo']))
    arbol = (
        "📁 Proyecto/<br/>"
        "├── descargar_youtube_pro.py<br/>"
        "├── generar_manual.py<br/>"
        "├── errores.log<br/>"
        "├── Manual_Tecnico.pdf<br/>"
        "├── Manual_Usuario.pdf<br/>"
        "├── .historial/<br/>"
        "│   ├── descargados_video.txt<br/>"
        "│   └── descargados_audio.txt<br/>"
        "└── descargas/<br/>"
        "    ├── videos/<br/>"
        "    └── audio/"
    )
    story.append(Paragraph(arbol.replace(" ", "&nbsp;"), s['Codigo']))

    doc.build(story, onFirstPage=numeracion_paginas, onLaterPages=numeracion_paginas)
    print(f"✅ Manual técnico generado: {ruta}")


# ═══════════════════════════════════════════════════════════════
#  MANUAL DE USUARIO
# ═══════════════════════════════════════════════════════════════

def generar_manual_usuario(ruta: str):
    doc = SimpleDocTemplate(
        ruta, pagesize=A4,
        leftMargin=2*cm, rightMargin=2*cm,
        topMargin=2*cm, bottomMargin=2*cm,
        title="Manual de Usuario - Descargador YouTube Pro",
        author="Sistema de Descarga"
    )
    s = crear_estilos()
    story = []

    # ---------- PORTADA ----------
    story.append(Spacer(1, 4*cm))
    story.append(Paragraph("Manual de Usuario", s['TituloManual']))
    story.append(Spacer(1, 1*cm))
    story.append(Paragraph(
        "Descargador de YouTube Pro<br/>"
        "Aprende a descargar videos y MP3 en 5 minutos",
        s['Subtitulo']
    ))
    story.append(Spacer(1, 3*cm))
    story.append(Paragraph(
        "Compatible con <b>Windows 11</b> y <b>Fedora 44</b>",
        s['Cuerpo']
    ))
    story.append(PageBreak())

    # ---------- TOC ----------
    story.append(Paragraph("Contenido", s['Subtitulo']))
    toc = [
        ["1.", "¿Qué hace este programa?"],
        ["2.", "Instalación en Windows 11"],
        ["3.", "Instalación en Fedora 44"],
        ["4.", "Cómo usarlo paso a paso"],
        ["5.", "Opciones de calidad y formato"],
        ["6.", "Normalización de volumen"],
        ["7.", "Notificaciones"],
        ["8.", "Preguntas frecuentes"],
        ["9.", "Solución de problemas"],
    ]
    story.append(tabla([["#", "Sección"]] + toc, [1.5*cm, 13.5*cm]))
    story.append(PageBreak())

    # ---------- 1. QUÉ HACE ----------
    story.append(Paragraph("1. ¿Qué hace este programa?", s['Subtitulo']))
    story.append(Paragraph(
        "Es un descargador de YouTube que funciona con un menú simple en la terminal. "
        "Puedes bajar videos completos o solo el audio (MP3) y aplicarles "
        "<b>normalización de volumen</b> para que todas tus pistas suenen al mismo nivel.",
        s['Cuerpo']
    ))
    story.append(Paragraph("Características principales:", s['Seccion']))
    features = [
        ["✅", "Descarga videos en MP4 (360p a 1080p o mejor)"],
        ["✅", "Extrae audio en MP3, M4A u Opus"],
        ["✅", "Normaliza el volumen automáticamente (-16 LUFS)"],
        ["✅", "Organiza archivos en carpetas separadas: videos/ y audio/"],
        ["✅", "Evita re-descargar lo que ya tienes (historial)"],
        ["✅", "Soporta playlists completas o videos individuales"],
        ["✅", "Notificaciones al terminar la descarga"],
        ["✅", "Crea un icono de acceso directo en el escritorio"],
    ]
    story.append(tabla([["", "Función"]] + features, [1*cm, 14*cm]))
    story.append(PageBreak())

    # ---------- 2. INSTALACIÓN WINDOWS ----------
    story.append(Paragraph("2. Instalación en Windows 11", s['Subtitulo']))
    story.append(Paragraph("Paso 1 — Abrir PowerShell", s['Seccion']))
    story.append(Paragraph(
        "Presiona <b>Win + X</b> y elige <i>Terminal (Admin)</i> o <i>PowerShell</i>.",
        s['Cuerpo']
    ))
    story.append(Paragraph("Paso 2 — Instalar Python y dependencias", s['Seccion']))
    story.append(Paragraph(
        "pip install yt-dlp pywin32 winshell reportlab",
        s['Codigo']
    ))
    story.append(Paragraph("Paso 3 — Instalar FFmpeg y Deno (opcional)", s['Seccion']))
    story.append(Paragraph(
        'winget install "FFmpeg (Essentials Build)"<br/>'
        'winget install DenoLand.Deno',
        s['Codigo']
    ))
    story.append(Paragraph(
        "Cierra y vuelve a abrir PowerShell para que reconozca los comandos.",
        s['Cuerpo']
    ))
    story.append(Paragraph("Paso 4 — Guardar el script", s['Seccion']))
    story.append(Paragraph(
        "Crea una carpeta (por ejemplo <i>D:\\YOUTUBE</i>) y guarda allí el archivo "
        "<b>descargar_youtube_pro.py</b>.",
        s['Cuerpo']
    ))

    # ---------- 3. INSTALACIÓN FEDORA ----------
    story.append(Paragraph("3. Instalación en Fedora 44", s['Subtitulo']))
    story.append(Paragraph("Paso 1 — Abrir terminal", s['Seccion']))
    story.append(Paragraph(
        "Presiona <b>Ctrl + Alt + T</b> o abre <i>Terminal</i> desde el menú de aplicaciones.",
        s['Cuerpo']
    ))
    story.append(Paragraph("Paso 2 — Instalar dependencias", s['Seccion']))
    story.append(Paragraph(
        "pip install yt-dlp reportlab<br/>"
        "sudo dnf install ffmpeg libnotify<br/>"
        "sudo dnf install deno    # opcional",
        s['Codigo']
    ))
    story.append(Paragraph("Paso 3 — Guardar el script", s['Seccion']))
    story.append(Paragraph(
        "Guarda <b>descargar_youtube_pro.py</b> en una carpeta, por ejemplo "
        "<i>~/Descargas_Youtube/</i>.",
        s['Cuerpo']
    ))
    story.append(PageBreak())

    # ---------- 4. USO PASO A PASO ----------
    story.append(Paragraph("4. Cómo usarlo paso a paso", s['Subtitulo']))
    story.append(Paragraph("Abrir el programa", s['Seccion']))
    story.append(Paragraph(
        "En Windows:<br/>"
        "<font face='Courier'>python descargar_youtube_pro.py</font><br/><br/>"
        "En Fedora:<br/>"
        "<font face='Courier'>python3 descargar_youtube_pro.py</font>",
        s['Cuerpo']
    ))
    story.append(Paragraph("Aparecerá un menú así:", s['Seccion']))
    menu = (
        "============================================================<br/>"
        "  📥  DESCARGADOR DE YOUTUBE - Video o MP3 (PRO)<br/>"
        "============================================================<br/>"
        "  SO                : WINDOWS<br/>"
        "  Navegador cookies : firefox<br/>"
        "  Normalizar audio  : ✅ Activado (-16 LUFS)<br/>"
        "  Notificaciones    : ✅ Activadas<br/>"
        "============================================================<br/>"
        "<br/>"
        "🔗 Introduce URL(s). Una por línea. Línea vacía para terminar:<br/>"
        "   > https://www.youtube.com/watch?v=XXXX<br/>"
        "   >"
    )
    story.append(Paragraph(menu, s['Codigo']))
    story.append(Paragraph("Pasos:", s['Seccion']))
    pasos = [
        ["1", "Pega la URL del video o playlist y presiona Enter."],
        ["2", "Si no quieres agregar más URLs, presiona Enter otra vez."],
        ["3", "Si es playlist: elige 1 (toda) o 2 (solo el video)."],
        ["4", "Elige 1 para video o 2 para audio."],
        ["5", "Si es audio: elige MP3, M4A u Opus."],
        ["6", "Si es video: elige la calidad (Mejor, 1080p, 720p…)."],
        ["7", "Presiona Enter para usar la carpeta por defecto."],
        ["8", "¡Listo! Verás la barra de progreso y al terminar, una notificación."],
    ]
    story.append(tabla([["#", "Acción"]] + pasos, [1*cm, 14*cm]))
    story.append(PageBreak())

    # ---------- 5. CALIDADES ----------
    story.append(Paragraph("5. Opciones de Calidad y Formato", s['Subtitulo']))
    story.append(Paragraph("Videos (MP4):", s['Seccion']))
    videos = [
        ["Opción", "Resolución", "Uso recomendado"],
        ["1. Mejor", "Hasta 4K/8K", "Máxima calidad, archivos grandes"],
        ["2. 1080p", "Full HD", "Ver en TV/monitor moderno"],
        ["3. 720p", "HD", "Buen balance calidad/tamaño"],
        ["4. 480p", "SD", "Ahorro de espacio"],
        ["5. 360p", "Baja", "Videos pequeños o móviles antiguos"],
    ]
    story.append(tabla(videos, [2.5*cm, 3*cm, 9.5*cm]))
    story.append(Spacer(1, 0.4*cm))
    story.append(Paragraph("Audio:", s['Seccion']))
    audio = [
        ["Formato", "Bitrate", "Uso recomendado"],
        ["MP3", "192 kbps", "Compatible con todo, ideal para música"],
        ["M4A", "192 kbps", "Mejor compresión que MP3"],
        ["Opus", "128 kbps", "Máxima eficiencia, moderno"],
    ]
    story.append(tabla(audio, [2.5*cm, 3*cm, 9.5*cm]))
    story.append(PageBreak())

    # ---------- 6. NORMALIZACIÓN ----------
    story.append(Paragraph("6. Normalización de Volumen", s['Subtitulo']))
    story.append(Paragraph(
        "Cuando descargas audio, el programa aplica automáticamente el filtro "
        "<b>loudnorm</b> de FFmpeg. Esto hace que todas tus pistas suenen al mismo "
        "volumen, sin tener que subir o bajar el control manualmente.",
        s['Cuerpo']
    ))
    story.append(Paragraph("¿Qué verás en pantalla?", s['Seccion']))
    story.append(Paragraph(
        "   🎚️  Normalizando volumen (dual-pass LUFS)...<br/>"
        "   ✅ Volumen normalizado (-16 LUFS)",
        s['Codigo']
    ))
    story.append(Paragraph(
        "<b>Nota:</b> Este proceso puede tardar unos segundos adicionales por archivo. "
        "Si prefieres desactivarlo, edita la constante <i>CONFIG[\"normalizar_audio\"]</i> "
        "y cámbiala a <i>False</i>.",
        s['Cuerpo']
    ))

    # ---------- 7. NOTIFICACIONES ----------
    story.append(Paragraph("7. Notificaciones", s['Subtitulo']))
    story.append(Paragraph(
        "Al terminar todas las descargas, recibirás una notificación del sistema:",
        s['Cuerpo']
    ))
    story.append(Paragraph(
        "<b>Windows 11:</b> Aparece en la esquina inferior derecha.<br/>"
        "<b>Fedora 44:</b> Aparece en la parte superior central de la pantalla.",
        s['Cuerpo']
    ))
    story.append(Paragraph(
        "La notificación incluye el número de archivos descargados y la carpeta destino. "
        "Si no la ves, revisa que las notificaciones estén habilitadas en tu SO.",
        s['Cuerpo']
    ))

    # ---------- 8. FAQ ----------
    story.append(Paragraph("8. Preguntas Frecuentes", s['Subtitulo']))
    faq = [
        ["¿Por qué se abre una ventana negra al hacer doble clic en el icono?",
         "Es normal: el programa usa la terminal para mostrar el progreso. Se cierra al terminar."],
        ["¿Puedo descargar solo una canción de una playlist?",
         "Sí, elige la opción 2 cuando te pregunte si quieres toda la lista o solo el video."],
        ["¿Dónde se guardan los archivos?",
         "En la carpeta 'descargas' junto al script. Dentro hay 'videos/' y 'audio/' separados."],
        ["¿Qué pasa si ya descargué un video antes?",
         "El programa lo detecta por su ID en el historial y lo salta automáticamente."],
        ["¿Cómo cambio la calidad por defecto?",
         "Edita la constante CONFIG al inicio del script (bitrate_audio, lufs_objetivo, etc.)."],
        ["¿Funciona en macOS?",
         "No está probado oficialmente, pero yt-dlp y FFmpeg sí funcionan en Mac."],
    ]
    for p, r in faq:
        story.append(Paragraph(f"<b>❓ {p}</b>", s['Cuerpo']))
        story.append(Paragraph(f"💡 {r}", s['Cuerpo']))
        story.append(Spacer(1, 0.2*cm))
    story.append(PageBreak())

    # ---------- 9. PROBLEMAS ----------
    story.append(Paragraph("9. Solución de Problemas", s['Subtitulo']))
    errores = [
        ["Error", "Causa", "Solución"],
        ["'python' no se reconoce",
         "Python no está en PATH",
         "Reinstala Python marcando 'Add to PATH'"],
        ["ffmpeg not found",
         "FFmpeg no instalado o no en PATH",
         "Instálalo con winget o dnf y reinicia la terminal"],
        ["Sign in to confirm you're not a bot",
         "YouTube pide verificación",
         "Abre YouTube en Firefox, loguéate y vuelve a ejecutar"],
        ["Video unavailable",
         "El video fue eliminado o es privado",
         "El programa lo omite y sigue con el resto"],
        ["No supported JavaScript runtime",
         "Falta Deno o Node",
         "winget install DenoLand.Deno / sudo dnf install deno"],
        ["No sound / volume bajo",
         "Audio sin normalizar o FFmpeg viejo",
         "Verifica que normalizar_audio esté en True y FFmpeg actualizado"],
    ]
    story.append(tabla(errores, [4*cm, 4*cm, 7*cm]))
    story.append(Spacer(1, 0.6*cm))

    story.append(Paragraph(
        "<b>Consejo:</b> Si algo falla, revisa el archivo <i>errores.log</i> en la "
        "carpeta del script. Allí se registran todos los mensajes de error con fecha y hora.",
        s['Cuerpo']
    ))

    doc.build(story, onFirstPage=numeracion_paginas, onLaterPages=numeracion_paginas)
    print(f"✅ Manual de usuario generado: {ruta}")


# ═══════════════════════════════════════════════════════════════
#  MAIN
# ═══════════════════════════════════════════════════════════════

def main():
    print("=" * 55)
    print("  📄  GENERADOR DE MANUALES PDF")
    print("=" * 55)

    generar_manual_tecnico("Manual_Tecnico.pdf")
    generar_manual_usuario("Manual_Usuario.pdf")

    print("\n✅ ¡Listo! Se generaron:")
    print("   📘 Manual_Tecnico.pdf")
    print("   📗 Manual_Usuario.pdf")


if __name__ == "__main__":
    main()