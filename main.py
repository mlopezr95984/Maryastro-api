from fastapi import FastAPI

app = FastAPI(
    title="MaryAstro API",
    version="1.0"
)

@app.get("/")
def inicio():
    return {
        "mensaje": "MaryAstro API funcionando correctamente"
    }