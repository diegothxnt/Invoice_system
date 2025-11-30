import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from jinja2 import Template
import config
from datetime import datetime

class EmailSystem:
    def __init__(self):
        self.config = config.Config
        print("✅ Sistema de Email Gmail inicializado")
    
    async def send_notification(self, to_email, invoice_data, invoice_id):
        """Envía email real por Gmail"""
        try:
            print(f"\n📧 ENVIANDO EMAIL REAL A: {to_email}")
            
            if not self.config.EMAIL_USER or not self.config.EMAIL_PASSWORD:
                print("❌ Credenciales de Gmail no configuradas")
                return False
            
            # Crear URLs
            base_url = self.config.BASE_URL
            approval_url = f"{base_url}/api/approve/{invoice_id}"
            rejection_url = f"{base_url}/reject-form/{invoice_id}"
            
            # Crear mensaje
            msg = MIMEMultipart()
            msg['Subject'] = f"✅ Revisión Requerida - Factura {invoice_data.get('numero_factura', 'N/A')}"
            msg['From'] = self.config.EMAIL_USER
            msg['To'] = to_email
            
            # Crear cuerpo del email
            html_content = self.create_email_template(invoice_data, approval_url, rejection_url)
            msg.attach(MIMEText(html_content, 'html'))
            
            # ENVÍO CON GMAIL
            print("🔄 Conectando a Gmail...")
            server = smtplib.SMTP(self.config.SMTP_SERVER, self.config.SMTP_PORT)
            server.starttls()
            print("🔐 Autenticando...")
            server.login(self.config.EMAIL_USER, self.config.EMAIL_PASSWORD)
            print("📤 Enviando email...")
            server.send_message(msg)
            server.quit()
            
            print("🎉 EMAIL GMAIL ENVIADO EXITOSAMENTE!")
            print(f"   Para: {to_email}")
            print("📨 Revisa tu bandeja de entrada y carpeta SPAM")
            return True
            
        except Exception as e:
            print(f"❌ Error enviando email: {e}")
            return False
    
    def create_email_template(self, invoice_data, approval_url, rejection_url):
        """Crea plantilla HTML profesional"""
        html_template = """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <style>
                body { 
                    font-family: 'Arial', sans-serif; 
                    margin: 0; padding: 0; 
                    background: #f5f5f5;
                }
                .container { 
                    max-width: 600px; 
                    margin: 20px auto; 
                    background: white; 
                    border-radius: 10px; 
                    overflow: hidden; 
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                }
                .header { 
                    background: #4285f4; 
                    color: white; 
                    padding: 30px; 
                    text-align: center; 
                }
                .header h1 { 
                    margin: 0; 
                    font-size: 24px;
                }
                .content { 
                    padding: 30px; 
                }
                .invoice-info { 
                    background: #f8f9fa; 
                    padding: 20px; 
                    border-radius: 8px; 
                    margin: 20px 0; 
                    border-left: 4px solid #4285f4;
                }
                table { 
                    width: 100%; 
                    border-collapse: collapse; 
                }
                th, td { 
                    padding: 12px; 
                    text-align: left; 
                    border-bottom: 1px solid #e0e0e0; 
                }
                th { 
                    background: #f1f3f4; 
                    font-weight: 600;
                    color: #333;
                }
                .actions { 
                    text-align: center; 
                    margin: 30px 0; 
                }
                .btn { 
                    display: inline-block; 
                    padding: 15px 30px; 
                    margin: 0 10px; 
                    text-decoration: none; 
                    border-radius: 8px; 
                    font-weight: bold; 
                    color: white;
                    font-size: 16px;
                }
                .btn-approve { 
                    background: #34a853; 
                }
                .btn-reject { 
                    background: #ea4335; 
                }
                .footer { 
                    text-align: center; 
                    padding: 20px; 
                    background: #f8f9fa; 
                    color: #666; 
                    font-size: 14px;
                }
                .btn:hover {
                    opacity: 0.9;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>📋 Factura para Revisión</h1>
                    <p>Sistema de Procesamiento de Facturas con IA</p>
                </div>
                
                <div class="content">
                    <div class="invoice-info">
                        <table>
                            <tr>
                                <th>Proveedor:</th>
                                <td>{{ proveedor }}</td>
                            </tr>
                            <tr>
                                <th>N° Factura:</th>
                                <td>{{ numero_factura }}</td>
                            </tr>
                            <tr>
                                <th>Fecha de Emisión:</th>
                                <td>{{ fecha_emision }}</td>
                            </tr>
                            <tr>
                                <th>Monto Total:</th>
                                <td style="color: #34a853; font-weight: bold;">${{ monto_total }}</td>
                            </tr>
                            <tr>
                                <th>Impuestos:</th>
                                <td>${{ impuestos }}</td>
                            </tr>
                            <tr>
                                <th>Fecha de Vencimiento:</th>
                                <td>{{ fecha_vencimiento }}</td>
                            </tr>
                            <tr>
                                <th>Confianza de Extracción:</th>
                                <td>{{ confianza_ocr }}%</td>
                            </tr>
                        </table>
                    </div>

                    <div class="actions">
                        <p style="margin-bottom: 20px; color: #333; font-size: 18px;">
                            <strong>¿Qué acción desea tomar?</strong>
                        </p>
                        <a href="{{ approval_url }}" class="btn btn-approve">
                            ✅ Aprobar Factura
                        </a>
                        <a href="{{ rejection_url }}" class="btn btn-reject">
                            ❌ Rechazar Factura
                        </a>
                    </div>

                    <div style="background: #e8f0fe; padding: 15px; border-radius: 8px; margin-top: 20px;">
                        <p style="margin: 0; color: #1967d2; font-size: 14px;">
                            <strong>ID de Transacción:</strong> {{ invoice_id }}<br>
                            <strong>Procesado el:</strong> {{ fecha_procesamiento }}
                        </p>
                    </div>
                </div>
                
                <div class="footer">
                    <p>🤖 Sistema Inteligente de Procesamiento de Facturas</p>
                    <p>Este es un mensaje automático, por favor no responda a este correo.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        template = Template(html_template)
        return template.render(
            proveedor=invoice_data.get('proveedor', 'No identificado'),
            numero_factura=invoice_data.get('numero_factura', 'N/A'),
            fecha_emision=invoice_data.get('fecha_emision', 'N/A'),
            monto_total=invoice_data.get('monto_total', '0.00'),
            impuestos=invoice_data.get('impuestos', '0.00'),
            fecha_vencimiento=invoice_data.get('fecha_vencimiento', 'N/A'),
            confianza_ocr=int(invoice_data.get('confianza_ocr', 0) * 100),
            invoice_id=invoice_data.get('_id', 'N/A'),
            fecha_procesamiento=datetime.now().strftime("%d/%m/%Y %H:%M"),
            approval_url=approval_url,
            rejection_url=rejection_url
        )

# Instancia global
email_system = EmailSystem()