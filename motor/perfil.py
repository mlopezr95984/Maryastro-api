from datetime import datetime
from typing import Any


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
        self.cuspides: list[float] = []
        self.posiciones: dict[str, Any] = {}
        self.aspectos: list[dict[str, Any]] = []

        # Resultados del Perfil Energético
        self.arquetipo_dominante: dict[str, Any] | None = None
        self.subtipo: dict[str, Any] | None = None
        self.dinamica_yin_yang: dict[str, Any] | None = None
        self.eje_nodal: dict[str, Any] | None = None
        self.arquetipo_complementario: dict[str, Any] | None = None

        # Interpretación futura
        self.interpretacion: str = ""

    def calcular(self) -> dict[str, Any]:
        """
        Ejecutará todos los cálculos del Perfil Energético.
        Por ahora solo devuelve la estructura inicial.
        """
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
                "ciudad": self.ciudad,
                "latitud": self.latitud,
                "longitud": self.longitud,
                "zona_horaria": self.zona_horaria,
                "orbe": self.orbe,
            },
            "arquetipo_dominante": self.arquetipo_dominante,
            "subtipo": self.subtipo,
            "dinamica_yin_yang": self.dinamica_yin_yang,
            "eje_nodal": self.eje_nodal,
            "arquetipo_complementario": self.arquetipo_complementario,
            "interpretacion": self.interpretacion,
        }