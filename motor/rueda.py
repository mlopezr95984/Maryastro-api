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

COLORES_ASPECTOS = {
    "Conjunción": "#6b7280", "Semisextil": "#8b5cf6",
    "Sextil": "#16a34a", "Cuadratura": "#dc2626",
    "Trígono": "#2563eb", "Quincuncio": "#d97706",
    "Oposición": "#b91c1c",
}

TRAZO_ASPECTOS = {
    "Conjunción": "", "Semisextil": "4 4", "Sextil": "",
    "Cuadratura": "", "Trígono": "", "Quincuncio": "6 4",
    "Oposición": "",
}

CUERPOS_NO_DIBUJADOS = {"Ascendente", "Medio Cielo"}


def _punto_polar(cx: float, cy: float, radio: float, angulo_grados: float) -> tuple[float, float]:
    angulo = math.radians(angulo_grados)
    return cx + radio * math.cos(angulo), cy - radio * math.sin(angulo)


def _angulo_rueda(longitud: float, ascendente: float) -> float:
    """Coloca el Ascendente a la izquierda y el zodiaco en sentido horario."""
    return 180.0 - ((longitud - ascendente) % 360.0)


def _escapar(valor: Any) -> str:
    return html.escape(str(valor), quote=True)


def _formato_grado(grado_en_signo: float) -> str:
    grado = int(grado_en_signo)
    minuto = int(round((grado_en_signo - grado) * 60))
    if minuto == 60:
        grado += 1
        minuto = 0
    return f"{grado:02d}°{minuto:02d}′"


def _ajustar_longitudes_visuales(
    posiciones: dict[str, dict[str, Any]],
    separacion_minima: float = 4.0,
) -> dict[str, float]:
    """Separa visualmente cuerpos muy próximos sin alterar sus longitudes reales."""
    grupos: dict[int, list[tuple[str, float]]] = defaultdict(list)
    for nombre, datos in posiciones.items():
        if nombre in CUERPOS_NO_DIBUJADOS:
            continue
        longitud = float(datos["longitud"]) % 360.0
        grupos[int(round(longitud / separacion_minima))].append((nombre, longitud))

    resultado: dict[str, float] = {}
    for cuerpos in grupos.values():
        cuerpos = sorted(cuerpos, key=lambda item: item[1])
        if len(cuerpos) == 1:
            nombre, longitud = cuerpos[0]
            resultado[nombre] = longitud
            continue
        centro = (len(cuerpos) - 1) / 2
        for indice, (nombre, longitud) in enumerate(cuerpos):
            resultado[nombre] = (longitud + (indice - centro) * separacion_minima) % 360.0
    return resultado


def dibujar_rueda(
    posiciones: dict[str, dict[str, Any]],
    cuspides: list[dict[str, Any]],
    aspectos: list[dict[str, Any]],
    angulos: dict[str, dict[str, Any]],
    *,
    titulo: str = "Carta natal",
    tamano: int = 900,
) -> str:
    """Dibuja una rueda astrológica SVG usando datos ya calculados."""
    if len(cuspides) != 12:
        raise ValueError("La rueda necesita exactamente 12 cúspides.")

    ascendente = float(
        angulos.get("Ascendente", {}).get("longitud", cuspides[0]["longitud"])
    ) % 360.0

    centro = tamano / 2
    radio_exterior = tamano * 0.43
    radio_zodiaco_interno = tamano * 0.34
    radio_planetas = tamano * 0.285
    radio_aspectos = tamano * 0.225
    radio_numeros_casas = tamano * 0.19

    partes = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {tamano} {tamano}" role="img" aria-label="{_escapar(titulo)}">',
        '<defs><style>'
        '.fondo{fill:#fff}.circulo{fill:none;stroke:#374151}.division{stroke:#9ca3af}'
        '.casa{stroke:#9ca3af}.eje{stroke:#111827}'
        '.signo{font-family:"Segoe UI Symbol","Noto Sans Symbols",sans-serif;font-size:28px;text-anchor:middle;dominant-baseline:middle}'
        '.planeta{font-family:"Segoe UI Symbol","Noto Sans Symbols",sans-serif;font-size:24px;text-anchor:middle;dominant-baseline:middle}'
        '.grado{font-family:Arial,sans-serif;font-size:11px;text-anchor:middle;fill:#4b5563}'
        '.casa-num{font-family:Arial,sans-serif;font-size:14px;text-anchor:middle;dominant-baseline:middle;fill:#6b7280}'
        '.angulo-etiqueta{font-family:Arial,sans-serif;font-size:13px;font-weight:700;fill:#111827}'
        '.titulo{font-family:Arial,sans-serif;font-size:20px;font-weight:700;text-anchor:middle;fill:#111827}'
        '</style></defs>',
        f'<rect class="fondo" width="{tamano}" height="{tamano}"/>',
        f'<text class="titulo" x="{centro}" y="32">{_escapar(titulo)}</text>',
        f'<circle class="circulo" cx="{centro}" cy="{centro}" r="{radio_exterior}" stroke-width="2"/>',
        f'<circle class="circulo" cx="{centro}" cy="{centro}" r="{radio_zodiaco_interno}" stroke-width="1.5"/>',
        f'<circle class="circulo" cx="{centro}" cy="{centro}" r="{radio_aspectos}" stroke-width="1"/>',
    ]

    for indice in range(12):
        angulo_inicio = _angulo_rueda(indice * 30.0, ascendente)
        x1, y1 = _punto_polar(centro, centro, radio_zodiaco_interno, angulo_inicio)
        x2, y2 = _punto_polar(centro, centro, radio_exterior, angulo_inicio)
        partes.append(f'<line class="division" x1="{x1:.2f}" y1="{y1:.2f}" x2="{x2:.2f}" y2="{y2:.2f}" stroke-width="1"/>')

        angulo_centro = _angulo_rueda(indice * 30.0 + 15.0, ascendente)
        radio_glifo = (radio_exterior + radio_zodiaco_interno) / 2
        xg, yg = _punto_polar(centro, centro, radio_glifo, angulo_centro)
        partes.append(f'<text class="signo" x="{xg:.2f}" y="{yg:.2f}">{GLIFOS_SIGNOS[indice]}</text>')

    for cuspide in cuspides:
        numero = int(cuspide["casa"])
        longitud = float(cuspide["longitud"]) % 360.0
        angulo = _angulo_rueda(longitud, ascendente)
        x1, y1 = _punto_polar(centro, centro, radio_aspectos, angulo)
        x2, y2 = _punto_polar(centro, centro, radio_zodiaco_interno, angulo)
        clase = "eje" if numero in {1, 4, 7, 10} else "casa"
        grosor = 2.3 if numero in {1, 4, 7, 10} else 1.0
        partes.append(f'<line class="{clase}" x1="{x1:.2f}" y1="{y1:.2f}" x2="{x2:.2f}" y2="{y2:.2f}" stroke-width="{grosor}"/>')

        siguiente = cuspides[numero % 12]
        lon_sig = float(siguiente["longitud"]) % 360.0
        arco = (lon_sig - longitud) % 360.0
        angulo_medio = _angulo_rueda((longitud + arco / 2.0) % 360.0, ascendente)
        xn, yn = _punto_polar(centro, centro, radio_numeros_casas, angulo_medio)
        partes.append(f'<text class="casa-num" x="{xn:.2f}" y="{yn:.2f}">{numero}</text>')

    abreviaturas = {"Ascendente": "AC", "Descendente": "DC", "Medio Cielo": "MC", "Fondo del Cielo": "IC"}
    for nombre, abreviatura in abreviaturas.items():
        datos = angulos.get(nombre)
        if not datos:
            continue
        angulo = _angulo_rueda(float(datos["longitud"]), ascendente)
        xa, ya = _punto_polar(centro, centro, radio_exterior + 18, angulo)
        ancla = "end" if xa < centro - 20 else "start" if xa > centro + 20 else "middle"
        partes.append(f'<text class="angulo-etiqueta" x="{xa:.2f}" y="{ya:.2f}" text-anchor="{ancla}">{abreviatura}</text>')

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
        partes.append(f'<line x1="{x1:.2f}" y1="{y1:.2f}" x2="{x2:.2f}" y2="{y2:.2f}" stroke="{color}" stroke-width="1.25" stroke-opacity="0.72"{dash_attr}/>')

    posiciones_visuales = _ajustar_longitudes_visuales(posiciones)
    for nombre, longitud_visual in posiciones_visuales.items():
        datos = posiciones[nombre]
        longitud_real = float(datos["longitud"]) % 360.0
        angulo_visual = _angulo_rueda(longitud_visual, ascendente)
        angulo_real = _angulo_rueda(longitud_real, ascendente)

        diferencia = abs((longitud_visual - longitud_real + 180) % 360 - 180)
        if diferencia > 0.1:
            gx1, gy1 = _punto_polar(centro, centro, radio_aspectos, angulo_real)
            gx2, gy2 = _punto_polar(centro, centro, radio_planetas - 18, angulo_visual)
            partes.append(f'<line x1="{gx1:.2f}" y1="{gy1:.2f}" x2="{gx2:.2f}" y2="{gy2:.2f}" stroke="#9ca3af" stroke-width="0.8"/>')

        xp, yp = _punto_polar(centro, centro, radio_planetas, angulo_visual)
        glifo = GLIFOS_CUERPOS.get(nombre, nombre[:2])
        grado = _formato_grado(float(datos.get("grado_en_signo", 0.0)))
        retrogrado = " ℞" if datos.get("retrogrado") else ""
        partes.append(
            f'<g><title>{_escapar(nombre)}: {_escapar(datos.get("signo", ""))} {grado}{retrogrado}</title>'
            f'<text class="planeta" x="{xp:.2f}" y="{yp:.2f}">{_escapar(glifo)}</text></g>'
        )
        xg, yg = _punto_polar(centro, centro, radio_planetas - 25, angulo_visual)
        partes.append(f'<text class="grado" x="{xg:.2f}" y="{yg:.2f}">{grado}{retrogrado}</text>')

    partes.append("</svg>")
    return "".join(partes)


def generar_rueda_svg(resultado: dict[str, Any], *, tamano: int = 900) -> str:
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
