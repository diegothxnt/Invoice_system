📄 Invoice System — Procesador Inteligente de Facturas



Sistema automático para extraer y procesar información de facturas utilizando OCR y técnicas de procesamiento de lenguaje natural. Convierte PDFs e imágenes en datos estructurados listos para análisis.

🎯 Características Principales
✅ Extracción Inteligente


OCR avanzado con Tesseract para PDFs e imágenes


Reconocimiento automático de campos clave


Preprocesamiento de imágenes para mayor precisión


Conversión integrada PDF → Imagen


✅ API REST


API en FastAPI para procesamiento en tiempo real


Endpoints RESTful para subida y consulta


Documentación automática (Swagger / OpenAPI)


Soporte async/await para alta concurrencia


✅ Funcionalidades Adicionales


Envío automático de resultados por email


Almacenamiento en PostgreSQL (opcional)


Validación y limpieza de datos


Interfaz web para gestión



🏗️ Arquitectura del Sistema
invoice-processor/
│
├── 📁 app/                    # Aplicación FastAPI
│   ├── main.py                # Punto de entrada API
│   ├── models.py              # Modelos SQLAlchemy
│   ├── schemas.py             # Esquemas Pydantic
│   ├── database.py            # Conexión DB
│   └── email_service.py       # Servicio de email
│
├── 📁 core/                   # Lógica de negocio
│   └── invoice_processor.py   # Motor de procesamiento
│
├── 📁 uploads/                # Archivos temporales
├── 📁 pdfs/                   # PDFs de prueba
├── 📁 pdf_images/             # Imágenes convertidas
│
├── config.py                  # Configuración
├── requirements.txt           # Dependencias
├── README.md                  # Documentación
└── .gitignore                 # Archivos ignorados


🚀 Instalación Rápida
1. Clonar el repositorio
git clone https://github.com/tuusuario/invoice-processor.git
cd invoice-processor

2. Crear entorno virtual
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate

3. Instalar dependencias
pip install -r requirements.txt

4. Instalar Tesseract OCR
Windows


Descargar: “Tesseract para Windows”


Instalar en: C:\Program Files\Tesseract-OCR


Agregar al PATH


Linux (Ubuntu/Debian)
sudo apt update
sudo apt install tesseract-ocr tesseract-ocr-spa

macOS
brew install tesseract

5. Configurar Variables (config.py)
class Config:
    TESSERACT_PATH = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
    # TESSERACT_PATH = '/usr/bin/tesseract'

    GMAIL_USER = "tu_email@gmail.com"
    GMAIL_APP_PASSWORD = "tu_contraseña_app"

    DATABASE_URL = "postgresql://user:pass@localhost/invoice_db"

    UPLOAD_FOLDER = "uploads"
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB


🧪 Uso Básico
Procesar Facturas desde Código
import asyncio
from invoice_processor import processor

async def ejemplo_procesamiento():
    resultado_pdf = await processor.process_invoice("pdfs/factura_1.pdf")
    resultado_img = await processor.process_invoice("uploads/factura.png")

    print(f"📄 Factura: {resultado_pdf['numero_factura']}")
    print(f"💰 Total: ${resultado_pdf['monto_total']}")
    print(f"🏢 Proveedor: {resultado_pdf['proveedor']}")

asyncio.run(ejemplo_procesamiento())

Generar Datos de Prueba
python create_test_pdfs.py
python create_test_invoices.py

Ejecutar API
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

Accesos:


API: http://localhost:8000


Docs (Swagger): http://localhost:8000/docs


Redoc: http://localhost:8000/redoc



📡 API Endpoints
▶️ POST /upload/ — Subir y procesar archivo
curl -X POST -F "file=@factura.pdf" http://localhost:8000/upload/

Respuesta:
{
  "id": 1,
  "numero_factura": "INV-2024-001",
  "proveedor": "TECNOLOGIAS ABC S.A.",
  "monto_total": 1250.00,
  "fecha_emision": "15/12/2024",
  "estado": "procesado"
}

▶️ POST /process/ — Procesar archivo existente
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{"file_path": "uploads/factura.pdf"}' \
  http://localhost:8000/process/

▶️ GET /invoices/ — Listar facturas
curl http://localhost:8000/invoices/

▶️ GET /invoices/{id} — Obtener una factura específica
curl http://localhost:8000/invoices/1


🔍 Campos Extraídos Automáticamente
CampoTipoDescripciónEjemplonumero_facturaStringIdentificador único"INV-2024-001"proveedorStringEmisor"TECNOLOGIAS ABC"clienteStringReceptor"EMPRESA XYZ"monto_totalFloatTotal1250.00impuestosFloatIVA / Impuestos200.00fecha_emisionStringFecha emisión"15/12/2024"fecha_vencimientoStringFecha de vencimiento"30/12/2024"descripcionStringServicios"CONSULTORÍA IA"condicionesStringTérminos de pago"PAGO A 30 DÍAS"confianza_ocrFloatNivel confianza OCR0.85

🛠️ Comandos Útiles
python -m pytest tests/          # Ejecutar tests
python -c "import pytesseract; print(pytesseract.get_tesseract_version())"  # Verificar Tesseract
python cleanup.py                # Limpiar archivos temporales
tail -f app.log                  # Logs en tiempo real


🐛 Solución de Problemas Comunes
❌ "Tesseract not found"
Verificar en config.py:
TESSERACT_PATH = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

❌ Error con PDFs
pip install PyMuPDF
python test_pdf_processor.py --use-pdfplumber

❌ Error de Email


Usar contraseña de aplicación Gmail


Revisar config.py


❌ Archivos demasiado grandes
MAX_FILE_SIZE = 10 * 1024 * 1024


📊 Rendimiento y Optimización
Tipo ArchivoTiempoPrecisiónPDF 1 página2-3 s85–95%Imagen PNG1-2 s90–95%PDF 10 páginas10-15 s80–90%
Tips:


Escanear a 300 DPI


Preferir PNG sobre JPG


Buen contraste


Texto horizontal



🤝 Contribuir


Hacer fork


Crear rama: git checkout -b feature/nueva-funcion


Commit: git commit -m 'Agrega nueva función'


Push: git push origin feature/nueva-funcion


Abrir Pull Request


Guías:


Formateo con Black


Docstrings en inglés


Incluir tests


Mantener README actualizado



📄 Licencia
MIT License — ver archivo LICENSE.

👥 Autor:


Diego Rojas. 2025


Contribuidores



🙏 Agradecimientos


Tesseract OCR


FastAPI


PyMuPDF


Pillow

