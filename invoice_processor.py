# invoice_processor.py (VERSIÓN QUE GUARDA IMÁGENES)
import pytesseract
import fitz  # PyMuPDF - no necesita poppler
from PIL import Image, ImageEnhance, ImageFilter
import io
import re
import aiofiles
import os
from datetime import datetime
import config

class InvoiceProcessor:
    def __init__(self):
        # Configurar Tesseract con la ruta correcta
        pytesseract.pytesseract.tesseract_cmd = config.Config.TESSERACT_PATH
        print(f"✅ Tesseract configurado en: {config.Config.TESSERACT_PATH}")
        print(f"📄 Usando PyMuPDF para conversión PDF → Imagen")
    
    async def extract_text_from_file(self, file_path):
        """Extrae texto de PDF o imágenes con preprocesamiento mejorado"""
        file_extension = file_path.split('.')[-1].lower()
        
        if file_extension == 'pdf':
            return await self._extract_from_pdf(file_path)
        else:
            return await self._extract_from_image(file_path)
    
    async def _extract_from_pdf(self, file_path):
        """Extrae texto de PDF usando PyMuPDF para convertir a imagen Y GUARDA LAS IMÁGENES"""
        try:
            print(f"📄 Convirtiendo PDF a imágenes con PyMuPDF: {file_path}")
            
            # Crear carpeta para imágenes si no existe
            images_folder = "pdf_images"
            if not os.path.exists(images_folder):
                os.makedirs(images_folder)
                print(f"📁 Carpeta creada: {images_folder}")
            
            # Abrir el PDF
            doc = fitz.open(file_path)
            text = ""
            
            for page_num in range(len(doc)):
                print(f"📄 Procesando página {page_num + 1}...")
                page = doc.load_page(page_num)
                
                # Convertir página a imagen (300 DPI para buena calidad)
                pix = page.get_pixmap(matrix=fitz.Matrix(300/72, 300/72))
                
                # Convertir a formato PIL Image
                img_data = pix.tobytes("ppm")
                image = Image.open(io.BytesIO(img_data))
                
                # GUARDAR IMAGEN
                pdf_name = os.path.splitext(os.path.basename(file_path))[0]
                image_path = os.path.join(images_folder, f"{pdf_name}_page_{page_num + 1}.png")
                image.save(image_path, "PNG")
                print(f"💾 Imagen guardada: {image_path}")
                
                # Preprocesar imagen para mejor OCR
                processed_image = self._preprocess_image(image)
                page_text = pytesseract.image_to_string(processed_image, lang='spa')
                text += f"\n--- Página {page_num + 1} ---\n{page_text}"
            
            doc.close()
            return text
            
        except Exception as e:
            raise Exception(f"Error procesando PDF: {str(e)}")

    async def _extract_from_image(self, file_path):
        """Extrae texto de imagen con preprocesamiento mejorado"""
        try:
            image = Image.open(file_path)
            print("🔧 Preprocesando imagen para mejor OCR...")
            
            # Probar diferentes configuraciones de OCR
            processed_image = self._preprocess_image(image)
            
            # Intentar con diferentes configuraciones
            configs = [
                '',  # Configuración por defecto
                '--psm 6',  # Bloque uniforme de texto
                '--psm 4',  # Columna única de texto
                '--psm 3',  # Página completamente automática
            ]
            
            best_text = ""
            best_score = 0
            
            for config_str in configs:
                try:
                    current_text = pytesseract.image_to_string(processed_image, lang='spa', config=config_str)
                    score = self._calculate_text_quality(current_text)
                    
                    if score > best_score:
                        best_score = score
                        best_text = current_text
                        print(f"  ✅ Config {config_str}: score {score}")
                except Exception as e:
                    print(f"  ⚠️  Config {config_str} falló: {e}")
                    continue
            
            return best_text if best_text else pytesseract.image_to_string(processed_image, lang='spa')
            
        except Exception as e:
            raise Exception(f"Error procesando imagen: {str(e)}")
    
    def _preprocess_image(self, image):
        """Mejora la imagen para mejor reconocimiento OCR"""
        try:
            # Convertir a escala de grises si es color
            if image.mode != 'L':
                image = image.convert('L')
            
            # Aumentar contraste
            enhancer = ImageEnhance.Contrast(image)
            image = enhancer.enhance(2.0)
            
            # Aumentar nitidez
            enhancer = ImageEnhance.Sharpness(image)
            image = enhancer.enhance(2.0)
            
            # Redimensionar si es muy pequeña
            if image.size[0] < 800:
                new_width = 1200
                ratio = new_width / image.size[0]
                new_height = int(image.size[1] * ratio)
                image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            # Suavizar ruido
            image = image.filter(ImageFilter.MedianFilter(size=3))
            
            # Aumentar brillo
            enhancer = ImageEnhance.Brightness(image)
            image = enhancer.enhance(1.1)
            
            return image
            
        except Exception as e:
            print(f"⚠️  Error en preprocesamiento: {e}")
            return image
    
    def _calculate_text_quality(self, text):
        """Calcula la calidad del texto extraído"""
        if not text:
            return 0
        
        # Contar palabras válidas
        words = re.findall(r'\b[a-zA-Z]{3,}\b', text)
        word_count = len(words)
        
        # Contar números (importante para facturas)
        numbers = re.findall(r'\b\d+\b', text)
        number_count = len(numbers)
        
        # Verificar presencia de palabras clave de facturas
        keywords = ['factura', 'invoice', 'total', 'monto', 'fecha', 'proveedor', 'iva', 'impuesto', 'cliente', 'descripción']
        keyword_matches = sum(1 for keyword in keywords if keyword in text.lower())
        
        # Calcular score
        total_score = (word_count * 0.3) + (number_count * 0.4) + (keyword_matches * 2.0)
        return total_score
    
    def parse_invoice_data(self, text):
        """Analiza el texto extraído con patrones más flexibles"""
        data = {}
        
        print("🔍 Analizando texto extraído...")
        print(f"📝 Texto completo:\n{text}")
        print("=" * 50)
        
        # Búsqueda por líneas (más efectivo para facturas simples)
        lines = text.split('\n')
        print(f"📄 Líneas detectadas: {len(lines)}")
        
        for i, line in enumerate(lines):
            line_clean = line.strip()
            line_lower = line_clean.lower()
            
            if line_clean:
                print(f"  Línea {i}: '{line_clean}'")
            
            # Buscar número de factura
            if not data.get('numero_factura') or data['numero_factura'] == "No encontrado":
                if 'factura' in line_lower:
                    # Extraer cualquier combinación de letras y números después de "factura"
                    match = re.search(r'(?:factura|invoice)[\s:]*([^\n\r]+)', line, re.IGNORECASE)
                    if match:
                        data['numero_factura'] = match.group(1).strip()
                        print(f"  ✅ Número factura encontrado: {data['numero_factura']}")
            
            # Buscar proveedor
            if not data.get('proveedor') or data['proveedor'] == "No encontrado":
                if 'proveedor' in line_lower:
                    match = re.search(r'(?:proveedor|vendor)[\s:]*([^\n\r]+)', line, re.IGNORECASE)
                    if match:
                        data['proveedor'] = match.group(1).strip()
                        print(f"  ✅ Proveedor encontrado: {data['proveedor']}")
            
            # Buscar montos - CORRECCIÓN ESPECÍFICA
            if not data.get('monto_total') or data['monto_total'] == "No encontrado":
                if 'total' in line_lower:
                    print(f"  🔍 Buscando monto en línea: '{line_clean}'")
                    # Buscar patrones de monto en esta línea
                    amount_patterns = [
                        r'[\$]?\s*(\d{1,3}(?:,\d{3})*\.\d{2})',  # $1,250.00
                        r'[\$]?\s*(\d{1,3}(?:\.\d{3})*,\d{2})',  # $1.250,00
                        r'[\$]?\s*(\d+\.\d{2})',                 # $1250.00
                        r'[\$]?\s*(\d+,\d{2})',                  # $1250,00
                        r'total[\s:]*[\$]?\s*([0-9,\.]+)'        # total: $1,250.00
                    ]
                    
                    for pattern in amount_patterns:
                        match = re.search(pattern, line_clean, re.IGNORECASE)
                        if match:
                            raw_amount = match.group(1)
                            print(f"  💰 Monto crudo encontrado: '{raw_amount}'")
                            data['monto_total'] = raw_amount
                            break
            
            # Buscar IVA/impuestos
            if not data.get('impuestos') or data['impuestos'] == "No encontrado":
                if 'iva' in line_lower:
                    match = re.search(r'[\$]?\s*(\d+[.,]\d{2})', line_clean)
                    if match:
                        data['impuestos'] = match.group(1)
                        print(f"  ✅ Impuestos encontrados: {data['impuestos']}")
            
            # Buscar fechas
            date_match = re.search(r'(\d{1,2}[/\-]\d{1,2}[/\-]\d{2,4})', line_clean)
            if date_match:
                date_str = date_match.group(1)
                if not data.get('fecha_emision') or data['fecha_emision'] == "No encontrado":
                    if 'fecha' in line_lower:
                        data['fecha_emision'] = date_str
                        print(f"  ✅ Fecha emisión encontrada: {data['fecha_emision']}")
                if not data.get('fecha_vencimiento') or data['fecha_vencimiento'] == "No encontrado":
                    if 'vencimiento' in line_lower:
                        data['fecha_vencimiento'] = date_str
                        print(f"  ✅ Fecha vencimiento encontrada: {data['fecha_vencimiento']}")
        
        # Si no encontramos algún campo, establecer "No encontrado"
        required_fields = ['numero_factura', 'monto_total', 'impuestos', 'fecha_emision', 'proveedor', 'fecha_vencimiento']
        for field in required_fields:
            if field not in data:
                data[field] = "No encontrado"
        
        # Validación y limpieza de datos
        self._validate_extracted_data(data)
        
        print(f"✅ Datos parseados finales: {data}")
        return data

    def _validate_extracted_data(self, data):
        """Valida y limpia los datos extraídos con manejo CORREGIDO de montos"""
        print("🔄 Validando y limpiando datos extraídos...")
        
        # Convertir montos a float - CORRECCIÓN ESPECÍFICA
        if data.get('monto_total') and data['monto_total'] != "No encontrado":
            try:
                raw_amount = data['monto_total']
                print(f"  💰 Procesando monto: '{raw_amount}'")
                
                # Limpiar el monto
                clean_amount = raw_amount.replace('$', '').replace(' ', '').strip()
                
                # DETECCIÓN ESPECÍFICA PARA TU CASO: "1,250.00"
                if ',' in clean_amount and '.' in clean_amount:
                    # Formato: 1,250.00 → quitar coma de miles
                    clean_amount = clean_amount.replace(',', '')
                    print(f"  🔄 Formato 1,250.00 detectado → {clean_amount}")
                
                # Convertir a float
                final_amount = float(clean_amount)
                data['monto_total'] = final_amount
                print(f"  ✅ Monto final convertido: {final_amount}")
                
            except (ValueError, TypeError) as e:
                print(f"⚠️  No se pudo convertir monto_total '{data['monto_total']}': {e}")
                data['monto_total'] = 0.0
        
        if data.get('impuestos') and data['impuestos'] != "No encontrado":
            try:
                raw_tax = data['impuestos']
                print(f"  💰 Procesando impuestos: '{raw_tax}'")
                
                clean_tax = raw_tax.replace('$', '').replace(' ', '').strip()
                
                if ',' in clean_tax and '.' in clean_tax:
                    clean_tax = clean_tax.replace(',', '')
                    print(f"  🔄 Formato impuestos convertido → {clean_tax}")
                
                final_tax = float(clean_tax)
                data['impuestos'] = final_tax
                print(f"  ✅ Impuestos finales convertidos: {final_tax}")
                
            except (ValueError, TypeError) as e:
                print(f"⚠️  No se pudo convertir impuestos '{data['impuestos']}': {e}")
                data['impuestos'] = 0.0
        
        # Limpiar texto de proveedor
        if data.get('proveedor') and data['proveedor'] != "No encontrado":
            data['proveedor'] = re.sub(r'\s+', ' ', data['proveedor']).strip()
        
        # Asegurar que las fechas tengan formato consistente
        date_fields = ['fecha_emision', 'fecha_vencimiento']
        for field in date_fields:
            if data.get(field) and data[field] != "No encontrado":
                # Normalizar formato de fecha
                date_str = data[field]
                date_str = date_str.replace('-', '/')
                data[field] = date_str
    
    async def process_invoice(self, file_path):
        """Procesa completo de una factura"""
        print("🔄 Iniciando procesamiento de factura...")
        
        # Extraer texto
        text = await self.extract_text_from_file(file_path)
        
        print(f"📝 Texto extraído ({len(text)} caracteres)")
        
        # Parsear datos
        invoice_data = self.parse_invoice_data(text)
        
        # Agregar metadatos
        invoice_data['texto_extraido'] = text[:1000] + "..." if len(text) > 1000 else text
        invoice_data['procesado_en'] = datetime.utcnow().isoformat()
        invoice_data['confianza_ocr'] = self._calculate_confidence(text)
        
        print("🎉 Procesamiento completado!")
        return invoice_data
    
    def _calculate_confidence(self, text):
        """Calcula una confianza basada en la calidad del texto extraído"""
        if not text or len(text.strip()) < 10:
            return 0.0
        
        # Métricas de calidad
        word_count = len(re.findall(r'\b[a-zA-Z]{3,}\b', text))
        number_count = len(re.findall(r'\b\d+\b', text))
        
        # Palabras clave de facturas
        keywords = ['factura', 'invoice', 'total', 'monto', 'fecha', 'proveedor', 'iva', 'impuesto', 'cliente', 'descripción']
        keyword_matches = sum(1 for keyword in keywords if keyword in text.lower())
        
        # Calcular confianza
        confidence = min(
            (word_count / 10) * 0.3 +
            (number_count / 5) * 0.3 +
            (keyword_matches / len(keywords)) * 0.4,
            1.0
        )
        
        return round(confidence, 2)

# Instancia global
processor = InvoiceProcessor()