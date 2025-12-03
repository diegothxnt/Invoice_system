from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks, Form, Request
from fastapi.responses import JSONResponse, HTMLResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import cv2
import numpy as np
from pdf2image import convert_from_path
import uvicorn
import os
import uuid
from datetime import datetime
import aiofiles
import traceback
import json

# Importar módulos
from database import db
from invoice_processor import processor
from email_system import email_system
import config

app = FastAPI(
    title="Sistema Inteligente de Procesamiento de Facturas", 
    version="2.1.0",
    description="Sistema de IA para procesamiento automático de facturas con OCR y notificaciones por email",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Montar carpeta estática para archivos
os.makedirs("static", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Crear directorio de uploads
os.makedirs(config.Config.UPLOAD_FOLDER, exist_ok=True)

@app.post("/api/upload-invoice")
async def upload_invoice(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    approver_email: str = Form("diego.31326600@uru.edu")
):
    """Endpoint para subir y procesar facturas - MEJORADO"""
    try:
        print(f"📥 Iniciando procesamiento MEJORADO de factura...")
        print(f"📧 Email destinatario: {approver_email}")
        
        # Validar archivo de manera más robusta
        if not file.filename or not file.content_type:
            raise HTTPException(status_code=400, detail="Archivo inválido")
        
        file_extension = file.filename.split('.')[-1].lower()
        
        # Validar tipos de archivo mejorados
        allowed_extensions = {'pdf', 'png', 'jpg', 'jpeg', 'tiff', 'bmp'}
        if file_extension not in allowed_extensions:
            raise HTTPException(
                status_code=400, 
                detail=f"Formato no soportado. Use: {', '.join(allowed_extensions)}"
            )
        
        print(f"✅ Archivo válido: {file.filename} ({file_extension})")
        
        # Resto del código permanece igual...
        
        # Validar extensión
        file_extension = file.filename.split('.')[-1].lower()
        if file_extension not in config.Config.ALLOWED_EXTENSIONS:
            raise HTTPException(status_code=400, detail=f"Formato de archivo no soportado. Formatos permitidos: {', '.join(config.Config.ALLOWED_EXTENSIONS)}")
        
        print(f"✅ Extensión válida: {file_extension}")
        
        # Guardar archivo temporal
        file_path = f"{config.Config.UPLOAD_FOLDER}/{uuid.uuid4()}.{file_extension}"
        
        print(f"📁 Guardando archivo temporal: {file_path}")
        
        # Guardar archivo con aiofiles
        async with aiofiles.open(file_path, 'wb') as f:
            content = await file.read()
            await f.write(content)
        
        print(f"✅ Archivo guardado ({len(content)} bytes), procesando con OCR...")
        
        # Procesar factura
        invoice_data = await processor.process_invoice(file_path)
        
        print(f"📊 Datos extraídos: {invoice_data}")
        
        # Guardar en base de datos
        invoice_id = db.save_invoice(invoice_data)
        
        if not invoice_id:
            raise HTTPException(status_code=500, detail="Error guardando factura en base de datos")
        
        print(f"💾 Guardado en BD con ID: {invoice_id}")
        
        # Enviar notificación por email (en background)
        background_tasks.add_task(
            email_system.send_notification,
            approver_email,
            invoice_data,
            str(invoice_id)
        )
        
        print(f"📧 Notificación en cola para: {approver_email}")
        
        # Limpiar archivo temporal
        if os.path.exists(file_path):
            os.remove(file_path)
            print("🧹 Archivo temporal eliminado")
        
        response_data = {
            "message": "Factura procesada exitosamente",
            "invoice_id": str(invoice_id),
            "extracted_data": invoice_data,
            "status": "En Proceso",
            "notification_sent_to": approver_email,
            "confianza_extraccion": invoice_data.get('confianza_ocr', 0),
            "timestamp": datetime.utcnow().isoformat()
        }
        
        print(f"🎉 Procesamiento completado exitosamente!")
        return JSONResponse(response_data)
        
    except Exception as e:
        # Mostrar el error completo
        print(f"❌ ERROR DETALLADO:")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Error procesando factura: {str(e)}")

@app.get("/api/approve/{invoice_id}")
async def approve_invoice(invoice_id: str):
    """Endpoint para aprobar factura - llamado desde el email"""
    try:
        print(f"✅ Aprobando factura desde email: {invoice_id}")
        result = db.update_invoice_status(invoice_id, "Aprobado", "Aprobado vía email")
        if result:
            # Obtener datos de la factura para el log
            invoice = db.get_invoice(invoice_id)
            print(f"🎉 Factura aprobada: {invoice.get('numero_factura', 'N/A')} - ${invoice.get('monto_total', 'N/A')}")
            
            # Página de confirmación HTML
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Factura Aprobada</title>
                <meta charset="utf-8">
                <meta name="viewport" content="width=device-width, initial-scale=1">
                <style>
                    body {{ 
                        font-family: 'Segoe UI', Arial, sans-serif; 
                        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
                        margin: 0; padding: 0; 
                        display: flex; 
                        align-items: center; 
                        justify-content: center; 
                        min-height: 100vh;
                    }}
                    .container {{
                        background: white; 
                        padding: 40px; 
                        border-radius: 15px; 
                        text-align: center;
                        box-shadow: 0 20px 40px rgba(0,0,0,0.1);
                        max-width: 500px;
                    }}
                    .success-icon {{
                        font-size: 80px; 
                        margin-bottom: 20px;
                    }}
                    h1 {{ color: #059669; margin-bottom: 15px; }}
                    .info {{ 
                        background: #f0fdf4; 
                        padding: 15px; 
                        border-radius: 8px; 
                        margin: 20px 0;
                        border-left: 4px solid #10b981;
                    }}
                    .btn {{
                        display: inline-block;
                        background: #10b981;
                        color: white;
                        padding: 12px 24px;
                        text-decoration: none;
                        border-radius: 8px;
                        margin-top: 15px;
                        font-weight: 600;
                    }}
                    .history {{
                        background: #f8f9fa;
                        padding: 15px;
                        border-radius: 8px;
                        margin: 15px 0;
                        text-align: left;
                    }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="success-icon">✅</div>
                    <h1>Factura Aprobada Exitosamente</h1>
                    <div class="info">
                        <p><strong>Número:</strong> {invoice.get('numero_factura', 'N/A')}</p>
                        <p><strong>Proveedor:</strong> {invoice.get('proveedor', 'N/A')}</p>
                        <p><strong>Monto:</strong> ${invoice.get('monto_total', 'N/A')}</p>
                        <p><strong>ID:</strong> {invoice_id}</p>
                    </div>
                    
                    <div class="history">
                        <strong>📋 Historial de Estados:</strong>
                        {"".join([f"<p>• {h['status']} - {h['timestamp'][:19]}</p>" for h in invoice.get('status_history', [])[-3:]])}
                    </div>
                    
                    <p>La factura ha sido aprobada y procederá al proceso de pago.</p>
                    <div style="margin-top: 20px;">
                        <a href="/" class="btn">🏠 Volver al Sistema</a>
                        <a href="/approved-invoices" class="btn" style="background: #3b82f6; margin-left: 10px;">📋 Ver Aprobadas</a>
                    </div>
                </div>
            </body>
            </html>
            """
            return HTMLResponse(content=html_content)
        else:
            raise HTTPException(status_code=404, detail="Factura no encontrada")
    except Exception as e:
        print(f"❌ Error aprobando factura: {e}")
        raise HTTPException(status_code=500, detail=f"Error aprobando factura: {str(e)}")

@app.post("/api/reject/{invoice_id}")
async def reject_invoice(
    invoice_id: str, 
    request: Request,
    comments: str = Form("Sin comentarios específicos")
):
    """Endpoint para rechazar factura - llamado desde el formulario"""
    try:
        print(f"❌ Rechazando factura: {invoice_id}")
        print(f"📝 Comentarios: {comments}")
        
        result = db.update_invoice_status(invoice_id, "Rechazado", comments)
        if result:
            # Obtener datos de la factura para el log
            invoice = db.get_invoice(invoice_id)
            print(f"📋 Factura rechazada: {invoice.get('numero_factura', 'N/A')} - Razón: {comments}")
            
            # Página de confirmación HTML
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Factura Rechazada</title>
                <meta charset="utf-8">
                <meta name="viewport" content="width=device-width, initial-scale=1">
                <style>
                    body {{ 
                        font-family: 'Segoe UI', Arial, sans-serif; 
                        background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
                        margin: 0; padding: 0; 
                        display: flex; 
                        align-items: center; 
                        justify-content: center; 
                        min-height: 100vh;
                    }}
                    .container {{
                        background: white; 
                        padding: 40px; 
                        border-radius: 15px; 
                        text-align: center;
                        box-shadow: 0 20px 40px rgba(0,0,0,0.1);
                        max-width: 500px;
                    }}
                    .reject-icon {{
                        font-size: 80px; 
                        margin-bottom: 20px;
                    }}
                    h1 {{ color: #dc2626; margin-bottom: 15px; }}
                    .info {{ 
                        background: #fef2f2; 
                        padding: 15px; 
                        border-radius: 8px; 
                        margin: 20px 0;
                        border-left: 4px solid #ef4444;
                    }}
                    .comments {{
                        background: #fef3c7;
                        padding: 15px;
                        border-radius: 8px;
                        margin: 15px 0;
                        text-align: left;
                    }}
                    .btn {{
                        display: inline-block;
                        background: #dc2626;
                        color: white;
                        padding: 12px 24px;
                        text-decoration: none;
                        border-radius: 8px;
                        margin-top: 15px;
                        font-weight: 600;
                    }}
                    .history {{
                        background: #f8f9fa;
                        padding: 15px;
                        border-radius: 8px;
                        margin: 15px 0;
                        text-align: left;
                    }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="reject-icon">❌</div>
                    <h1>Factura Rechazada</h1>
                    <div class="info">
                        <p><strong>Número:</strong> {invoice.get('numero_factura', 'N/A')}</p>
                        <p><strong>Proveedor:</strong> {invoice.get('proveedor', 'N/A')}</p>
                        <p><strong>Monto:</strong> ${invoice.get('monto_total', 'N/A')}</p>
                        <p><strong>ID:</strong> {invoice_id}</p>
                    </div>
                    <div class="comments">
                        <strong>📝 Comentarios de Rechazo:</strong><br>
                        {comments}
                    </div>
                    
                    <div class="history">
                        <strong>📋 Historial de Estados:</strong>
                        {"".join([f"<p>• {h['status']} - {h['timestamp'][:19]}</p>" for h in invoice.get('status_history', [])[-3:]])}
                    </div>
                    
                    <p>La factura ha sido rechazada y no procederá a pago.</p>
                    <div style="margin-top: 20px;">
                        <a href="/" class="btn">🏠 Volver al Sistema</a>
                        <a href="/rejected-invoices" class="btn" style="background: #6b7280; margin-left: 10px;">📋 Ver Rechazadas</a>
                    </div>
                </div>
            </body>
            </html>
            """
            return HTMLResponse(content=html_content)
        else:
            raise HTTPException(status_code=404, detail="Factura no encontrada")
    except Exception as e:
        print(f"❌ Error rechazando factura: {e}")
        raise HTTPException(status_code=500, detail=f"Error rechazando factura: {str(e)}")

@app.get("/reject-form/{invoice_id}", response_class=HTMLResponse)
async def reject_form(invoice_id: str):
    """Página de formulario para rechazar factura - llamado desde el email"""
    invoice = db.get_invoice(invoice_id)
    if not invoice:
        raise HTTPException(status_code=404, detail="Factura no encontrada")
        
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Rechazar Factura</title>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            * {{ margin: 0; padding: 0; box-sizing: border-box; }}
            body {{ 
                font-family: 'Segoe UI', Arial, sans-serif; 
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                padding: 20px;
                display: flex;
                align-items: center;
                justify-content: center;
            }}
            .container {{
                max-width: 500px;
                width: 100%;
                background: white;
                border-radius: 15px;
                padding: 30px;
                box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            }}
            .header {{
                text-align: center;
                margin-bottom: 25px;
                padding-bottom: 20px;
                border-bottom: 2px solid #e2e8f0;
            }}
            .header h1 {{
                color: #dc2626;
                margin-bottom: 10px;
            }}
            .invoice-preview {{
                background: #f8f9fa;
                padding: 15px;
                border-radius: 8px;
                margin-bottom: 20px;
                border-left: 4px solid #dc2626;
            }}
            .form-group {{
                margin-bottom: 20px;
            }}
            label {{
                display: block;
                margin-bottom: 8px;
                font-weight: 600;
                color: #374151;
            }}
            textarea {{
                width: 100%;
                height: 120px;
                padding: 12px;
                border: 2px solid #e2e8f0;
                border-radius: 8px;
                font-size: 16px;
                font-family: inherit;
                resize: vertical;
            }}
            textarea:focus {{
                outline: none;
                border-color: #dc2626;
            }}
            .buttons {{
                display: flex;
                gap: 15px;
                margin-top: 25px;
            }}
            .btn {{
                flex: 1;
                padding: 14px;
                border: none;
                border-radius: 8px;
                font-size: 16px;
                font-weight: 600;
                cursor: pointer;
                transition: all 0.3s ease;
                text-align: center;
                text-decoration: none;
            }}
            .btn-reject {{
                background: #dc2626;
                color: white;
            }}
            .btn-cancel {{
                background: #6b7280;
                color: white;
            }}
            .btn:hover {{
                transform: translateY(-2px);
                box-shadow: 0 5px 15px rgba(0,0,0,0.2);
            }}
            .info {{
                background: #fef2f2;
                border: 1px solid #fecaca;
                padding: 15px;
                border-radius: 8px;
                margin-bottom: 20px;
                color: #dc2626;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>❌ Rechazar Factura</h1>
                <p>ID: {invoice_id}</p>
            </div>

            <div class="invoice-preview">
                <p><strong>Proveedor:</strong> {invoice.get('proveedor', 'N/A')}</p>
                <p><strong>N° Factura:</strong> {invoice.get('numero_factura', 'N/A')}</p>
                <p><strong>Monto:</strong> ${invoice.get('monto_total', 'N/A')}</p>
                <p><strong>Fecha:</strong> {invoice.get('fecha_emision', 'N/A')}</p>
            </div>

            <div class="info">
                <strong>⚠️ Importante:</strong> Esta acción no se puede deshacer. 
                Por favor proporcione una explicación detallada para el rechazo.
            </div>

            <form action="/api/reject/{invoice_id}" method="post">
                <div class="form-group">
                    <label for="comments">📝 Comentarios (requeridos):</label>
                    <textarea 
                        id="comments" 
                        name="comments" 
                        placeholder="Explique detalladamente por qué está rechazando esta factura..."
                        required
                    ></textarea>
                </div>

                <div class="buttons">
                    <button type="submit" class="btn btn-reject">
                        🚫 Confirmar Rechazo
                    </button>
                    <a href="/" class="btn btn-cancel">
                        ↩️ Cancelar
                    </a>
                </div>
            </form>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@app.get("/rejected-invoices", response_class=HTMLResponse)
async def rejected_invoices():
    """Página para ver todas las facturas rechazadas"""
    rejected = db.get_rejected_invoices()
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Facturas Rechazadas</title>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            * {{ margin: 0; padding: 0; box-sizing: border-box; }}
            body {{ 
                font-family: 'Segoe UI', Arial, sans-serif; 
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                padding: 20px;
            }}
            .container {{
                max-width: 1000px;
                margin: 0 auto;
                background: white;
                border-radius: 15px;
                padding: 30px;
                box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            }}
            .header {{
                text-align: center;
                margin-bottom: 30px;
                padding-bottom: 20px;
                border-bottom: 2px solid #e2e8f0;
            }}
            .header h1 {{
                color: #dc2626;
                margin-bottom: 10px;
            }}
            .stats {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 15px;
                margin-bottom: 30px;
            }}
            .stat-card {{
                background: #fef2f2;
                padding: 20px;
                border-radius: 8px;
                text-align: center;
                border-left: 4px solid #dc2626;
            }}
            .stat-number {{
                font-size: 24px;
                font-weight: bold;
                color: #dc2626;
            }}
            .invoice-grid {{
                display: grid;
                gap: 20px;
            }}
            .invoice-card {{
                border: 1px solid #e2e8f0;
                border-radius: 10px;
                padding: 20px;
                background: #fafafa;
                border-left: 5px solid #dc2626;
            }}
            .invoice-header {{
                display: flex;
                justify-content: between;
                align-items: center;
                margin-bottom: 15px;
            }}
            .invoice-title {{
                font-size: 18px;
                font-weight: bold;
                color: #dc2626;
            }}
            .invoice-details {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 10px;
                margin-bottom: 15px;
            }}
            .comments {{
                background: #fef3c7;
                padding: 15px;
                border-radius: 8px;
                margin-top: 10px;
            }}
            .btn {{
                display: inline-block;
                background: #2563eb;
                color: white;
                padding: 10px 20px;
                text-decoration: none;
                border-radius: 6px;
                margin-top: 10px;
            }}
            .empty-state {{
                text-align: center;
                padding: 40px;
                color: #6b7280;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>📋 Facturas Rechazadas</h1>
                <p>Historial completo de facturas rechazadas en el sistema</p>
            </div>

            <div class="stats">
                <div class="stat-card">
                    <div class="stat-number">{len(rejected)}</div>
                    <div class="stat-label">Total Rechazadas</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{len([inv for inv in rejected.values() if inv.get('rejection_comments')])}</div>
                    <div class="stat-label">Con Comentarios</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">${sum([float(inv.get('monto_total', 0)) for inv in rejected.values()]):.2f}</div>
                    <div class="stat-label">Monto Total Rechazado</div>
                </div>
            </div>

            <div class="invoice-grid">
                {"".join([f'''
                <div class="invoice-card">
                    <div class="invoice-header">
                        <div class="invoice-title">Factura: {inv.get('numero_factura', 'N/A')}</div>
                        <div style="color: #6b7280; font-size: 14px;">ID: {inv_id}</div>
                    </div>
                    
                    <div class="invoice-details">
                        <div><strong>Proveedor:</strong> {inv.get('proveedor', 'N/A')}</div>
                        <div><strong>Monto:</strong> ${inv.get('monto_total', 'N/A')}</div>
                        <div><strong>Fecha Emisión:</strong> {inv.get('fecha_emision', 'N/A')}</div>
                        <div><strong>Rechazado el:</strong> {inv.get('rejected_at', 'N/A')[:19]}</div>
                    </div>
                    
                    <div class="comments">
                        <strong>📝 Razón del Rechazo:</strong><br>
                        {inv.get('rejection_comments', 'No se proporcionaron comentarios')}
                    </div>
                    
                    <div style="margin-top: 15px;">
                        <strong>📋 Historial:</strong>
                        <div style="font-size: 12px; margin-top: 5px;">
                            {" → ".join([h['status'] for h in inv.get('status_history', [])])}
                        </div>
                    </div>
                </div>
                ''' for inv_id, inv in rejected.items()]) if rejected else '''
                <div class="empty-state">
                    <h3>🎉 No hay facturas rechazadas</h3>
                    <p>No se han rechazado facturas en el sistema.</p>
                </div>
                '''}
            </div>

            <div style="text-align: center; margin-top: 30px;">
                <a href="/" class="btn">🏠 Volver al Inicio</a>
                <a href="/all-invoices" class="btn" style="background: #6b7280; margin-left: 10px;">📊 Ver Todas las Facturas</a>
            </div>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@app.get("/approved-invoices", response_class=HTMLResponse)
async def approved_invoices():
    """Página para ver todas las facturas aprobadas"""
    approved = db.get_approved_invoices()
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Facturas Aprobadas</title>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            * {{ margin: 0; padding: 0; box-sizing: border-box; }}
            body {{ 
                font-family: 'Segoe UI', Arial, sans-serif; 
                background: linear-gradient(135deg, #10b981 0%, #059669 100%);
                min-height: 100vh;
                padding: 20px;
            }}
            .container {{
                max-width: 1000px;
                margin: 0 auto;
                background: white;
                border-radius: 15px;
                padding: 30px;
                box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            }}
            .header {{
                text-align: center;
                margin-bottom: 30px;
                padding-bottom: 20px;
                border-bottom: 2px solid #e2e8f0;
            }}
            .header h1 {{
                color: #059669;
                margin-bottom: 10px;
            }}
            .stats {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 15px;
                margin-bottom: 30px;
            }}
            .stat-card {{
                background: #f0fdf4;
                padding: 20px;
                border-radius: 8px;
                text-align: center;
                border-left: 4px solid #10b981;
            }}
            .stat-number {{
                font-size: 24px;
                font-weight: bold;
                color: #059669;
            }}
            .invoice-grid {{
                display: grid;
                gap: 20px;
            }}
            .invoice-card {{
                border: 1px solid #e2e8f0;
                border-radius: 10px;
                padding: 20px;
                background: #fafafa;
                border-left: 5px solid #10b981;
            }}
            .invoice-header {{
                display: flex;
                justify-content: between;
                align-items: center;
                margin-bottom: 15px;
            }}
            .invoice-title {{
                font-size: 18px;
                font-weight: bold;
                color: #059669;
            }}
            .invoice-details {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 10px;
                margin-bottom: 15px;
            }}
            .btn {{
                display: inline-block;
                background: #2563eb;
                color: white;
                padding: 10px 20px;
                text-decoration: none;
                border-radius: 6px;
                margin-top: 10px;
            }}
            .empty-state {{
                text-align: center;
                padding: 40px;
                color: #6b7280;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>✅ Facturas Aprobadas</h1>
                <p>Historial completo de facturas aprobadas en el sistema</p>
            </div>

            <div class="stats">
                <div class="stat-card">
                    <div class="stat-number">{len(approved)}</div>
                    <div class="stat-label">Total Aprobadas</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">${sum([float(inv.get('monto_total', 0)) for inv in approved.values()]):.2f}</div>
                    <div class="stat-label">Monto Total Aprobado</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{len([inv for inv in approved.values() if inv.get('updated_at')])}</div>
                    <div class="stat-label">Procesadas</div>
                </div>
            </div>

            <div class="invoice-grid">
                {"".join([f'''
                <div class="invoice-card">
                    <div class="invoice-header">
                        <div class="invoice-title">Factura: {inv.get('numero_factura', 'N/A')}</div>
                        <div style="color: #6b7280; font-size: 14px;">ID: {inv_id}</div>
                    </div>
                    
                    <div class="invoice-details">
                        <div><strong>Proveedor:</strong> {inv.get('proveedor', 'N/A')}</div>
                        <div><strong>Monto:</strong> ${inv.get('monto_total', 'N/A')}</div>
                        <div><strong>Fecha Emisión:</strong> {inv.get('fecha_emision', 'N/A')}</div>
                        <div><strong>Aprobado el:</strong> {inv.get('updated_at', 'N/A')[:19]}</div>
                    </div>
                    
                    <div style="margin-top: 15px;">
                        <strong>📋 Historial:</strong>
                        <div style="font-size: 12px; margin-top: 5px;">
                            {" → ".join([h['status'] for h in inv.get('status_history', [])])}
                        </div>
                    </div>
                </div>
                ''' for inv_id, inv in approved.items()]) if approved else '''
                <div class="empty-state">
                    <h3>📝 No hay facturas aprobadas</h3>
                    <p>No se han aprobado facturas en el sistema.</p>
                </div>
                '''}
            </div>

            <div style="text-align: center; margin-top: 30px;">
                <a href="/" class="btn">🏠 Volver al Inicio</a>
                <a href="/rejected-invoices" class="btn" style="background: #dc2626; margin-left: 10px;">📋 Ver Rechazadas</a>
            </div>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@app.get("/all-invoices", response_class=HTMLResponse)
async def all_invoices():
    """Página para ver todas las facturas"""
    invoices = db.invoices
    
    # Contar facturas por estado
    status_counts = {
        'En Proceso': len([inv for inv in invoices.values() if inv.get('status') == 'En Proceso']),
        'Aprobado': len([inv for inv in invoices.values() if inv.get('status') == 'Aprobado']),
        'Rechazado': len([inv for inv in invoices.values() if inv.get('status') == 'Rechazado'])
    }
    
    # Generar filas de la tabla
    table_rows = ""
    if invoices:
        for inv_id, inv in invoices.items():
            status = inv.get('status', 'En Proceso')
            status_class = f"status-{status.lower().replace(' ', '-')}"
            
            table_rows += f'''
            <tr class="invoice-row" data-status="{status}">
                <td style="font-size: 12px; color: #6b7280;">{inv_id[:8]}...</td>
                <td>{inv.get('numero_factura', 'N/A')}</td>
                <td>{inv.get('proveedor', 'N/A')}</td>
                <td>${inv.get('monto_total', 'N/A')}</td>
                <td>{inv.get('fecha_emision', 'N/A')}</td>
                <td>
                    <span class="status-badge {status_class}">
                        {status}
                    </span>
                </td>
                <td>
                    <a href="/api/invoice/{inv_id}" style="color: #2563eb; text-decoration: none;">👁️ Ver</a>
                </td>
            </tr>
            '''
    else:
        table_rows = '''
        <tr>
            <td colspan="7" class="empty-state">
                <h3>📝 No hay facturas en el sistema</h3>
                <p>Sube tu primera factura para comenzar.</p>
            </td>
        </tr>
        '''
    
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Todas las Facturas</title>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body { 
                font-family: 'Segoe UI', Arial, sans-serif; 
                background: linear-gradient(135deg, #6366f1 0%, #4f46e5 100%);
                min-height: 100vh;
                padding: 20px;
            }
            .container {
                max-width: 1200px;
                margin: 0 auto;
                background: white;
                border-radius: 15px;
                padding: 30px;
                box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            }
            .header {
                text-align: center;
                margin-bottom: 30px;
                padding-bottom: 20px;
                border-bottom: 2px solid #e2e8f0;
            }
            .header h1 {
                color: #4f46e5;
                margin-bottom: 10px;
            }
            .filters {
                display: flex;
                gap: 15px;
                margin-bottom: 20px;
                flex-wrap: wrap;
            }
            .filter-btn {
                padding: 10px 20px;
                border: 2px solid #e2e8f0;
                background: white;
                border-radius: 8px;
                cursor: pointer;
                transition: all 0.3s ease;
            }
            .filter-btn.active {
                background: #4f46e5;
                color: white;
                border-color: #4f46e5;
            }
            .invoice-table {
                width: 100%;
                border-collapse: collapse;
                margin-top: 20px;
            }
            .invoice-table th,
            .invoice-table td {
                padding: 12px;
                text-align: left;
                border-bottom: 1px solid #e2e8f0;
            }
            .invoice-table th {
                background: #f8fafc;
                font-weight: 600;
                color: #374151;
            }
            .status-badge {
                padding: 6px 12px;
                border-radius: 20px;
                font-size: 12px;
                font-weight: 600;
            }
            .status-pending { background: #fef3c7; color: #d97706; }
            .status-approved { background: #d1fae5; color: #059669; }
            .status-rejected { background: #fef2f2; color: #dc2626; }
            .btn {
                display: inline-block;
                background: #2563eb;
                color: white;
                padding: 10px 20px;
                text-decoration: none;
                border-radius: 6px;
                margin-top: 20px;
            }
            .empty-state {
                text-align: center;
                padding: 40px;
                color: #6b7280;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>📊 Todas las Facturas</h1>
                <p>Vista completa del historial de facturas en el sistema</p>
            </div>

            <div class="filters" id="filters">
                <button class="filter-btn active" onclick="filterInvoices('all')">Todas (""" + str(len(invoices)) + """)</button>
                <button class="filter-btn" onclick="filterInvoices('En Proceso')">En Proceso (""" + str(status_counts['En Proceso']) + """)</button>
                <button class="filter-btn" onclick="filterInvoices('Aprobado')">Aprobadas (""" + str(status_counts['Aprobado']) + """)</button>
                <button class="filter-btn" onclick="filterInvoices('Rechazado')">Rechazadas (""" + str(status_counts['Rechazado']) + """)</button>
            </div>

            <table class="invoice-table" id="invoiceTable">
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>N° Factura</th>
                        <th>Proveedor</th>
                        <th>Monto</th>
                        <th>Fecha</th>
                        <th>Estado</th>
                        <th>Acciones</th>
                    </tr>
                </thead>
                <tbody>
                    """ + table_rows + """
                </tbody>
            </table>

            <div style="text-align: center; margin-top: 30px;">
                <a href="/" class="btn">🏠 Volver al Inicio</a>
                <a href="/rejected-invoices" class="btn" style="background: #dc2626; margin-left: 10px;">📋 Rechazadas</a>
                <a href="/approved-invoices" class="btn" style="background: #059669; margin-left: 10px;">✅ Aprobadas</a>
            </div>
        </div>

        <script>
            function filterInvoices(status) {
                const rows = document.querySelectorAll('.invoice-row');
                const buttons = document.querySelectorAll('.filter-btn');
                
                rows.forEach(row => {
                    if (status === 'all' || row.dataset.status === status) {
                        row.style.display = '';
                    } else {
                        row.style.display = 'none';
                    }
                });
                
                buttons.forEach(btn => {
                    btn.classList.remove('active');
                });
                event.target.classList.add('active');
            }
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@app.get("/api/invoice/{invoice_id}")
async def get_invoice(invoice_id: str):
    """Obtener información de una factura"""
    try:
        print(f"🔍 Consultando factura: {invoice_id}")
        invoice = db.get_invoice(invoice_id)
        if invoice:
            return {
                "invoice": invoice,
                "message": "Factura encontrada"
            }
        else:
            raise HTTPException(status_code=404, detail="Factura no encontrada")
    except Exception as e:
        print(f"❌ Error obteniendo factura: {e}")
        raise HTTPException(status_code=500, detail=f"Error obteniendo factura: {str(e)}")

@app.get("/api/invoices")
async def get_all_invoices():
    """Obtener todas las facturas"""
    try:
        print("📋 Listando todas las facturas...")
        invoices = db.invoices
        return {
            "total": len(invoices),
            "invoices": invoices
        }
    except Exception as e:
        print(f"❌ Error listando facturas: {e}")
        raise HTTPException(status_code=500, detail=f"Error listando facturas: {str(e)}")

@app.get("/api/stats")
async def get_stats():
    """Obtener estadísticas del sistema"""
    try:
        invoices = db.invoices
        total_invoices = len(invoices)
        status_count = {
            "En Proceso": 0,
            "Aprobado": 0,
            "Rechazado": 0
        }
        
        total_amount = 0
        rejected_with_comments = 0
        
        for invoice_id, invoice in invoices.items():
            status = invoice.get('status', 'En Proceso')
            status_count[status] = status_count.get(status, 0) + 1
            
            # Sumar montos de facturas aprobadas
            if status == "Aprobado" and invoice.get('monto_total'):
                try:
                    total_amount += float(invoice['monto_total'])
                except (ValueError, TypeError):
                    pass
            
            # Contar rechazos con comentarios
            if status == "Rechazado" and invoice.get('rejection_comments'):
                rejected_with_comments += 1
        
        return {
            "total_facturas": total_invoices,
            "por_estado": status_count,
            "monto_total_aprobado": round(total_amount, 2),
            "rechazos_con_comentarios": rejected_with_comments,
            "facturas_procesadas_hoy": len([inv for inv in invoices.values() 
                                          if inv.get('created_at', '').startswith(datetime.utcnow().strftime('%Y-%m-%d'))]),
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        print(f"❌ Error obteniendo estadísticas: {e}")
        raise HTTPException(status_code=500, detail=f"Error obteniendo estadísticas: {str(e)}")

# Interfaz web principal (ACTUALIZADA con nuevos enlaces)
@app.get("/", response_class=HTMLResponse)
async def read_root():
    """Interfaz web para subir facturas - VERSIÓN MEJORADA"""
    stats_data = await get_stats()
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Sistema de Facturas - IA</title>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            * {{ margin: 0; padding: 0; box-sizing: border-box; }}
            body {{ 
                font-family: 'Segoe UI', Arial, sans-serif; 
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                padding: 20px;
            }}
            .container {{
                max-width: 800px;
                margin: 0 auto;
                background: white;
                border-radius: 15px;
                padding: 30px;
                box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            }}
            .header {{
                text-align: center;
                margin-bottom: 30px;
            }}
            .header h1 {{
                color: #2563eb;
                margin-bottom: 10px;
                font-size: 2.5em;
            }}
            .header p {{
                color: #6b7280;
                font-size: 1.1em;
            }}
            .upload-area {{
                border: 3px dashed #cbd5e1;
                border-radius: 12px;
                padding: 40px;
                text-align: center;
                margin-bottom: 25px;
                transition: all 0.3s ease;
                background: #f8fafc;
            }}
            .upload-area:hover {{
                border-color: #2563eb;
                background: #f0f9ff;
            }}
            .upload-area.dragover {{
                border-color: #10b981;
                background: #f0fdf4;
            }}
            .form-group {{
                margin-bottom: 20px;
            }}
            label {{
                display: block;
                margin-bottom: 8px;
                font-weight: 600;
                color: #374151;
            }}
            input[type="email"], input[type="file"] {{
                width: 100%;
                padding: 12px 15px;
                border: 2px solid #e2e8f0;
                border-radius: 8px;
                font-size: 16px;
                transition: border-color 0.3s ease;
            }}
            input[type="email"]:focus, input[type="file"]:focus {{
                outline: none;
                border-color: #2563eb;
            }}
            .btn {{
                background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
                color: white;
                border: none;
                padding: 15px 30px;
                border-radius: 8px;
                font-size: 16px;
                font-weight: 600;
                cursor: pointer;
                transition: all 0.3s ease;
                width: 100%;
            }}
            .btn:hover {{
                transform: translateY(-2px);
                box-shadow: 0 10px 25px rgba(37, 99, 235, 0.3);
            }}
            .btn:disabled {{
                background: #9ca3af;
                cursor: not-allowed;
                transform: none;
                box-shadow: none;
            }}
            .result {{
                margin-top: 25px;
                padding: 20px;
                border-radius: 8px;
                display: none;
            }}
            .success {{
                background: #f0fdf4;
                border: 2px solid #10b981;
                color: #065f46;
            }}
            .error {{
                background: #fef2f2;
                border: 2px solid #ef4444;
                color: #7f1d1d;
            }}
            .loading {{
                display: none;
                text-align: center;
                margin: 20px 0;
            }}
            .stats {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
                gap: 15px;
                margin-top: 30px;
            }}
            .stat-card {{
                background: #f8fafc;
                padding: 20px;
                border-radius: 8px;
                text-align: center;
                border-left: 4px solid #2563eb;
            }}
            .stat-number {{
                font-size: 24px;
                font-weight: bold;
                color: #2563eb;
            }}
            .stat-label {{
                font-size: 14px;
                color: #64748b;
                margin-top: 5px;
            }}
            .features {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 15px;
                margin: 30px 0;
            }}
            .feature-card {{
                background: #f0f9ff;
                padding: 20px;
                border-radius: 8px;
                text-align: center;
                border: 1px solid #bae6fd;
            }}
            .nav-buttons {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 15px;
                margin-top: 30px;
            }}
            .nav-btn {{
                display: block;
                background: white;
                color: #374151;
                padding: 20px;
                text-align: center;
                border-radius: 10px;
                text-decoration: none;
                border: 2px solid #e2e8f0;
                transition: all 0.3s ease;
                font-weight: 600;
            }}
            .nav-btn:hover {{
                transform: translateY(-3px);
                box-shadow: 0 10px 25px rgba(0,0,0,0.1);
            }}
            .nav-btn.approved {{ border-color: #10b981; color: #10b981; }}
            .nav-btn.rejected {{ border-color: #ef4444; color: #ef4444; }}
            .nav-btn.all {{ border-color: #6366f1; color: #6366f1; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🧠 Sistema Inteligente de Facturas</h1>
                <p>Procesamiento automático con IA • OCR • Notificaciones por Email</p>
            </div>

            <div class="features">
                <div class="feature-card">
                    <h3>🔍 OCR Inteligente</h3>
                    <p>Extrae datos automáticamente de facturas</p>
                </div>
                <div class="feature-card">
                    <h3>📧 Notificaciones</h3>
                    <p>Envía emails con botones interactivos</p>
                </div>
                <div class="feature-card">
                    <h3>✅ Flujo Completo</h3>
                    <p>Aprobación, rechazo y historial</p>
                </div>
            </div>

            <form id="uploadForm" enctype="multipart/form-data">
                <div class="form-group">
                    <label for="file">📄 Selecciona una factura (PDF, PNG, JPG):</label>
                    <div class="upload-area" id="uploadArea">
                        <p style="font-size: 18px; margin-bottom: 15px;">Arrastra tu archivo aquí o haz click para seleccionar</p>
                        <input type="file" id="file" name="file" accept=".pdf,.png,.jpg,.jpeg" required 
                               style="display: none;">
                        <button type="button" onclick="document.getElementById('file').click()" 
                                style="background: #2563eb; color: white; border: none; padding: 10px 20px; border-radius: 6px; cursor: pointer;">
                            Seleccionar Archivo
                        </button>
                        <p id="fileName" style="margin-top: 15px; color: #64748b;"></p>
                    </div>
                </div>

                <div class="form-group">
                    <label for="email">📧 Email del aprobador:</label>
                    <input type="email" id="email" name="approver_email" 
                           value="diego.31326600@uru.edu" required>
                </div>

                <button type="submit" class="btn" id="submitBtn">
                    🚀 Procesar Factura con IA
                </button>
            </form>

            <div class="loading" id="loading">
                <p>🔄 Procesando factura con inteligencia artificial...</p>
                <p style="font-size: 14px; color: #64748b;">Esto puede tomar unos segundos</p>
            </div>

            <div class="result success" id="successResult"></div>
            <div class="result error" id="errorResult"></div>

            <div class="nav-buttons">
                <a href="/approved-invoices" class="nav-btn approved">
                    ✅ Facturas Aprobadas<br>
                    <small>{stats_data['por_estado']['Aprobado']} facturas</small>
                </a>
                <a href="/rejected-invoices" class="nav-btn rejected">
                    ❌ Facturas Rechazadas<br>
                    <small>{stats_data['por_estado']['Rechazado']} facturas</small>
                </a>
                <a href="/all-invoices" class="nav-btn all">
                    📊 Todas las Facturas<br>
                    <small>{stats_data['total_facturas']} total</small>
                </a>
            </div>

            <div class="stats" id="stats">
                <div class="stat-card">
                    <div class="stat-number">{stats_data['total_facturas']}</div>
                    <div class="stat-label">Total Facturas</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{stats_data['por_estado']['En Proceso']}</div>
                    <div class="stat-label">En Proceso</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{stats_data['por_estado']['Aprobado']}</div>
                    <div class="stat-label">Aprobadas</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">${stats_data['monto_total_aprobado']}</div>
                    <div class="stat-label">Total Aprobado</div>
                </div>
            </div>
        </div>

        <script>
            // Manejar drag & drop
            const uploadArea = document.getElementById('uploadArea');
            const fileInput = document.getElementById('file');
            const fileName = document.getElementById('fileName');

            uploadArea.addEventListener('click', () => fileInput.click());
            
            fileInput.addEventListener('change', function(e) {{
                if (this.files.length > 0) {{
                    fileName.textContent = `Archivo seleccionado: ${{this.files[0].name}}`;
                    uploadArea.style.borderColor = '#10b981';
                    uploadArea.style.background = '#f0fdf4';
                }}
            }});

            // Manejar envío del formulario
            document.getElementById('uploadForm').addEventListener('submit', async function(e) {{
                e.preventDefault();
                
                const formData = new FormData();
                formData.append('file', fileInput.files[0]);
                formData.append('approver_email', document.getElementById('email').value);

                // Mostrar loading
                document.getElementById('loading').style.display = 'block';
                document.getElementById('submitBtn').disabled = true;
                document.getElementById('successResult').style.display = 'none';
                document.getElementById('errorResult').style.display = 'none';

                try {{
                    const response = await fetch('/api/upload-invoice', {{
                        method: 'POST',
                        body: formData
                    }});

                    const result = await response.json();

                    if (response.ok) {{
                        document.getElementById('successResult').innerHTML = `
                            <h3>✅ ¡Factura procesada exitosamente!</h3>
                            <p><strong>ID:</strong> ${{result.invoice_id}}</p>
                            <p><strong>Estado:</strong> ${{result.status}}</p>
                            <p><strong>Confianza de extracción:</strong> ${{Math.round(result.confianza_extraccion * 100)}}%</p>
                            <p><strong>Notificación enviada a:</strong> ${{result.notification_sent_to}}</p>
                            <p><strong>Datos extraídos:</strong></p>
                            <ul>
                                <li>Proveedor: ${{result.extracted_data.proveedor}}</li>
                                <li>N° Factura: ${{result.extracted_data.numero_factura}}</li>
                                <li>Monto: $${{result.extracted_data.monto_total}}</li>
                                <li>Fecha: ${{result.extracted_data.fecha_emision}}</li>
                            </ul>
                            <p><em>📧 Se ha enviado un email con botones de aprobación/rechazo</em></p>
                        `;
                        document.getElementById('successResult').style.display = 'block';
                        
                        // Recargar estadísticas
                        setTimeout(() => window.location.reload(), 2000);
                    }} else {{
                        throw new Error(result.detail || 'Error desconocido');
                    }}
                }} catch (error) {{
                    document.getElementById('errorResult').innerHTML = `
                        <h3>❌ Error al procesar la factura</h3>
                        <p>${{error.message}}</p>
                    `;
                    document.getElementById('errorResult').style.display = 'block';
                }} finally {{
                    document.getElementById('loading').style.display = 'none';
                    document.getElementById('submitBtn').disabled = false;
                }}
            }});
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@app.get("/health")
async def health_check():
    """Endpoint de salud"""
    return {
        "status": "healthy",
        "service": "Invoice Processing System v2.1",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "2.1.0",
        "features": [
            "OCR inteligente con Tesseract",
            "Procesamiento de PDF e imágenes", 
            "Extracción automática de datos",
            "Sistema de notificaciones por email",
            "Botones interactivos en emails",
            "Interfaz web responsive",
            "Base de datos JSON con historial",
            "Gestión completa de rechazos",
            "API REST completa",
            "Estadísticas en tiempo real"
        ]
    }

if __name__ == "__main__":
    print("🚀 Iniciando Servidor de Procesamiento Inteligente de Facturas v2.1...")
    print(f"📊 Tesseract path: {config.Config.TESSERACT_PATH}")
    print(f"📁 Upload folder: {config.Config.UPLOAD_FOLDER}")
    print(f"📧 Email configurado: {config.Config.EMAIL_USER}")
    print("🌐 Servidor disponible en: http://localhost:8000")
    print("📚 Documentación API: http://localhost:8000/api/docs")
    print("🖥️  Interfaz web: http://localhost:8000/")
    print("📋 Nuevas características:")
    print("   • Página de facturas rechazadas: /rejected-invoices")
    print("   • Página de facturas aprobadas: /approved-invoices") 
    print("   • Todas las facturas: /all-invoices")
    print("   • Historial completo de estados")
    print("   • Comentarios persistentes en rechazos")
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)