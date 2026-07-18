from typing import Any

from motor.firma import ARQUETIPOS, ELEMENTOS, MODALIDADES
from motor.subtipo import CUERPOS_SUBTIPO, SUBTIPOS, TIPOS_CASA


APOYOS_EXTERNOS_ELEMENTO = {
    "Fuego": [
        "Participar en proyectos que exijan iniciativa y decisión.",
        "Buscar grupos, mentores o entrenadores que estimulen la confianza y la acción.",
        "Crear desafíos concretos que ayuden a movilizar la energía.",
    ],
    "Tierra": [
        "Apoyarse en sistemas de organización, agendas, presupuestos y rutinas.",
        "Buscar personas o equipos que modelen constancia, practicidad y estabilidad.",
        "Utilizar métodos de seguimiento que permitan materializar y sostener los objetivos.",
    ],
    "Aire": [
        "Participar en redes, grupos de estudio y espacios de conversación.",
        "Buscar personas que aporten perspectiva, intercambio de ideas y pensamiento crítico.",
        "Usar herramientas de lectura, escritura y comunicación para ordenar la experiencia.",
    ],
    "Agua": [
        "Buscar comunidades de apoyo, espacios terapéuticos o vínculos de confianza.",
        "Incorporar prácticas artísticas, contemplativas o emocionales.",
        "Apoyarse en personas que faciliten la empatía, la escucha y la conexión afectiva.",
    ],
}


APOYOS_EXTERNOS_MODALIDAD = {
    "Cardinal": [
        "Trabajar con calendarios, fechas de inicio y compromisos concretos.",
        "Buscar equipos o personas que ayuden a tomar decisiones y poner los proyectos en marcha.",
        "Crear pequeñas acciones iniciales que reduzcan la dificultad de comenzar.",
    ],
    "Fija": [
        "Utilizar rutinas, sistemas de continuidad y revisiones periódicas.",
        "Buscar personas o grupos que ayuden a sostener los procesos a largo plazo.",
        "Dividir los objetivos en etapas estables y medibles.",
    ],
    "Mutable": [
        "Participar en espacios de aprendizaje, supervisión y actualización.",
        "Buscar redes diversas que aporten nuevas perspectivas y alternativas.",
        "Incorporar momentos de revisión para ajustar los planes sin abandonar el propósito.",
    ],
}


APOYOS_EXTERNOS_SUBTIPO = {
    "Iniciador": [
        "Buscar estructuras que ayuden a decidir, priorizar y comenzar.",
        "Participar en proyectos donde exista una función clara de liderazgo o activación.",
        "Apoyarse en personas que faciliten la toma de iniciativa.",
    ],
    "Sostenedor": [
        "Crear sistemas de seguimiento y mantenimiento de los proyectos.",
        "Buscar equipos estables que aporten continuidad, recursos y acompañamiento.",
        "Establecer hábitos y compromisos periódicos.",
    ],
    "Transformador": [
        "Buscar espacios de estudio, reflexión, terapia, mentoría o retiro.",
        "Participar en grupos que favorezcan el aprendizaje y el cambio de perspectiva.",
        "Crear momentos conscientes para revisar, comprender y transformar la experiencia.",
    ],
}


DESCRIPCIONES_ELEMENTOS = {
    "Fuego": (
        "impulso, confianza, entusiasmo y capacidad para poner "
        "la experiencia en movimiento"
    ),
    "Tierra": (
        "estabilidad, sentido práctico, constancia y capacidad "
        "para materializar"
    ),
    "Aire": (
        "comunicación, perspectiva, intercambio y capacidad "
        "para conectar ideas"
    ),
    "Agua": (
        "sensibilidad, intuición, profundidad emocional y capacidad "
        "para crear vínculos"
    ),
}


DESCRIPCIONES_MODALIDADES = {
    "Cardinal": (
        "iniciar, decidir y orientar la energía hacia una dirección concreta"
    ),
    "Fija": (
        "sostener, consolidar y profundizar los procesos"
    ),
    "Mutable": (
        "adaptarse, revisar y transformar la experiencia"
    ),
}


DESCRIPCIONES_SUBTIPOS = {
    "Iniciador": (
        "actuar desde espacios de comienzo, dirección y decisión"
    ),
    "Sostenedor": (
        "dar continuidad, recursos y estabilidad a lo iniciado"
    ),
    "Transformador": (
        "procesar, comprender y convertir la experiencia"
    ),
}


def obtener_minimos(conteo: dict[str, int]) -> list[str]:
    """
    Devuelve todas las categorías que comparten el valor mínimo.
    Los empates se conservan; nunca se resuelven arbitrariamente.
    """

    if not conteo:
        return []

    valor_minimo = min(conteo.values())

    return [
        categoria
        for categoria, valor in conteo.items()
        if valor == valor_minimo
    ]


def crear_nombre_hibrido(nombres: list[str]) -> str:
    """
    Devuelve un nombre único o un nombre híbrido unido por un guion largo.
    """

    if not nombres:
        return "Sin resultado"

    return "–".join(nombres)


def construir_arquetipos(
    elementos_minimos: list[str],
    modalidades_minimas: list[str],
) -> list[str]:
    """
    Combina todos los elementos y modalidades mínimos.

    Si hay empate en alguna categoría, conserva todas las
    combinaciones posibles.
    """

    arquetipos: list[str] = []

    for elemento in elementos_minimos:
        for modalidad in modalidades_minimas:
            arquetipo = ARQUETIPOS[(elemento, modalidad)]

            if arquetipo not in arquetipos:
                arquetipos.append(arquetipo)

    return arquetipos


def calcular_puentes_energeticos(
    elementos_minimos: list[str],
    modalidades_minimas: list[str],
    tipos_casa_minimos: list[str],
    posiciones: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    """
    Busca puentes internos hacia cada energía complementaria.

    - Elemento: planetas en signos del elemento mínimo.
    - Modalidad: planetas en signos de la modalidad mínima.
    - Subtipo: planetas en casas del tipo de casa mínimo.

    Cuando una energía no tiene puentes internos, propone apoyos externos.
    """

    planetas_elemento: list[dict[str, Any]] = []
    planetas_modalidad: list[dict[str, Any]] = []
    planetas_subtipo: list[dict[str, Any]] = []

    for cuerpo in CUERPOS_SUBTIPO:
        if cuerpo not in posiciones:
            continue

        datos = posiciones[cuerpo]
        signo = datos.get("signo")
        casa = datos.get("casa")

        if not signo:
            continue

        elemento = ELEMENTOS[signo]
        modalidad = MODALIDADES[signo]
        tipo_casa = TIPOS_CASA.get(casa)

        if elemento in elementos_minimos:
            planetas_elemento.append(
                {
                    "cuerpo": cuerpo,
                    "signo": signo,
                    "casa": casa,
                    "elemento": elemento,
                }
            )

        if modalidad in modalidades_minimas:
            planetas_modalidad.append(
                {
                    "cuerpo": cuerpo,
                    "signo": signo,
                    "casa": casa,
                    "modalidad": modalidad,
                }
            )

        if tipo_casa in tipos_casa_minimos:
            planetas_subtipo.append(
                {
                    "cuerpo": cuerpo,
                    "signo": signo,
                    "casa": casa,
                    "tipo_casa": tipo_casa,
                    "subtipo": SUBTIPOS[tipo_casa],
                }
            )

    planetas_elemento.sort(key=lambda item: item["cuerpo"])
    planetas_modalidad.sort(key=lambda item: item["cuerpo"])
    planetas_subtipo.sort(key=lambda item: item["cuerpo"])

    apoyos_elemento = {
        elemento: APOYOS_EXTERNOS_ELEMENTO[elemento]
        for elemento in elementos_minimos
        if not any(
            puente["elemento"] == elemento
            for puente in planetas_elemento
        )
    }

    apoyos_modalidad = {
        modalidad: APOYOS_EXTERNOS_MODALIDAD[modalidad]
        for modalidad in modalidades_minimas
        if not any(
            puente["modalidad"] == modalidad
            for puente in planetas_modalidad
        )
    }

    apoyos_subtipo = {
        SUBTIPOS[tipo_casa]: APOYOS_EXTERNOS_SUBTIPO[
            SUBTIPOS[tipo_casa]
        ]
        for tipo_casa in tipos_casa_minimos
        if not any(
            puente["tipo_casa"] == tipo_casa
            for puente in planetas_subtipo
        )
    }

    return {
        "internos": {
            "por_elemento": planetas_elemento,
            "por_modalidad": planetas_modalidad,
            "por_subtipo": planetas_subtipo,
        },
        "externos": {
            "por_elemento": apoyos_elemento,
            "por_modalidad": apoyos_modalidad,
            "por_subtipo": apoyos_subtipo,
        },
        "requiere_apoyo_externo": {
            "elemento": bool(apoyos_elemento),
            "modalidad": bool(apoyos_modalidad),
            "subtipo": bool(apoyos_subtipo),
        },
    }


def construir_descripcion_energia(
    elementos_minimos: list[str],
    modalidades_minimas: list[str],
    subtipos_complementarios: list[str],
) -> str:
    """
    Construye una descripción breve que conserva todos los empates.
    """

    texto_elementos = "; ".join(
        DESCRIPCIONES_ELEMENTOS[elemento]
        for elemento in elementos_minimos
    )

    texto_modalidades = "; ".join(
        DESCRIPCIONES_MODALIDADES[modalidad]
        for modalidad in modalidades_minimas
    )

    texto_subtipos = "; ".join(
        DESCRIPCIONES_SUBTIPOS[subtipo]
        for subtipo in subtipos_complementarios
    )

    return (
        "El arquetipo complementario invita a desarrollar "
        f"{texto_elementos}. Su modalidad propone aprender a "
        f"{texto_modalidades}. El subtipo complementario señala "
        f"el reto de {texto_subtipos}."
    )


def calcular_arquetipo_complementario(
    firma: dict[str, Any],
    subtipo: dict[str, Any],
    posiciones: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    """
    Calcula el arquetipo y el subtipo complementarios.

    Los empates de elemento, modalidad o tipo de casa se mantienen.
    Por tanto, el resultado puede ser definido o híbrido.
    """

    if firma is None:
        raise ValueError(
            "No se puede calcular el complementario sin la firma energética."
        )

    if subtipo is None:
        raise ValueError(
            "No se puede calcular el complementario sin el subtipo."
        )

    conteo_elementos = firma["elementos"]
    conteo_modalidades = firma["modalidades"]
    conteo_tipos_casa = subtipo["conteo"]

    elementos_bajos = [
        elemento
        for elemento, puntos in conteo_elementos.items()
        if puntos < 2
    ]

    modalidades_bajas = [
        modalidad
        for modalidad, puntos in conteo_modalidades.items()
        if puntos < 2
    ]

    tipos_casa_bajos = [
        tipo_casa
        for tipo_casa, puntos in conteo_tipos_casa.items()
        if puntos < 2
    ]

    elementos_minimos = obtener_minimos(conteo_elementos)
    modalidades_minimas = obtener_minimos(conteo_modalidades)
    tipos_casa_minimos = obtener_minimos(conteo_tipos_casa)

    arquetipos = construir_arquetipos(
        elementos_minimos,
        modalidades_minimas,
    )

    subtipos_complementarios = [
        SUBTIPOS[tipo_casa]
        for tipo_casa in tipos_casa_minimos
    ]

    nombre_arquetipo = crear_nombre_hibrido(arquetipos)
    nombre_subtipo = crear_nombre_hibrido(
        subtipos_complementarios
    )

    hubo_empate_arquetipo = len(arquetipos) > 1
    hubo_empate_subtipo = len(subtipos_complementarios) > 1
    hubo_empate = (
        hubo_empate_arquetipo
        or hubo_empate_subtipo
    )

    aplica = bool(
        elementos_bajos
        or modalidades_bajas
        or tipos_casa_bajos
    )

    puentes = calcular_puentes_energeticos(
        elementos_minimos,
        modalidades_minimas,
        tipos_casa_minimos,
        posiciones,
    )

    resultado = {
        "aplica": aplica,
        "elementos_bajos": elementos_bajos,
        "modalidades_bajas": modalidades_bajas,
        "tipos_casa_bajos": tipos_casa_bajos,
        "elementos_minimos": elementos_minimos,
        "modalidades_minimas": modalidades_minimas,
        "tipos_casa_minimos": tipos_casa_minimos,
        "arquetipos": arquetipos,
        "nombre_arquetipo": nombre_arquetipo,
        "subtipos": subtipos_complementarios,
        "nombre_subtipo": nombre_subtipo,
        "tipo_complementario": (
            "Híbrido" if hubo_empate else "Definido"
        ),
        "hubo_empate": hubo_empate,
        "hubo_empate_arquetipo": hubo_empate_arquetipo,
        "hubo_empate_subtipo": hubo_empate_subtipo,
        "descripcion_energia": construir_descripcion_energia(
            elementos_minimos,
            modalidades_minimas,
            subtipos_complementarios,
        ),
        "puentes": puentes,
    }

    if not aplica:
        resultado["motivo"] = (
            "No hay elementos, modalidades de signo ni tipos "
            "de casa con menos de 2 puntos. Se muestran las "
            "categorías relativamente menos representadas, "
            "pero no se consideran una carencia marcada."
        )

    return resultado
