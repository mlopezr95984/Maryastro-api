from datetime import date, datetime, time
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from motor import PerfilEnergetico


app = FastAPI(
    title="MaryAstro API",
    version="1.1.0",
    description=(
        "API para calcular la carta natal y el Perfil Energético "
        "de MaryAstro."
    ),
)


# Durante la primera integración con Wix no utilizamos cookies,
# sesiones ni credenciales. Por eso podemos permitir temporalmente
# solicitudes desde cualquier origen.
#
# Más adelante podremos reemplazar ["*"] por los dominios concretos
# de MaryAstro y de la vista previa de Wix.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)


class DatosPerfil(BaseModel):
    """
    Datos que enviará Wix para calcular un Perfil Energético.
    """

    nombre: str = Field(
        min_length=1,
        max_length=120,
        examples=["María López"],
    )
    fecha: date = Field(
        examples=["1990-06-15"],
    )
    hora: time = Field(
        examples=["12:00:00"],
    )
    ciudad: str = Field(
        min_length=1,
        max_length=150,
        examples=["Bogotá"],
    )
    latitud: float = Field(
        ge=-90,
        le=90,
        examples=[4.711],
    )
    longitud: float = Field(
        ge=-180,
        le=180,
        examples=[-74.0721],
    )
    zona_horaria: str = Field(
        min_length=1,
        examples=["America/Bogota"],
    )
    orbe: float = Field(
        default=6.0,
        ge=0,
        le=10,
        examples=[6.0],
    )


@app.get("/", summary="Inicio")
def inicio() -> dict[str, str]:
    """
    Confirma que la API está activa.
    """

    return {
        "mensaje": "MaryAstro API está funcionando.",
        "version": app.version,
    }


@app.get("/prueba", summary="Prueba")
def prueba() -> dict[str, str]:
    """
    Endpoint mínimo para comprobar la respuesta del servidor.
    """

    return {
        "estado": "ok",
        "servicio": "MaryAstro API",
    }


def ejecutar_calculo(
    *,
    nombre: str,
    fecha_local: datetime,
    ciudad: str,
    latitud: float,
    longitud: float,
    zona_horaria: str,
    orbe: float,
) -> dict[str, Any]:
    """
    Crea y ejecuta el Perfil Energético.

    Esta función evita repetir la construcción de PerfilEnergetico
    entre el endpoint de prueba y el endpoint público.
    """

    try:
        perfil = PerfilEnergetico(
            nombre=nombre,
            fecha_local=fecha_local,
            ciudad=ciudad,
            latitud=latitud,
            longitud=longitud,
            zona_horaria=zona_horaria,
            orbe=orbe,
        )

        return perfil.calcular()

    except (ValueError, KeyError) as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        ) from error

    except Exception as error:
        print(
            "Error inesperado al calcular el Perfil Energético:",
            repr(error),
        )

        raise HTTPException(
            status_code=500,
            detail=(
                "No fue posible calcular el Perfil Energético. "
                "Revisa los datos e inténtalo nuevamente."
            ),
        ) from error


@app.get("/carta-prueba", summary="Carta de prueba")
def carta_prueba() -> dict[str, Any]:
    """
    Calcula una carta fija para verificar que el motor completo
    continúa funcionando después de cada despliegue.
    """

    return ejecutar_calculo(
        nombre="Prueba MaryAstro",
        fecha_local=datetime(
            year=1990,
            month=6,
            day=15,
            hour=12,
            minute=0,
        ),
        ciudad="Bogotá",
        latitud=4.711,
        longitud=-74.0721,
        zona_horaria="America/Bogota",
        orbe=6.0,
    )


@app.post(
    "/perfil-energetico",
    summary="Calcular Perfil Energético",
)
def calcular_perfil_energetico(
    datos: DatosPerfil,
) -> dict[str, Any]:
    """
    Recibe los datos de una persona y devuelve su carta natal
    y su Perfil Energético completo.

    Este será el endpoint que consumirá Wix.
    """

    fecha_local = datetime.combine(
        datos.fecha,
        datos.hora,
    )

    return ejecutar_calculo(
        nombre=datos.nombre.strip(),
        fecha_local=fecha_local,
        ciudad=datos.ciudad.strip(),
        latitud=datos.latitud,
        longitud=datos.longitud,
        zona_horaria=datos.zona_horaria.strip(),
        orbe=datos.orbe,
    )

