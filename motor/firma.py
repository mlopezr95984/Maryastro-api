from typing import Any


SIGNOS = [
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


CUERPOS_FIRMA = {
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
    "Ascendente",
    "Medio Cielo",
}


ELEMENTOS = {
    "Aries": "Fuego",
    "Leo": "Fuego",
    "Sagitario": "Fuego",
    "Tauro": "Tierra",
    "Virgo": "Tierra",
    "Capricornio": "Tierra",
    "Géminis": "Aire",
    "Libra": "Aire",
    "Acuario": "Aire",
    "Cáncer": "Agua",
    "Escorpio": "Agua",
    "Piscis": "Agua",
}


MODALIDADES = {
    "Aries": "Cardinal",
    "Cáncer": "Cardinal",
    "Libra": "Cardinal",
    "Capricornio": "Cardinal",
    "Tauro": "Fija",
    "Leo": "Fija",
    "Escorpio": "Fija",
    "Acuario": "Fija",
    "Géminis": "Mutable",
    "Virgo": "Mutable",
    "Sagitario": "Mutable",
    "Piscis": "Mutable",
}


ARQUETIPOS = {
    ("Fuego", "Cardinal"): "Aries",
    ("Fuego", "Fija"): "Leo",
    ("Fuego", "Mutable"): "Sagitario",
    ("Tierra", "Cardinal"): "Capricornio",
    ("Tierra", "Fija"): "Tauro",
    ("Tierra", "Mutable"): "Virgo",
    ("Aire", "Cardinal"): "Libra",
    ("Aire", "Fija"): "Acuario",
    ("Aire", "Mutable"): "Géminis",
    ("Agua", "Cardinal"): "Cáncer",
    ("Agua", "Fija"): "Escorpio",
    ("Agua", "Mutable"): "Piscis",
}


def indice_signo(longitud: float) -> int:
    """
    Devuelve el índice del signo zodiacal correspondiente
    a una longitud entre 0 y 360 grados.
    """
    return int((longitud % 360) // 30)


def nombre_signo(longitud: float) -> str:
    """
    Devuelve el nombre del signo zodiacal correspondiente
    a una longitud.
    """
    return SIGNOS[indice_signo(longitud)]


def obtener_maximos(conteo: dict[str, int]) -> list[str]:
    """
    Devuelve todas las categorías que poseen el valor máximo.

    Puede devolver una sola categoría o varias en caso de empate.
    """
    mayor = max(conteo.values())

    return [
        categoria
        for categoria, valor in conteo.items()
        if valor == mayor
    ]


def crear_nombre_hibrido(arquetipos: list[str]) -> str:
    """
    Crea el nombre final del arquetipo.

    Si hay un solo resultado devuelve ese signo.
    Si hay varios, los une con un guion largo.
    """
    if not arquetipos:
        return "Sin resultado"

    if len(arquetipos) == 1:
        return arquetipos[0]

    return "–".join(arquetipos)


def determinar_tipo_firma(
    elementos_dominantes: list[str],
    modalidades_dominantes: list[str],
) -> str:
    """
    Clasifica la firma según la existencia o no de empates.
    """
    hay_empate_elemental = len(elementos_dominantes) > 1
    hay_empate_modal = len(modalidades_dominantes) > 1

    if hay_empate_elemental and hay_empate_modal:
        return "Híbrida compuesta"

    if hay_empate_elemental:
        return "Híbrida elemental"

    if hay_empate_modal:
        return "Híbrida modal"

    return "Pura"


def calcular_firma_energetica(
    posiciones: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    """
    Calcula la Firma Energética mediante el conteo de elementos
    y modalidades de los cuerpos definidos en CUERPOS_FIRMA.

    El Sol participa en el conteo como cualquier otro cuerpo,
    pero no se utiliza como criterio adicional de desempate.
    """

    conteo_elementos = {
        "Fuego": 0,
        "Tierra": 0,
        "Aire": 0,
        "Agua": 0,
    }

    conteo_modalidades = {
        "Cardinal": 0,
        "Fija": 0,
        "Mutable": 0,
    }

    detalle = []

    for cuerpo in CUERPOS_FIRMA:
        if cuerpo not in posiciones:
            continue

        longitud = posiciones[cuerpo]["longitud"]
        signo = nombre_signo(longitud)
        elemento = ELEMENTOS[signo]
        modalidad = MODALIDADES[signo]

        conteo_elementos[elemento] += 1
        conteo_modalidades[modalidad] += 1

        detalle.append(
            {
                "cuerpo": cuerpo,
                "signo": signo,
                "elemento": elemento,
                "modalidad": modalidad,
            }
        )

    elementos_dominantes = obtener_maximos(
        conteo_elementos
    )

    modalidades_dominantes = obtener_maximos(
        conteo_modalidades
    )

    arquetipos_resultantes = []

    for elemento in elementos_dominantes:
        for modalidad in modalidades_dominantes:
            arquetipo = ARQUETIPOS[
                (elemento, modalidad)
            ]

            if arquetipo not in arquetipos_resultantes:
                arquetipos_resultantes.append(arquetipo)

    signo_solar = None
    elemento_solar = None
    modalidad_solar = None

    if "Sol" in posiciones:
        signo_solar = nombre_signo(
            posiciones["Sol"]["longitud"]
        )
        elemento_solar = ELEMENTOS[signo_solar]
        modalidad_solar = MODALIDADES[signo_solar]

    tipo_firma = determinar_tipo_firma(
        elementos_dominantes,
        modalidades_dominantes,
    )

    return {
        "elementos": conteo_elementos,
        "modalidades": conteo_modalidades,
        "signo_solar": signo_solar,
        "elemento_solar": elemento_solar,
        "modalidad_solar": modalidad_solar,
        "elementos_dominantes": elementos_dominantes,
        "modalidades_dominantes": modalidades_dominantes,
        "hubo_empate_elemental": (
            len(elementos_dominantes) > 1
        ),
        "hubo_empate_modal": (
            len(modalidades_dominantes) > 1
        ),
        "arquetipos": arquetipos_resultantes,
        "nombre_arquetipo": crear_nombre_hibrido(
            arquetipos_resultantes
        ),
        "tipo_firma": tipo_firma,
        "detalle": sorted(
            detalle,
            key=lambda item: item["cuerpo"],
        ),
    }