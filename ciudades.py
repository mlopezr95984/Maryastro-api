# ciudades.py

from __future__ import annotations

import unicodedata
from functools import lru_cache
from typing import Any

import geonamescache
from timezonefinder import TimezoneFinder


# ---------------------------------------------------------
# Carga única de datos
# ---------------------------------------------------------

_gc = geonamescache.GeonamesCache()
_tf = TimezoneFinder()

_CIUDADES_RAW = _gc.get_cities()
_PAISES_RAW = _gc.get_countries()


def _normalizar_texto(texto: str) -> str:
    """
    Convierte el texto a minúsculas y elimina tildes.

    Ejemplos:
        Bogotá -> bogota
        Medellín -> medellin
    """
    texto = texto.strip().casefold()

    return "".join(
        caracter
        for caracter in unicodedata.normalize("NFKD", texto)
        if not unicodedata.combining(caracter)
    )


def _construir_indice_ciudades() -> list[dict[str, Any]]:
    """
    Convierte la estructura interna de geonamescache en una lista
    más fácil de buscar.
    """
    indice: list[dict[str, Any]] = []

    for geoname_id, datos in _CIUDADES_RAW.items():
        nombre = datos.get("name", "").strip()

        if not nombre:
            continue

        codigo_pais = datos.get("countrycode", "")
        datos_pais = _PAISES_RAW.get(codigo_pais, {})
        nombre_pais = datos_pais.get("name", codigo_pais)

        try:
            latitud = float(datos["latitude"])
            longitud = float(datos["longitude"])
        except (KeyError, TypeError, ValueError):
            continue

        poblacion = datos.get("population", 0)

        try:
            poblacion = int(poblacion or 0)
        except (TypeError, ValueError):
            poblacion = 0

        region = (
            datos.get("admin1name")
            or datos.get("admin1code")
            or ""
        )

        nombres_alternativos = datos.get("alternatenames", [])

        if isinstance(nombres_alternativos, str):
            nombres_alternativos = [
                nombre.strip()
                for nombre in nombres_alternativos.split(",")
                if nombre.strip()
            ]

        textos_busqueda = [nombre, *nombres_alternativos]

        indice.append(
            {
                "id": str(geoname_id),
                "nombre": nombre,
                "nombre_normalizado": _normalizar_texto(nombre),
                "nombres_busqueda": [
                    _normalizar_texto(valor)
                    for valor in textos_busqueda
                    if valor
                ],
                "region": region,
                "pais": nombre_pais,
                "codigo_pais": codigo_pais,
                "latitud": latitud,
                "longitud": longitud,
                "poblacion": poblacion,
            }
        )

    return indice


# Se construye una sola vez cuando inicia la API.
_INDICE_CIUDADES = _construir_indice_ciudades()


# ---------------------------------------------------------
# Zona horaria
# ---------------------------------------------------------

@lru_cache(maxsize=4096)
def obtener_zona_horaria(
    latitud: float,
    longitud: float,
) -> str | None:
    """
    Obtiene la zona horaria IANA correspondiente a unas coordenadas.

    Ejemplo:
        America/Bogota
    """
    return _tf.timezone_at(
        lat=latitud,
        lng=longitud,
    )


# ---------------------------------------------------------
# Búsqueda
# ---------------------------------------------------------

def buscar_ciudades(
    texto: str,
    limite: int = 8,
    codigo_pais: str | None = None,
) -> list[dict[str, Any]]:
    """
    Busca ciudades por nombre o nombre alternativo.

    Prioridad:
    1. Coincidencia exacta.
    2. El nombre comienza con el texto.
    3. El nombre contiene el texto.
    4. Mayor población.

    Args:
        texto:
            Texto escrito por el usuario.

        limite:
            Cantidad máxima de resultados.

        codigo_pais:
            Código ISO opcional, por ejemplo "CO" o "ES".

    Returns:
        Lista de ciudades preparada para ser enviada a Wix.
    """
    consulta = _normalizar_texto(texto)

    if len(consulta) < 2:
        return []

    limite = max(1, min(limite, 20))

    filtro_pais = (
        codigo_pais.strip().upper()
        if codigo_pais
        else None
    )

    coincidencias: list[tuple[int, int, dict[str, Any]]] = []

    for ciudad in _INDICE_CIUDADES:
        if (
            filtro_pais
            and ciudad["codigo_pais"] != filtro_pais
        ):
            continue

        mejor_prioridad: int | None = None

        for nombre in ciudad["nombres_busqueda"]:
            if nombre == consulta:
                prioridad = 0
            elif nombre.startswith(consulta):
                prioridad = 1
            elif consulta in nombre:
                prioridad = 2
            else:
                continue

            if (
                mejor_prioridad is None
                or prioridad < mejor_prioridad
            ):
                mejor_prioridad = prioridad

        if mejor_prioridad is not None:
            coincidencias.append(
                (
                    mejor_prioridad,
                    -ciudad["poblacion"],
                    ciudad,
                )
            )

    coincidencias.sort(
        key=lambda elemento: (
            elemento[0],
            elemento[1],
            elemento[2]["nombre"],
        )
    )

    resultados: list[dict[str, Any]] = []

    for _, _, ciudad in coincidencias[:limite]:
        zona_horaria = obtener_zona_horaria(
            ciudad["latitud"],
            ciudad["longitud"],
        )

        partes_etiqueta = [ciudad["nombre"]]

        if ciudad["region"]:
            partes_etiqueta.append(ciudad["region"])

        partes_etiqueta.append(ciudad["pais"])

        resultados.append(
            {
                "id": ciudad["id"],
                "nombre": ciudad["nombre"],
                "region": ciudad["region"],
                "pais": ciudad["pais"],
                "codigo_pais": ciudad["codigo_pais"],
                "etiqueta": ", ".join(partes_etiqueta),
                "latitud": ciudad["latitud"],
                "longitud": ciudad["longitud"],
                "zona_horaria": zona_horaria,
                "poblacion": ciudad["poblacion"],
            }
        )

    return resultados


def obtener_ciudad_por_id(
    ciudad_id: str | int,
) -> dict[str, Any] | None:
    """
    Busca una ciudad por su identificador interno de GeoNames.
    """
    ciudad_id = str(ciudad_id)

    for ciudad in _INDICE_CIUDADES:
        if ciudad["id"] == ciudad_id:
            zona_horaria = obtener_zona_horaria(
                ciudad["latitud"],
                ciudad["longitud"],
            )

            return {
                "id": ciudad["id"],
                "nombre": ciudad["nombre"],
                "region": ciudad["region"],
                "pais": ciudad["pais"],
                "codigo_pais": ciudad["codigo_pais"],
                "latitud": ciudad["latitud"],
                "longitud": ciudad["longitud"],
                "zona_horaria": zona_horaria,
                "poblacion": ciudad["poblacion"],
            }

    return None