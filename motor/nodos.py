from typing import Any


POLARIDAD_SIGNOS = {
    "Aries": "Yang",
    "Tauro": "Yin",
    "Géminis": "Yang",
    "Cáncer": "Yin",
    "Leo": "Yang",
    "Virgo": "Yin",
    "Libra": "Yang",
    "Escorpio": "Yin",
    "Sagitario": "Yang",
    "Capricornio": "Yin",
    "Acuario": "Yang",
    "Piscis": "Yin",
}


REGENTES_SIGNOS = {
    "Aries": "Marte",
    "Tauro": "Venus",
    "Géminis": "Mercurio",
    "Cáncer": "Luna",
    "Leo": "Sol",
    "Virgo": "Mercurio",
    "Libra": "Venus",
    "Escorpio": "Plutón",
    "Sagitario": "Júpiter",
    "Capricornio": "Saturno",
    "Acuario": "Urano",
    "Piscis": "Neptuno",
}


RECURSOS_NODO_SUR_SIGNO = {
    "Aries": (
        "la iniciativa, el valor para actuar y la capacidad de abrir caminos"
    ),
    "Tauro": (
        "la constancia, el sentido práctico y la capacidad de crear estabilidad"
    ),
    "Géminis": (
        "la curiosidad, la comunicación y la habilidad para conectar información"
    ),
    "Cáncer": (
        "la sensibilidad, la memoria y la capacidad de cuidar y proteger"
    ),
    "Leo": (
        "la creatividad, la confianza y la capacidad de expresar una identidad propia"
    ),
    "Virgo": (
        "el discernimiento, la observación y la capacidad de mejorar lo cotidiano"
    ),
    "Libra": (
        "la diplomacia, la cooperación y la capacidad de considerar otras perspectivas"
    ),
    "Escorpio": (
        "la profundidad, la resistencia emocional y la capacidad de atravesar transformaciones"
    ),
    "Sagitario": (
        "la visión, la confianza y la capacidad de encontrar sentido en la experiencia"
    ),
    "Capricornio": (
        "la disciplina, la responsabilidad y la capacidad de construir a largo plazo"
    ),
    "Acuario": (
        "la originalidad, la independencia y la capacidad de pensar en términos colectivos"
    ),
    "Piscis": (
        "la intuición, la compasión y la capacidad de percibir dimensiones sutiles"
    ),
}


PROPOSITO_NODO_NORTE_SIGNO = {
    "Aries": (
        "desarrollar autonomía, decisión y confianza para actuar desde el propio deseo"
    ),
    "Tauro": (
        "construir estabilidad, valorar lo esencial y aprender a sostener procesos"
    ),
    "Géminis": (
        "cultivar curiosidad, flexibilidad y apertura al intercambio de ideas"
    ),
    "Cáncer": (
        "desarrollar sensibilidad, pertenencia y una relación más consciente con el cuidado"
    ),
    "Leo": (
        "expresar creatividad, ocupar un lugar visible y confiar en la propia singularidad"
    ),
    "Virgo": (
        "ordenar la experiencia, desarrollar discernimiento y convertir la inspiración en práctica"
    ),
    "Libra": (
        "aprender cooperación, reciprocidad y construcción consciente de vínculos"
    ),
    "Escorpio": (
        "aceptar la transformación, profundizar y compartir recursos con mayor confianza"
    ),
    "Sagitario": (
        "ampliar la visión, construir sentido y orientar la experiencia hacia un propósito mayor"
    ),
    "Capricornio": (
        "asumir responsabilidad, estructurar metas y desarrollar autoridad interior"
    ),
    "Acuario": (
        "abrirse a lo colectivo, innovar y contribuir desde una perspectiva más amplia"
    ),
    "Piscis": (
        "desarrollar entrega, intuición y confianza en procesos que no pueden controlarse por completo"
    ),
}


TEMAS_CASAS = {
    1: "la identidad, la autonomía y la manera de iniciar",
    2: "los valores, los recursos y la seguridad personal",
    3: "la comunicación, el aprendizaje y el entorno cercano",
    4: "las raíces, la vida interior y el sentido de pertenencia",
    5: "la creatividad, el disfrute y la expresión personal",
    6: "los hábitos, el servicio, el trabajo cotidiano y el cuidado del cuerpo",
    7: "los vínculos, los acuerdos y el encuentro con otras personas",
    8: "la intimidad, los recursos compartidos y los procesos de transformación",
    9: "las creencias, el conocimiento, los viajes y la ampliación de la visión",
    10: "la vocación, la responsabilidad y la proyección pública",
    11: "las redes, los grupos, los proyectos y la participación colectiva",
    12: "el mundo interior, la espiritualidad, el retiro y los procesos inconscientes",
}


def obtener_datos_nodo(
    posiciones: dict[str, dict[str, Any]],
    nombre_nodo: str,
) -> dict[str, Any]:
    """
    Extrae y estructura los datos de un nodo lunar.
    """

    if nombre_nodo not in posiciones:
        raise ValueError(
            f"No se encontró {nombre_nodo} en las posiciones calculadas."
        )

    datos = posiciones[nombre_nodo]
    signo = datos.get("signo")
    casa = datos.get("casa")

    if not signo:
        raise ValueError(
            f"{nombre_nodo} no contiene información de signo."
        )

    if casa is None:
        raise ValueError(
            f"{nombre_nodo} no contiene información de casa."
        )

    return {
        "nombre": nombre_nodo,
        "longitud": datos.get("longitud"),
        "signo": signo,
        "grado_en_signo": datos.get("grado_en_signo"),
        "casa": casa,
        "polaridad": POLARIDAD_SIGNOS[signo],
        "regente": REGENTES_SIGNOS[signo],
    }


def obtener_nombre_arquetipo(
    firma: dict[str, Any],
) -> str:
    """
    Obtiene el nombre del arquetipo dominante tolerando
    distintas versiones del diccionario de firma.
    """

    for clave in (
        "nombre_arquetipo",
        "arquetipo_dominante",
        "nombre",
    ):
        valor = firma.get(clave)
        if valor:
            return str(valor)

    arquetipos = firma.get("arquetipos")
    if isinstance(arquetipos, list) and arquetipos:
        return "–".join(str(item) for item in arquetipos)

    return "Sin determinar"


def obtener_nombre_subtipo(
    subtipo: dict[str, Any],
) -> str:
    """
    Obtiene el subtipo dominante, incluyendo configuraciones híbridas.
    """

    for clave in (
        "nombre_subtipo",
        "tipo_subtipo",
        "subtipo_dominante",
        "nombre",
    ):
        valor = subtipo.get(clave)
        if valor:
            return str(valor)

    subtipos = subtipo.get("subtipos")
    if isinstance(subtipos, list) and subtipos:
        return "–".join(str(item) for item in subtipos)

    return "Sin determinar"


def construir_recursos_nodo_sur(
    nodo_sur: dict[str, Any],
) -> str:
    """
    Describe los recursos disponibles del Nodo Sur.
    """

    signo = nodo_sur["signo"]
    casa = nodo_sur["casa"]

    return (
        f"El Nodo Sur en {signo} aporta "
        f"{RECURSOS_NODO_SUR_SIGNO[signo]}. "
        f"En la casa {casa}, estos recursos se han desarrollado "
        f"especialmente en relación con {TEMAS_CASAS[casa]}."
    )


def construir_proposito_nodo_norte(
    nodo_norte: dict[str, Any],
) -> str:
    """
    Describe la dirección evolutiva del Nodo Norte.
    """

    signo = nodo_norte["signo"]
    casa = nodo_norte["casa"]

    return (
        f"El Nodo Norte en {signo} invita a "
        f"{PROPOSITO_NODO_NORTE_SIGNO[signo]}. "
        f"En la casa {casa}, este aprendizaje se despliega a través de "
        f"{TEMAS_CASAS[casa]}."
    )


def construir_descripcion_energia_disponible(
    firma: dict[str, Any],
    subtipo: dict[str, Any],
) -> str:
    """
    Resume la energía dominante que la persona tiene disponible
    para recorrer el eje nodal.
    """

    nombre_arquetipo = obtener_nombre_arquetipo(firma)
    nombre_subtipo = obtener_nombre_subtipo(subtipo)

    descripcion_firma = firma.get(
        "descripcion_energia",
        firma.get("descripcion", ""),
    )

    descripcion_subtipo = subtipo.get(
        "descripcion_energia",
        subtipo.get("descripcion", ""),
    )

    partes = [
        (
            f"Para recorrer este camino dispone de la energía de su "
            f"arquetipo dominante {nombre_arquetipo}, expresada mediante "
            f"el subtipo {nombre_subtipo}."
        )
    ]

    if descripcion_firma:
        partes.append(str(descripcion_firma))

    if descripcion_subtipo:
        partes.append(str(descripcion_subtipo))

    return " ".join(partes)


def construir_descripcion_reto_complementario(
    complementario: dict[str, Any],
) -> str:
    """
    Resume el reto de integración representado por el
    arquetipo complementario y sus subtipos.
    """

    nombre_arquetipo = complementario.get(
        "nombre_arquetipo",
        "Sin determinar",
    )
    nombre_subtipo = complementario.get(
        "nombre_subtipo",
        "Sin determinar",
    )
    tipo = complementario.get(
        "tipo_complementario",
        "Definido",
    )
    descripcion = complementario.get(
        "descripcion_energia",
        "",
    )

    texto = (
        f"El reto complementario es integrar la energía de "
        f"{nombre_arquetipo} con el subtipo {nombre_subtipo}. "
        f"Se trata de un complementario {tipo.lower()}."
    )

    if descripcion:
        texto += f" {descripcion}"

    return texto


def construir_integracion_eje(
    nodo_sur: dict[str, Any],
    nodo_norte: dict[str, Any],
    firma: dict[str, Any],
    subtipo: dict[str, Any],
    complementario: dict[str, Any],
) -> str:
    """
    Construye una síntesis que conecta recursos, propósito,
    energía dominante y reto complementario.
    """

    nombre_dominante = obtener_nombre_arquetipo(firma)
    subtipo_dominante = obtener_nombre_subtipo(subtipo)

    nombre_complementario = complementario.get(
        "nombre_arquetipo",
        "Sin determinar",
    )
    subtipo_complementario = complementario.get(
        "nombre_subtipo",
        "Sin determinar",
    )

    return (
        f"Los recursos del Nodo Sur en {nodo_sur['signo']} y casa "
        f"{nodo_sur['casa']} sirven como punto de partida para avanzar "
        f"hacia el Nodo Norte en {nodo_norte['signo']} y casa "
        f"{nodo_norte['casa']}. Para cumplir esta misión, la persona "
        f"dispone de la energía de {nombre_dominante} "
        f"{subtipo_dominante}. Su crecimiento requiere integrar "
        f"conscientemente los retos de {nombre_complementario} "
        f"{subtipo_complementario}, utilizando sus puentes internos "
        f"o buscando apoyo externo cuando sea necesario."
    )


def calcular_eje_nodal(
    posiciones: dict[str, dict[str, Any]],
    firma: dict[str, Any],
    subtipo: dict[str, Any],
    complementario: dict[str, Any],
) -> dict[str, Any]:
    """
    Calcula y estructura la lectura evolutiva del eje nodal.

    No recalcula posiciones ni aspectos. Consume los resultados
    ya generados por perfil.py, firma.py, subtipo.py y
    complementario.py.
    """

    if firma is None:
        raise ValueError(
            "No se puede calcular el eje nodal sin la firma energética."
        )

    if subtipo is None:
        raise ValueError(
            "No se puede calcular el eje nodal sin el subtipo."
        )

    if complementario is None:
        raise ValueError(
            "No se puede calcular el eje nodal sin el complementario."
        )

    nodo_sur = obtener_datos_nodo(
        posiciones,
        "Nodo Sur medio",
    )
    nodo_norte = obtener_datos_nodo(
        posiciones,
        "Nodo Norte medio",
    )

    recursos = construir_recursos_nodo_sur(nodo_sur)
    proposito = construir_proposito_nodo_norte(nodo_norte)

    energia_disponible = (
        construir_descripcion_energia_disponible(
            firma,
            subtipo,
        )
    )

    reto_complementario = (
        construir_descripcion_reto_complementario(
            complementario
        )
    )

    integracion = construir_integracion_eje(
        nodo_sur,
        nodo_norte,
        firma,
        subtipo,
        complementario,
    )

    return {
        "nodo_sur": nodo_sur,
        "nodo_norte": nodo_norte,
        "eje": {
            "recursos": recursos,
            "proposito": proposito,
            "energia_disponible": energia_disponible,
            "reto_complementario": reto_complementario,
            "integracion": integracion,
        },
        "perfil_aplicado": {
            "arquetipo_dominante": obtener_nombre_arquetipo(
                firma
            ),
            "subtipo_dominante": obtener_nombre_subtipo(
                subtipo
            ),
            "arquetipo_complementario": complementario.get(
                "nombre_arquetipo"
            ),
            "subtipo_complementario": complementario.get(
                "nombre_subtipo"
            ),
            "tipo_complementario": complementario.get(
                "tipo_complementario"
            ),
            "puentes": complementario.get("puentes", {}),
        },
    }
