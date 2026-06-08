# Agente de Triaje Preventivo v3.0

Este proyecto es una aplicación web y API REST diseñada para automatizar y recomendar la categorización de pacientes en un sistema de **Triaje Médico**. Utiliza técnicas de procesamiento de datos y un modelo de aprendizaje automático basado en un árbol de decisión entrenado sobre un dataset sintético de registros clínicos.

---

## 👥 Autores y Colaboradores
El desarrollo de este proyecto fue realizado por:
*   **Nancy Julieta Cassano**
*   **Mariano Buet**
*   **Gustavo Mansilla**

---

## 📝 Descripción del Proyecto
El **Agente de Triaje Preventivo** evalúa la prioridad de atención médica de un paciente a partir de una serie de signos vitales e indicadores clínicos.

### Características Principales:
*   **Interfaz de Usuario Interactiva**: Formulario web para ingresar datos clínicos del paciente de forma sencilla y directa.
*   **Motor de Reglas y Machine Learning**:
    *   Entrena un clasificador de árbol de decisión (`DecisionTreeClassifier` de `scikit-learn`) con profundidad máxima controlada para clasificar el nivel de urgencia.
    *   Preprocesamiento robusto en Pandas: Imputación de nulos por mediana/moda, eliminación de duplicados, limitación de rangos biológicos coherentes y normalización Z-Score.
    *   Generación de variables derivadas (scores de riesgo de signos vitales, índices de riesgo combinados y ratios fisiológicos).
    *   Ajuste clínico dinámico según el modo de llegada del paciente (ej. la ambulancia o silla de ruedas incrementa el nivel de urgencia de forma preventiva).
*   **API REST**: Endpoints `/api/evaluar`, `/modelo/accuracy`, `/modelo/reentrenar`, `/dataset` y `/dataset/resumen` para consultar la precisión del modelo, forzar su reentrenamiento, visualizar datos del procesamiento y realizar integraciones.
*   **Historial Clínico**: Vista ordenada por prioridad de pacientes ingresados, que permite llevar el control y dar de alta/baja registros del flujo de atención.

---

## 🛠️ Tecnologías Utilizadas
*   **Backend & API**: Python, [FastAPI](https://fastapi.tiangolo.com/), Uvicorn, Pydantic
*   **Procesamiento de Datos & Machine Learning**: Pandas, NumPy, Scikit-learn, Joblib
*   **Frontend**: HTML5, CSS3, Jinja2 Templates (Renderizado del lado del servidor)

---

## 📂 Estructura del Proyecto
*   [main.py](file:///c:/Users/gusta/OneDrive/Desktop/TP-Triaje_Medico-FINAL/triajle_medico/main.py): Archivo principal que expone los endpoints de FastAPI y maneja el flujo de la aplicación.
*   [reglas/modelo_triaje.py](file:///c:/Users/gusta/OneDrive/Desktop/TP-Triaje_Medico-FINAL/triajle_medico/reglas/modelo_triaje.py): Contiene las funciones de carga de datos, limpieza con Pandas, ingeniería de variables, entrenamiento y evaluación del modelo predictivo.
*   `DATA/`: Directorio donde se encuentra el dataset original (`synthetic_medical_triage.csv`) y se almacena el modelo serializado (`modelo_triaje.pkl`).
*   `templates/`: Plantillas HTML utilizadas por FastAPI para renderizar las vistas web ([index.html](file:///c:/Users/gusta/OneDrive/Desktop/TP-Triaje_Medico-FINAL/triajle_medico/templates/index.html), [resultado.html](file:///c:/Users/gusta/OneDrive/Desktop/TP-Triaje_Medico-FINAL/triajle_medico/templates/resultado.html), [historial.html](file:///c:/Users/gusta/OneDrive/Desktop/TP-Triaje_Medico-FINAL/triajle_medico/templates/historial.html) y [error_validacion.html](file:///c:/Users/gusta/OneDrive/Desktop/TP-Triaje_Medico-FINAL/triajle_medico/templates/error_validacion.html)).
*   `static/`: Contiene los archivos estáticos de la interfaz (`styles.css`).
*   [requirements.txt](file:///c:/Users/gusta/OneDrive/Desktop/TP-Triaje_Medico-FINAL/triajle_medico/requirements.txt): Archivo de dependencias del proyecto.
*   [Iniciar_Servidor.bat](file:///c:/Users/gusta/OneDrive/Desktop/TP-Triaje_Medico-FINAL/triajle_medico/Iniciar_Servidor.bat): Script automatizado en Windows para levantar el servidor web local con recarga en caliente y abrir el navegador en la URL correcta.

---

## 🚀 Instalación y Ejecución

### Requisitos previos:
*   Python 3.10 o superior instalado en el sistema.

### Instrucciones de Configuración rápida:
1.  Abre una terminal o consola de comandos en la carpeta raíz del proyecto.
2.  Crea un entorno virtual:
    ```bash
    python -m venv .venv
    ```
3.  Activa el entorno virtual:
    *   En Windows (PowerShell): `.venv\Scripts\Activate.ps1`
    *   En Windows (CMD): `.venv\Scripts\activate.bat`
    *   En macOS/Linux: `source .venv/bin/activate`
4.  Instala las dependencias del proyecto:
    ```bash
    pip install -r requirements.txt
    ```

### Ejecutar la Aplicación:
*   **Opción 1 (Windows)**: Haz doble clic en el archivo [Iniciar_Servidor.bat](file:///c:/Users/gusta/OneDrive/Desktop/TP-Triaje_Medico-FINAL/triajle_medico/Iniciar_Servidor.bat). Esto abrirá de forma automática tu navegador en `http://127.0.0.1:8000` e iniciará el servidor de desarrollo.
*   **Opción 2 (Consola)**: Ejecuta el siguiente comando en la raíz del proyecto (con el entorno virtual activo):
    ```bash
    uvicorn main:app --reload
    ```
    Luego abre tu navegador preferido e ingresa a `http://127.0.0.1:8000`.

---
en su defecto se prodria usar la siguiente pagina de manera online

https://triaje-medico.onrender.com/
