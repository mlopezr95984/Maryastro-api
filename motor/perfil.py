from datetime import datetime
from typing import Any
from zoneinfo import ZoneInfo

import swisseph as swe
from motor.firma import calcular_firma_energetica
from motor.subtipo import calcular_subtipo
from motor.aspectos import calcular_aspectos


PLANETAS = {
    "Sol": swe.SUN,
    "Luna": swe.MOON,
    "Mercurio": swe.MERCURY,
    "Venus": swe.VENUS,
    "Marte": swe.MARS,
    "Júpiter": swe.JUPITER,
    "Saturno": swe.SATURN,
    "Urano": swe.URANUS,
    "Neptuno": swe.NEPTUNE,
    "Plutón": swe.PLUTO,
    "Nodo Norte medio": swe.MEAN_NODE,
}


class PerfilEnergetico:
    def __init__(
        self,
        nombre: str,
        fecha_local: datetime,
        ciudad: str,
        latitud: float,
        longitud: float,
        zona_horaria: str,
        orbe: float = 6.0,
    ):
        # Datos de entrada
        self.nombre = nombre
        self.fecha_local = fecha_local
        self.ciudad = ciudad
        self.latitud = latitud
        self.longitud = longitud
        self.zona_horaria = zona_horaria
        self.orbe = orbe

        # Datos calculados de la carta
        self.fecha_utc: datetime | None = None
        self.dia_juliano: float | None = None
        self.cuspides: list[float] = []
        self.posiciones: dict[str, Any] = {}
        self.angulos: dict[str, float] = {}
        self.aspectos: list[dict[str, Any]] = []
        self.advertencias: list[str] = []

        # Resultados del Perfil Energético
        self.arquetipo_dominante: dict[str, Any] | None = None
        self.subtipo: dict[str, Any] | None = None
        self.dinamica_yin_yang: dict[str, Any] | None = None
        self.eje_nodal: dict[str, Any] | None = None
        self.arquetipo_complementario: dict[str, Any] | None = None

        # Interpretación futura
        self.interpretacion: str = ""

    @staticmethod
    def calcular_casa(
        longitud: float,
        cuspides: list[float],
    ) -> int | None:
        """
        Determina en qué casa se encuentra una longitud zodiacal.
        """

        longitud = longitud % 360

        for indice in range(12):
            inicio = cuspides[indice] % 360
            fin = cuspides[(indice + 1) % 12] % 360

            if inicio < fin:
                if inicio <= longitud < fin:
                    return indice + 1
            else:
                # Cruce entre Piscis y Aries: 360° / 0°.
                if longitud >= inicio or longitud < fin:
                    return indice + 1

        return None

    def preparar_fecha_local(self) -> datetime:
        """
        Comprueba que la fecha tenga la zona horaria correcta.

        Si la fecha recibida no tiene zona horaria, utiliza la zona
        indicada en zona_horaria.
        """

        zona = ZoneInfo(self.zona_horaria)

        if self.fecha_local.tzinfo is None:
            return self.fecha_local.replace(tzinfo=zona)

        return self.fecha_local.astimezone(zona)

    def calcular_cuerpo(
        self,
        dia_juliano: float,
        codigo: int,
    ) -> dict[str, Any]:
        """
        Calcula la longitud, velocidad, retrogradación y casa
        de un planeta o punto astrológico.
        """

        resultado, _flags = swe.calc_ut(
            dia_juliano,
            codigo,
            swe.FLG_SWIEPH | swe.FLG_SPEED,
        )

        longitud = resultado[0]
        velocidad = resultado[3]

        return {
            "longitud": longitud,
            "velocidad": velocidad,
            "retrogrado": velocidad < 0,
            "casa": self.calcular_casa(
                longitud,
                self.cuspides,
            ),
        }

    def calcular_carta(self) -> None:
        """
        Calcula la fecha UTC, el día juliano, las casas,
        los ángulos, los planetas y el eje nodal.
        """

        if not -90 <= self.latitud <= 90:
            raise ValueError(
                "La latitud debe estar entre -90 y 90 grados."
            )

        if not -180 <= self.longitud <= 180:
            raise ValueError(
                "La longitud debe estar entre -180 y 180 grados."
            )

        if not 0 <= self.orbe <= 10:
            raise ValueError(
                "El orbe debe estar entre 0 y 10 grados."
            )

        fecha_local_con_zona = self.preparar_fecha_local()
        self.fecha_local = fecha_local_con_zona

        self.fecha_utc = fecha_local_con_zona.astimezone(
            ZoneInfo("UTC")
        )

        hora_decimal = (
            self.fecha_utc.hour
            + self.fecha_utc.minute / 60
            + self.fecha_utc.second / 3600
            + self.fecha_utc.microsecond / 3_600_000_000
        )

        self.dia_juliano = swe.julday(
            self.fecha_utc.year,
            self.fecha_utc.month,
            self.fecha_utc.day,
            hora_decimal,
        )

        cuspides, ascmc = swe.houses(
            self.dia_juliano,
            self.latitud,
            self.longitud,
            b"P",
        )

        self.cuspides = list(cuspides)

        ascendente = ascmc[0]
        medio_cielo = ascmc[1]
        descendente = (ascendente + 180) % 360
        fondo_cielo = (medio_cielo + 180) % 360

        self.angulos = {
            "Ascendente": ascendente,
            "Medio Cielo": medio_cielo,
            "Descendente": descendente,
            "Fondo del Cielo": fondo_cielo,
        }

        self.posiciones = {}
        self.advertencias = []

        for nombre_cuerpo, codigo in PLANETAS.items():
            try:
                self.posiciones[nombre_cuerpo] = (
                    self.calcular_cuerpo(
                        self.dia_juliano,
                        codigo,
                    )
                )
            except swe.Error as error:
                self.advertencias.append(
                    f"No se pudo calcular {nombre_cuerpo}: {error}"
                )

        self.posiciones["Ascendente"] = {
            "longitud": ascendente,
            "velocidad": 0.0,
            "retrogrado": False,
            "casa": 1,
        }

        self.posiciones["Medio Cielo"] = {
            "longitud": medio_cielo,
            "velocidad": 0.0,
            "retrogrado": False,
            "casa": 10,
        }

        if "Nodo Norte medio" in self.posiciones:
            datos_nodo_norte = self.posiciones[
                "Nodo Norte medio"
            ]

            longitud_nodo_sur = (
                datos_nodo_norte["longitud"] + 180
            ) % 360

            self.posiciones["Nodo Sur medio"] = {
                "longitud": longitud_nodo_sur,
                "velocidad": datos_nodo_norte["velocidad"],
                "retrogrado": datos_nodo_norte["retrogrado"],
                "casa": self.calcular_casa(
                    longitud_nodo_sur,
                    self.cuspides,
                ),
            }

    def calcular(self) -> dict[str, Any]:

     """
     Ejecuta los cálculos disponibles del Perfil Energético.
     """

     self.calcular_carta()

     self.arquetipo_dominante = calcular_firma_energetica(
        self.posiciones
    )

     self.subtipo = calcular_subtipo(self.posiciones)

     self.aspectos = calcular_aspectos(
        self.posiciones,
        self.orbe
     )

     return self.obtener_resultado()

    def obtener_resultado(self) -> dict[str, Any]:
        """
        Devuelve información estructurada que podrán utilizar
        FastAPI, Wix o la aplicación de escritorio.
        """

        return {
            "datos": {
                "nombre": self.nombre,
                "fecha_local": self.fecha_local.isoformat(),
                "fecha_utc": (
                    self.fecha_utc.isoformat()
                    if self.fecha_utc
                    else None
                ),
                "ciudad": self.ciudad,
                "latitud": self.latitud,
                "longitud": self.longitud,
                "zona_horaria": self.zona_horaria,
                "orbe": self.orbe,
                "sistema_casas": "Placidus",
                "dia_juliano": self.dia_juliano,
            },
            "cuspides": self.cuspides,
            "angulos": self.angulos,
            "posiciones": self.posiciones,
            "advertencias": self.advertencias,
            "aspectos": self.aspectos,
            "arquetipo_dominante": self.arquetipo_dominante,
            "subtipo": self.subtipo,
            "dinamica_yin_yang": self.dinamica_yin_yang,
            "eje_nodal": self.eje_nodal,
            "arquetipo_complementario": (
                self.arquetipo_complementario
            ),
            "interpretacion": self.interpretacion,
        }