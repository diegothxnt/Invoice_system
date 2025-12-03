# Invoice_system
📄 Invoice Processor - Procesador Inteligente de Facturas

Sistema automático para extraer y procesar información de facturas en formato PDF e imágenes usando OCR y procesamiento de lenguaje natural.

🚀 Características Principales
✅ Extracción OCR de facturas en PDF e imágenes (PNG, JPG, JPEG)

✅ Reconocimiento inteligente de campos de facturas

✅ API REST con FastAPI para procesamiento en tiempo real

✅ Envío automático de facturas procesadas por email

✅ Interfaz web para subida y visualización de resultados

✅ Almacenamiento en base de datos PostgreSQL

✅ Validación y limpieza automática de datos extraídos

📦 Estructura del Proyecto
text
invoice-processor/
├── app/
│   ├── main.py              # Aplicación FastAPI principal
│   ├── models.py            # Modelos de base de datos
│   ├── schemas.py           # Esquemas Pydantic
│   ├── database.py          # Configuración de base de datos
│   └── email_service.py     # Servicio de envío de emails
├── invoice_processor.py     # Motor de procesamiento de facturas
├── config.py               # Configuración de la aplicación
├── requirements.txt        # Dependencias del proyecto
├── uploads/               # Archivos subidos temporalmente
├── pdf_images/            # Imágenes convertidas de PDFs
└── pdfs/                  # PDFs de prueba
🔧 Instalación
1. Requisitos Previos
Python 3.8 o superior

Tesseract OCR instalado en el sistema

PostgreSQL (opcional, para almacenamiento)

Cuenta de Gmail (para envío de emails)

2. Instalar Dependencias
bash
# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt
3. Configurar Tesseract OCR
Windows:

Descargar e instalar desde: https://github.com/UB-Mannheim/tesseract/wiki

Agregar al PATH: C:\Program Files\Tesseract-OCR

Linux (Ubuntu/Debian):

bash
sudo apt update
sudo apt install tesseract-ocr tesseract-ocr-spa
macOS:

bash
brew install tesseract
4. Configurar Variables de Entorno
Crear archivo config.py:

python
class Config:
    # Ruta de Tesseract OCR
    TESSERACT_PATH = r'C:\Program Files\Tesseract-OCR\tesseract.exe'  # Windows
    # TESSERACT_PATH = '/usr/bin/tesseract'  # Linux/Mac
    
    # Configuración de Gmail
    GMAIL_USER = "tu_email@gmail.com"
    GMAIL_APP_PASSWORD = "tu_contraseña_de_aplicación"
    
    # Base de datos
    DATABASE_URL = "postgresql://usuario:contraseña@localhost/invoice_db"
    
    # Configuración de la aplicación
    UPLOAD_FOLDER = "uploads"
    ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg'}



# La API estará disponible en: http://localhost:8000
🌐 API Endpoints
POST /upload/
Subir y procesar una factura

bash
curl -X POST -F "file=@factura.pdf" http://localhost:8000/upload/
POST /process/
Procesar una factura existente

bash
curl -X POST -H "Content-Type: application/json" \
     -d '{"file_path": "uploads/factura.pdf"}' \
     http://localhost:8000/process/
GET /invoices/
Obtener todas las facturas procesadas

GET /invoices/{invoice_id}
Obtener una factura específica

📋 Campos Extraídos
El sistema extrae automáticamente:

Campo	Descripción	Ejemplo
numero_factura	Número único de factura	"INV-2024-001"
proveedor	Nombre del proveedor	"TECNOLOGIAS ABC S.A."
cliente	Nombre del cliente	"EMPRESA XYZ"
monto_total	Total de la factura	1250.00
impuestos	Monto de IVA/impuestos	200.00
fecha_emision	Fecha de emisión	"15/12/2024"
fecha_vencimiento	Fecha de vencimiento	"30/12/2024"
descripcion	Descripción del servicio	"SERVICIOS CONSULTORIA IA"
condiciones	Condiciones de pago	"PAGO A 30 DIAS"
🧪 Generar Facturas de Prueba
bash
# Generar 3 PDFs de prueba
python create_test_pdfs.py

# Generar 3 imágenes de prueba
python create_test_invoices.py
Los archivos se guardarán en:

pdfs/ para PDFs

uploads/ para imágenes

🔍 Flujo de Procesamiento
Subida de archivo (PDF o imagen)

Conversión PDF → Imagen (si es necesario)

Preprocesamiento de imagen (mejora de calidad)

OCR con Tesseract (extracción de texto)

Análisis de texto (búsqueda de patrones)

Validación de datos (limpieza y formato)

Almacenamiento en base de datos

Notificación por email (opcional)

🐛 Solución de Problemas
Error: "Tesseract not found"
Verifica la ruta en config.py

Asegúrate de que Tesseract esté instalado

Error: "Unable to get page count" (PDFs)
Instala PyMuPDF: pip install PyMuPDF

Error de envío de email
Usa contraseñas de aplicación de Gmail

Verifica credenciales en config.py

📝 Formato de Factura Recomendado
Para mejores resultados, las facturas deben tener:

Texto claro y legible

Formato estructurado

Campos claramente etiquetados

Resolución mínima de 300 DPI


📄 Licencia
Este proyecto está bajo la Licencia MIT. Ver LICENSE para más detalles.

✨ Autores:
Diego Rojas

🙏 Agradecimientos
Tesseract OCR

FastAPI

PyMuPDF

Pillow

