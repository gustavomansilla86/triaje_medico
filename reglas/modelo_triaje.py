import os

import joblib
import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier


ARCHIVO = "DATA/synthetic_medical_triage.csv"
MODELO_PATH = "DATA/modelo_triaje.pkl"
MODELO_VERSION = "3.0"

# Variables originales del dataset
FEATURES = [
    "age",
    "heart_rate",
    "systolic_blood_pressure",
    "oxygen_saturation",
    "body_temperature",
    "pain_level",
    "chronic_disease_count",
    "previous_er_visits"
]

# Nuevas columnas creadas con Pandas para enriquecer el análisis
FEATURES_DERIVADAS = [
    "score_signos_vitales",
    "riesgo_oxigenacion",
    "riesgo_temperatura",
    "riesgo_dolor",
    "riesgo_comorbilidad",
    "score_riesgo_total",
    "ratio_fc_presion"
]

# Columnas normalizadas utilizadas por el modelo
FEATURES_NORMALIZADAS = [f"{col}_norm" for col in FEATURES]

# Variables finales usadas en el entrenamiento
FEATURES_MODELO = FEATURES_NORMALIZADAS + FEATURES_DERIVADAS

FEATURE_LABELS = {
    "age": "Edad",
    "heart_rate": "Frecuencia cardíaca",
    "systolic_blood_pressure": "Presión sistólica",
    "oxygen_saturation": "Saturación de oxígeno",
    "body_temperature": "Temperatura corporal",
    "pain_level": "Nivel de dolor",
    "chronic_disease_count": "Enfermedades crónicas",
    "previous_er_visits": "Visitas previas a guardia"
}

# Rangos normales para generar motivos legibles
RANGOS_NORMALES = {
    "age": (0, 60),
    "heart_rate": (60, 100),
    "systolic_blood_pressure": (90, 140),
    "oxygen_saturation": (95, 100),
    "body_temperature": (36.0, 37.5),
    "pain_level": (0, 4),
    "chronic_disease_count": (0, 1),
    "previous_er_visits": (0, 2)
}


# ──────────────────────────────────────────────
# Limpieza, transformación y normalización con Pandas
# ──────────────────────────────────────────────

def cargar_dataset(procesado: bool = True):
    """Carga el dataset. Si procesado=True aplica limpieza y transformaciones Pandas."""
    df = pd.read_csv(ARCHIVO)

    if not procesado:
        return df

    df = limpiar_dataset(df)
    df = generar_columnas_derivadas(df)
    df, _ = normalizar_dataset(df)
    return df


def limpiar_dataset(df: pd.DataFrame) -> pd.DataFrame:
    """Limpieza básica: duplicados, infinitos, tipos numéricos, nulos y rangos extremos."""
    df = df.copy()

    # Elimina registros duplicados
    df = df.drop_duplicates()

    # Reemplaza infinitos por NaN para poder imputarlos
    df = df.replace([np.inf, -np.inf], np.nan)

    # Convierte columnas numéricas al tipo correcto
    columnas_numericas = FEATURES + ["triage_level"]
    for col in columnas_numericas:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # Imputación de nulos: mediana para variables clínicas, moda para la clase
    for col in FEATURES:
        df[col] = df[col].fillna(df[col].median())

    df["triage_level"] = df["triage_level"].fillna(df["triage_level"].mode()[0])

    # Control de rangos para evitar valores clínicamente imposibles
    df["age"] = df["age"].clip(0, 120)
    df["heart_rate"] = df["heart_rate"].clip(20, 250)
    df["systolic_blood_pressure"] = df["systolic_blood_pressure"].clip(50, 260)
    df["oxygen_saturation"] = df["oxygen_saturation"].clip(50, 100)
    df["body_temperature"] = df["body_temperature"].clip(30, 45)
    df["pain_level"] = df["pain_level"].clip(0, 10)
    df["chronic_disease_count"] = df["chronic_disease_count"].clip(0, 10)
    df["previous_er_visits"] = df["previous_er_visits"].clip(0, 30)

    return df


def generar_columnas_derivadas(df: pd.DataFrame) -> pd.DataFrame:
    """Genera métricas, scores y ratios para cumplir la capa Pandas de la rúbrica."""
    df = df.copy()

    df["riesgo_oxigenacion"] = (df["oxygen_saturation"] < 92).astype(int)
    df["riesgo_temperatura"] = ((df["body_temperature"] < 36) | (df["body_temperature"] > 38)).astype(int)
    df["riesgo_dolor"] = (df["pain_level"] >= 7).astype(int)
    df["riesgo_comorbilidad"] = (df["chronic_disease_count"] >= 2).astype(int)

    df["score_signos_vitales"] = (
        (df["heart_rate"] > 100).astype(int)
        + (df["systolic_blood_pressure"] < 90).astype(int)
        + (df["oxygen_saturation"] < 92).astype(int)
        + (df["body_temperature"] > 38).astype(int)
    )

    df["score_riesgo_total"] = (
        df["score_signos_vitales"]
        + df["riesgo_oxigenacion"]
        + df["riesgo_temperatura"]
        + df["riesgo_dolor"]
        + df["riesgo_comorbilidad"]
    )

    df["ratio_fc_presion"] = df["heart_rate"] / df["systolic_blood_pressure"].replace(0, np.nan)
    df["ratio_fc_presion"] = df["ratio_fc_presion"].fillna(df["ratio_fc_presion"].median())

    return df


def normalizar_dataset(df: pd.DataFrame):
    """Normalización Z-score: (valor - media) / desvío estándar."""
    df = df.copy()
    stats = {}

    for col in FEATURES:
        media = df[col].mean()
        desvio = df[col].std()

        if desvio == 0 or pd.isna(desvio):
            desvio = 1

        df[f"{col}_norm"] = (df[col] - media) / desvio
        stats[col] = {"media": float(media), "desvio": float(desvio)}

    return df, stats


def preparar_input_modelo(valores: dict, stats: dict) -> pd.DataFrame:
    """Aplica al paciente individual las mismas transformaciones usadas en entrenamiento."""
    df = pd.DataFrame([valores])
    df = generar_columnas_derivadas(df)

    for col in FEATURES:
        media = stats[col]["media"]
        desvio = stats[col]["desvio"]
        df[f"{col}_norm"] = (df[col] - media) / desvio

    return df[FEATURES_MODELO]


def obtener_resumen_pandas():
    """Resumen para mostrar en la demo qué limpieza y transformaciones se aplicaron."""
    df_original = pd.read_csv(ARCHIVO)
    nulos_antes = df_original.isnull().sum().to_dict()
    duplicados_antes = int(df_original.duplicated().sum())

    df_limpio = limpiar_dataset(df_original)
    df_procesado = generar_columnas_derivadas(df_limpio)
    df_procesado, _ = normalizar_dataset(df_procesado)

    return {
        "registros_originales": int(len(df_original)),
        "registros_procesados": int(len(df_procesado)),
        "duplicados_eliminados": duplicados_antes,
        "nulos_antes": nulos_antes,
        "nulos_despues": df_procesado.isnull().sum().to_dict(),
        "columnas_originales": FEATURES,
        "columnas_derivadas": FEATURES_DERIVADAS,
        "columnas_normalizadas": FEATURES_NORMALIZADAS,
        "decision_pandas": "Se limpiaron nulos y duplicados, se controlaron rangos clínicos, se generaron scores de riesgo y se normalizaron variables numéricas con Z-score."
    }


# ──────────────────────────────────────────────
# Entrenamiento del modelo
# ──────────────────────────────────────────────

def entrenar_modelo():
    """Entrena un árbol de decisión y guarda modelo, accuracy y estadísticas de normalización."""
    df_original = pd.read_csv(ARCHIVO)
    df = limpiar_dataset(df_original)
    df = generar_columnas_derivadas(df)
    df, stats = normalizar_dataset(df)

    X = df[FEATURES_MODELO]
    y = df["triage_level"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    modelo = DecisionTreeClassifier(max_depth=5, random_state=42)
    modelo.fit(X_train, y_train)

    y_pred = modelo.predict(X_test)
    accuracy = round(accuracy_score(y_test, y_pred) * 100, 2)

    os.makedirs(os.path.dirname(MODELO_PATH), exist_ok=True)
    joblib.dump(
        {
            "version": MODELO_VERSION,
            "modelo": modelo,
            "accuracy": accuracy,
            "stats": stats,
            "features_modelo": FEATURES_MODELO
        },
        MODELO_PATH
    )

    return modelo, accuracy, stats


# ──────────────────────────────────────────────
# Cache global
# ──────────────────────────────────────────────

_MODELO_CACHED = None
_ACCURACY_CACHED = None
_STATS_CACHED = None


def obtener_modelo():
    global _MODELO_CACHED, _ACCURACY_CACHED, _STATS_CACHED

    if _MODELO_CACHED is None:
        if os.path.exists(MODELO_PATH):
            datos = joblib.load(MODELO_PATH)

            # Si existe un modelo viejo, se reentrena automáticamente.
            if isinstance(datos, dict) and datos.get("version") == MODELO_VERSION:
                _MODELO_CACHED = datos["modelo"]
                _ACCURACY_CACHED = datos["accuracy"]
                _STATS_CACHED = datos["stats"]
            else:
                _MODELO_CACHED, _ACCURACY_CACHED, _STATS_CACHED = entrenar_modelo()
        else:
            _MODELO_CACHED, _ACCURACY_CACHED, _STATS_CACHED = entrenar_modelo()

    return _MODELO_CACHED


def obtener_accuracy():
    obtener_modelo()
    return _ACCURACY_CACHED


def obtener_stats():
    obtener_modelo()
    return _STATS_CACHED


# ──────────────────────────────────────────────
# Interpretación del nivel
# ──────────────────────────────────────────────

def interpretar_resultado(nivel):
    if nivel == 0:
        return "Reposo", "Baja"
    elif nivel == 1:
        return "Médico de cabecera", "Media"
    elif nivel == 2:
        return "Guardia", "Alta"
    elif nivel == 3:
        return "Guardia urgente", "Crítica"

    return "Revisión médica", "Media"


# ──────────────────────────────────────────────
# Generación de motivos legibles
# ──────────────────────────────────────────────

def generar_motivos(valores: dict, modo_llegada: str) -> list:
    """Compara los valores del paciente contra rangos normales."""
    motivos = []

    for feature, value in valores.items():
        low, high = RANGOS_NORMALES[feature]
        label = FEATURE_LABELS[feature]

        if feature == "oxygen_saturation" and value < low:
            motivos.append(f"Saturación de oxígeno baja: {round(value, 1)}%")
        elif feature == "body_temperature" and value > high:
            motivos.append(f"Temperatura elevada: {round(value, 1)} °C")
        elif feature == "body_temperature" and value < low:
            motivos.append(f"Temperatura baja: {round(value, 1)} °C")
        elif feature == "age" and value >= high:
            motivos.append(f"Edad de mayor riesgo: {int(value)} años")
        elif feature not in ("age", "oxygen_saturation", "body_temperature") and value > high:
            motivos.append(f"{label} elevado: {round(value, 1)}")

    if modo_llegada == "ambulance":
        motivos.append("Ingreso por ambulancia")
    elif modo_llegada == "wheelchair":
        motivos.append("Ingreso en silla de ruedas")

    return motivos if motivos else ["No se detectaron indicadores de urgencia"]


# ──────────────────────────────────────────────
# Evaluación del paciente
# ──────────────────────────────────────────────

def evaluar_paciente(
    edad,
    frecuencia_cardiaca,
    presion_sistolica,
    saturacion_oxigeno,
    temperatura,
    nivel_dolor,
    cantidad_enfermedades_cronicas,
    visitas_previas_guardia,
    modo_llegada
):
    modelo = obtener_modelo()
    stats = obtener_stats()

    valores = {
        "age": edad,
        "heart_rate": frecuencia_cardiaca,
        "systolic_blood_pressure": presion_sistolica,
        "oxygen_saturation": saturacion_oxigeno,
        "body_temperature": temperatura,
        "pain_level": nivel_dolor,
        "chronic_disease_count": cantidad_enfermedades_cronicas,
        "previous_er_visits": visitas_previas_guardia
    }

    X_input = preparar_input_modelo(valores, stats)

    # Predicción del árbol
    nivel = int(modelo.predict(X_input)[0])

    # Confianza de la clase predicha
    proba = modelo.predict_proba(X_input)[0]
    confianza = round(float(proba[nivel]) * 100, 1)

    # Ajuste clínico por modo de llegada
    if modo_llegada in ("ambulance", "wheelchair"):
        nivel = min(nivel + 1, 3)

    derivacion, prioridad = interpretar_resultado(nivel)
    motivos = generar_motivos(valores, modo_llegada)

    return {
        "triage_level_estimado": nivel,
        "prioridad": prioridad,
        "derivacion": derivacion,
        "puntaje": confianza,
        "motivos": motivos
    }
