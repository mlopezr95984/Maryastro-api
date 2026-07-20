from datetime import datetime
from typing import Any
from zoneinfo import ZoneInfo

import swisseph as swe

from motor.aspectos import calcular_aspectos
from motor.dinamica import calcular_dinamica_yin_yang
from motor.firma import calcular_firma_energetica
from motor.subtipo import calcular_subtipo
from motor.complementario import calcular_arquetipo_complementario
from motor.nodos import calcular_eje_nodal
from motor.puentes import calcular_puentes_energeticos
from motor.reporte import generar_reporte



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
        self.posiciones: dict[str, dict[str, Any]] = {}
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
    def obtener_datos_zodiacales(
        longitud: float,
    ) -> tuple[str, float]:
        """
        Devuelve el nombre del signo y el grado dentro del signo
        para una longitud zodiacal.
        """

        longitud_normalizada = longitud % 360
        indice_signo = int(longitud_normalizada // 30)

        return (
            SIGNOS[indice_signo],
            longitud_normalizada % 30,
        )

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
        Calcula la longitud, el signo, el grado dentro del signo,
        la velocidad, la retrogradación y la casa de un cuerpo.
        """

        resultado, _flags = swe.calc_ut(
            dia_juliano,
            codigo,
            swe.FLG_SWIEPH | swe.FLG_SPEED,
        )

        longitud = resultado[0] % 360
        velocidad = resultado[3]
        signo, grado_en_signo = self.obtener_datos_zodiacales(
            longitud
        )

        return {
            "longitud": longitud,
            "signo": signo,
            "grado_en_signo": grado_en_signo,
            "velocidad": velocidad,
            "retrogrado": velocidad < 0,
            "casa": self.calcular_casa(
                longitud,
                self.cuspides,
            ),
        }

    def crear_posicion_angular(
        self,
        longitud: float,
        casa: int,
    ) -> dict[str, Any]:
        """
        Crea la estructura común para Ascendente y Medio Cielo.
        """

        longitud = longitud % 360
        signo, grado_en_signo = self.obtener_datos_zodiacales(
            longitud
        )

        return {
            "longitud": longitud,
            "signo": signo,
            "grado_en_signo": grado_en_signo,
            "velocidad": 0.0,
            "retrogrado": False,
            "casa": casa,
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

        ascendente = ascmc[0] % 360
        medio_cielo = ascmc[1] % 360
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

        self.posiciones["Ascendente"] = (
            self.crear_posicion_angular(
                ascendente,
                casa=1,
            )
        )

        self.posiciones["Medio Cielo"] = (
            self.crear_posicion_angular(
                medio_cielo,
                casa=10,
            )
        )

        if "Nodo Norte medio" in self.posiciones:
            datos_nodo_norte = self.posiciones[
                "Nodo Norte medio"
            ]

            longitud_nodo_sur = (
                datos_nodo_norte["longitud"] + 180
            ) % 360

            signo_nodo_sur, grado_nodo_sur = (
                self.obtener_datos_zodiacales(
                    longitud_nodo_sur
                )
            )

       
        self.posiciones["Nodo Sur medio"] = {
                "longitud": longitud_nodo_sur,
                "signo": signo_nodo_sur,
                "grado_en_signo": grado_nodo_sur,
                "velocidad": datos_nodo_norte["velocidad"],
                "retrogrado": datos_nodo_norte["retrogrado"],
                "casa": self.calcular_casa(
                    longitud_nodo_sur,
                    self.cuspides,
                ),
            }


    def obtener_cuspides_formateadas(
        self,
    ) -> list[dict[str, Any]]:
        """
        Devuelve las cúspides con su longitud absoluta, signo
        y grado dentro del signo.
        """

        resultado: list[dict[str, Any]] = []

        for numero_casa, longitud in enumerate(
            self.cuspides,
            start=1,
        ):
            signo, grado_en_signo = (
                self.obtener_datos_zodiacales(longitud)
            )

            resultado.append(
                {
                    "casa": numero_casa,
                    "longitud": longitud,
                    "signo": signo,
                    "grado_en_signo": grado_en_signo,
                }
            )

        return resultado

    def obtener_angulos_formateados(
        self,
    ) -> dict[str, dict[str, Any]]:
        """
        Devuelve los ángulos con su longitud absoluta, signo
        y grado dentro del signo.
        """

        resultado: dict[str, dict[str, Any]] = {}

        for nombre, longitud in self.angulos.items():
            signo, grado_en_signo = (
                self.obtener_datos_zodiacales(longitud)
            )

            resultado[nombre] = {
                "longitud": longitud,
                "signo": signo,
                "grado_en_signo": grado_en_signo,
            }

        return resultado

    def calcular(self) -> dict[str, Any]:
        """
        Ejecuta los cálculos disponibles del Perfil Energético.
        """

        self.calcular_carta()

        self.arquetipo_dominante = calcular_firma_energetica(
            self.posiciones
        )

        self.subtipo = calcular_subtipo(
            self.posiciones
        )

        self.aspectos = calcular_aspectos(
            self.posiciones,
            self.orbe,
        )

        self.dinamica_yin_yang = calcular_dinamica_yin_yang(
            self.aspectos
        )

        self.arquetipo_complementario = (
            calcular_arquetipo_complementario(
                firma=self.arquetipo_dominante,
                subtipo=self.subtipo,
                posiciones=self.posiciones,
            )
        )

        self.eje_nodal = calcular_eje_nodal(
            posiciones=self.posiciones,
            firma=self.arquetipo_dominante,
            subtipo=self.subtipo,
            complementario=self.arquetipo_complementario,
        )

        return self.obtener_resultado()

    def obtener_resultado(self):

        resultado = {
        "posiciones": self.posiciones,
        "cuspides": self.cuspides,
        "angulos": self.angulos,
        "aspectos": self.aspectos,
        "arquetipo_dominante": self.arquetipo_dominante,
        "subtipo": self.subtipo,
        "dinamica_yin_yang": self.dinamica_yin_yang,
        "eje_nodal": self.eje_nodal,
        "arquetipo_complementario": self.arquetipo_complementario,
        "interpretacion": self.interpretacion,
    }

        resultado["puentes_energeticos"] = calcular_puentes_energeticos(
        posiciones=resultado["posiciones"],
        arquetipo_complementario=resultado["arquetipo_complementario"],
    )

        resultado["reporte"] = generar_reporte(resultado)

        return resultado