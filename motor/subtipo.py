from typing import Any


CUERPOS_SUBTIPO = {
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
}


TIPOS_CASA = {
    1: "Angular",
    4: "Angular",
    7: "Angular",
    10: "Angular",
    2: "Sucedente",
    5: "Sucedente",
    8: "Sucedente",
    11: "Sucedente",
    3: "Cadente",
    6: "Cadente",
    9: "Cadente",
    12: "Cadente",
}


SUBTIPOS = {
    "Angular": "Iniciador",
    "Sucedente": "Sostenedor",
    "Cadente": "Transformador",
}


def obtener_maximos(conteo: dict[str, int]) -> list[str]:
    """
    Devuelve todas las categorías que tienen el valor máximo.

    Si hay empate, conserva todas las categorías dominantes.
    """
    mayor = max(conteo.values())

    return [
        categoria
        for categoria, valor in conteo.items()
        if valor == mayor
    ]


def crear_nombre_hibrido(subtipos: list[str]) -> str:
    """
    Devuelve un subtipo definido o un nombre híbrido.
    """
    if not subtipos:
        return "Sin resultado"

    if len(subtipos) == 1:
        return subtipos[0]

    return "–".join(subtipos)


def calcular_subtipo(
    posiciones: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    """
    Calcula el subtipo energético mediante la distribución
    de los planetas por casas angulares, sucedentes y cadentes.

    No incluye Ascendente, Medio Cielo ni nodos.
    """

    conteo = {
        "Angular": 0,
        "Sucedente": 0,
        "Cadente": 0,
    }

    detalle = []

    for cuerpo in CUERPOS_SUBTIPO:
        if cuerpo not in posiciones:
            continue

        casa = posiciones[cuerpo].get("casa")

        if casa is None:
            continue

        tipo_casa = TIPOS_CASA.get(casa)

        if tipo_casa is None:
            continue

        conteo[tipo_casa] += 1

        detalle.append(
            {
                "cuerpo": cuerpo,
                "casa": casa,
                "tipo_casa": tipo_casa,
                "subtipo": SUBTIPOS[tipo_casa],
            }
        )

    tipos_dominantes = obtener_maximos(conteo)

    subtipos_resultantes = [
        SUBTIPOS[tipo]
        for tipo in tipos_dominantes
    ]

    if len(subtipos_resultantes) == 1:
        tipo_resultado = "Definido"
    else:
        tipo_resultado = "Híbrido"

    return {
        "conteo": conteo,
        "tipos_dominantes": tipos_dominantes,
        "subtipos": subtipos_resultantes,
        "nombre_subtipo": crear_nombre_hibrido(
            subtipos_resultantes
        ),
        "tipo_subtipo": tipo_resultado,
        "hubo_empate": len(tipos_dominantes) > 1,
        "detalle": sorted(
            detalle,
            key=lambda item: item["cuerpo"],
        ),
    }