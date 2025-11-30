# database.py
from datetime import datetime
import json
import os

class DatabaseSimple:
    def __init__(self):
        self.data_file = "invoices_data.json"
        self.invoices = self._load_data()
        print("✅ Base de datos simple inicializada (JSON)")
    
    def _load_data(self):
        """Cargar datos desde archivo JSON"""
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    print(f"📊 Datos cargados: {len(data)} facturas")
                    return data
            return {}
        except Exception as e:
            print(f"❌ Error cargando datos: {e}")
            return {}
    
    def _save_data(self):
        """Guardar datos en archivo JSON"""
        try:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(self.invoices, f, indent=2, ensure_ascii=False, default=str)
            print("💾 Datos guardados correctamente")
        except Exception as e:
            print(f"❌ Error guardando datos: {e}")
    
    def save_invoice(self, invoice_data):
        """Guardar nueva factura"""
        try:
            invoice_id = str(datetime.utcnow().timestamp()).replace('.', '')
            invoice_data['_id'] = invoice_id
            invoice_data['created_at'] = datetime.utcnow().isoformat()
            invoice_data['status'] = "En Proceso"
            
            # Inicializar historial
            invoice_data['status_history'] = [{
                'status': "En Proceso",
                'timestamp': datetime.utcnow().isoformat(),
                'comments': "Factura creada y enviada para aprobación"
            }]
            
            self.invoices[invoice_id] = invoice_data
            self._save_data()
            
            print(f"💾 Factura guardada con ID: {invoice_id}")
            return invoice_id
        except Exception as e:
            print(f"❌ Error guardando factura: {e}")
            return None
    
    def update_invoice_status(self, invoice_id, status, comments=None):
        """Actualizar estado de factura con historial"""
        try:
            if invoice_id in self.invoices:
                self.invoices[invoice_id]['status'] = status
                self.invoices[invoice_id]['updated_at'] = datetime.utcnow().isoformat()
                
                # Guardar comentarios de rechazo
                if comments and comments != "Sin comentarios específicos":
                    self.invoices[invoice_id]['rejection_comments'] = comments
                    self.invoices[invoice_id]['rejected_at'] = datetime.utcnow().isoformat()
                
                # Agregar al historial
                history_entry = {
                    'status': status,
                    'timestamp': datetime.utcnow().isoformat()
                }
                
                if comments:
                    history_entry['comments'] = comments
                
                self.invoices[invoice_id]['status_history'].append(history_entry)
                self._save_data()
                
                print(f"✅ Estado actualizado: {invoice_id} -> {status}")
                return True
            return False
        except Exception as e:
            print(f"❌ Error actualizando estado: {e}")
            return False
    
    def get_invoice(self, invoice_id):
        """Obtener factura por ID"""
        return self.invoices.get(invoice_id)
    
    def get_rejected_invoices(self):
        """Obtener todas las facturas rechazadas"""
        rejected = {}
        for invoice_id, invoice in self.invoices.items():
            if invoice.get('status') == 'Rechazado':
                rejected[invoice_id] = invoice
        return rejected
    
    def get_approved_invoices(self):
        """Obtener todas las facturas aprobadas"""
        approved = {}
        for invoice_id, invoice in self.invoices.items():
            if invoice.get('status') == 'Aprobado':
                approved[invoice_id] = invoice
        return approved
    
    def get_invoices_by_status(self, status):
        """Obtener facturas por estado"""
        filtered = {}
        for invoice_id, invoice in self.invoices.items():
            if invoice.get('status') == status:
                filtered[invoice_id] = invoice
        return filtered

# Instancia global
db = DatabaseSimple()