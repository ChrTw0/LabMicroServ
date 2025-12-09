/**
 * InvoiceDetailPage Component
 * Página de detalle de comprobante electrónico con acciones de SUNAT
 */
import { useEffect, useState } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { useBilling } from '../../hooks/useBilling';
import './InvoiceDetailPage.css';

const InvoiceDetailPage = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const { loading, error, fetchInvoiceById, sendToSUNAT, voidInvoice, getUBL, getCDR } = useBilling();

  const [invoice, setInvoice] = useState(null);
  const [showVoidModal, setShowVoidModal] = useState(false);
  const [voidReason, setVoidReason] = useState('');
  const [actionLoading, setActionLoading] = useState(false);

  useEffect(() => {
    loadInvoice();
  }, [id]);

  const loadInvoice = async () => {
    const result = await fetchInvoiceById(id);
    if (result.success) {
      setInvoice(result.data);
    } else {
      alert(`Error: ${result.error}`);
      navigate('/dashboard/billing');
    }
  };

  const handleSendToSUNAT = async () => {
    if (!window.confirm('¿Enviar este comprobante a SUNAT?')) {
      return;
    }

    setActionLoading(true);
    const result = await sendToSUNAT(id);
    if (result.success) {
      alert('Comprobante enviado a SUNAT correctamente');
      await loadInvoice();
    } else {
      alert(`Error al enviar: ${result.error}`);
    }
    setActionLoading(false);
  };

  const handleVoid = async (e) => {
    e.preventDefault();

    if (!voidReason.trim()) {
      alert('Debe especificar un motivo de anulación');
      return;
    }

    setActionLoading(true);
    const result = await voidInvoice(id, voidReason);
    if (result.success) {
      alert('Comprobante anulado correctamente');
      setShowVoidModal(false);
      await loadInvoice();
    } else {
      alert(`Error al anular: ${result.error}`);
    }
    setActionLoading(false);
  };

  const handleDownloadUBL = async () => {
    const result = await getUBL(id);
    if (result.success) {
      // Crear un blob con el XML y descargarlo
      const blob = new Blob([result.data.xml_content], { type: 'application/xml' });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${invoice.invoice_number}.xml`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } else {
      alert(`Error al descargar XML: ${result.error}`);
    }
  };

  const handleDownloadCDR = async () => {
    const result = await getCDR(id);
    if (result.success) {
      // Crear un blob con el CDR y descargarlo
      const blob = new Blob([result.data.cdr_content], { type: 'application/xml' });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `R-${invoice.invoice_number}.xml`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } else {
      alert(`Error al descargar CDR: ${result.error}`);
    }
  };

  const getStatusBadge = (status) => {
    const badges = {
      DRAFT: 'badge-secondary',
      PENDING: 'badge-warning',
      SENT: 'badge-info',
      ACCEPTED: 'badge-success',
      REJECTED: 'badge-danger',
      VOIDED: 'badge-dark',
    };
    return badges[status] || 'badge-secondary';
  };

  const getStatusLabel = (status) => {
    const labels = {
      DRAFT: 'Borrador',
      PENDING: 'Pendiente',
      SENT: 'Enviado',
      ACCEPTED: 'Aceptado',
      REJECTED: 'Rechazado',
      VOIDED: 'Anulado',
    };
    return labels[status] || status;
  };

  const getDocumentTypeLabel = (type) => {
    const labels = {
      '01': 'Factura Electrónica',
      '03': 'Boleta de Venta Electrónica',
      '07': 'Nota de Crédito Electrónica',
      '08': 'Nota de Débito Electrónica',
    };
    return labels[type] || type;
  };

  const formatCurrency = (amount) => {
    return `S/ ${parseFloat(amount).toFixed(2)}`;
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('es-PE', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    });
  };

  if (loading || !invoice) {
    return (
      <div className="loading-container">
        <p>Cargando comprobante...</p>
      </div>
    );
  }

  return (
    <div className="invoice-detail-page">
      <div className="page-header">
        <div>
          <Link to="/dashboard/billing" className="btn-back">← Volver</Link>
          <h1>{invoice.invoice_number}</h1>
          <p className="document-type">{getDocumentTypeLabel(invoice.invoice_type)}</p>
        </div>
        <span className={`badge ${getStatusBadge(invoice.invoice_status)}`}>
          {getStatusLabel(invoice.invoice_status)}
        </span>
      </div>

      {error && (
        <div className="alert alert-error">
          {error}
        </div>
      )}

      <div className="detail-grid">
        {/* Información del Comprobante */}
        <div className="detail-card">
          <h2>Información del Comprobante</h2>
          <div className="detail-row">
            <span className="detail-label">N° Comprobante:</span>
            <span className="detail-value"><strong>{invoice.invoice_number}</strong></span>
          </div>
          <div className="detail-row">
            <span className="detail-label">Tipo:</span>
            <span className="detail-value">{getDocumentTypeLabel(invoice.invoice_type)}</span>
          </div>
          <div className="detail-row">
            <span className="detail-label">Fecha de Emisión:</span>
            <span className="detail-value">{formatDate(invoice.issue_date)}</span>
          </div>
          <div className="detail-row">
            <span className="detail-label">Moneda:</span>
            <span className="detail-value">{invoice.currency || 'PEN'}</span>
          </div>
          {invoice.order_id && (
            <div className="detail-row">
              <span className="detail-label">Orden Relacionada:</span>
              <Link to={`/dashboard/orders/${invoice.order_id}`} className="link-primary">
                Ver Orden #{invoice.order_id}
              </Link>
            </div>
          )}
        </div>

        {/* Información del Cliente */}
        <div className="detail-card">
          <h2>Cliente</h2>
          <div className="detail-row">
            <span className="detail-label">Razón Social/Nombre:</span>
            <span className="detail-value">{invoice.customer_name}</span>
          </div>
          <div className="detail-row">
            <span className="detail-label">Documento:</span>
            <span className="detail-value">{invoice.customer_document_type} {invoice.customer_document_number}</span>
          </div>
          {invoice.customer_address && (
            <div className="detail-row">
              <span className="detail-label">Dirección:</span>
              <span className="detail-value">{invoice.customer_address}</span>
            </div>
          )}
          {invoice.customer_email && (
            <div className="detail-row">
              <span className="detail-label">Email:</span>
              <span className="detail-value">{invoice.customer_email}</span>
            </div>
          )}
        </div>
      </div>

      {/* Items del Comprobante */}
      <div className="detail-card full-width">
        <h2>Detalle de Items</h2>
        <div className="table-container">
          <table className="items-table">
            <thead>
              <tr>
                <th>Descripción</th>
                <th>Cantidad</th>
                <th>Precio Unit.</th>
                <th>Subtotal</th>
              </tr>
            </thead>
            <tbody>
              {invoice.items && invoice.items.length > 0 ? (
                invoice.items.map((item, index) => (
                  <tr key={index}>
                    <td>{item.description}</td>
                    <td>{item.quantity}</td>
                    <td>{formatCurrency(item.unit_price)}</td>
                    <td>{formatCurrency(item.subtotal)}</td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan="4" className="text-center">No hay items</td>
                </tr>
              )}
            </tbody>
            <tfoot>
              <tr>
                <td colSpan="3" className="text-right">Subtotal:</td>
                <td>{formatCurrency(invoice.subtotal || 0)}</td>
              </tr>
              <tr>
                <td colSpan="3" className="text-right">IGV (18%):</td>
                <td>{formatCurrency(invoice.tax || 0)}</td>
              </tr>
              <tr className="total-row">
                <td colSpan="3" className="text-right"><strong>TOTAL:</strong></td>
                <td><strong>{formatCurrency(invoice.total)}</strong></td>
              </tr>
            </tfoot>
          </table>
        </div>
      </div>

      {/* Información de SUNAT */}
      {invoice.invoice_status !== 'DRAFT' && (
        <div className="detail-card full-width">
          <h2>Estado SUNAT</h2>
          <div className="sunat-info">
            <div className="detail-row">
              <span className="detail-label">Estado:</span>
              <span className={`badge ${getStatusBadge(invoice.invoice_status)}`}>
                {getStatusLabel(invoice.invoice_status)}
              </span>
            </div>
            {invoice.sunat_response_code && (
              <div className="detail-row">
                <span className="detail-label">Código de Respuesta:</span>
                <span className="detail-value">{invoice.sunat_response_code}</span>
              </div>
            )}
            {invoice.sunat_response_description && (
              <div className="detail-row">
                <span className="detail-label">Descripción:</span>
                <span className="detail-value">{invoice.sunat_response_description}</span>
              </div>
            )}
            {invoice.cdr_hash && (
              <div className="detail-row">
                <span className="detail-label">Hash CDR:</span>
                <span className="detail-value code">{invoice.cdr_hash}</span>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Acciones */}
      <div className="actions-card">
        <h2>Acciones</h2>
        <div className="actions-buttons">
          {invoice.invoice_status === 'DRAFT' && (
            <button
              onClick={handleSendToSUNAT}
              className="btn btn-primary"
              disabled={actionLoading}
            >
              📤 Enviar a SUNAT
            </button>
          )}

          {invoice.invoice_status === 'SENT' || invoice.invoice_status === 'ACCEPTED' ? (
            <>
              <button onClick={handleDownloadUBL} className="btn btn-secondary">
                📄 Descargar XML/UBL
              </button>
              {invoice.invoice_status === 'ACCEPTED' && (
                <button onClick={handleDownloadCDR} className="btn btn-secondary">
                  📥 Descargar CDR
                </button>
              )}
            </>
          ) : null}

          {(invoice.invoice_status === 'ACCEPTED' || invoice.invoice_status === 'SENT') && (
            <button
              onClick={() => setShowVoidModal(true)}
              className="btn btn-danger"
              disabled={actionLoading}
            >
              🗑️ Anular Comprobante
            </button>
          )}
        </div>
      </div>

      {/* Modal de Anulación */}
      {showVoidModal && (
        <div className="modal-overlay" onClick={() => setShowVoidModal(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <h2>Anular Comprobante</h2>
            <form onSubmit={handleVoid}>
              <div className="form-group">
                <label>Motivo de Anulación: *</label>
                <textarea
                  value={voidReason}
                  onChange={(e) => setVoidReason(e.target.value)}
                  placeholder="Ingrese el motivo de la anulación..."
                  className="form-control"
                  rows="4"
                  required
                />
              </div>
              <div className="modal-actions">
                <button
                  type="submit"
                  className="btn btn-danger"
                  disabled={actionLoading}
                >
                  {actionLoading ? 'Procesando...' : 'Confirmar Anulación'}
                </button>
                <button
                  type="button"
                  onClick={() => setShowVoidModal(false)}
                  className="btn btn-outline"
                  disabled={actionLoading}
                >
                  Cancelar
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default InvoiceDetailPage;
