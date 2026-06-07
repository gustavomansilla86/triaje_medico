@echo off
title Servidor del Agente de Triaje Preventivo
echo 65001 > nul

:: Asegurar que el directorio de trabajo siempre sea el del script
cd /d "%~dp0"

echo =====================================================================
echo INICIANDO EL AGENTE DE TRIAJE PREVENTIVO V3.0
echo =====================================================================
echo.

if not exist ".venv\Scripts\python.exe" (
    echo.
    echo =====================================================================
    echo [ERROR] No se encontro el entorno virtual .venv en esta carpeta.
    echo Por favor, crea el entorno virtual e instala las dependencias primero.
    echo =====================================================================
    echo.
    pause
    exit /b
)

echo [1/2] Abriendo el navegador web en http://127.0.0.1:8000 ...
start explorer "http://127.0.0.1:8000"

echo [2/2] Lanzando el servidor local con FastAPI y Uvicorn...
echo.
echo ---------------------------------------------------------------------
echo IMPORTANTE: No cierres esta ventana mientras uses la aplicacion.
echo Para apagar el servidor, cierra esta ventana o presiona Ctrl + C.
echo ---------------------------------------------------------------------
echo.

".venv\Scripts\python.exe" -m uvicorn main:app --reload
pause
