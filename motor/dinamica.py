from typing import Any


SIGNOS_YIN = {
    "Tauro",
    "Cáncer",
    "Virgo",
    "Escorpio",
    "Capricornio",
    "Piscis",
}


SIGNOS_YANG = {
    "Aries",
    "Géminis",
    "Leo",
    "Libra",
    "Sagitario",
    "Acuario",
}


POLARIDAD_ASPECTOS = {
    "Semisextil": "Yang",
    "Sextil": "Yin",
    "Cuadratura": "Yang",
    "Trígono": "Yin",
    "Quincuncio": "Yang",
    "Oposición": "Yin",
}


def obtener_polaridad_signo(signo: str) -> str:
    """
    Devuelve la polaridad energética de un signo.

    Fuego y Aire son Yang.
    Tierra y Agua son Yin.
    """

    if signo in SIGNOS_YIN:
        return "Yin"

    if signo in SIGNOS_YANG:
        return "Yang"

    raise ValueError(
        f"No se reconoce el signo astrológico: {signo}"
    )


def clasificar_conjuncion(
    signo_1: str,
    signo_2: str,
) -> dict[str, Any]:
    """
    Clasifica una conjunción según los signos
    donde se encuentran los dos cuerpos.

    Una conjunción entre signos diferentes
    se considera híbrida.
    """

    if signo_1 != signo_2:
        return {
            "polaridad": "Híbrida",
            "valor_yin": 0.5,
            "valor_yang": 0.5,
        }

    polaridad = obtener_polaridad_signo(signo_1)

    if polaridad == "Yin":
        return {
            "polaridad": "Yin",
            "valor_yin": 1.0,
            "valor_yang": 0.0,
        }

    return {
        "polaridad": "Yang",
        "valor_yin": 0.0,
        "valor_yang": 1.0,
    }


def clasificar_aspecto(
    aspecto: dict[str, Any],
) -> dict[str, Any]:
    """
    Clasifica energéticamente un aspecto
    previamente calculado por aspectos.py.
    """

    nombre_aspecto = aspecto.get("aspecto")

    if not nombre_aspecto:
        raise ValueError(
            "El aspecto no contiene el campo 'aspecto'."
        )

    if nombre_aspecto == "Conjunción":
        signo_1 = aspecto.get("signo1")
        signo_2 = aspecto.get("signo2")

        if not signo_1 or not signo_2:
            raise ValueError(
                "La conjunción necesita los campos "
                "'signo1' y 'signo2'."
            )

        return clasificar_conjuncion(
            signo_1,
            signo_2,
        )

    polaridad = POLARIDAD_ASPECTOS.get(
        nombre_aspecto
    )

    if polaridad is None:
        raise ValueError(
            "No existe una clasificación energética "
            f"para el aspecto: {nombre_aspecto}"
        )

    if polaridad == "Yin":
        return {
            "polaridad": "Yin",
            "valor_yin": 1.0,
            "valor_yang": 0.0,
        }

    return {
        "polaridad": "Yang",
        "valor_yin": 0.0,
        "valor_yang": 1.0,
    }


def determinar_predominio(
    total_yin: float,
    total_yang: float,
) -> str:
    """
    Determina el predominio energético.
    """

    if total_yin > total_yang:
        return "Yin"

    if total_yang > total_yin:
        return "Yang"

    return "Equilibrado"


def calcular_dinamica_yin_yang(
    aspectos: list[dict[str, Any]],
) -> dict[str, Any]:
    """
    Calcula la dinámica Yin/Yang de una lista
    de aspectos previamente calculados.

    Cada aspecto aporta una unidad energética:

    - Yin: 1 punto Yin.
    - Yang: 1 punto Yang.
    - Híbrido: 0.5 Yin y 0.5 Yang.
    """

    total_yin = 0.0
    total_yang = 0.0

    cantidad_yin = 0
    cantidad_yang = 0
    cantidad_hibrida = 0

    detalle = []

    for aspecto in aspectos:
        clasificacion = clasificar_aspecto(
            aspecto
        )

        polaridad = clasificacion["polaridad"]
        valor_yin = clasificacion["valor_yin"]
        valor_yang = clasificacion["valor_yang"]

        total_yin += valor_yin
        total_yang += valor_yang

        if polaridad == "Yin":
            cantidad_yin += 1

        elif polaridad == "Yang":
            cantidad_yang += 1

        else:
            cantidad_hibrida += 1

        detalle.append(
            {
                **aspecto,
                "polaridad": polaridad,
                "valor_yin": valor_yin,
                "valor_yang": valor_yang,
            }
        )

    total_energetico = total_yin + total_yang

    if total_energetico == 0:
        porcentaje_yin = 0.0
        porcentaje_yang = 0.0
    else:
        porcentaje_yin = round(
            total_yin / total_energetico * 100,
            2,
        )

        porcentaje_yang = round(
            total_yang / total_energetico * 100,
            2,
        )

    return {
        "total_aspectos": len(aspectos),
        "conteo": {
            "yin": cantidad_yin,
            "yang": cantidad_yang,
            "hibridos": cantidad_hibrida,
        },
        "valor_energetico": {
            "yin": total_yin,
            "yang": total_yang,
        },
        "porcentaje_yin": porcentaje_yin,
        "porcentaje_yang": porcentaje_yang,
        "predominio": determinar_predominio(
            total_yin,
            total_yang,
        ),
        "detalle": detalle,
    }
