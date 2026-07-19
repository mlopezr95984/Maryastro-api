# ciudades.py

from __future__ import annotations

import unicodedata
from collections import defaultdict
from functools import lru_cache
from typing import Any

import geonamescache
from timezonefinder import TimezoneFinder


# =========================================================
# INICIALIZACIÓN
# =========================================================

_gc = geonamescache.GeonamesCache()
_tf = TimezoneFinder()

_CIUDADES_ORIGINALES = _gc.get_cities()
_PAISES = _gc.get_countries()

# Lista procesada de ciudades.
_CIUDADES: list[dict[str, Any]] = []

# Índice:
# "bo" -> posiciones de ciudades cuyos nombres comienzan por "bo".
_INDICE_PREFIJOS: dict[str, list[int]] = defaultdict(list)


# =========================================================
# UTILIDADES
# =========================================================

def normalizar_texto(texto: str) -> str:
    """
    Convierte el texto a minúsculas, elimina tildes
    y normaliza espacios.

    Ejemplos:
        Bogotá        -> bogota
        Ciudad de México -> ciudad de mexico
    """
    if not texto:
        return ""

    texto = " ".join(texto.strip().casefold().split())

    return "".join(
        caracter
        for caracter in unicodedata.normalize("NFKD", texto)
        if not unicodedata.combining(caracter)
    )


def _convertir_entero(valor: Any, default: int = 0) -> int:
    try:
        return int(valor or default)
    except (TypeError, ValueError):
        return default


def _convertir_float(valor: Any) -> float | None:
    try:
        return float(valor)
    except (TypeError, ValueError):
        return None


def _obtener_nombre_pais(codigo_pais: str) -> str:
    datos_pais = _PAISES.get(codigo_pais, {})
    return datos_pais.get("name", codigo_pais)


def _obtener_nombres_alternativos(datos: dict[str, Any]) -> list[str]:
    """
    Convierte alternatenames en una lista segura.
    """
    alternativos = datos.get("alternatenames", [])

    if isinstance(alternativos, str):
        alternativos = [
            nombre.strip()
            for nombre in alternativos.split(",")
            if nombre.strip()
        ]

    if not isinstance(alternativos, list):
        return []

    return [
        str(nombre).strip()
        for nombre in alternativos
        if str(nombre).strip()
    ]


# =========================================================
# CONSTRUCCIÓN DEL ÍNDICE
# =========================================================

def _cargar_ciudades() -> None:
    """
    Procesa las ciudades de geonamescache una sola vez
    cuando se importa este módulo.
    """
    for geoname_id, datos in _CIUDADES_ORIGINALES.items():
        nombre = str(datos.get("name", "")).strip()

        if not nombre:
            continue

        latitud = _convertir_float(datos.get("latitude"))
        longitud = _convertir_float(datos.get("longitude"))

        if latitud is None or longitud is None:
            continue

        codigo_pais = str(
            datos.get("countrycode", "")
        ).strip().upper()

        pais = _obtener_nombre_pais(codigo_pais)
        poblacion = _convertir_entero(datos.get("population"))

        nombre_normalizado = normalizar_texto(nombre)

        if len(nombre_normalizado) < 2:
            continue

        nombres_alternativos = _obtener_nombres_alternativos(datos)

        nombres_busqueda = {nombre_normalizado}

        for nombre_alternativo in nombres_alternativos:
            normalizado = normalizar_texto(nombre_alternativo)

            if normalizado:
                nombres_busqueda.add(normalizado)

        ciudad = {
            "id": str(geoname_id),
            "nombre": nombre,
            "nombre_normalizado": nombre_normalizado,
            "nombres_busqueda": tuple(nombres_busqueda),
            "pais": pais,
            "codigo_pais": codigo_pais,
            "latitud": latitud,
            "longitud": longitud,
            "poblacion": poblacion,
            "zona_horaria_original": datos.get("timezone"),
            "admin1code": str(
                datos.get("admin1code", "")
            ).strip(),
        }

        posicion = len(_CIUDADES)
        _CIUDADES.append(ciudad)

        # Indexamos la ciudad por las dos primeras letras
        # de su nombre y de sus nombres alternativos.
        prefijos_agregados: set[str] = set()

        for nombre_busqueda in nombres_busqueda:
            if len(nombre_busqueda) < 2:
                continue

            prefijo = nombre_busqueda[:2]

            if prefijo not in prefijos_agregados:
                _INDICE_PREFIJOS[prefijo].append(posicion)
                prefijos_agregados.add(prefijo)


_cargar_ciudades()


# =========================================================
# ZONA HORARIA
# =========================================================

@lru_cache(maxsize=10_000)
def obtener_zona_horaria(
    latitud: float,
    longitud: float,
    zona_guardada: str | None = None,
) -> str | None:
    """
    Usa primero la zona horaria incluida en geonamescache.
    Si no está disponible, la calcula con timezonefinder.
    """
    if zona_guardada:
        return str(zona_guardada)

    return _tf.timezone_at(
        lat=latitud,
        lng=longitud,
    )


# =========================================================
# BÚSQUEDA
# =========================================================

def _calcular_prioridad(
    consulta: str,
    ciudad: dict[str, Any],
) -> int | None:
    """
    Asigna prioridad a cada coincidencia:

    0 = nombre principal exacto
    1 = nombre alternativo exacto
    2 = nombre principal comienza por la consulta
    3 = nombre alternativo comienza por la consulta
    4 = nombre principal contiene la consulta
    5 = nombre alternativo contiene la consulta
    """
    nombre_principal = ciudad["nombre_normalizado"]
    nombres = ciudad["nombres_busqueda"]

    if nombre_principal == consulta:
        return 0

    if consulta in nombres:
        return 1

    if nombre_principal.startswith(consulta):
        return 2

    if any(
        nombre.startswith(consulta)
        for nombre in nombres
    ):
        return 3

    if consulta in nombre_principal:
        return 4

    if any(
        consulta in nombre
        for nombre in nombres
    ):
        return 5

    return None


def _preparar_resultado(
    ciudad: dict[str, Any],
) -> dict[str, Any]:
    zona_horaria = obtener_zona_horaria(
        latitud=ciudad["latitud"],
        longitud=ciudad["longitud"],
        zona_guardada=ciudad["zona_horaria_original"],
    )

    etiqueta = f'{ciudad["nombre"]}, {ciudad["pais"]}'

    return {
        "id": ciudad["id"],
        "nombre": ciudad["nombre"],
        "pais": ciudad["pais"],
        "codigo_pais": ciudad["codigo_pais"],
        "etiqueta": etiqueta,
        "latitud": ciudad["latitud"],
        "longitud": ciudad["longitud"],
        "zona_horaria": zona_horaria,
        "poblacion": ciudad["poblacion"],
    }


@lru_cache(maxsize=2_000)
def _buscar_ciudades_cache(
    consulta: str,
    limite: int,
    codigo_pais: str,
) -> tuple[tuple[tuple[str, Any], ...], ...]:
    """
    Versión interna cacheada.

    Devuelve tuplas para que lru_cache pueda almacenar
    los resultados de manera segura.
    """
    if len(consulta) < 2:
        return tuple()

    prefijo = consulta[:2]
    posiciones = _INDICE_PREFIJOS.get(prefijo, [])

    coincidencias: list[
        tuple[int, int, str, dict[str, Any]]
    ] = []

    for posicion in posiciones:
        ciudad = _CIUDADES[posicion]

        if (
            codigo_pais
            and ciudad["codigo_pais"] != codigo_pais
        ):
            continue

        prioridad = _calcular_prioridad(
            consulta=consulta,
            ciudad=ciudad,
        )

        if prioridad is None:
            continue

        coincidencias.append(
            (
                prioridad,
                -ciudad["poblacion"],
                ciudad["nombre_normalizado"],
                ciudad,
            )
        )

    coincidencias.sort(
        key=lambda item: (
            item[0],
            item[1],
            item[2],
        )
    )

    resultados: list[dict[str, Any]] = []
    ids_agregados: set[str] = set()

    for _, _, _, ciudad in coincidencias:
        if ciudad["id"] in ids_agregados:
            continue

        resultados.append(
            _preparar_resultado(ciudad)
        )
        ids_agregados.add(ciudad["id"])

        if len(resultados) >= limite:
            break

    # Convertimos los diccionarios en tuplas para la caché.
    return tuple(
        tuple(resultado.items())
        for resultado in resultados
    )


def buscar_ciudades(
    texto: str,
    limite: int = 8,
    codigo_pais: str | None = None,
) -> list[dict[str, Any]]:
    """
    Busca ciudades para el autocompletado de Wix.

    Ejemplos:
        buscar_ciudades("Bog")
        buscar_ciudades("Med", limite=10)
        buscar_ciudades("Santiago", codigo_pais="CL")
    """
    consulta = normalizar_texto(texto)

    if len(consulta) < 2:
        return []

    limite = max(1, min(int(limite), 20))

    pais_normalizado = (
        codigo_pais.strip().upper()
        if codigo_pais
        else ""
    )

    resultados_cache = _buscar_ciudades_cache(
        consulta=consulta,
        limite=limite,
        codigo_pais=pais_normalizado,
    )

    return [
        dict(resultado)
        for resultado in resultados_cache
    ]


# =========================================================
# BÚSQUEDA POR ID
# =========================================================

@lru_cache(maxsize=5_000)
def obtener_ciudad_por_id(
    ciudad_id: str | int,
) -> dict[str, Any] | None:
    """
    Obtiene una ciudad usando el identificador de GeoNames.
    """
    identificador = str(ciudad_id)

    datos = _CIUDADES_ORIGINALES.get(identificador)

    if datos is None:
        # Algunas versiones podrían usar claves numéricas.
        try:
            datos = _CIUDADES_ORIGINALES.get(
                int(identificador)
            )
        except (TypeError, ValueError):
            datos = None

    if datos is None:
        return None

    nombre = str(datos.get("name", "")).strip()
    latitud = _convertir_float(datos.get("latitude"))
    longitud = _convertir_float(datos.get("longitude"))

    if not nombre or latitud is None or longitud is None:
        return None

    codigo_pais = str(
        datos.get("countrycode", "")
    ).strip().upper()

    zona_horaria = obtener_zona_horaria(
        latitud=latitud,
        longitud=longitud,
        zona_guardada=datos.get("timezone"),
    )

    return {
        "id": identificador,
        "nombre": nombre,
        "pais": _obtener_nombre_pais(codigo_pais),
        "codigo_pais": codigo_pais,
        "latitud": latitud,
        "longitud": longitud,
        "zona_horaria": zona_horaria,
        "poblacion": _convertir_entero(
            datos.get("population")
        ),
    }


# =========================================================
# PRUEBA LOCAL
# =========================================================

if __name__ == "__main__":
    print(f"Ciudades cargadas: {len(_CIUDADES):,}")
    print(f"Prefijos indexados: {len(_INDICE_PREFIJOS):,}")
    print()

    pruebas = [
        "Bog",
        "Med",
        "Cartag",
        "Madrid",
        "Santiago",
    ]

    for prueba in pruebas:
        print(f'Búsqueda: "{prueba}"')

        resultados = buscar_ciudades(
            texto=prueba,
            limite=8,
        )

        for resultado in resultados:
            print(
                f'  - {resultado["etiqueta"]} '
                f'({resultado["zona_horaria"]})'
            )

        print()