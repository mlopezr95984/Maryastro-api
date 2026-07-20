from __future__ import annotations

import html
import math
from collections import defaultdict
from typing import Any


GLIFOS_SIGNOS = [
    "♈", "♉", "♊", "♋", "♌", "♍",
    "♎", "♏", "♐", "♑", "♒", "♓",
]

GLIFOS_CUERPOS = {
    "Sol": "☉",
    "Luna": "☽",
    "Mercurio": "☿",
    "Venus": "♀",
    "Marte": "♂",
    "Júpiter": "♃",
    "Saturno": "♄",
    "Urano": "♅",
    "Neptuno": "♆",
    "Plutón": "♇",
    "Quirón": "⚷",
    "Lilith media": "⚸",
    "Lilith verdadera": "⚸",
    "Nodo Norte medio": "☊",
    "Nodo Sur medio": "☋",
    "Ascendente": "AC",
    "Medio Cielo": "MC",
}

COLORES_SIGNOS = [
    "#dc2626",  # Aries
    "#3f7d20",  # Tauro
    "#d97706",  # Géminis
    "#1d4ed8",  # Cáncer
    "#dc2626",  # Leo
    "#3f7d20",  # Virgo
    "#d97706",  # Libra
    "#1d4ed8",  # Escorpio
    "#dc2626",  # Sagitario
    "#8a5a16",  # Capricornio
    "#0f8b8d",  # Acuario
    "#1d4ed8",  # Piscis
]

COLORES_ASPECTOS = {
    "Conjunción": "#6b7280",
    "Semisextil": "#8b5cf6",
    "Sextil": "#16a34a",
    "Cuadratura": "#ef4444",
    "Trígono": "#4f83ff",
    "Quincuncio": "#f59e0b",
    "Oposición": "#dc2626",
}

TRAZO_ASPECTOS = {
    "Conjunción": "",
    "Semisextil": "4 4",
    "Sextil": "",
    "Cuadratura": "",
    "Trígono": "",
    "Quincuncio": "7 5",
    "Oposición": "7 4",
}

CUERPOS_NO_DIBUJADOS = {
    "Ascendente",
    "Medio Cielo",
}


def _punto_polar(
    centro_x: float,
    centro_y: float,
    radio: float,
    angulo_grados: float,
) -> tuple[float, float]:
    angulo = math.radians(angulo_grados)
    return (
        centro_x + radio * math.cos(angulo),
        centro_y - radio * math.sin(angulo),
    )


def _angulo_rueda(longitud: float, ascendente: float) -> float:
    """
    Coloca el Ascendente a la izquierda y conserva la orientación
    zodiacal validada en Wix.
    """
    return 180.0 + ((longitud - ascendente) % 360.0)


def _escapar(valor: Any) -> str:
    return html.escape(str(valor), quote=True)


def _formato_grado(grado_en_signo: float) -> str:
    grado = int(grado_en_signo)
    minuto = int(round((grado_en_signo - grado) * 60))

    if minuto == 60:
        grado += 1
        minuto = 0

    return f"{grado:02d}°{minuto:02d}′"


def _formato_angulo(longitud: float) -> str:
    return _formato_grado(longitud % 30)


def _ajustar_longitudes_visuales(
    posiciones: dict[str, dict[str, Any]],
    separacion_minima: float = 4.0,
) -> dict[str, float]:
    """
    Separa visualmente cuerpos muy próximos sin alterar
    sus longitudes astrológicas reales.
    """
    grupos: dict[int, list[tuple[str, float]]] = defaultdict(list)

    for nombre, datos in posiciones.items():
        if nombre in CUERPOS_NO_DIBUJADOS:
            continue

        longitud = float(datos["longitud"]) % 360.0
        grupo = int(round(longitud / separacion_minima))
        grupos[grupo].append((nombre, longitud))

    resultado: dict[str, float] = {}

    for cuerpos in grupos.values():
        cuerpos_ordenados = sorted(
            cuerpos,
            key=lambda elemento: elemento[1],
        )

        cantidad = len(cuerpos_ordenados)

        if cantidad == 1:
            nombre, longitud = cuerpos_ordenados[0]
            resultado[nombre] = longitud
            continue

        centro_grupo = (cantidad - 1) / 2

        for indice, (nombre, longitud) in enumerate(cuerpos_ordenados):
            desplazamiento = (
                indice - centro_grupo
            ) * separacion_minima

            resultado[nombre] = (
                longitud + desplazamiento
            ) % 360.0

    return resultado


def _agregar_escala_grados(
    partes: list[str],
    *,
    centro: float,
    radio_exterior: float,
    radio_escala_interior: float,
    ascendente: float,
) -> None:
    """
    Dibuja una marca fina por grado y una marca roja más larga
    y gruesa cada 5°.
    """
    for longitud in range(360):
        angulo = _angulo_rueda(float(longitud), ascendente)

        if longitud % 5 == 0:
            radio_inicio = radio_escala_interior
            color = "#ef4444"
            grosor = 1.8
        else:
            radio_inicio = radio_exterior - 7
            color = "#6b7280"
            grosor = 0.5

        x1, y1 = _punto_polar(
            centro,
            centro,
            radio_inicio,
            angulo,
        )
        x2, y2 = _punto_polar(
            centro,
            centro,
            radio_exterior,
            angulo,
        )

        partes.append(
            f'<line x1="{x1:.2f}" y1="{y1:.2f}" '
            f'x2="{x2:.2f}" y2="{y2:.2f}" '
            f'stroke="{color}" stroke-width="{grosor}"/>'
        )


def dibujar_rueda(
    posiciones: dict[str, dict[str, Any]],
    cuspides: list[dict[str, Any]],
    aspectos: list[dict[str, Any]],
    angulos: dict[str, dict[str, Any]],
    *,
    titulo: str = "Carta natal",
    tamano: int = 1000,
) -> str:
    """
    Dibuja una rueda astrológica SVG con signos, casas,
    posiciones planetarias, aspectos y escala de grados.
    """
    if len(cuspides) != 12:
        raise ValueError(
            "La rueda necesita exactamente 12 cúspides."
        )

    ascendente = float(
        angulos.get("Ascendente", {}).get(
            "longitud",
            cuspides[0]["longitud"],
        )
    ) % 360.0

    centro = tamano / 2

    radio_exterior = tamano * 0.438
    radio_escala_interior = tamano * 0.418
    radio_zodiaco_exterior = tamano * 0.405
    radio_zodiaco_interior = tamano * 0.330

    radio_planetas = tamano * 0.282
    radio_grados_planetas = tamano * 0.253

    radio_aspectos = tamano * 0.205
    radio_numeros_casas = tamano * 0.225

    partes: list[str] = [
        (
            f'<svg xmlns="http://www.w3.org/2000/svg" '
            f'viewBox="0 0 {tamano} {tamano}" '
            f'role="img" aria-label="{_escapar(titulo)}">'
        ),
        "<defs>",
        (
            "<style>"
            '.fondo{fill:#ffffff;}'
            '.circulo{fill:none;stroke:#1f2937;}'
            '.division-signo{stroke:#64748b;}'
            '.casa{stroke:#9ca3af;}'
            '.eje{stroke:#111827;}'
            '.signo{'
            'font-family:"Segoe UI Symbol","Noto Sans Symbols",sans-serif;'
            'font-size:32px;font-weight:600;'
            'text-anchor:middle;dominant-baseline:middle;'
            '}'
            '.planeta{'
            'font-family:"Segoe UI Symbol","Noto Sans Symbols",sans-serif;'
            'font-size:27px;'
            'text-anchor:middle;dominant-baseline:middle;'
            '}'
            '.grado{'
            'font-family:Arial,sans-serif;'
            'font-size:10px;font-weight:600;'
            'text-anchor:middle;fill:#374151;'
            '}'
            '.retro{fill:#1d4ed8;}'
            '.casa-num{'
            'font-family:Arial,sans-serif;'
            'font-size:13px;'
            'text-anchor:middle;dominant-baseline:middle;'
            'fill:#6b7280;'
            '}'
            '.angulo-etiqueta{'
            'font-family:Arial,sans-serif;'
            'font-size:15px;font-weight:700;fill:#111827;'
            '}'
            '.angulo-grado{'
            'font-family:Arial,sans-serif;'
            'font-size:11px;font-weight:600;fill:#374151;'
            '}'
            '.titulo{'
            'font-family:Arial,sans-serif;'
            'font-size:23px;font-weight:700;'
            'text-anchor:middle;fill:#111827;'
            '}'
            "</style>"
        ),
        "</defs>",
        (
            f'<rect class="fondo" width="{tamano}" '
            f'height="{tamano}"/>'
        ),
        (
            f'<text class="titulo" x="{centro}" y="34">'
            f'{_escapar(titulo)}</text>'
        ),
        (
            f'<circle class="circulo" cx="{centro}" '
            f'cy="{centro}" r="{radio_exterior}" '
            f'stroke-width="1.8"/>'
        ),
        (
            f'<circle class="circulo" cx="{centro}" '
            f'cy="{centro}" r="{radio_zodiaco_exterior}" '
            f'stroke-width="1.1"/>'
        ),
        (
            f'<circle class="circulo" cx="{centro}" '
            f'cy="{centro}" r="{radio_zodiaco_interior}" '
            f'stroke-width="1.4"/>'
        ),
        (
            f'<circle class="circulo" cx="{centro}" '
            f'cy="{centro}" r="{radio_aspectos}" '
            f'stroke-width="0.9"/>'
        ),
    ]

    _agregar_escala_grados(
        partes,
        centro=centro,
        radio_exterior=radio_exterior,
        radio_escala_interior=radio_escala_interior,
        ascendente=ascendente,
    )

    # Divisiones zodiacales y glifos.
    for indice in range(12):
        longitud_inicio = indice * 30.0
        angulo_inicio = _angulo_rueda(
            longitud_inicio,
            ascendente,
        )

        x1, y1 = _punto_polar(
            centro,
            centro,
            radio_zodiaco_interior,
            angulo_inicio,
        )
        x2, y2 = _punto_polar(
            centro,
            centro,
            radio_zodiaco_exterior,
            angulo_inicio,
        )

        partes.append(
            f'<line class="division-signo" '
            f'x1="{x1:.2f}" y1="{y1:.2f}" '
            f'x2="{x2:.2f}" y2="{y2:.2f}" '
            f'stroke-width="1"/>'
        )

        longitud_centro = longitud_inicio + 15.0
        angulo_centro = _angulo_rueda(
            longitud_centro,
            ascendente,
        )

        radio_glifo = (
            radio_zodiaco_exterior
            + radio_zodiaco_interior
        ) / 2

        xg, yg = _punto_polar(
            centro,
            centro,
            radio_glifo,
            angulo_centro,
        )

        partes.append(
            f'<text class="signo" '
            f'x="{xg:.2f}" y="{yg:.2f}" '
            f'fill="{COLORES_SIGNOS[indice]}">'
            f'{GLIFOS_SIGNOS[indice]}</text>'
        )

    # Cúspides y números de casas.
    for cuspide in cuspides:
        numero_casa = int(cuspide["casa"])
        longitud = float(cuspide["longitud"]) % 360.0
        angulo = _angulo_rueda(longitud, ascendente)

        x1, y1 = _punto_polar(
            centro,
            centro,
            radio_aspectos,
            angulo,
        )
        x2, y2 = _punto_polar(
            centro,
            centro,
            radio_zodiaco_interior,
            angulo,
        )

        es_eje = numero_casa in {1, 4, 7, 10}
        clase = "eje" if es_eje else "casa"
        grosor = 2.0 if es_eje else 0.85

        partes.append(
            f'<line class="{clase}" '
            f'x1="{x1:.2f}" y1="{y1:.2f}" '
            f'x2="{x2:.2f}" y2="{y2:.2f}" '
            f'stroke-width="{grosor}"/>'
        )

        siguiente = cuspides[numero_casa % 12]
        longitud_siguiente = (
            float(siguiente["longitud"]) % 360.0
        )

        arco = (
            longitud_siguiente - longitud
        ) % 360.0

        longitud_media = (
            longitud + arco / 2.0
        ) % 360.0

        angulo_medio = _angulo_rueda(
            longitud_media,
            ascendente,
        )

        xn, yn = _punto_polar(
            centro,
            centro,
            radio_numeros_casas,
            angulo_medio,
        )

        partes.append(
            f'<text class="casa-num" '
            f'x="{xn:.2f}" y="{yn:.2f}">'
            f'{numero_casa}</text>'
        )

    # Solo AC y MC, colocados fuera del anillo interno.
    etiquetas_angulares = {
        "Ascendente": "AC",
        "Medio Cielo": "MC",
    }

    for nombre, abreviatura in etiquetas_angulares.items():
        datos = angulos.get(nombre)

        if not datos:
            continue

        longitud = float(datos["longitud"]) % 360.0
        angulo = _angulo_rueda(longitud, ascendente)

        radio_etiqueta = radio_exterior + 20
        radio_grado = radio_exterior + 38

        xa, ya = _punto_polar(
            centro,
            centro,
            radio_etiqueta,
            angulo,
        )
        xgrado, ygrado = _punto_polar(
            centro,
            centro,
            radio_grado,
            angulo,
        )

        ancla = "middle"

        if xa < centro - 20:
            ancla = "end"
        elif xa > centro + 20:
            ancla = "start"

        partes.append(
            f'<text class="angulo-etiqueta" '
            f'x="{xa:.2f}" y="{ya:.2f}" '
            f'text-anchor="{ancla}">'
            f'{abreviatura}</text>'
        )

        partes.append(
            f'<text class="angulo-grado" '
            f'x="{xgrado:.2f}" y="{ygrado:.2f}" '
            f'text-anchor="{ancla}">'
            f'{_formato_angulo(longitud)}</text>'
        )

    # Aspectos.
    for aspecto in aspectos:
        cuerpo_1 = aspecto.get("cuerpo1")
        cuerpo_2 = aspecto.get("cuerpo2")
        tipo = aspecto.get("aspecto", "")

        if (
            cuerpo_1 not in posiciones
            or cuerpo_2 not in posiciones
        ):
            continue

        longitud_1 = float(
            posiciones[cuerpo_1]["longitud"]
        )
        longitud_2 = float(
            posiciones[cuerpo_2]["longitud"]
        )

        angulo_1 = _angulo_rueda(
            longitud_1,
            ascendente,
        )
        angulo_2 = _angulo_rueda(
            longitud_2,
            ascendente,
        )

        x1, y1 = _punto_polar(
            centro,
            centro,
            radio_aspectos - 5,
            angulo_1,
        )
        x2, y2 = _punto_polar(
            centro,
            centro,
            radio_aspectos - 5,
            angulo_2,
        )

        color = COLORES_ASPECTOS.get(
            tipo,
            "#9ca3af",
        )
        dash = TRAZO_ASPECTOS.get(tipo, "")
        dash_attr = (
            f' stroke-dasharray="{dash}"'
            if dash
            else ""
        )

        partes.append(
            f'<line x1="{x1:.2f}" y1="{y1:.2f}" '
            f'x2="{x2:.2f}" y2="{y2:.2f}" '
            f'stroke="{color}" '
            f'stroke-width="1.1" '
            f'stroke-opacity="0.62"'
            f'{dash_attr}/>'
        )

    # Planetas y puntos.
    posiciones_visuales = _ajustar_longitudes_visuales(
        posiciones
    )

    for nombre, longitud_visual in posiciones_visuales.items():
        datos = posiciones[nombre]
        longitud_real = float(datos["longitud"]) % 360.0

        angulo_visual = _angulo_rueda(
            longitud_visual,
            ascendente,
        )
        angulo_real = _angulo_rueda(
            longitud_real,
            ascendente,
        )

        diferencia = abs(
            (
                longitud_visual
                - longitud_real
                + 180
            )
            % 360
            - 180
        )

        if diferencia > 0.1:
            gx1, gy1 = _punto_polar(
                centro,
                centro,
                radio_aspectos,
                angulo_real,
            )
            gx2, gy2 = _punto_polar(
                centro,
                centro,
                radio_planetas - 18,
                angulo_visual,
            )

            partes.append(
                f'<line x1="{gx1:.2f}" y1="{gy1:.2f}" '
                f'x2="{gx2:.2f}" y2="{gy2:.2f}" '
                f'stroke="#94a3b8" '
                f'stroke-width="0.7"/>'
            )

        xp, yp = _punto_polar(
            centro,
            centro,
            radio_planetas,
            angulo_visual,
        )

        glifo = GLIFOS_CUERPOS.get(
            nombre,
            nombre[:2],
        )
        grado = _formato_grado(
            float(datos.get("grado_en_signo", 0.0))
        )
        retrogrado = bool(datos.get("retrogrado"))

        partes.append(
            "<g>"
            f"<title>{_escapar(nombre)}: "
            f'{_escapar(datos.get("signo", ""))} '
            f'{grado}'
            f'{" ℞" if retrogrado else ""}'
            "</title>"
            f'<text class="planeta" '
            f'x="{xp:.2f}" y="{yp:.2f}">'
            f'{_escapar(glifo)}</text>'
            "</g>"
        )

        xg, yg = _punto_polar(
            centro,
            centro,
            radio_grados_planetas,
            angulo_visual,
        )

        partes.append(
            f'<text class="grado" '
            f'x="{xg:.2f}" y="{yg:.2f}">'
            f'{grado}</text>'
        )

        if retrogrado:
            xr, yr = _punto_polar(
                centro,
                centro,
                radio_grados_planetas - 13,
                angulo_visual,
            )

            partes.append(
                f'<text class="grado retro" '
                f'x="{xr:.2f}" y="{yr:.2f}">'
                f'R</text>'
            )

    partes.append("</svg>")
    return "".join(partes)


def generar_rueda_svg(
    resultado: dict[str, Any],
    *,
    tamano: int = 1000,
) -> str:
    """
    Adaptador para el diccionario producido por
    PerfilEnergetico.obtener_resultado().
    """
    datos = resultado.get("datos", {})

    nombre = datos.get("nombre") or "Carta natal"
    ciudad = datos.get("ciudad")

    titulo = f"Carta natal de {nombre}"

    if ciudad:
        titulo += f" · {ciudad}"

    return dibujar_rueda(
        posiciones=resultado["posiciones"],
        cuspides=resultado["cuspides"],
        aspectos=resultado.get("aspectos", []),
        angulos=resultado["angulos"],
        titulo=titulo,
        tamano=tamano,
    )
