from __future__ import annotations

from datetime import datetime
from typing import Any, Iterable, Mapping


# ==========================================================
# Configuración visual
# ==========================================================

ANCHO_REPORTE = 62
ANCHO_BARRA = 22

SIMBOLOS_SIGNOS = {
    "Aries": "♈",
    "Tauro": "♉",
    "Géminis": "♊",
    "Geminis": "♊",
    "Cáncer": "♋",
    "Cancer": "♋",
    "Leo": "♌",
    "Virgo": "♍",
    "Libra": "♎",
    "Escorpio": "♏",
    "Sagitario": "♐",
    "Capricornio": "♑",
    "Acuario": "♒",
    "Piscis": "♓",
}

ORDEN_ELEMENTOS = ["Fuego", "Tierra", "Aire", "Agua"]
ORDEN_MODALIDADES = ["Cardinal", "Fija", "Mutable"]
ORDEN_SIGNOS = [
    "Aries",
    "Tauro",
    "Géminis",
    "Cáncer",
    "Leo",
    "Virgo",
    "Libra",
    "Escorpio",
    "Sagitario",
    "Capricornio",
    "Acuario",
    "Piscis",
]

ORDEN_POSICIONES = [
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
    "Quirón",
    "Lilith media",
    "Nodo Norte medio",
    "Nodo Sur medio",
    "Ascendente",
    "Medio Cielo",
]


# ==========================================================
# Utilidades generales
# ==========================================================

def grado(valor: float | int | str | None) -> str:
    """Convierte un valor decimal, por ejemplo 18.6956, en 18°42'."""
    try:
        numero = float(valor)
    except (TypeError, ValueError):
        return "—"

    grados = int(numero)
    minutos = int(round((numero - grados) * 60))

    if minutos == 60:
        grados += 1
        minutos = 0

    return f"{grados:02d}°{minutos:02d}'"


def numero_romano(numero: Any) -> str:
    try:
        valor = int(numero)
    except (TypeError, ValueError):
        return str(numero) if numero not in (None, "") else "—"

    romanos = {
        1: "I",
        2: "II",
        3: "III",
        4: "IV",
        5: "V",
        6: "VI",
        7: "VII",
        8: "VIII",
        9: "IX",
        10: "X",
        11: "XI",
        12: "XII",
    }
    return romanos.get(valor, str(valor))


def retrogrado(datos: Mapping[str, Any]) -> str:
    return " ℞" if datos.get("retrogrado") else ""


def separador(caracter: str = "─") -> str:
    return caracter * ANCHO_REPORTE


def titulo_seccion(titulo: str) -> str:
    return f"{separador()}\n{titulo.upper()}\n{separador()}"


def texto_no_vacio(valor: Any) -> str:
    return str(valor).strip() if valor not in (None, "") else ""


def agregar_parrafos(destino: list[str], valores: Iterable[Any]) -> None:
    for valor in valores:
        texto = texto_no_vacio(valor)
        if texto:
            destino.append(texto)


def primer_valor(diccionario: Mapping[str, Any], claves: Iterable[str], defecto: Any = "") -> Any:
    for clave in claves:
        if clave in diccionario and diccionario[clave] not in (None, "", [], {}):
            return diccionario[clave]
    return defecto


def normalizar_mapeo(valor: Any) -> dict[str, float]:
    if not isinstance(valor, Mapping):
        return {}

    salida: dict[str, float] = {}
    for clave, cantidad in valor.items():
        try:
            salida[str(clave)] = float(cantidad)
        except (TypeError, ValueError):
            continue
    return salida


def porcentajes_desde_valores(valores: Mapping[str, float]) -> dict[str, float]:
    if not valores:
        return {}

    total = sum(max(0.0, float(v)) for v in valores.values())
    if total <= 0:
        return {str(k): 0.0 for k in valores}

    # Si los valores ya parecen porcentajes, se conservan.
    if 99.0 <= total <= 101.0:
        return {str(k): round(float(v), 2) for k, v in valores.items()}

    return {
        str(k): round((max(0.0, float(v)) / total) * 100, 2)
        for k, v in valores.items()
    }


def obtener_distribucion(
    fuente: Mapping[str, Any],
    posibles_claves: Iterable[str],
) -> dict[str, float]:
    for clave in posibles_claves:
        valor = fuente.get(clave)
        mapeo = normalizar_mapeo(valor)
        if mapeo:
            return porcentajes_desde_valores(mapeo)
    return {}


def ordenar_distribucion(
    distribucion: Mapping[str, float],
    orden_preferido: Iterable[str],
) -> list[tuple[str, float]]:
    encontrados: list[tuple[str, float]] = []
    usados: set[str] = set()

    for nombre in orden_preferido:
        if nombre in distribucion:
            encontrados.append((nombre, float(distribucion[nombre])))
            usados.add(nombre)

    restantes = [
        (nombre, float(valor))
        for nombre, valor in distribucion.items()
        if nombre not in usados
    ]
    restantes.sort(key=lambda item: item[1], reverse=True)
    return encontrados + restantes


def barra_texto(etiqueta: str, porcentaje: float, ancho_etiqueta: int = 12) -> str:
    valor = max(0.0, min(100.0, float(porcentaje)))
    llenos = round((valor / 100) * ANCHO_BARRA)
    barra = "█" * llenos + "░" * (ANCHO_BARRA - llenos)
    return f"{etiqueta:<{ancho_etiqueta}} {barra} {valor:6.2f} %"


def bloque_barras(
    titulo: str,
    distribucion: Mapping[str, float],
    orden: Iterable[str],
    *,
    mostrar_ceros: bool = True,
) -> str:
    if not distribucion:
        return ""

    lineas = [titulo.upper()]
    for etiqueta, porcentaje in ordenar_distribucion(distribucion, orden):
        if not mostrar_ceros and porcentaje <= 0:
            continue
        lineas.append(barra_texto(etiqueta, porcentaje))
    return "\n".join(lineas)


def formatear_fecha(fecha_iso: str) -> tuple[str, str]:
    if not fecha_iso:
        return "—", "—"

    try:
        fecha = datetime.fromisoformat(fecha_iso.replace("Z", "+00:00"))
        return fecha.strftime("%d/%m/%Y"), fecha.strftime("%H:%M")
    except ValueError:
        fecha = fecha_iso[:10] or "—"
        hora = fecha_iso[11:16] if len(fecha_iso) >= 16 else "—"
        return fecha, hora


# ==========================================================
# Portada y resumen visual
# ==========================================================

def portada(resultado: Mapping[str, Any]) -> str:
    firma = resultado.get("arquetipo_dominante", {})
    subtipo = resultado.get("subtipo", {})
    datos = resultado.get("datos", {})

    arquetipo = texto_no_vacio(
        primer_valor(
            firma,
            ["nombre_arquetipo", "arquetipo", "resultado"],
            "Arquetipo no disponible",
        )
    )
    nombre_subtipo = texto_no_vacio(
        primer_valor(
            subtipo,
            ["nombre_subtipo", "subtipo", "dominante"],
            "",
        )
    )

    simbolo = SIMBOLOS_SIGNOS.get(arquetipo, "")
    nombre_persona = texto_no_vacio(datos.get("nombre"))

    lineas = [
        "═" * ANCHO_REPORTE,
        "PERFIL ENERGÉTICO".center(ANCHO_REPORTE),
        "",
        f"{simbolo} {arquetipo}".strip().center(ANCHO_REPORTE),
    ]

    if nombre_subtipo:
        lineas.append(nombre_subtipo.center(ANCHO_REPORTE))

    if nombre_persona:
        lineas.extend(["", nombre_persona.center(ANCHO_REPORTE)])

    lineas.append("═" * ANCHO_REPORTE)
    return "\n".join(lineas)


def resumen_visual(resultado: Mapping[str, Any]) -> str:
    firma = resultado.get("arquetipo_dominante", {})
    dinamica = resultado.get("dinamica_yin_yang", {})
    subtipo = resultado.get("subtipo", {})

    elementos = obtener_distribucion(
        firma,
        [
            "porcentajes_elementos",
            "porcentaje_elementos",
            "distribucion_elementos",
            "conteo_elementos",
            "elementos",
        ],
    )

    modalidades = obtener_distribucion(
        firma,
        [
            "porcentajes_modalidades",
            "porcentaje_modalidades",
            "distribucion_modalidades",
            "conteo_modalidades",
            "modalidades",
        ],
    )

    signos = obtener_distribucion(
        firma,
        [
            "porcentajes_signos",
            "porcentaje_signos",
            "distribucion_signos",
            "conteo_signos",
            "signos",
        ],
    )

    yin_yang = {
        "Yang": float(dinamica.get("porcentaje_yang", 0) or 0),
        "Yin": float(dinamica.get("porcentaje_yin", 0) or 0),
    }

    conteo_subtipo = normalizar_mapeo(subtipo.get("conteo", {}))
    distribucion_subtipo = porcentajes_desde_valores(conteo_subtipo)

    bloques = [titulo_seccion("Mapa energético")]

    for bloque in [
        bloque_barras("Elementos", elementos, ORDEN_ELEMENTOS),
        bloque_barras("Modalidades", modalidades, ORDEN_MODALIDADES),
        bloque_barras("Signos", signos, ORDEN_SIGNOS, mostrar_ceros=False),
        bloque_barras("Yin • Yang", yin_yang, ["Yang", "Yin"]),
        bloque_barras(
            "Distribución por casas",
            distribucion_subtipo,
            ["Angular", "Sucedente", "Cadente"],
        ),
    ]:
        if bloque:
            bloques.extend(["", bloque])

    return "\n".join(bloques)


# ==========================================================
# Lectura interpretativa
# ==========================================================

def subtipo_energetico(resultado: Mapping[str, Any]) -> str:
    sub = resultado.get("subtipo", {})
    nombre = texto_no_vacio(
        primer_valor(sub, ["nombre_subtipo", "subtipo", "dominante"])
    )

    lineas = [titulo_seccion("Subtipo energético")]
    if nombre:
        lineas.extend(["", nombre.upper()])

    agregar_parrafos(
        lineas,
        [
            primer_valor(sub, ["descripcion", "interpretacion", "texto"]),
            primer_valor(sub, ["fortaleza", "talento"]),
            primer_valor(sub, ["reto", "desafio"]),
        ],
    )

    return "\n\n".join(lineas[:2]) + (
        ("\n\n" + "\n\n".join(lineas[2:])) if len(lineas) > 2 else ""
    )


def dinamica_interpretativa(resultado: Mapping[str, Any]) -> str:
    d = resultado.get("dinamica_yin_yang", {})

    lineas = [titulo_seccion("Dinámica Yin • Yang")]

    predominio = texto_no_vacio(d.get("predominio"))
    if predominio:
        lineas.extend(["", f"Predominio: {predominio}"])

    # Se incorporan textos interpretativos solo si el motor los entrega.
    agregar_parrafos(
        lineas,
        [
            primer_valor(d, ["descripcion", "interpretacion", "lectura"]),
            primer_valor(d, ["integracion", "síntesis", "sintesis"]),
        ],
    )

    return "\n\n".join(lineas[:2]) + (
        ("\n\n" + "\n\n".join(lineas[2:])) if len(lineas) > 2 else ""
    )


def eje_nodal(resultado: Mapping[str, Any]) -> str:
    contenedor = resultado.get("eje_nodal", {})
    eje = contenedor.get("eje", contenedor)

    lineas = [titulo_seccion("Camino evolutivo")]

    agregar_parrafos(
        lineas,
        [
            eje.get("recursos"),
            eje.get("proposito"),
            eje.get("energia_disponible"),
            eje.get("reto_complementario"),
            eje.get("integracion"),
        ],
    )

    aliados = primer_valor(
        contenedor,
        ["aliados_nodales", "aliados", "planetas_aliados"],
        [],
    )
    if isinstance(aliados, Mapping):
        aliados = list(aliados.values())

    if isinstance(aliados, (list, tuple)) and aliados:
        lineas.extend(["", "ALIADOS NODALES"])
        for aliado in aliados:
            if isinstance(aliado, Mapping):
                nombre = primer_valor(
                    aliado,
                    ["nombre", "planeta", "cuerpo", "titulo"],
                    "Aliado",
                )
                descripcion = primer_valor(
                    aliado,
                    ["descripcion", "interpretacion", "texto"],
                    "",
                )
                texto = f"• {nombre}"
                if descripcion:
                    texto += f": {descripcion}"
                lineas.append(texto)
            else:
                lineas.append(f"• {aliado}")

    return "\n\n".join(lineas[:1]) + (
        ("\n\n" + "\n\n".join(lineas[1:])) if len(lineas) > 1 else ""
    )


def complementario(resultado: Mapping[str, Any]) -> str:
    c = resultado.get("arquetipo_complementario", {})

    arquetipo = texto_no_vacio(
        primer_valor(c, ["nombre_arquetipo", "arquetipo"])
    )
    subtipo = texto_no_vacio(
        primer_valor(c, ["nombre_subtipo", "subtipo"])
    )

    resultado_nombre = " ".join(parte for parte in [arquetipo, subtipo] if parte)

    lineas = [titulo_seccion("Arquetipo complementario")]
    if resultado_nombre:
        simbolo = SIMBOLOS_SIGNOS.get(arquetipo, "")
        lineas.extend(["", f"{simbolo} {resultado_nombre}".strip().upper()])

    agregar_parrafos(
        lineas,
        [
            primer_valor(
                c,
                ["descripcion_energia", "descripcion", "interpretacion"],
            ),
            primer_valor(c, ["aporte", "funcion", "propósito", "proposito"]),
            primer_valor(c, ["reto", "integracion"]),
        ],
    )

    return "\n\n".join(lineas[:2]) + (
        ("\n\n" + "\n\n".join(lineas[2:])) if len(lineas) > 2 else ""
    )


def puentes_energeticos(resultado: Mapping[str, Any]) -> str:
    eje = resultado.get("eje_nodal", {})
    complementario = resultado.get("arquetipo_complementario", {})

    puentes = primer_valor(
        eje,
        ["puentes_energeticos", "puentes", "aspectos_puente"],
        None,
    )
    if not puentes:
        puentes = primer_valor(
            complementario,
            ["puentes_energeticos", "puentes", "aspectos_puente"],
            None,
        )
    if not puentes:
        puentes = resultado.get("puentes_energeticos")

    if not puentes:
        return ""

    lineas = [titulo_seccion("Puentes energéticos")]

    if isinstance(puentes, Mapping):
        puentes = list(puentes.values())

    if isinstance(puentes, (list, tuple)):
        for puente in puentes:
            if isinstance(puente, Mapping):
                titulo = primer_valor(
                    puente,
                    ["titulo", "nombre", "planeta", "aspecto"],
                    "Puente",
                )
                descripcion = primer_valor(
                    puente,
                    ["descripcion", "interpretacion", "texto"],
                    "",
                )
                texto = f"• {titulo}"
                if descripcion:
                    texto += f": {descripcion}"
                lineas.append(texto)
            else:
                lineas.append(f"• {puente}")
    else:
        lineas.append(str(puentes))

    return "\n\n".join(lineas[:1]) + (
        ("\n\n" + "\n\n".join(lineas[1:])) if len(lineas) > 1 else ""
    )


# ==========================================================
# Información técnica
# ==========================================================

def datos_tecnicos(resultado: Mapping[str, Any]) -> str:
    datos = resultado.get("datos", {})
    fecha, hora = formatear_fecha(texto_no_vacio(datos.get("fecha_local")))

    lineas = [
        titulo_seccion("Datos del cálculo"),
        "",
        f"Nombre      : {datos.get('nombre', '—')}",
        f"Ciudad      : {datos.get('ciudad', '—')}",
        f"Fecha       : {fecha}",
        f"Hora local  : {hora}",
        f"Orbe        : {datos.get('orbe', '—')}°",
    ]

    campos_opcionales = [
        ("Latitud", ["latitud", "latitude"]),
        ("Longitud", ["longitud", "longitude"]),
        ("Zona horaria", ["zona_horaria", "timezone", "tz"]),
    ]

    for etiqueta, claves in campos_opcionales:
        valor = primer_valor(datos, claves, "")
        if valor not in ("", None):
            lineas.append(f"{etiqueta:<12}: {valor}")

    return "\n".join(lineas)


def angulos(resultado: Mapping[str, Any]) -> str:
    datos_angulos = resultado.get("angulos", {})
    if not datos_angulos:
        return ""

    lineas = [titulo_seccion("Ángulos"), ""]

    orden = ["Ascendente", "Medio Cielo", "Descendente", "Fondo del Cielo"]
    nombres = [n for n in orden if n in datos_angulos]
    nombres += [n for n in datos_angulos if n not in nombres]

    for nombre in nombres:
        datos = datos_angulos[nombre]
        lineas.append(
            f"{nombre:<21}"
            f"{grado(datos.get('grado_en_signo'))} "
            f"{datos.get('signo', '')}"
        )

    return "\n".join(lineas)


def cuspides(resultado: Mapping[str, Any]) -> str:
    datos_cuspides = resultado.get("cuspides", {})
    if not datos_cuspides:
        return ""

    lineas = [titulo_seccion("Cúspides de las casas"), ""]

    if isinstance(datos_cuspides, Mapping):
        elementos = list(datos_cuspides.items())
    elif isinstance(datos_cuspides, (list, tuple)):
        elementos = list(enumerate(datos_cuspides, start=1))
    else:
        return ""

    def clave_orden(item: tuple[Any, Any]) -> int:
        try:
            return int(item[0])
        except (TypeError, ValueError):
            return 99

    for casa, datos in sorted(elementos, key=clave_orden):
        if not isinstance(datos, Mapping):
            continue
        numero = datos.get("casa", casa)
        lineas.append(
            f"Casa {numero_romano(numero):<5}"
            f"{grado(datos.get('grado_en_signo'))} "
            f"{datos.get('signo', '')}"
        )

    return "\n".join(lineas)


def posiciones(resultado: Mapping[str, Any]) -> str:
    posiciones_resultado = resultado.get("posiciones", {})
    if not posiciones_resultado:
        return ""

    lineas = [titulo_seccion("Planetas y puntos"), ""]

    orden = [c for c in ORDEN_POSICIONES if c in posiciones_resultado]
    orden += [c for c in posiciones_resultado if c not in orden]

    for cuerpo in orden:
        p = posiciones_resultado[cuerpo]
        if not isinstance(p, Mapping):
            continue

        casa = p.get("casa")
        casa_texto = (
            f"Casa {numero_romano(casa)}"
            if casa not in (None, "")
            else ""
        )

        lineas.append(
            f"{cuerpo + retrogrado(p):<20}"
            f"{grado(p.get('grado_en_signo'))} "
            f"{p.get('signo', ''):<11}"
            f"{casa_texto}"
        )

    return "\n".join(lineas)


def aspectos(resultado: Mapping[str, Any]) -> str:
    aspectos_resultado = resultado.get("aspectos", [])
    if not aspectos_resultado:
        return ""

    lineas = [titulo_seccion("Aspectos básicos"), ""]

    for asp in aspectos_resultado:
        if not isinstance(asp, Mapping):
            continue

        polaridad = primer_valor(
            asp,
            ["polaridad", "energia", "yin_yang", "tipo_energia"],
            "",
        )
        sufijo = f" · {polaridad}" if polaridad else ""

        try:
            orbe = f"{float(asp.get('orbe', 0)):.2f}°"
        except (TypeError, ValueError):
            orbe = str(asp.get("orbe", "—"))

        lineas.append(
            f"{asp.get('cuerpo1', ''):<13}"
            f"{asp.get('aspecto', ''):<14}"
            f"{asp.get('cuerpo2', ''):<13}"
            f"Orbe {orbe}{sufijo}"
        )

    return "\n".join(lineas)


# ==========================================================
# Reporte completo
# ==========================================================

def generar_reporte(resultado: dict[str, Any]) -> str:
    """
    Genera el reporte en texto plano que Wix muestra al usuario.

    El orden de lectura es:
    1. Resultado principal.
    2. Resumen visual.
    3. Interpretación.
    4. Información técnica.
    """
    secciones = [
        portada(resultado),
        resumen_visual(resultado),
        subtipo_energetico(resultado),
        dinamica_interpretativa(resultado),
        eje_nodal(resultado),
        complementario(resultado),
        puentes_energeticos(resultado),
        datos_tecnicos(resultado),
        angulos(resultado),
        cuspides(resultado),
        posiciones(resultado),
        aspectos(resultado),
    ]

    return "\n\n".join(
        seccion.strip()
        for seccion in secciones
        if seccion and seccion.strip()
    )
