from datetime import datetime

from fastapi import FastAPI

from motor import PerfilEnergetico


app = FastAPI(
    title="MaryAstro API",
    version="1.0",
)


@app.get("/")
def inicio():
    return {
        "mensaje": "MaryAstro API funcionando correctamente"
    }


@app.get("/prueba")
def prueba():
    return {
        "estado": "OK",
        "motor": "PerfilEnergetico importado correctamente",
    }


@app.get("/carta-prueba")
def carta_prueba():
    perfil = PerfilEnergetico(
        nombre="Prueba MaryAstro",
        fecha_local=datetime(
            1990,
            6,
            15,
            12,
            0,
        ),
        ciudad="Bogotá",
        latitud=4.7110,
        longitud=-74.0721,
        zona_horaria="America/Bogota",
        orbe=6.0,
    )

    return perfil.calcular()
