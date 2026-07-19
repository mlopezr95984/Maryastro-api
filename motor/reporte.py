from __future__ import annotations

from typing import Any


# ==========================================================
# Utilidades
# ==========================================================

def grado(valor: float) -> str:
    """
    Convierte 18.6956 -> 18°41'
    """
    grados = int(valor)
    minutos = int(round((valor - grados) * 60))

    if minutos == 60:
        grados += 1
        minutos = 0

    return f"{grados:02d}°{minutos:02d}'"


def linea(titulo: str) -> str:
    ancho = 70
    return (
        "\n"
        + "═" * ancho
        + f"\n{titulo.center(ancho)}\n"
        + "═" * ancho
    )


def retrogrado(datos: dict) -> str:
    return " Rx" if datos.get("retrogrado") else ""


# ==========================================================
# Encabezado
# ==========================================================

def encabezado(resultado: dict) -> str:

    datos = resultado["datos"]

    return (
        linea("PERFIL ENERGÉTICO")
        + "\n\n"
        + f"Nombre : {datos['nombre']}\n"
        + f"Ciudad : {datos['ciudad']}\n"
        + f"Fecha  : {datos['fecha_local'][:10]}\n"
        + f"Hora   : {datos['fecha_local'][11:16]}\n"
        + f"Orbe   : {datos['orbe']}°"
    )


# ==========================================================
# Posiciones
# ==========================================================

def posiciones(resultado: dict) -> str:

    texto = linea("POSICIONES PLANETARIAS") + "\n\n"

    orden = [
        "Sol",
        "Luna",
        "Mercurio",
        "Venus",
        "Marte",
        "Júpiter",
        "Saturno",
        "Urano",
        "Neptuno",
        "Plutón",
        "Nodo Norte medio",
        "Nodo Sur medio",
        "Ascendente",
        "Medio Cielo",
    ]

    posiciones = resultado["posiciones"]

    for cuerpo in orden:

        if cuerpo not in posiciones:
            continue

        p = posiciones[cuerpo]

        texto += (
            f"{cuerpo:<18}"
            f"{grado(p['grado_en_signo'])} "
            f"{p['signo']:<10}"
            f"{retrogrado(p):<3}"
            f" Casa {p['casa']}\n"
        )

    return texto


# ==========================================================
# Ángulos
# ==========================================================

def angulos(resultado: dict) -> str:

    texto = linea("ÁNGULOS") + "\n\n"

    for nombre, datos in resultado["angulos"].items():

        texto += (
            f"{nombre:<20}"
            f"{grado(datos['grado_en_signo'])} "
            f"{datos['signo']}\n"
        )

    return texto


# ==========================================================
# Aspectos
# ==========================================================

def aspectos(resultado: dict) -> str:

    texto = linea("ASPECTOS") + "\n\n"

    for asp in resultado["aspectos"]:

        texto += (
            f"{asp['cuerpo1']:<12}"
            f"{asp['aspecto']:<12}"
            f"{asp['cuerpo2']:<12}"
            f"Orbe {asp['orbe']:.2f}°\n"
        )

    return texto


# ==========================================================
# Firma energética
# ==========================================================

def firma(resultado: dict) -> str:

    firma = resultado["arquetipo_dominante"]

    texto = linea("FIRMA ENERGÉTICA") + "\n\n"

    texto += f"Arquetipo : {firma['nombre_arquetipo']}\n"
    texto += f"Tipo      : {firma['tipo_firma']}\n"
    texto += (
        f"Elemento  : "
        + ", ".join(firma["elementos_dominantes"])
        + "\n"
    )

    texto += (
        f"Modalidad : "
        + ", ".join(firma["modalidades_dominantes"])
        + "\n"
    )

    return texto


# ==========================================================
# Subtipo
# ==========================================================

def subtipo(resultado: dict) -> str:

    sub = resultado["subtipo"]

    texto = linea("SUBTIPO") + "\n\n"

    texto += f"Dominante : {sub['nombre_subtipo']}\n\n"

    texto += (
        f"Angular     : {sub['conteo']['Angular']}\n"
    )

    texto += (
        f"Sucedente   : {sub['conteo']['Sucedente']}\n"
    )

    texto += (
        f"Cadente     : {sub['conteo']['Cadente']}\n"
    )

    return texto


# ==========================================================
# Dinámica Yin Yang
# ==========================================================

def dinamica(resultado: dict) -> str:

    d = resultado["dinamica_yin_yang"]

    texto = linea("DINÁMICA YIN • YANG") + "\n\n"

    texto += (
        f"Predominio : {d['predominio']}\n\n"
    )

    texto += (
        f"Yang : {d['porcentaje_yang']} %\n"
    )

    texto += (
        f"Yin  : {d['porcentaje_yin']} %\n"
    )

    return texto


# ==========================================================
# Nodo Norte
# ==========================================================

def eje_nodal(resultado: dict) -> str:

    eje = resultado["eje_nodal"]

    texto = linea("CAMINO EVOLUTIVO") + "\n\n"

    texto += eje["eje"]["recursos"] + "\n\n"

    texto += eje["eje"]["proposito"] + "\n\n"

    texto += eje["eje"]["energia_disponible"] + "\n\n"

    texto += eje["eje"]["reto_complementario"] + "\n\n"

    texto += eje["eje"]["integracion"]

    return texto


# ==========================================================
# Complementario
# ==========================================================

def complementario(resultado: dict) -> str:

    c = resultado["arquetipo_complementario"]

    texto = linea("ARQUETIPO COMPLEMENTARIO") + "\n\n"

    texto += f"Arquetipo : {c['nombre_arquetipo']}\n"

    texto += f"Subtipo   : {c['nombre_subtipo']}\n\n"

    texto += c["descripcion_energia"]

    return texto


# ==========================================================
# Reporte completo
# ==========================================================

def generar_reporte(resultado: dict) -> str:

    return "\n\n".join(
        [
            encabezado(resultado),
            posiciones(resultado),
            angulos(resultado),
            aspectos(resultado),
            firma(resultado),
            subtipo(resultado),
            dinamica(resultado),
            eje_nodal(resultado),
            complementario(resultado),
        ]
    )