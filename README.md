# InstaShare

Una plataforma para compartir archivos que permite a los usuarios subir archivos, los cuales son procesados asíncronamente (comprimidos en ZIP) y luego disponibles para descargar.

## Características

- **Autenticación de usuarios**: Registro e inicio de sesión seguro
- **Subida de archivos**: Interfaz intuitiva para subir archivos
- **Procesamiento asíncrono**: Los archivos se comprimen automáticamente en segundo plano
- **Gestión de archivos**: Renombrar y ver el estado de los archivos subidos
- **Descarga de archivos**: Descarga de archivos comprimidos en formato ZIP
- **API RESTful**: Endpoints JSON para integración con otros sistemas
- **Interfaz moderna**: Diseño responsivo con Bootstrap 5

## Tecnologías utilizadas

- **Backend**: Django 5.0
- **Frontend**: HTML5, CSS3, Bootstrap 5, JavaScript
- **Base de datos**: SQLite (desarrollo), compatible con PostgreSQL/MySQL (producción)
- **Procesamiento de archivos**: Biblioteca estándar de Python (zipfile)

## Requisitos del sistema

- Python 3.8+
- Django 5.0
- Pillow (para manejo de imágenes, si se agrega en el futuro)

## Instalación

1. **Clonar el repositorio**:
   
   git clone <url-del-repositorio>
   cd instashare

2. **Crear un entorno virtual**:
    python -m venv env
    source env/bin/activate  # Linux/Mac
     
    .\env\Scripts\activate  # Windows

3. **Instalar dependencias**:
    pip install -r requirements.txt


4. **API DOCS**
  # Endpoint 
    # Include URLs from apps
    'api/'

    # swagger-ui
    'api/docs/'

    # redoc
    'api/redoc/'

# Ejecutar todos los tests
python manage.py test


# Ejecutar tests y generar reporte de coverage
coverage run manage.py test
coverage report
coverage html