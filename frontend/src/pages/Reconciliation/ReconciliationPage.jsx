/**
 * ReconciliationPage Component
 * Página de conciliación y cierre de caja - RF-056 a RF-064
 */
import { useEffect, useState } from 'react';
import { useReconciliation } from '../../hooks';
import { useAuth } from '../../hooks';
import jsPDF from 'jspdf';
import 'jspdf-autotable';
import './ReconciliationPage.css';

const ReconciliationPage = () => {
  const { hasRole } = useAuth();
  const {
    loading,
    error,
    closures,
    currentClosure,
    reconciliationReport,
    pagination,
    fetchClosures,
    fetchClosureById,
    createDailyClosure,
    closeDailyClosure,
    reopenClosure,
    fetchReconciliationReport,
    addDiscrepancy,
    resolveDiscrepancy,
  } = useReconciliation();

  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showDetailModal, setShowDetailModal] = useState(false);
  const [showReopenModal, setShowReopenModal] = useState(false);
  const [showReportModal, setShowReportModal] = useState(false);

  const [newClosure, setNewClosure] = useState({
    location_id: '',
    closure_date: new Date().toISOString().split('T')[0],
    registered_total: '',
  });

  const [reopenData, setReopenData] = useState({
    closureId: null,
    reason: '',
  });

  const [reportFilters, setReportFilters] = useState({
    location_id: '',
    closure_date: new Date().toISOString().split('T')[0],
  });

  const [filters, setFilters] = useState({
    page: 1,
    page_size: 10,
    location_id: '',
    status: '',
    date_from: '',
    date_to: '',
  });

  useEffect(() => {
    loadClosures();
  }, [filters.page]);

  const loadClosures = () => {
    // Filtrar parámetros vacíos para evitar errores de validación
    const cleanFilters = Object.fromEntries(
      Object.entries(filters).filter(([_, value]) => value !== '' && value !== null)
    );
    fetchClosures(cleanFilters);
  };

  const handleFilterChange = (e) => {
    const { name, value } = e.target;
    setFilters((prev) => ({ ...prev, [name]: value, page: 1 }));
  };

  const handleApplyFilters = (e) => {
    e.preventDefault();
    loadClosures();
  };

  const handleClearFilters = () => {
    setFilters({
      page: 1,
      page_size: 10,
      location_id: '',
      status: '',
      date_from: '',
      date_to: '',
    });
  };

  // Crear cierre - RF-056, RF-057, RF-058
  const handleCreateClosure = async (e) => {
    e.preventDefault();
    const result = await createDailyClosure({
      ...newClosure,
      location_id: parseInt(newClosure.location_id),
      registered_total: parseFloat(newClosure.registered_total),
    });

    if (result.success) {
      alert('Cierre creado correctamente. Revisa las discrepancias detectadas.');
      setShowCreateModal(false);
      setNewClosure({
        location_id: '',
        closure_date: new Date().toISOString().split('T')[0],
        registered_total: '',
      });
      loadClosures();
      // Mostrar detalle del cierre creado
      if (result.data.id) {
        handleViewDetail(result.data.id);
      }
    } else {
      alert(`Error: ${result.error}`);
    }
  };

  // Ver detalle de cierre
  const handleViewDetail = async (id) => {
    const result = await fetchClosureById(id);
    if (result.success) {
      setShowDetailModal(true);
    }
  };

  // Cerrar cierre
  const handleCloseClosure = async (id) => {
    if (window.confirm('¿Estás seguro de cerrar este cierre? No podrás modificarlo después.')) {
      const result = await closeDailyClosure(id);
      if (result.success) {
        alert('Cierre cerrado correctamente');
        loadClosures();
        setShowDetailModal(false);
      } else {
        alert(`Error: ${result.error}`);
      }
    }
  };

  // Reabrir cierre - RF-063
  const handleReopenClosure = async (e) => {
    e.preventDefault();
    if (reopenData.reason.length < 10) {
      alert('La justificación debe tener al menos 10 caracteres');
      return;
    }

    const result = await reopenClosure(reopenData.closureId, reopenData.reason);
    if (result.success) {
      alert('Cierre reabierto correctamente');
      setShowReopenModal(false);
      setReopenData({ closureId: null, reason: '' });
      loadClosures();
      setShowDetailModal(false);
    } else {
      alert(`Error: ${result.error}`);
    }
  };

  // Resolver discrepancia
  const handleResolveDiscrepancy = async (discrepancyId) => {
    if (window.confirm('¿Marcar esta discrepancia como resuelta?')) {
      const result = await resolveDiscrepancy(discrepancyId);
      if (result.success) {
        alert('Discrepancia resuelta');
        // Recargar detalle del cierre
        if (currentClosure) {
          fetchClosureById(currentClosure.id);
        }
      } else {
        alert(`Error: ${result.error}`);
      }
    }
  };

  // Generar reporte de conciliación - RF-057, RF-059
  const handleGenerateReport = async (e) => {
    e.preventDefault();
    const result = await fetchReconciliationReport({
      ...reportFilters,
      location_id: parseInt(reportFilters.location_id),
    });

    if (result.success) {
      setShowReportModal(true);
    } else {
      alert(`Error: ${result.error}`);
    }
  };

  // Exportar reporte a PDF - RF-064
  const exportReportToPDF = () => {
    if (!reconciliationReport) return;

    const doc = new jsPDF();
    const currentDate = new Date().toLocaleDateString('es-PE');

    // Header
    doc.setFontSize(18);
    doc.text('Reporte de Conciliación de Caja', 14, 20);
    doc.setFontSize(10);
    doc.text(`Fecha: ${reconciliationReport.closure_date}`, 14, 28);
    doc.text(`Sede: ${reconciliationReport.location_id}`, 14, 34);
    doc.text(`Generado: ${currentDate}`, 14, 40);

    let yPosition = 50;

    // Resumen general
    doc.setFontSize(14);
    doc.text('Resumen General', 14, yPosition);
    yPosition += 8;

    const summaryData = [
      ['Total Órdenes', reconciliationReport.total_orders.toString()],
      ['Total Facturas', reconciliationReport.total_invoices.toString()],
      ['Total Pagos', `S/ ${parseFloat(reconciliationReport.total_payments).toFixed(2)}`],
      ['Total Facturado', `S/ ${parseFloat(reconciliationReport.total_billed).toFixed(2)}`],
    ];

    doc.autoTable({
      startY: yPosition,
      head: [['Concepto', 'Valor']],
      body: summaryData,
      theme: 'grid',
    });

    yPosition = doc.lastAutoTable.finalY + 10;

    // Métodos de pago
    if (reconciliationReport.payment_methods && reconciliationReport.payment_methods.length > 0) {
      doc.setFontSize(14);
      doc.text('Detalle por Método de Pago', 14, yPosition);
      yPosition += 8;

      const paymentData = reconciliationReport.payment_methods.map((pm) => [
        pm.payment_method,
        `S/ ${parseFloat(pm.expected_total).toFixed(2)}`,
        `S/ ${parseFloat(pm.registered_total).toFixed(2)}`,
        `S/ ${parseFloat(pm.difference).toFixed(2)}`,
      ]);

      doc.autoTable({
        startY: yPosition,
        head: [['Método', 'Esperado', 'Registrado', 'Diferencia']],
        body: paymentData,
        theme: 'grid',
      });

      yPosition = doc.lastAutoTable.finalY + 10;
    }

    // Discrepancias
    if (reconciliationReport.discrepancies && reconciliationReport.discrepancies.length > 0) {
      doc.setFontSize(14);
      doc.text('Discrepancias Detectadas', 14, yPosition);
      yPosition += 8;

      const discrepancyData = reconciliationReport.discrepancies.map((disc) => [
        disc.description,
        disc.is_resolved ? 'Resuelta' : 'Pendiente',
      ]);

      doc.autoTable({
        startY: yPosition,
        head: [['Descripción', 'Estado']],
        body: discrepancyData,
        theme: 'grid',
      });
    }

    doc.save(`conciliacion_${reconciliationReport.closure_date}_${currentDate}.pdf`);
  };

  const formatCurrency = (value) => {
    return `S/ ${parseFloat(value).toLocaleString('es-PE', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('es-PE');
  };

  const getStatusBadge = (status) => {
    return status === 'OPEN' ? 'badge-warning' : 'badge-success';
  };

  return (
    <div className="reconciliation-page">
      <div className="page-header">
        <h1>Conciliación y Cierre de Caja</h1>
        <div className="header-buttons">
          <button onClick={() => setShowCreateModal(true)} className="btn btn-primary">
            + Nuevo Cierre
          </button>
          <button onClick={() => setShowReportModal(true)} className="btn btn-secondary">
            📊 Generar Reporte
          </button>
        </div>
      </div>

      {error && (
        <div className="alert alert-error">
          {typeof error === 'string' ? error : 'Ha ocurrido un error. Por favor, intenta nuevamente.'}
        </div>
      )}

      {/* Filtros - RF-062 */}
      <div className="filters-section">
        <form className="filters-form" onSubmit={handleApplyFilters}>
          <div className="filter-row">
            <input
              type="number"
              name="location_id"
              value={filters.location_id}
              onChange={handleFilterChange}
              className="filter-input"
              placeholder="ID de Sede"
            />
            <select
              name="status"
              value={filters.status}
              onChange={handleFilterChange}
              className="filter-select"
            >
              <option value="">Todos los estados</option>
              <option value="OPEN">Abierto</option>
              <option value="CLOSED">Cerrado</option>
            </select>
            <input
              type="date"
              name="date_from"
              value={filters.date_from}
              onChange={handleFilterChange}
              className="filter-input-date"
            />
            <input
              type="date"
              name="date_to"
              value={filters.date_to}
              onChange={handleFilterChange}
              className="filter-input-date"
            />
            <button type="submit" className="btn btn-primary">
              Buscar
            </button>
            <button type="button" onClick={handleClearFilters} className="btn btn-secondary">
              Limpiar
            </button>
          </div>
        </form>
      </div>

      {/* Tabla de cierres */}
      <div className="table-container">
        {loading && closures.length === 0 ? (
          <div className="loading-container">
            <p>Cargando cierres...</p>
          </div>
        ) : (
          <table className="closures-table">
            <thead>
              <tr>
                <th>ID</th>
                <th>Fecha</th>
                <th>Sede</th>
                <th>Estado</th>
                <th>Total Esperado</th>
                <th>Total Registrado</th>
                <th>Diferencia</th>
                <th>Discrepancias</th>
                <th>Acciones</th>
              </tr>
            </thead>
            <tbody>
              {!Array.isArray(closures) || closures.length === 0 ? (
                <tr>
                  <td colSpan="9" className="no-data">
                    No hay cierres registrados
                  </td>
                </tr>
              ) : (
                closures.map((closure) => (
                  <tr key={closure.id}>
                    <td>{closure.id}</td>
                    <td>{formatDate(closure.closure_date)}</td>
                    <td>{closure.location_id}</td>
                    <td>
                      <span className={`badge ${getStatusBadge(closure.status)}`}>
                        {closure.status}
                      </span>
                    </td>
                    <td>{formatCurrency(closure.expected_total)}</td>
                    <td>{formatCurrency(closure.registered_total)}</td>
                    <td className={parseFloat(closure.difference) !== 0 ? 'difference-highlight' : ''}>
                      {formatCurrency(closure.difference)}
                    </td>
                    <td>{closure.discrepancy_count || 0}</td>
                    <td>
                      <button
                        onClick={() => handleViewDetail(closure.id)}
                        className="btn-action btn-view"
                        title="Ver detalle"
                      >
                        👁️
                      </button>
                      {closure.status === 'CLOSED' && hasRole('Administrador General') && (
                        <button
                          onClick={() => {
                            setReopenData({ closureId: closure.id, reason: '' });
                            setShowReopenModal(true);
                          }}
                          className="btn-action btn-reopen"
                          title="Reabrir cierre"
                        >
                          🔓
                        </button>
                      )}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        )}

        {/* Paginación */}
        {pagination.pages > 1 && (
          <div className="pagination">
            <button
              onClick={() => setFilters((prev) => ({ ...prev, page: prev.page - 1 }))}
              disabled={filters.page === 1}
              className="btn btn-secondary"
            >
              Anterior
            </button>
            <span className="page-info">
              Página {pagination.page} de {pagination.pages}
            </span>
            <button
              onClick={() => setFilters((prev) => ({ ...prev, page: prev.page + 1 }))}
              disabled={filters.page >= pagination.pages}
              className="btn btn-secondary"
            >
              Siguiente
            </button>
          </div>
        )}
      </div>

      {/* Modal: Crear Cierre */}
      {showCreateModal && (
        <div className="modal-overlay" onClick={() => setShowCreateModal(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>Crear Cierre Diario</h2>
              <button onClick={() => setShowCreateModal(false)} className="modal-close">
                ×
              </button>
            </div>
            <form onSubmit={handleCreateClosure} className="modal-form">
              <div className="form-group">
                <label>Sede ID*</label>
                <input
                  type="number"
                  value={newClosure.location_id}
                  onChange={(e) => setNewClosure({ ...newClosure, location_id: e.target.value })}
                  required
                  min="1"
                  className="form-input"
                />
              </div>
              <div className="form-group">
                <label>Fecha de Cierre*</label>
                <input
                  type="date"
                  value={newClosure.closure_date}
                  onChange={(e) => setNewClosure({ ...newClosure, closure_date: e.target.value })}
                  required
                  className="form-input"
                />
              </div>
              <div className="form-group">
                <label>Total Registrado (S/)*</label>
                <input
                  type="number"
                  step="0.01"
                  value={newClosure.registered_total}
                  onChange={(e) => setNewClosure({ ...newClosure, registered_total: e.target.value })}
                  required
                  min="0"
                  className="form-input"
                />
              </div>
              <div className="modal-actions">
                <button type="button" onClick={() => setShowCreateModal(false)} className="btn btn-secondary">
                  Cancelar
                </button>
                <button type="submit" className="btn btn-primary" disabled={loading}>
                  {loading ? 'Creando...' : 'Crear Cierre'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Modal: Detalle de Cierre */}
      {showDetailModal && currentClosure && (
        <div className="modal-overlay" onClick={() => setShowDetailModal(false)}>
          <div className="modal-content modal-large" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>Detalle de Cierre #{currentClosure.id}</h2>
              <button onClick={() => setShowDetailModal(false)} className="modal-close">
                ×
              </button>
            </div>
            <div className="modal-body">
              <div className="closure-info">
                <div className="info-row">
                  <span className="info-label">Fecha:</span>
                  <span className="info-value">{formatDate(currentClosure.closure_date)}</span>
                </div>
                <div className="info-row">
                  <span className="info-label">Sede:</span>
                  <span className="info-value">{currentClosure.location_id}</span>
                </div>
                <div className="info-row">
                  <span className="info-label">Estado:</span>
                  <span className={`badge ${getStatusBadge(currentClosure.status)}`}>
                    {currentClosure.status}
                  </span>
                </div>
                <div className="info-row">
                  <span className="info-label">Total Esperado:</span>
                  <span className="info-value">{formatCurrency(currentClosure.expected_total)}</span>
                </div>
                <div className="info-row">
                  <span className="info-label">Total Registrado:</span>
                  <span className="info-value">{formatCurrency(currentClosure.registered_total)}</span>
                </div>
                <div className="info-row">
                  <span className="info-label">Diferencia:</span>
                  <span className={`info-value ${parseFloat(currentClosure.difference) !== 0 ? 'difference-highlight' : ''}`}>
                    {formatCurrency(currentClosure.difference)}
                  </span>
                </div>
              </div>

              {/* Discrepancias */}
              {currentClosure.discrepancies && currentClosure.discrepancies.length > 0 && (
                <div className="discrepancies-section">
                  <h3>Discrepancias</h3>
                  <div className="discrepancies-list">
                    {currentClosure.discrepancies.map((disc) => (
                      <div key={disc.id} className={`discrepancy-item ${disc.is_resolved ? 'resolved' : 'pending'}`}>
                        <div className="discrepancy-header">
                          <span className={`badge ${disc.is_resolved ? 'badge-success' : 'badge-danger'}`}>
                            {disc.is_resolved ? 'Resuelta' : 'Pendiente'}
                          </span>
                          {!disc.is_resolved && (
                            <button
                              onClick={() => handleResolveDiscrepancy(disc.id)}
                              className="btn btn-sm btn-success"
                            >
                              Marcar Resuelta
                            </button>
                          )}
                        </div>
                        <p className="discrepancy-description">{disc.description}</p>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
            <div className="modal-actions">
              <button onClick={() => setShowDetailModal(false)} className="btn btn-secondary">
                Cerrar
              </button>
              {currentClosure.status === 'OPEN' && (
                <button onClick={() => handleCloseClosure(currentClosure.id)} className="btn btn-primary">
                  Cerrar Cierre
                </button>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Modal: Reabrir Cierre - RF-063 */}
      {showReopenModal && (
        <div className="modal-overlay" onClick={() => setShowReopenModal(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>Reabrir Cierre</h2>
              <button onClick={() => setShowReopenModal(false)} className="modal-close">
                ×
              </button>
            </div>
            <form onSubmit={handleReopenClosure} className="modal-form">
              <div className="form-group">
                <label>Justificación* (mínimo 10 caracteres)</label>
                <textarea
                  value={reopenData.reason}
                  onChange={(e) => setReopenData({ ...reopenData, reason: e.target.value })}
                  required
                  minLength="10"
                  rows="4"
                  className="form-textarea"
                  placeholder="Explica por qué necesitas reabrir este cierre..."
                />
              </div>
              <div className="modal-actions">
                <button type="button" onClick={() => setShowReopenModal(false)} className="btn btn-secondary">
                  Cancelar
                </button>
                <button type="submit" className="btn btn-primary" disabled={loading}>
                  {loading ? 'Reabriendo...' : 'Reabrir Cierre'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Modal: Reporte de Conciliación - RF-057, RF-059 */}
      {showReportModal && (
        <div className="modal-overlay" onClick={() => setShowReportModal(false)}>
          <div className="modal-content modal-large" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>Reporte de Conciliación</h2>
              <button onClick={() => setShowReportModal(false)} className="modal-close">
                ×
              </button>
            </div>
            <div className="modal-body">
              {!reconciliationReport ? (
                <form onSubmit={handleGenerateReport} className="modal-form">
                  <div className="form-group">
                    <label>Sede ID*</label>
                    <input
                      type="number"
                      value={reportFilters.location_id}
                      onChange={(e) => setReportFilters({ ...reportFilters, location_id: e.target.value })}
                      required
                      min="1"
                      className="form-input"
                    />
                  </div>
                  <div className="form-group">
                    <label>Fecha*</label>
                    <input
                      type="date"
                      value={reportFilters.closure_date}
                      onChange={(e) => setReportFilters({ ...reportFilters, closure_date: e.target.value })}
                      required
                      className="form-input"
                    />
                  </div>
                  <div className="modal-actions">
                    <button type="button" onClick={() => setShowReportModal(false)} className="btn btn-secondary">
                      Cancelar
                    </button>
                    <button type="submit" className="btn btn-primary" disabled={loading}>
                      {loading ? 'Generando...' : 'Generar Reporte'}
                    </button>
                  </div>
                </form>
              ) : (
                <div className="report-content">
                  <div className="report-summary">
                    <h3>Resumen General</h3>
                    <div className="summary-grid">
                      <div className="summary-item">
                        <span className="summary-label">Total Órdenes</span>
                        <span className="summary-value">{reconciliationReport.total_orders}</span>
                      </div>
                      <div className="summary-item">
                        <span className="summary-label">Total Facturas</span>
                        <span className="summary-value">{reconciliationReport.total_invoices}</span>
                      </div>
                      <div className="summary-item">
                        <span className="summary-label">Total Pagos</span>
                        <span className="summary-value">{formatCurrency(reconciliationReport.total_payments)}</span>
                      </div>
                      <div className="summary-item">
                        <span className="summary-label">Total Facturado</span>
                        <span className="summary-value">{formatCurrency(reconciliationReport.total_billed)}</span>
                      </div>
                    </div>
                  </div>

                  {reconciliationReport.payment_methods && reconciliationReport.payment_methods.length > 0 && (
                    <div className="payment-methods-section">
                      <h3>Detalle por Método de Pago</h3>
                      <table className="report-table">
                        <thead>
                          <tr>
                            <th>Método de Pago</th>
                            <th>Esperado</th>
                            <th>Registrado</th>
                            <th>Diferencia</th>
                          </tr>
                        </thead>
                        <tbody>
                          {reconciliationReport.payment_methods.map((pm, index) => (
                            <tr key={index}>
                              <td>{pm.payment_method}</td>
                              <td>{formatCurrency(pm.expected_total)}</td>
                              <td>{formatCurrency(pm.registered_total)}</td>
                              <td className={parseFloat(pm.difference) !== 0 ? 'difference-highlight' : ''}>
                                {formatCurrency(pm.difference)}
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  )}

                  {reconciliationReport.has_discrepancies && (
                    <div className="alert alert-warning">
                      ⚠️ Se detectaron discrepancias en este cierre
                    </div>
                  )}

                  <div className="modal-actions">
                    <button onClick={() => {
                      setShowReportModal(false);
                      setReportFilters({ location_id: '', closure_date: new Date().toISOString().split('T')[0] });
                    }} className="btn btn-secondary">
                      Cerrar
                    </button>
                    <button onClick={exportReportToPDF} className="btn btn-primary">
                      📄 Exportar PDF
                    </button>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ReconciliationPage;
