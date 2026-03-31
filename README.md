# 🧠 IA Assistant XBlock - Open edX (UAGRM)

![Open edX](https://img.shields.io/badge/Open%20edX-Framework-blue?logo=openedx)
![Python](https://img.shields.io/badge/Python-3.12-yellow?logo=python)
![Django](https://img.shields.io/badge/Django-5.2-green?logo=django)
![Status](https://img.shields.io/badge/Status-Development-orange)

**Asistente Inteligente integrado en Open edX para la generación dinámica de contenido educativo y apoyo al aprendizaje personalizado utilizando Modelos de Lenguaje Avanzados (LLM).**

Este repositorio contiene el entorno de desarrollo profesional, configurado específicamente para trabajar de manera local en Windows sin depender de contenedores pesados. Utiliza el **Framework oficial de XBlock** y el **Workbench SDK** como simulador.

---

## 🏗️ Arquitectura y Estructura del Repositorio

Para mantener el código limpio y profesional, este proyecto utiliza una arquitectura modular basada en **Git Submodules**. Esto significa que no mezclamos el código base de Open edX con el código de nuestra Inteligencia Artificial.

| Directorio / Archivo | Descripción Técnica |
| :--- | :--- |
| 📁 `XBlock/` | **Framework Core:** Es un submódulo que apunta al repositorio oficial de Open edX. Contiene las clases base (`XBlock`, `Fragment`, `Scope`) necesarias para que el plugin exista. |
| 📁 `xblock-sdk/` | **Workbench (Simulador):** Entorno de pruebas basado en Django. Permite levantar un servidor local (`localhost:8000`) para renderizar y probar el XBlock sin necesidad de instalar toda la plataforma LMS de edX. |
| 📁 `ia_assistant/` | **(En desarrollo)** Directorio principal donde residirá la lógica de Python, los templates HTML y los estilos CSS de la Inteligencia Artificial. |
| 📄 `.gitignore` | Configurado para excluir entornos virtuales (`venv/`), binarios de Python (`__pycache__`) y logs locales de bases de datos para mantener el repositorio ligero. |

---

## ⚙️ Requisitos Previos (Prerequisites)

Antes de iniciar, asegúrate de tener instalado en tu máquina (Windows/Linux/macOS):
* **Python 3.12+** (Asegúrate de agregarlo al PATH).
* **Git** (Para el control de versiones).
* **Visual Studio Code** (O tu IDE de preferencia).

---

## 🚀 Guía de Instalación y Despliegue Local

Sigue **estrictamente** este orden para levantar el proyecto sin errores de dependencias. 

### Paso 1: Clonar el Repositorio
Al clonar, asegúrate de inicializar los submódulos para descargar el Framework y el SDK.
```powershell
git clone [https://github.com/Mau8877/ia-xblock-assistant.git](https://github.com/Mau8877/ia-xblock-assistant.git)
cd ia-xblock-assistant
```

---

### Paso 2: Configurar el Entorno Virtual (Aislamiento)
Es mandatorio usar un entorno virtual para no contaminar el sistema operativo con librerías de edX.
```powershell
python -m venv venv
# Activar en Windows:
.\venv\Scripts\activate
# (Si usas Linux/Mac: source venv/bin/activate)
```

---

### Paso 3: Instalar el Core Framework
Primero, registramos la librería base de XBlock en el entorno.
```powershell
cd XBlock
pip install -e .
cd ..
```

---

### Paso 4: Instalar y Configurar el SDK (Workbench)
El SDK requiere sus propias dependencias para levantar el servidor web de Django.
```powershell
cd xblock-sdk
pip install -e .
pip install -r requirements.txt
```

---

### Paso 5: Preparación de Base de Datos y Fixes para Windows
Nota: Windows suele bloquear archivos en uso (Error 32). Para evitar que el logger de Django colapse, debemos crear la estructura de logs manualmente.

Ejecuta estos comandos dentro de la carpeta xblock-sdk:

```powershell
# 1. Crear directorio de variables y archivo de log
mkdir var
echo "" > var\workbench.log

# 2. Migrar la base de datos (Soluciona el error 'no such table: workbench_xblockstate')
python manage.py migrate
```

---

### Ejecución del Servidor de Desarrollo

Una vez instaladas las dependencias y migrada la base de datos, levanta el servidor. Usa el flag --noreload en Windows para evitar que el sistema operativo bloquee el archivo workbench.log por permisos de lectura múltiple.

Asegúrate de estar en C:\...\ia-xblock-assistant\xblock-sdk> y ejecuta:

```powershell
python manage.py runserver --noreload
```