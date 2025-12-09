/**
 * BillingListPage Component
 * Página de listado de comprobantes electrónicos (facturas/boletas)
 */
import { useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useBilling } from '../../hooks/useBilling';
import './BillingListPage.css';

const BillingListPage = () => {
  const navigate = useNavigate();
  const { invoices, loading, error, pagination, fetchInvoices } = useBilling();

  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [typeFilter, setTypeFilter] = useState('');
  const [dateFrom, setDateFrom] = useState('');
  const [dateTo, setDateTo] = useState('');

  useEffect(() => {
    fetchInvoices();
  }, []);

  const handleSearch = (e) => {
    e.preventDefault();

    const params = {};
    if (searchTerm) params.search = searchTerm;
    if (statusFilter) params.status = statusFilter;
    if (typeFilter) params.document_type = typeFilter;
    if (dateFrom) params.date_from = dateFrom;
    if (dateTo) params.date_to = dateTo;

    fetchInvoices(params);
  };

  const handleClearFilters = () => {
    setSearchTerm('');
    setStatusFilter('');
    setTypeFilter('');
    setDateFrom('');
    setDateTo('');
    fetchInvoices();
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

  const getDocumentTypeBadge = (type) => {
    const badges = {
      '01': 'badge-invoice',
      '03': 'badge-boleta',
      '07': 'badge-credit',
      '08': 'badge-debit',
    };
    return badges[type] || 'badge-secondary';
  };

  const getDocumentTypeLabel = (type) => {
    const labels = {
      '01': 'Factura',
      '03': 'Boleta',
      '07': 'Nota de Crédito',
      '08': 'Nota de Débito',
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
      month: '2-digit',
      day: '2-digit',
    });
  };

  if (loading && invoices.length === 0) {
    return (
      <div className="loading-container">
        <p>Cargando comprobantes...</p>
      </div>
    );
  }

  return (
    <div className="billing-list-page">
      <div className="page-header">
        <h1>Facturación Electrónica</h1>
        <Link to="/dashboard/billing/new" className="btn btn-primary">
          + Nuevo Comprobante
        </Link>
      </div>

      {error && (
        <div className="alert alert-error">
          {error}
        </div>
      )}

      <div className="filters-section">
        <form onSubmit={handleSearch} className="filters-form">
            <input
              type="text"
              placeholder="Buscar por número de comprobante..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="filter-input"
            />

            <select
              value={typeFilter}
              onChange={(e) => setTypeFilter(e.target.value)}
              className="filter-select"
            >
              <option value="">Todos los tipos</option>
              <option value="01">Factura</option>
              <option value="03">Boleta</option>
              <option value="07">Nota de Crédito</option>
              <option value="08">Nota de Débito</option>
            </select>

            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="filter-select"
            >
              <option value="">Todos los estados</option>
              <option value="DRAFT">Borrador</option>
              <option value="PENDING">Pendiente</option>
              <option value="SENT">Enviado</option>
              <option value="ACCEPTED">Aceptado</option>
              <option value="REJECTED">Rechazado</option>
              <option value="VOIDED">Anulado</option>
            </select>

            <input
              type="date"
              value={dateFrom}
              onChange={(e) => setDateFrom(e.target.value)}
              className="filter-input-date"
            />

            <input
              type="date"
              value={dateTo}
              onChange={(e) => setDateTo(e.target.value)}
              className="filter-input-date"
            />

            <button type="submit" className="btn btn-secondary">
              Buscar
            </button>

            {(searchTerm || statusFilter || typeFilter || dateFrom || dateTo) && (
              <button
                type="button"
                onClick={handleClearFilters}
                className="btn btn-outline"
              >
                Limpiar
              </button>
            )}
        </form>
      </div>

      <div className="invoices-stats">
        <p>
          Mostrando <strong>{invoices.length}</strong> de <strong>{pagination.total}</strong> comprobantes
        </p>
      </div>

      <div className="table-container">
        <table className="invoices-table">
          <thead>
            <tr>
              <th>N° Comprobante</th>
              <th>Tipo</th>
              <th>Cliente</th>
              <th>Fecha</th>
              <th>Total</th>
              <th>Estado</th>
              <th>Acciones</th>
            </tr>
          </thead>
          <tbody>
            {invoices.length === 0 ? (
              <tr>
                <td colSpan="7" className="text-center">
                  No se encontraron comprobantes
                </td>
              </tr>
            ) : (
              invoices.map((invoice) => (
                <tr key={invoice.id}>
                  <td>
                    <strong>{invoice.invoice_number}</strong>
                  </td>
                  <td>
                    <span className={`badge ${getDocumentTypeBadge(invoice.invoice_type)}`}>
                      {getDocumentTypeLabel(invoice.invoice_type)}
                    </span>
                  </td>
                  <td>
                    <div className="customer-info">
                      <div>{invoice.customer_name}</div>
                      <small className="text-muted">{invoice.customer_document_type} {invoice.customer_document_number}</small>
                    </div>
                  </td>
                  <td>{formatDate(invoice.issue_date)}</td>
                  <td>
                    <strong className="amount-highlight">
                      {formatCurrency(invoice.total)}
                    </strong>
                  </td>
                  <td>
                    <span className={`badge ${getStatusBadge(invoice.invoice_status)}`}>
                      {getStatusLabel(invoice.invoice_status)}
                    </span>
                  </td>
                  <td>
                    <div className="action-buttons">
                      <button
                        onClick={() => navigate(`/dashboard/billing/${invoice.id}`)}
                        className="btn-icon btn-view"
                        title="Ver detalle"
                      >
                        👁️
                      </button>
                      {invoice.status === 'DRAFT' && (
                        <button
                          onClick={() => navigate(`/dashboard/billing/${invoice.id}/edit`)}
                          className="btn-icon btn-edit"
                          title="Editar"
                        >
                          ✏️
                        </button>
                      )}
                    </div>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {loading && (
        <div className="loading-overlay">
          <p>Cargando...</p>
        </div>
      )}
    </div>
  );
};

export default BillingListPage;
