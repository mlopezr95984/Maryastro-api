from typing import Any


ASPECTOS = {
    "Conjunción": 0,
    "Semisextil": 30,
    "Sextil": 60,
    "Cuadratura": 90,
    "Trígono": 120,
    "Quincuncio": 150,
    "Oposición": 180,
}


NODOS_EXCLUIDOS = {
    "Nodo Norte medio",
    "Nodo Sur medio",
}


def distancia_angular(
    longitud_1: float,
    longitud_2: float,
) -> float:
    """
    Calcula la distancia angular mínima entre dos posiciones.

    El resultado siempre queda entre 0 y 180 grados.
    """

    diferencia = abs(longitud_1 - longitud_2) % 360

    return min(
        diferencia,
        360 - diferencia,
    )


def calcular_aspectos(
    posiciones: dict[str, dict[str, Any]],
    orbe_maximo: float,
) -> list[dict[str, Any]]:
    """
    Calcula los aspectos básicos entre los cuerpos disponibles.

    Los nodos se conservan en la carta y en el eje evolutivo,
    pero no participan en esta lista general de aspectos.
    """

    if not 0 <= orbe_maximo <= 10:
        raise ValueError(
            "El orbe máximo debe estar entre 0 y 10 grados."
        )

    resultados = []

    cuerpos = [
        cuerpo
        for cuerpo in posiciones
        if cuerpo not in NODOS_EXCLUIDOS
    ]

    for indice_1 in range(len(cuerpos)):
        for indice_2 in range(
            indice_1 + 1,
            len(cuerpos),
        ):
            cuerpo_1 = cuerpos[indice_1]
            cuerpo_2 = cuerpos[indice_2]

            longitud_1 = posiciones[cuerpo_1]["longitud"]
            longitud_2 = posiciones[cuerpo_2]["longitud"]

            distancia = distancia_angular(
                longitud_1,
                longitud_2,
            )

            for nombre_aspecto, angulo_exacto in ASPECTOS.items():
                orbe = abs(
                    distancia - angulo_exacto
                )

                if orbe <= orbe_maximo:
                    resultados.append(
                        {
                            "cuerpo1": cuerpo_1,
                            "cuerpo2": cuerpo_2,
                            "aspecto": nombre_aspecto,
                            "angulo_exacto": angulo_exacto,
                            "distancia": distancia,
                            "orbe": orbe,
                        }
                    )

                    # Una pareja solo recibe el aspecto más cercano
                    # encontrado dentro del orbe permitido.
                    break

    return sorted(
        resultados,
        key=lambda aspecto: aspecto["orbe"],
    )


def calcular_aspectos_de_cuerpo(
    nombre_cuerpo: str,
    posiciones: dict[str, dict[str, Any]],
    orbe_maximo: float,
    incluir_nodos: bool = True,
) -> list[dict[str, Any]]:
    """
    Calcula los aspectos de un cuerpo específico.

    Esta función será útil después para los aliados nodales,
    porque necesitaremos consultar los aspectos del planeta
    regente de cada nodo.
    """

    if nombre_cuerpo not in posiciones:
        return []

    if not 0 <= orbe_maximo <= 10:
        raise ValueError(
            "El orbe máximo debe estar entre 0 y 10 grados."
        )

    longitud_base = posiciones[
        nombre_cuerpo
    ]["longitud"]

    resultados = []

    for otro_cuerpo, datos in posiciones.items():
        if otro_cuerpo == nombre_cuerpo:
            continue

        if (
            not incluir_nodos
            and otro_cuerpo in NODOS_EXCLUIDOS
        ):
            continue

        distancia = distancia_angular(
            longitud_base,
            datos["longitud"],
        )

        for nombre_aspecto, angulo_exacto in ASPECTOS.items():
            orbe = abs(
                distancia - angulo_exacto
            )

            if orbe <= orbe_maximo:
                resultados.append(
                    {
                        "cuerpo1": nombre_cuerpo,
                        "cuerpo2": otro_cuerpo,
                        "aspecto": nombre_aspecto,
                        "angulo_exacto": angulo_exacto,
                        "distancia": distancia,
                        "orbe": orbe,
                    }
                )
                break

    return sorted(
        resultados,
        key=lambda aspecto: aspecto["orbe"],
    )