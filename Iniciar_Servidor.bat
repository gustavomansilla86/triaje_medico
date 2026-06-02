@echo off
title Servidor del Agente de Triaje Preventivo
:: Habilitar codificación UTF-8 para mostrar tildes y caracteres especiales correctamente
chcp 65001 > nul

echo =====================================================================
echo          INICIANDO EL AGENTE DE TRIAJE PREVENTIVO V3.0
echo =====================================================================
echo.
echo [1/2] Abriendo el navegador web en http://127.0.0.1:8000 ...
start "" "http://127.0.0.1:8000"

echo [2/2] Lanzando el servidor local con FastAPI y Uvicorn...
echo.
echo ---------------------------------------------------------------------
echo  IMPORTANTE: No cierres esta ventana mientras uses la aplicación.
echo  Para apagar el servidor, cierra esta ventana o presiona Ctrl + C.
echo ---------------------------------------------------------------------
echo.

:: Comprobar si existe el entorno virtual e iniciar uvicorn
if exist "%~dp0.venv\Scripts\uvicorn.exe" (
    "%~dp0.venv\Scripts\uvicorn.exe" main:app --reload
) else (
    echo.
    echo =====================================================================
    echo [ERROR] No se encontró el entorno virtual (.venv) en esta carpeta.
    echo Asegúrate de que el proyecto contenga la carpeta '.venv'.
    echo =====================================================================
    echo.
    pause
)
