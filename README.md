# 📄 Invoice System --- Procesador Inteligente de Facturas

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)\
![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)\
![Tesseract](https://img.shields.io/badge/Tesseract-OCR-orange.svg)

Sistema automático para extraer, interpretar y estructurar información
proveniente de facturas PDF o imágenes utilizando OCR + NLP.

## Tabla de Contenidos

-   Características Principales
-   Arquitectura
-   Instalación
-   Uso
-   API
-   Campos Extraídos
-   Comandos Útiles
-   Troubleshooting
-   Rendimiento
-   Contribuir
-   Licencia
-   Autores
-   Soporte

## 🎯 Características Principales

### Extracción Inteligente

-   OCR avanzado con Tesseract\
-   Preprocesamiento automático\
-   Detección de campos clave\
-   Conversión PDF → Imagen integrada

### API REST

-   FastAPI\
-   Endpoints RESTful\
-   Documentación Swagger / OpenAPI\
-   Operaciones async/await

### Funcionalidades Extra

-   Envío por email\
-   PostgreSQL opcional\
-   Validación & limpieza de datos\
-   Interfaz web de gestión

## 🏗️ Arquitectura del Sistema

    invoice-processor/
    ├── app/
    │   ├── main.py
    │   ├── models.py
    │   ├── schemas.py
    │   ├── database.py
    │   └── email_service.py
    ├── core/
    │   └── invoice_processor.py
    ├── uploads/
    ├── pdfs/
    ├── pdf_images/
    ├── config.py
    ├── requirements.txt
    ├── README.md
    └── .gitignore

## 🚀 Instalación

1.  Clonar repo\
2.  Crear entorno virtual\
3.  Instalar dependencias\
4.  Instalar Tesseract
