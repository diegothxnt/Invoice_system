# Invoice_system
📄 Invoice Processor - Sistema Inteligente de Procesamiento de Facturas
https://img.shields.io/badge/Python-3.8+-blue.svg
https://img.shields.io/badge/FastAPI-0.104+-green.svg
https://img.shields.io/badge/Tesseract-OCR-orange.svg

Sistema automático para extraer y procesar información de facturas utilizando OCR y procesamiento de lenguaje natural. Convierte PDFs e imágenes en datos estructurados listos para análisis.

🎯 Características Principales
✅ Extracción Inteligente
OCR avanzado con Tesseract para PDFs e imágenes

Reconocimiento automático de campos de facturas

Preprocesamiento de imágenes para mejorar precisión

Conversión PDF → Imagen integrada

✅ API REST
FastAPI para procesamiento en tiempo real

Endpoints RESTful para subida y consulta

Documentación automática (Swagger/OpenAPI)

Async/await para alta concurrencia

✅ Funcionalidades Adicionales
Envío automático de resultados por email

Almacenamiento en PostgreSQL (opcional)

Validación y limpieza de datos

Interfaz web para gestión

🏗️ Arquitectura del Sistema
text
invoice-processor/
│
├── 📁 app/                    # Aplicación FastAPI
│   ├── main.py              # Punto de entrada API
│   ├── models.py            # Modelos SQLAlchemy
│   ├── schemas.py           # Esquemas Pydantic
│   ├── database.py          # Conexión DB
│   └── email_service.py     # Servicio de email
│
├── 📁 core/                  # Lógica de negocio
│   └── invoice_processor.py # Motor de procesamiento
│
├── 📁 uploads/              # Archivos temporales
├── 📁 pdfs/                 # PDFs de prueba
├── 📁 pdf_images/          # Imágenes convertidas
│
├── config.py               # Configuración
├── requirements.txt        # Dependencias
├── README.md              # Documentación
└── .gitignore            # Archivos ignorados
🚀 Instalación Rápida
1. Clonar el Repositorio
bash
git clone https://github.com/tuusuario/invoice-processor.git
cd invoice-processor
2. Crear Entorno Virtual
bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
3. Instalar Dependencias
bash
pip install -r requirements.txt
4. Configurar Tesseract OCR
Windows:

Descargar desde: Tesseract para Windows

Instalar en: C:\Program Files\Tesseract-OCR

Agregar al PATH del sistema

Linux (Ubuntu/Debian):

bash
sudo apt update
sudo apt install tesseract-ocr tesseract-ocr-spa
macOS:

bash
brew install tesseract
5. Configurar Variables
Crear config.py:

python
class Config:
    # Ruta de Tesseract (Windows)
    TESSERACT_PATH = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
    
    # Ruta de Tesseract (Linux/Mac)
    # TESSERACT_PATH = '/usr/bin/tesseract'
    
    # Configuración de Gmail
    GMAIL_USER = "tu_email@gmail.com"
    GMAIL_APP_PASSWORD = "tu_contraseña_app"
    
    # Base de datos (opcional)
    DATABASE_URL = "postgresql://user:pass@localhost/invoice_db"
    
    # Configuración general
    UPLOAD_FOLDER = "uploads"
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
🧪 Uso Básico
Procesar Facturas desde Código
python
import asyncio
from invoice_processor import processor

async def ejemplo_procesamiento():
    # Procesar PDF
    resultado_pdf = await processor.process_invoice("pdfs/factura_1.pdf")
    
    # Procesar imagen
    resultado_img = await processor.process_invoice("uploads/factura.png")
    
    # Mostrar resultados
    print(f"📄 Factura: {resultado_pdf['numero_factura']}")
    print(f"💰 Total: ${resultado_pdf['monto_total']}")
    print(f"🏢 Proveedor: {resultado_pdf['proveedor']}")

# Ejecutar
asyncio.run(ejemplo_procesamiento())
Generar Datos de Prueba
bash
# Crear 3 PDFs de ejemplo
python create_test_pdfs.py

# Crear 3 imágenes de ejemplo
python create_test_invoices.py
Ejecutar la API
bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
Accede a:

API: http://localhost:8000

Documentación: http://localhost:8000/docs

Redoc: http://localhost:8000/redoc

📡 API Endpoints
POST /upload/
Subir y procesar archivo

bash
curl -X POST -F "file=@factura.pdf" http://localhost:8000/upload/
Response:

json
{
  "id": 1,
  "numero_factura": "INV-2024-001",
  "proveedor": "TECNOLOGIAS ABC S.A.",
  "monto_total": 1250.00,
  "fecha_emision": "15/12/2024",
  "estado": "procesado"
}
POST /process/
Procesar archivo existente

bash
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{"file_path": "uploads/factura.pdf"}' \
  http://localhost:8000/process/
GET /invoices/
Listar todas las facturas

bash
curl http://localhost:8000/invoices/
GET /invoices/{id}
Obtener factura específica

bash
curl http://localhost:8000/invoices/1
🔍 Campos Extraídos Automáticamente
Campo	Tipo	Descripción	Ejemplo
numero_factura	String	Identificador único	"INV-2024-001"
proveedor	String	Nombre del emisor	"TECNOLOGIAS ABC S.A."
cliente	String	Nombre del receptor	"EMPRESA XYZ"
monto_total	Float	Total facturado	1250.00
impuestos	Float	IVA/Impuestos	200.00
fecha_emision	String	Fecha de emisión	"15/12/2024"
fecha_vencimiento	String	Fecha límite pago	"30/12/2024"
descripcion	String	Descripción servicios	"CONSULTORÍA IA"
condiciones	String	Términos de pago	"PAGO A 30 DÍAS"
confianza_ocr	Float	Confianza extracción	0.85
🔄 Flujo de Procesamiento













🛠️ Comandos Útiles
bash
# Ejecutar tests
python -m pytest tests/

# Verificar instalación Tesseract
python -c "import pytesseract; print(pytesseract.get_tesseract_version())"

# Limpiar archivos temporales
python cleanup.py

# Ver logs en tiempo real
tail -f app.log
🐛 Solución de Problemas Comunes
❌ "Tesseract not found"
python
# Verifica config.py
TESSERACT_PATH = r'C:\Program Files\Tesseract-OCR\tesseract.exe'  # Windows
# TESSERACT_PATH = '/usr/bin/tesseract'  # Linux/Mac
❌ Error con PDFs
bash
# Instalar PyMuPDF
pip install PyMuPDF

# O usar alternativa
python test_pdf_processor.py --use-pdfplumber
❌ Error de Email
Usar contraseña de aplicación de Gmail

Habilitar acceso apps menos seguras

Verificar configuración en config.py

❌ Archivos muy grandes
python
# En config.py
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB máximo
📊 Rendimiento y Optimización
Tipo Archivo	Tiempo Procesamiento	Precisión
PDF 1 página	2-3 segundos	85-95%
Imagen PNG	1-2 segundos	90-95%
PDF 10 páginas	10-15 segundos	80-90%
Tips para mejor precisión:

Escanear a 300 DPI mínimo

Usar formato PNG en lugar de JPG

Asegurar contraste adecuado

Texto orientado horizontalmente

🤝 Contribuir al Proyecto
Fork el repositorio

Crea rama de feature: git checkout -b feature/nueva-funcion

Commit cambios: git commit -m 'Agrega nueva función'

Push a la rama: git push origin feature/nueva-funcion

Abre Pull Request

Guías de Estilo
Usar Black para formateo

Escribir docstrings en inglés

Incluir tests para nuevas funciones

Actualizar README.md si es necesario

📄 Licencia
MIT License - ver archivo LICENSE para detalles.

👥 Autores
Tu Nombre - @tuusuario

Contribuidores - Lista de contribuidores

🙏 Agradecimientos
Tesseract OCR - Motor OCR

FastAPI - Framework web

PyMuPDF - Procesamiento PDF

Pillow - Procesamiento imágenes

📞 Soporte
📧 Email: soporte@tudominio.com

🐛 Issues: GitHub Issues

💬 Discord: Canal de Discord

<div align="center">
⭐ Si este proyecto te ayudó, ¡dale una estrella en GitHub!
https://api.star-history.com/svg?repos=tuusuario/invoice-processor&type=Date

</div>

