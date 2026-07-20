from __future__ import annotations

from typing import Any, Iterable, Mapping


# ==========================================================
# Configuración metodológica
# ==========================================================

ELEMENTOS_POR_SIGNO = {
    "Aries": "Fuego",
    "Leo": "Fuego",
    "Sagitario": "Fuego",
    "Tauro": "Tierra",
    "Virgo": "Tierra",
    "Capricornio": "Tierra",
    "Géminis": "Aire",
    "Geminis": "Aire",
    "Libra": "Aire",
    "Acuario": "Aire",
    "Cáncer": "Agua",
    "Cancer": "Agua",
    "Escorpio": "Agua",
    "Piscis": "Agua",
}

MODALIDADES_POR_SIGNO = {
    "Aries": "Cardinal",
    "Cáncer": "Cardinal",
    "Cancer": "Cardinal",
    "Libra": "Cardinal",
    "Capricornio": "Cardinal",
    "Tauro": "Fija",
    "Leo": "Fija",
    "Escorpio": "Fija",
    "Acuario": "Fija",
    "Géminis": "Mutable",
    "Geminis": "Mutable",
    "Virgo": "Mutable",
    "Sagitario": "Mutable",
    "Piscis": "Mutable",
}

CASAS_POR_SUBTIPO = {
    "Iniciador": {1, 4, 7, 10},
    "Sostenedor": {2, 5, 8, 11},
    "Transformador": {3, 6, 9, 12},
}

MODALIDAD_TECNICA_POR_SUBTIPO = {
    "Iniciador": "Angular",
    "Sostenedor": "Sucedente",
    "Transformador": "Cadente",
}

CUERPOS_PERMITIDOS = [
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
    "Lilith media",
]

MENSAJE_APOYO_EXTERNO = (
    "La carta no muestra un puente interno suficiente hacia esta cualidad. "
    "Su desarrollo puede apoyarse en el entorno mediante personas que la encarnen, "
    "grupos, redes sociales, terapia, mentoría, hábitos, sistemas de organización, "
    "rutinas o experiencias que permitan incorporarla de manera consciente."
)


# ==========================================================
# Utilidades
# ==========================================================

def _texto(valor: Any) -> str:
    return str(valor).strip() if valor not in (None, "") else ""


def _entero(valor: Any) -> int | None:
    try:
        return int(valor)
    except (TypeError, ValueError):
        return None


def _primer_valor(
    diccionario: Mapping[str, Any],
    claves: Iterable[str],
    defecto: Any = "",
) -> Any:
    for clave in claves:
        if clave in diccionario and diccionario[clave] not in (None, "", [], {}):
            return diccionario[clave]
    return defecto


def _normalizar_nombre(nombre: str) -> str:
    equivalencias = {
        "Geminis": "Géminis",
        "Cancer": "Cáncer",
        "Jupiter": "Júpiter",
        "Pluton": "Plutón",
        "Lilit media": "Lilith media",
        "Lilith": "Lilith media",
    }
    return equivalencias.get(nombre, nombre)


def _obtener_posiciones_validas(
    posiciones: Mapping[str, Any],
    cuerpos_permitidos: Iterable[str],
) -> list[dict[str, Any]]:
    permitidos = {_normalizar_nombre(cuerpo) for cuerpo in cuerpos_permitidos}
    salida: list[dict[str, Any]] = []

    for cuerpo, datos in posiciones.items():
        cuerpo_normalizado = _normalizar_nombre(str(cuerpo))

        if cuerpo_normalizado not in permitidos:
            continue

        if not isinstance(datos, Mapping):
            continue

        signo = _normalizar_nombre(_texto(datos.get("signo")))
        casa = _entero(datos.get("casa"))

        if not signo:
            continue

        salida.append(
            {
                "cuerpo": cuerpo_normalizado,
                "signo": signo,
                "casa": casa,
                "retrogrado": bool(datos.get("retrogrado")),
                "grado_en_signo": datos.get("grado_en_signo"),
            }
        )

    return salida


def _crear_puente(
    posicion: Mapping[str, Any],
    tipo: str,
    cualidad: str,
) -> dict[str, Any]:
    return {
        "tipo": tipo,
        "cualidad": cualidad,
        "cuerpo": posicion["cuerpo"],
        "signo": posicion["signo"],
        "casa": posicion.get("casa"),
        "retrogrado": posicion.get("retrogrado", False),
        "grado_en_signo": posicion.get("grado_en_signo"),
    }


def _resultado_categoria(
    *,
    tipo: str,
    nombre: str,
    representantes: int | None,
    puentes: list[dict[str, Any]],
    modalidad_tecnica: str | None = None,
) -> dict[str, Any]:
    resultado = {
        "tipo": tipo,
        "nombre": nombre,
        "representantes": representantes,
        "puentes": puentes,
        "requiere_apoyo_externo": len(puentes) == 0,
        "mensaje_apoyo_externo": MENSAJE_APOYO_EXTERNO if not puentes else "",
    }

    if modalidad_tecnica:
        resultado["modalidad_tecnica"] = modalidad_tecnica

    return resultado


# ==========================================================
# Identificación del arquetipo complementario
# ==========================================================

def _obtener_elemento_complementario(
    arquetipo_complementario: Mapping[str, Any],
) -> str:
    return _normalizar_nombre(
        _texto(
            _primer_valor(
                arquetipo_complementario,
                [
                    "elemento_complementario",
                    "elemento_menos_representado",
                    "elemento",
                ],
            )
        )
    )


def _obtener_modalidad_complementaria(
    arquetipo_complementario: Mapping[str, Any],
) -> str:
    return _normalizar_nombre(
        _texto(
            _primer_valor(
                arquetipo_complementario,
                [
                    "modalidad_complementaria",
                    "modalidad_signo_complementaria",
                    "modalidad_menos_representada",
                    "modalidad",
                ],
            )
        )
    )


def _obtener_subtipo_complementario(
    arquetipo_complementario: Mapping[str, Any],
) -> str:
    return _normalizar_nombre(
        _texto(
            _primer_valor(
                arquetipo_complementario,
                [
                    "nombre_subtipo",
                    "subtipo_complementario",
                    "modalidad_casa_complementaria",
                    "subtipo",
                ],
            )
        )
    )


def _obtener_representantes(
    arquetipo_complementario: Mapping[str, Any],
    claves: Iterable[str],
) -> int | None:
    valor = _primer_valor(arquetipo_complementario, claves, None)
    return _entero(valor)


# ==========================================================
# Búsqueda de puentes
# ==========================================================

def buscar_puentes_elemento(
    posiciones: list[dict[str, Any]],
    elemento: str,
) -> list[dict[str, Any]]:
    if not elemento:
        return []

    puentes: list[dict[str, Any]] = []

    for posicion in posiciones:
        signo = posicion["signo"]
        if ELEMENTOS_POR_SIGNO.get(signo) == elemento:
            puentes.append(
                _crear_puente(
                    posicion,
                    tipo="elemento",
                    cualidad=elemento,
                )
            )

    return puentes


def buscar_puentes_modalidad_signo(
    posiciones: list[dict[str, Any]],
    modalidad: str,
) -> list[dict[str, Any]]:
    if not modalidad:
        return []

    puentes: list[dict[str, Any]] = []

    for posicion in posiciones:
        signo = posicion["signo"]
        if MODALIDADES_POR_SIGNO.get(signo) == modalidad:
            puentes.append(
                _crear_puente(
                    posicion,
                    tipo="modalidad_signo",
                    cualidad=modalidad,
                )
            )

    return puentes


def buscar_puentes_subtipo(
    posiciones: list[dict[str, Any]],
    subtipo: str,
) -> list[dict[str, Any]]:
    casas_objetivo = CASAS_POR_SUBTIPO.get(subtipo, set())
    if not casas_objetivo:
        return []

    puentes: list[dict[str, Any]] = []

    for posicion in posiciones:
        casa = posicion.get("casa")
        if casa in casas_objetivo:
            puentes.append(
                _crear_puente(
                    posicion,
                    tipo="subtipo",
                    cualidad=subtipo,
                )
            )

    return puentes


# ==========================================================
# Función principal
# ==========================================================

def calcular_puentes_energeticos(
    posiciones: Mapping[str, Any],
    arquetipo_complementario: Mapping[str, Any],
    *,
    cuerpos_permitidos: Iterable[str] = CUERPOS_PERMITIDOS,
) -> dict[str, Any]:
    """
    Identifica los recursos internos de la carta que facilitan el desarrollo
    del arquetipo complementario.

    Reglas:
    - Elemento complementario:
      busca planetas en signos de ese elemento.
    - Modalidad complementaria por signo:
      busca planetas en signos de esa modalidad.
    - Subtipo complementario:
      busca planetas en casas angulares, sucedentes o cadentes según corresponda.
    - Ascendente, Medio Cielo y nodos no se consideran puentes.
    - Cuando no hay puentes internos, se recomienda apoyo externo.

    El módulo asume que `arquetipo_complementario` ya fue calculado por el motor.
    """
    posiciones_validas = _obtener_posiciones_validas(
        posiciones,
        cuerpos_permitidos,
    )

    elemento = _obtener_elemento_complementario(arquetipo_complementario)
    modalidad = _obtener_modalidad_complementaria(arquetipo_complementario)
    subtipo = _obtener_subtipo_complementario(arquetipo_complementario)

    representantes_elemento = _obtener_representantes(
        arquetipo_complementario,
        [
            "representantes_elemento",
            "conteo_elemento_complementario",
            "cantidad_elemento",
        ],
    )
    representantes_modalidad = _obtener_representantes(
        arquetipo_complementario,
        [
            "representantes_modalidad_signo",
            "conteo_modalidad_complementaria",
            "cantidad_modalidad",
        ],
    )
    representantes_subtipo = _obtener_representantes(
        arquetipo_complementario,
        [
            "representantes_modalidad_casa",
            "conteo_subtipo_complementario",
            "cantidad_subtipo",
        ],
    )

    puentes_elemento = buscar_puentes_elemento(
        posiciones_validas,
        elemento,
    )
    puentes_modalidad = buscar_puentes_modalidad_signo(
        posiciones_validas,
        modalidad,
    )
    puentes_subtipo = buscar_puentes_subtipo(
        posiciones_validas,
        subtipo,
    )

    resultado = {
        "elemento": _resultado_categoria(
            tipo="elemento",
            nombre=elemento,
            representantes=representantes_elemento,
            puentes=puentes_elemento,
        ),
        "modalidad_signo": _resultado_categoria(
            tipo="modalidad_signo",
            nombre=modalidad,
            representantes=representantes_modalidad,
            puentes=puentes_modalidad,
        ),
        "modalidad_casa": _resultado_categoria(
            tipo="modalidad_casa",
            nombre=subtipo,
            representantes=representantes_subtipo,
            puentes=puentes_subtipo,
            modalidad_tecnica=MODALIDAD_TECNICA_POR_SUBTIPO.get(subtipo),
        ),
    }

    resultado["hay_puentes_internos"] = any(
        categoria["puentes"]
        for categoria in (
            resultado["elemento"],
            resultado["modalidad_signo"],
            resultado["modalidad_casa"],
        )
    )

    return resultado
