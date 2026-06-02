from typing import Literal

from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.exceptions import RequestValidationError
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field

from reglas.modelo_triaje import (
    evaluar_paciente,
    entrenar_modelo,
    obtener_accuracy,
    cargar_dataset,
    obtener_resumen_pandas,
    FEATURES,
    FEATURES_MODELO,
)


historial_triaje = []
contador_id = 1


app = FastAPI(
    title="Agente de Triaje Preventivo",
    description="Sistema de recomendación médica con árbol de decisión entrenado sobre dataset.",
    version="3.0"
)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):

    errores = []

    for error in exc.errors():
        campo = error["loc"][-1]
        mensaje = error["msg"]

        errores.append(f"{campo}: {mensaje}")

    return templates.TemplateResponse(
        request=request,
        name="error_validacion.html",
        context={
            "errores": errores
        },
        status_code=422
    )


# ──────────────────────────────────────────────
# Modelo Pydantic para validar los datos del paciente
# ──────────────────────────────────────────────

class PacienteInput(BaseModel):
    edad: float = Field(..., ge=0, le=120, description="Edad del paciente")
    frecuencia_cardiaca: float = Field(..., ge=20, le=250, description="Frecuencia cardíaca")
    presion_sistolica: float = Field(..., ge=50, le=260, description="Presión arterial sistólica")
    saturacion_oxigeno: float = Field(..., ge=50, le=100, description="Saturación de oxígeno")
    temperatura: float = Field(..., ge=30, le=45, description="Temperatura corporal")
    nivel_dolor: int = Field(..., ge=0, le=10, description="Nivel de dolor entre 0 y 10")
    cantidad_enfermedades_cronicas: int = Field(..., ge=0, le=10, description="Cantidad de enfermedades crónicas")
    visitas_previas_guardia: int = Field(..., ge=0, le=30, description="Visitas previas a guardia")
    modo_llegada: Literal["walk-in", "wheelchair", "ambulance"] = Field(
        ..., description="Modo de llegada del paciente"
    )


# ──────────────────────────────────────────────
# Formulario principal
# ──────────────────────────────────────────────

@app.get("/", response_class=HTMLResponse)
def formulario(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={}
    )


# ──────────────────────────────────────────────
# Evaluación del paciente desde formulario HTML
# ──────────────────────────────────────────────

@app.post("/resultado", response_class=HTMLResponse)
def resultado(
    request: Request,
    edad: float = Form(..., ge=0, le=120),
    frecuencia_cardiaca: float = Form(..., ge=20, le=250),
    presion_sistolica: float = Form(..., ge=50, le=260),
    saturacion_oxigeno: float = Form(..., ge=50, le=100),
    temperatura: float = Form(..., ge=30, le=45),
    nivel_dolor: int = Form(..., ge=0, le=10),
    cantidad_enfermedades_cronicas: int = Form(..., ge=0, le=10),
    visitas_previas_guardia: int = Form(..., ge=0, le=30),
    modo_llegada: Literal["walk-in", "wheelchair", "ambulance"] = Form(...)
):
    global contador_id

    # Se crea un objeto Pydantic para dejar explícita la validación del paciente.
    paciente = PacienteInput(
        edad=edad,
        frecuencia_cardiaca=frecuencia_cardiaca,
        presion_sistolica=presion_sistolica,
        saturacion_oxigeno=saturacion_oxigeno,
        temperatura=temperatura,
        nivel_dolor=nivel_dolor,
        cantidad_enfermedades_cronicas=cantidad_enfermedades_cronicas,
        visitas_previas_guardia=visitas_previas_guardia,
        modo_llegada=modo_llegada
    )

    resultado = evaluar_paciente(**paciente.model_dump())

    registro = {
        "id": contador_id,
        **paciente.model_dump(),
        "resultado": resultado
    }

    historial_triaje.append(registro)
    contador_id += 1

    return templates.TemplateResponse(
        request=request,
        name="resultado.html",
        context={**paciente.model_dump(), "resultado": resultado}
    )


# ──────────────────────────────────────────────
# Evaluación del paciente como API REST JSON
# ──────────────────────────────────────────────

@app.post("/api/evaluar")
def evaluar_api(paciente: PacienteInput):
    """Endpoint REST con validación Pydantic automática."""
    resultado = evaluar_paciente(**paciente.model_dump())
    return {
        "paciente_validado": paciente.model_dump(),
        "resultado": resultado
    }


# ──────────────────────────────────────────────
# Precisión del modelo
# ──────────────────────────────────────────────

@app.get("/modelo/accuracy")
def ver_accuracy():
    accuracy = obtener_accuracy()
    return {
        "descripcion": "Árbol de decisión entrenado sobre dataset de triaje con limpieza, normalización y métricas derivadas en Pandas",
        "features_originales": FEATURES,
        "features_modelo": FEATURES_MODELO,
        "precision_porcentaje": accuracy,
        "nota": "Evaluado sobre el 20% del dataset reservado para test (random_state=42)"
    }


@app.get("/modelo/reentrenar")
def reentrenar():
    """Fuerza el reentrenamiento del modelo si cambia el dataset."""
    from reglas import modelo_triaje
    modelo_triaje._MODELO_CACHED = None
    modelo_triaje._ACCURACY_CACHED = None
    modelo_triaje._STATS_CACHED = None
    modelo, accuracy, stats = entrenar_modelo()
    return {
        "mensaje": "Modelo reentrenado correctamente",
        "precision_porcentaje": accuracy,
        "variables_normalizadas": list(stats.keys())
    }


# ──────────────────────────────────────────────
# Dataset y resumen de procesamiento Pandas
# ──────────────────────────────────────────────

@app.get("/dataset")
def ver_dataset():
    df = cargar_dataset(procesado=True)
    return df.head(20).to_dict(orient="records")


@app.get("/dataset/resumen")
def resumen_dataset():
    return obtener_resumen_pandas()


# ──────────────────────────────────────────────
# Historial
# ──────────────────────────────────────────────

@app.get("/historial", response_class=HTMLResponse)
def ver_historial(request: Request):
    orden_prioridad = {
        "Crítica": 4,
        "Alta": 3,
        "Media": 2,
        "Baja": 1
    }

    historial_ordenado = sorted(
        historial_triaje,
        key=lambda x: orden_prioridad.get(x["resultado"]["prioridad"], 0),
        reverse=True
    )

    return templates.TemplateResponse(
        request=request,
        name="historial.html",
        context={"historial": historial_ordenado}
    )


@app.post("/dar_baja/{registro_id}")
def dar_baja(registro_id: int):
    global historial_triaje
    historial_triaje = [
        r for r in historial_triaje if r["id"] != registro_id
    ]
    return RedirectResponse(url="/historial", status_code=303)
