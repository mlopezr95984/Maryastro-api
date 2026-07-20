from __future__ import annotations

import html
import math
from collections import defaultdict
from typing import Any

GLIFOS_SIGNOS = ["♈", "♉", "♊", "♋", "♌", "♍", "♎", "♏", "♐", "♑", "♒", "♓"]

GLIFOS_CUERPOS = {
    "Sol": "☉", "Luna": "☽", "Mercurio": "☿", "Venus": "♀",
    "Marte": "♂", "Júpiter": "♃", "Saturno": "♄", "Urano": "♅",
    "Neptuno": "♆", "Plutón": "♇", "Quirón": "⚷",
    "Lilith media": "⚸", "Lilith verdadera": "⚸",
    "Nodo Norte medio": "☊", "Nodo Sur medio": "☋",
    "Ascendente": "AC", "Medio Cielo": "MC",
}

COLORES_SIGNOS = [
    "#d62828", "#3f7d20", "#d97706", "#1d4ed8",
    "#d62828", "#3f7d20", "#d97706", "#1d4ed8",
    "#d62828", "#8a5a16", "#0f8b8d", "#1d4ed8",
]

COLORES_ASPECTOS = {
    "Conjunción": "#6b7280", "Semisextil": "#8b5cf6",
    "Sextil": "#16a34a", "Cuadratura": "#ef4444",
    "Trígono": "#4f83ff", "Quincuncio": "#f59e0b",
    "Oposición": "#dc2626",
}

TRAZO_ASPECTOS = {
    "Conjunción": "", "Semisextil": "4 4", "Sextil": "",
    "Cuadratura": "", "Trígono": "", "Quincuncio": "7 5",
    "Oposición": "7 4",
}

CUERPOS_NO_DIBUJADOS = {"Ascendente", "Medio Cielo"}


def _punto_polar(cx: float, cy: float, radio: float, angulo_grados: float) -> tuple[float, float]:
    angulo = math.radians(angulo_grados)
    return cx + radio * math.cos(angulo), cy - radio * math.sin(angulo)


def _angulo_rueda(longitud: float, ascendente: float) -> float:
    """Coloca el Ascendente a la izquierda, con la orientación ya validada en Wix."""
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
    separacion_minima: float = 4.2,
) -> dict[str, float]:
    """Separa visualmente cuerpos próximos sin alterar sus longitudes reales."""
    grupos: dict[int, list[tuple[str, float]]] = defaultdict(list)

    for nombre, datos in posiciones.items():
        if nombre in CUERPOS_NO_DIBUJADOS:
            continue
        longitud = float(datos["longitud"]) % 360.0
        grupos[int(round(longitud / separacion_minima))].append((nombre, longitud))

    resultado: dict[str, float] = {}
    for cuerpos in grupos.values():
        cuerpos = sorted(cuerpos, key=lambda elemento: elemento[1])
        if len(cuerpos) == 1:
            nombre, longitud = cuerpos[0]
            resultado[nombre] = longitud
            continue

        centro_grupo = (len(cuerpos) - 1) / 2
        for indice, (nombre, longitud) in enumerate(cuerpos):
            desplazamiento = (indice - centro_grupo) * separacion_minima
            resultado[nombre] = (longitud + desplazamiento) % 360.0

    return resultado


def _agregar_escala_grados(
    partes: list[str],
    *,
    centro: float,
    radio_exterior: float,
    radio_escala_interior: float,
    ascendente: float,
) -> None:
    """Marca cada grado; cada 5° usa una línea roja más larga y gruesa."""
    for longitud in range(360):
        angulo = _angulo_rueda(float(longitud), ascendente)

        if longitud % 5 == 0:
            radio_inicio = radio_escala_interior
            color = "#ef4444"
            grosor = 1.9
        else:
            radio_inicio = radio_exterior - 8
            color = "#6b7280"
            grosor = 0.55

        x1, y1 = _punto_polar(centro, centro, radio_inicio, angulo)
        x2, y2 = _punto_polar(centro, centro, radio_exterior, angulo)
        partes.append(
            f'<line x1="{x1:.2f}" y1="{y1:.2f}" x2="{x2:.2f}" y2="{y2:.2f}" '
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
    """Dibuja una rueda astrológica SVG usando datos ya calculados."""
    if len(cuspides) != 12:
        raise ValueError("La rueda necesita exactamente 12 cúspides.")

    ascendente = float(
        angulos.get("Ascendente", {}).get("longitud", cuspides[0]["longitud"])
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
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {tamano} {tamano}" role="img" aria-label="{_escapar(titulo)}">',
        '<defs><style>'
        '.fondo{fill:#ffffff}.circulo{fill:none;stroke:#1f2937}.division-signo{stroke:#64748b}'
        '.casa{stroke:#9ca3af}.eje{stroke:#111827}'
        '.signo{font-family:"Segoe UI Symbol","Noto Sans Symbols",sans-serif;font-size:36px;font-weight:600;text-anchor:middle;dominant-baseline:middle}'
        '.planeta{font-family:"Segoe UI Symbol","Noto Sans Symbols",sans-serif;font-size:31px;text-anchor:middle;dominant-baseline:middle}'
        '.grado{font-family:Arial,sans-serif;font-size:11px;font-weight:600;text-anchor:middle;fill:#374151}'
        '.retro{fill:#1d4ed8}.casa-num{font-family:Arial,sans-serif;font-size:14px;text-anchor:middle;dominant-baseline:middle;fill:#6b7280}'
        '.angulo-etiqueta{font-family:Arial,sans-serif;font-size:14px;font-weight:700;fill:#111827}'
        '.angulo-grado{font-family:Arial,sans-serif;font-size:11px;font-weight:600;fill:#374151}'
        '.titulo{font-family:Arial,sans-serif;font-size:23px;font-weight:700;text-anchor:middle;fill:#111827}'
        '</style></defs>',
        f'<rect class="fondo" width="{tamano}" height="{tamano}"/>',
        f'<text class="titulo" x="{centro}" y="34">{_escapar(titulo)}</text>',
        f'<circle class="circulo" cx="{centro}" cy="{centro}" r="{radio_exterior}" stroke-width="1.8"/>',
        f'<circle class="circulo" cx="{centro}" cy="{centro}" r="{radio_zodiaco_exterior}" stroke-width="1.2"/>',
        f'<circle class="circulo" cx="{centro}" cy="{centro}" r="{radio_zodiaco_interior}" stroke-width="1.5"/>',
        f'<circle class="circulo" cx="{centro}" cy="{centro}" r="{radio_aspectos}" stroke-width="0.9"/>',
    ]

    _agregar_escala_grados(
        partes,
        centro=centro,
        radio_exterior=radio_exterior,
        radio_escala_interior=radio_escala_interior,
        ascendente=ascendente,
    )

    for indice in range(12):
        angulo_inicio = _angulo_rueda(indice * 30.0, ascendente)
        x1, y1 = _punto_polar(centro, centro, radio_zodiaco_interior, angulo_inicio)
        x2, y2 = _punto_polar(centro, centro, radio_zodiaco_exterior, angulo_inicio)
        partes.append(
            f'<line class="division-signo" x1="{x1:.2f}" y1="{y1:.2f}" '
            f'x2="{x2:.2f}" y2="{y2:.2f}" stroke-width="1"/>'
        )

        angulo_centro = _angulo_rueda(indice * 30.0 + 15.0, ascendente)
        radio_glifo = (radio_zodiaco_exterior + radio_zodiaco_interior) / 2
        xg, yg = _punto_polar(centro, centro, radio_glifo, angulo_centro)
        partes.append(
            f'<text class="signo" x="{xg:.2f}" y="{yg:.2f}" fill="{COLORES_SIGNOS[indice]}">'
            f'{GLIFOS_SIGNOS[indice]}</text>'
        )

    for cuspide in cuspides:
        numero = int(cuspide["casa"])
        longitud = float(cuspide["longitud"]) % 360.0
        angulo = _angulo_rueda(longitud, ascendente)
        x1, y1 = _punto_polar(centro, centro, radio_aspectos, angulo)
        x2, y2 = _punto_polar(centro, centro, radio_zodiaco_interior, angulo)
        es_eje = numero in {1, 4, 7, 10}
        partes.append(
            f'<line class="{"eje" if es_eje else "casa"}" x1="{x1:.2f}" y1="{y1:.2f}" '
            f'x2="{x2:.2f}" y2="{y2:.2f}" stroke-width="{2.0 if es_eje else 0.85}"/>'
        )

        siguiente = cuspides[numero % 12]
        lon_sig = float(siguiente["longitud"]) % 360.0
        arco = (lon_sig - longitud) % 360.0
        angulo_medio = _angulo_rueda((longitud + arco / 2.0) % 360.0, ascendente)
        xn, yn = _punto_polar(centro, centro, radio_numeros_casas, angulo_medio)
        partes.append(f'<text class="casa-num" x="{xn:.2f}" y="{yn:.2f}">{numero}</text>')

    abreviaturas = {
        "Ascendente": "AC", "Descendente": "DC",
        "Medio Cielo": "MC", "Fondo del Cielo": "IC",
    }
    for nombre, abreviatura in abreviaturas.items():
        datos = angulos.get(nombre)
        if not datos:
            continue

        longitud = float(datos["longitud"]) % 360.0
        angulo = _angulo_rueda(longitud, ascendente)
        xa, ya = _punto_polar(centro, centro, radio_exterior + 22, angulo)
        xg, yg = _punto_polar(centro, centro, radio_exterior + 39, angulo)
        ancla = "end" if xa < centro - 20 else "start" if xa > centro + 20 else "middle"
        partes.append(
            f'<text class="angulo-etiqueta" x="{xa:.2f}" y="{ya:.2f}" text-anchor="{ancla}">{abreviatura}</text>'
        )
        partes.append(
            f'<text class="angulo-grado" x="{xg:.2f}" y="{yg:.2f}" text-anchor="{ancla}">{_formato_angulo(longitud)}</text>'
        )

    for aspecto in aspectos:
        c1, c2 = aspecto.get("cuerpo1"), aspecto.get("cuerpo2")
        tipo = aspecto.get("aspecto", "")
        if c1 not in posiciones or c2 not in posiciones:
            continue

        a1 = _angulo_rueda(float(posiciones[c1]["longitud"]), ascendente)
        a2 = _angulo_rueda(float(posiciones[c2]["longitud"]), ascendente)
        x1, y1 = _punto_polar(centro, centro, radio_aspectos - 5, a1)
        x2, y2 = _punto_polar(centro, centro, radio_aspectos - 5, a2)
        color = COLORES_ASPECTOS.get(tipo, "#9ca3af")
        dash = TRAZO_ASPECTOS.get(tipo, "")
        dash_attr = f' stroke-dasharray="{dash}"' if dash else ""
        partes.append(
            f'<line x1="{x1:.2f}" y1="{y1:.2f}" x2="{x2:.2f}" y2="{y2:.2f}" '
            f'stroke="{color}" stroke-width="1.15" stroke-opacity="0.62"{dash_attr}/>'
        )

    posiciones_visuales = _ajustar_longitudes_visuales(posiciones)
    for nombre, longitud_visual in posiciones_visuales.items():
        datos = posiciones[nombre]
        longitud_real = float(datos["longitud"]) % 360.0
        angulo_visual = _angulo_rueda(longitud_visual, ascendente)
        angulo_real = _angulo_rueda(longitud_real, ascendente)
        diferencia = abs((longitud_visual - longitud_real + 180) % 360 - 180)

        if diferencia > 0.1:
            gx1, gy1 = _punto_polar(centro, centro, radio_aspectos, angulo_real)
            gx2, gy2 = _punto_polar(centro, centro, radio_planetas - 20, angulo_visual)
            partes.append(
                f'<line x1="{gx1:.2f}" y1="{gy1:.2f}" x2="{gx2:.2f}" y2="{gy2:.2f}" '
                f'stroke="#94a3b8" stroke-width="0.7"/>'
            )

        xp, yp = _punto_polar(centro, centro, radio_planetas, angulo_visual)
        glifo = GLIFOS_CUERPOS.get(nombre, nombre[:2])
        grado = _formato_grado(float(datos.get("grado_en_signo", 0.0)))
        retrogrado = bool(datos.get("retrogrado"))

        partes.append(
            f'<g><title>{_escapar(nombre)}: {_escapar(datos.get("signo", ""))} {grado}{" ℞" if retrogrado else ""}</title>'
            f'<text class="planeta" x="{xp:.2f}" y="{yp:.2f}">{_escapar(glifo)}</text></g>'
        )

        xgrado, ygrado = _punto_polar(centro, centro, radio_grados_planetas, angulo_visual)
        partes.append(f'<text class="grado" x="{xgrado:.2f}" y="{ygrado:.2f}">{grado}</text>')

        if retrogrado:
            xr, yr = _punto_polar(centro, centro, radio_grados_planetas - 13, angulo_visual)
            partes.append(f'<text class="grado retro" x="{xr:.2f}" y="{yr:.2f}">R</text>')

    partes.append("</svg>")
    return "".join(partes)


def generar_rueda_svg(resultado: dict[str, Any], *, tamano: int = 1000) -> str:
    """Adaptador para el diccionario producido por PerfilEnergetico."""
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
