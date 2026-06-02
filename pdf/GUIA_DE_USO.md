# Guía de Uso del Agente de Triaje Preventivo 🏥

Esta guía te explicará cómo poner en marcha y utilizar la aplicación de Triaje Preventivo para la toma de decisiones clínicas asistida por Machine Learning (Árbol de Decisión).

---

## 1. Requisitos Previos e Instalación

Antes de iniciar la aplicación, asegúrate de tener instalado **Python 3.8 o superior** y las librerías necesarias.

### Instalación de dependencias
Puedes instalar las librerías requeridas ejecutando el siguiente comando en tu terminal (en el directorio del proyecto):

```bash
pip install fastapi uvicorn pandas numpy scikit-learn jinja2 python-multipart joblib
```

*Nota: `python-multipart` es obligatorio en FastAPI para procesar datos provenientes de formularios HTML tradicionales.*

---

## 2. Cómo Iniciar la Aplicación

Tienes dos formas de iniciar la aplicación:

### Método A: Doble clic en el Ejecutador Automático (Recomendado)
Para evitar tener que abrir la terminal y aprender comandos, simplemente haz **doble clic** en el archivo:
👉 **`Iniciar_Servidor.bat`** (ubicado en la carpeta raíz del proyecto).

Este archivo por lotes ejecutará automáticamente las siguientes acciones:
1. Abrirá de forma automática tu navegador web en la dirección de la app: **[http://127.0.0.1:8000](http://127.0.0.1:8000)**.
2. Cargará el entorno virtual local (`.venv`) y lanzará el servidor FastAPI/Uvicorn.
3. *Para apagar la aplicación, solo debes cerrar esa ventana de la consola.*

### Método B: Ejecución manual desde la Terminal
Si prefieres iniciarla de manera manual, abre tu terminal en la carpeta raíz del proyecto y ejecuta:

*   **Sin activar el entorno (Ejecución Directa):**
    ```bash
    .\.venv\Scripts\uvicorn main:app --reload
    ```
*   **Activando el entorno previamente:**
    ```bash
    .\.venv\Scripts\Activate.ps1   # En PowerShell
    .venv\Scripts\activate.bat     # En CMD
    uvicorn main:app --reload
    ```

---

## 3. Uso de la Aplicación Paso a Paso

La aplicación consta de tres pantallas principales muy fáciles de usar:

### Paso 1: Carga de Datos en la Ficha de Triaje (Página Principal `/`)
Al ingresar a la aplicación web, verás un formulario llamado **Ficha de Triaje Preventivo** donde deberás completar los parámetros clínicos del paciente:
*   **Edad:** Edad del paciente (entre 0 y 120 años).
*   **Frecuencia cardíaca:** Latidos por minuto (LPM) (entre 20 y 250).
*   **Presión sistólica:** Presión arterial máxima (entre 50 y 260 mmHg).
*   **Saturación de oxígeno (%):** Porcentaje de oxígeno en sangre (entre 50% y 100%).
*   **Temperatura corporal:** Temperatura en °C (ej: `37.5`).
*   **Nivel de dolor (0 a 10):** Escala analógica del dolor (donde 0 es sin dolor y 10 es el peor dolor imaginable).
*   **Enfermedades crónicas:** Cantidad de patologías previas del paciente (hipertensión, diabetes, etc.).
*   **Visitas previas a guardia:** Historial de veces que asistió a emergencias recientemente.
*   **Modo de llegada:** Selecciona si el paciente llegó *Por sus propios medios (walk-in)*, en *Silla de ruedas (wheelchair)* o en *Ambulancia (ambulance)*.

Haz clic en el botón azul **"Evaluar paciente"** para enviar los datos.

---

### Paso 2: Análisis del Resultado del Triaje (`/resultado`)
Una vez enviado el formulario, la aplicación procesará los datos a través del Árbol de Decisión y te redirigirá a la pantalla de resultados, donde verás:
1.  **Recomendación de Derivación (Ej: "Guardia urgente", "Guardia", "Médico de cabecera", "Reposo").**
2.  **Nivel de Prioridad:** Representado con colores y categorías claras:
    *   🔴 **Crítica:** Atención inmediata.
    *   🟠 **Alta:** Atención prioritaria.
    *   🟡 **Media:** Atención general.
    *   🟢 **Baja:** No urgente.
3.  **Puntaje de Confianza:** El porcentaje de certeza que tiene el modelo de Machine Learning sobre esta clasificación.
4.  **Motivos detectados:** Una lista con las razones médicas específicas que justifican la decisión (ej: *"Saturación de oxígeno baja: 89%"* o *"Ingreso por ambulancia"*).
5.  **Datos ingresados:** Un resumen detallado para corroborar que la información cargada sea correcta.

Para continuar con otro paciente, presiona el botón **"Cargar otro paciente"** en la parte inferior.

---

### Paso 3: Gestión de Pacientes en Espera (`/historial`)
Si deseas ver todos los pacientes que han sido evaluados y se encuentran en lista de espera, haz clic en **"Ver historial de pacientes"** desde la pantalla principal o ve directamente a **[http://127.0.0.1:8000/historial](http://127.0.0.1:8000/historial)**.

*   **Orden de Prioridad Automático:** El historial ordena a los pacientes de forma inteligente. Los casos **Críticos** aparecen en primer lugar, seguidos de los de prioridad **Alta**, **Media** y finalmente **Baja**. Esto permite a los médicos saber instantáneamente a quién atender primero.
*   **Tarjetas visuales identificativas:** Cada tarjeta de paciente cuenta con un borde lateral coloreado según su nivel de urgencia para facilitar su identificación rápida en salas de espera con alta concurrencia.
*   **Botón "Dar de baja / Atendido":** Al atender a un paciente o darle de alta médica, haz clic en este botón para removerlo del historial activo.

---

## 4. Endpoints de la API y Funcionalidades Avanzadas

Como el backend está construido sobre **FastAPI**, cuenta con rutas avanzadas que exponen el comportamiento del modelo e integran el procesamiento en tiempo real:

1.  **Ver el Dataset Procesado:**  
    Si quieres ver las primeras 20 filas del dataset transformado por Pandas, ingresa a:  
    👉 **[http://127.0.0.1:8000/dataset](http://127.0.0.1:8000/dataset)**
2.  **Resumen de Calidad del Dataset:**  
    Muestra estadísticas sobre duplicados eliminados, nulos imputados y las transformaciones realizadas en la carga de datos:  
    👉 **[http://127.0.0.1:8000/dataset/resumen](http://127.0.0.1:8000/dataset/resumen)**
3.  **Precisión del Modelo (`Accuracy`):**  
    Para conocer la exactitud del Árbol de Decisión entrenado y las variables que utiliza, accede a:  
    👉 **[http://127.0.0.1:8000/modelo/accuracy](http://127.0.0.1:8000/modelo/accuracy)**
4.  **Forzar Reentrenamiento del Modelo:**  
    Si modificas el archivo del dataset original y deseas que el modelo aprenda de los nuevos datos inmediatamente sin reiniciar la app, haz una petición a:  
    👉 **[http://127.0.0.1:8000/modelo/reentrenar](http://127.0.0.1:8000/modelo/reentrenar)**
5.  **API REST JSON (`/api/evaluar`):**  
    Puedes enviar una solicitud POST con formato JSON desde herramientas como Postman o cualquier otro sistema para obtener la predicción directamente en formato JSON:
    
    *   **Método:** `POST`
    *   **URL:** `http://127.0.0.1:8000/api/evaluar`
    *   **Cuerpo (JSON):**
        ```json
        {
          "edad": 45.0,
          "frecuencia_cardiaca": 110.0,
          "presion_sistolica": 135.0,
          "saturacion_oxigeno": 91.0,
          "temperatura": 38.2,
          "nivel_dolor": 8,
          "cantidad_enfermedades_cronicas": 2,
          "visitas_previas_guardia": 1,
          "modo_llegada": "ambulance"
        }
        ```
