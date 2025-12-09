/**
 * ContadorDashboard Component
 * Dashboard para el rol Contador
 * RF-057, RF-058, RF-075, RF-077: Enfocado en facturación, ventas y conciliación financiera
 */
import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { orderService, billingService } from '../../services';
import './Dashboard.css';

const ContadorDashboard = () => {
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState({
    billing: {
      total: 0,
      today: 0,
      accepted: 0,
      pending: 0,
      rejected: 0,
    },
    orders: {
      total: 0,
      today: 0,
    },
  });

  const [recentInvoices, setRecentInvoices] = useState([]);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    setLoading(true);
    try {
      // Cargar estadísticas de facturación - RF-075
      const billingStats = await billingService.getStatistics();

      // Cargar estadísticas de órdenes
      const ordersStats = await orderService.getStatistics();

      setStats({
        billing: billingStats || { total: 0, today: 0, accepted: 0, pending: 0, rejected: 0 },
        orders: ordersStats || { total: 0, today: 0 },
      });

      // Cargar últimos comprobantes
      const invoicesData = await billingService.getAll({ limit: 5 });
      setRecentInvoices(invoicesData.items || []);
    } catch (err) {
      console.error('Error al cargar datos:', err);
    } finally {
      setLoading(false);
    }
  };

  const formatCurrency = (amount) => {
    return `S/ ${parseFloat(amount).toFixed(2)}`;
  };

  const getDocumentTypeName = (type) => {
    const types = {
      '01': 'Factura',
      '03': 'Boleta',
      '07': 'Nota de Crédito',
      '08': 'Nota de Débito',
    };
    return types[type] || type;
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

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('es-PE', { day: '2-digit', month: '2-digit', year: 'numeric' });
  };

  if (loading) {
    return (
      <div className="dashboard-loading">
        <p>Cargando datos financieros...</p>
      </div>
    );
  }

  return (
    <div className="role-dashboard">
      <h2>Panel de Contabilidad</h2>
      <p className="dashboard-subtitle">Facturación, ventas y conciliación financiera</p>

      {/* Resumen financiero - RF-075 */}
      <div className="financial-section">
        <h3>Resumen Financiero</h3>
        <div className="financial-grid">
          <div className="financial-card financial-primary">
            <div className="financial-icon">💰</div>
            <div className="financial-content">
              <h4>Facturación Total</h4>
              <p className="financial-value">{formatCurrency(stats.billing.total || 0)}</p>
              <p className="financial-label">Comprobantes emitidos</p>
            </div>
          </div>

          <div className="financial-card financial-success">
            <div className="financial-icon">📈</div>
            <div className="financial-content">
              <h4>Ventas del Día</h4>
              <p className="financial-value">{formatCurrency(stats.billing.today || 0)}</p>
              <p className="financial-label">Ingresos de hoy</p>
            </div>
          </div>
        </div>
      </div>

      {/* Estado de comprobantes - RF-057, RF-058 */}
      <div className="status-section">
        <h3>Estado de Comprobantes</h3>
        <div className="status-grid">
          <div className="status-card status-success">
            <div className="status-icon">✅</div>
            <div className="status-content">
              <h4>Aceptados</h4>
              <p className="status-value">{stats.billing.accepted || 0}</p>
            </div>
          </div>

          <div className="status-card status-warning">
            <div className="status-icon">⏳</div>
            <div className="status-content">
              <h4>Pendientes</h4>
              <p className="status-value">{stats.billing.pending || 0}</p>
            </div>
          </div>

          <div className="status-card status-danger">
            <div className="status-icon">❌</div>
            <div className="status-content">
              <h4>Rechazados</h4>
              <p className="status-value">{stats.billing.rejected || 0}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Últimos comprobantes - RF-046 */}
      <div className="recent-section">
        <div className="section-header">
          <h3>Últimos Comprobantes Emitidos</h3>
          <Link to="/dashboard/billing" className="btn btn-outline btn-sm">
            Ver todos →
          </Link>
        </div>

        {recentInvoices.length === 0 ? (
          <p className="empty-message">No hay comprobantes registrados</p>
        ) : (
          <div className="table-responsive">
            <table className="dashboard-table">
              <thead>
                <tr>
                  <th>Serie-Número</th>
                  <th>Tipo</th>
                  <th>Cliente</th>
                  <th>Fecha</th>
                  <th>Total</th>
                  <th>Estado</th>
                </tr>
              </thead>
              <tbody>
                {recentInvoices.map((invoice) => (
                  <tr key={invoice.id}>
                    <td>
                      <strong>{invoice.series}-{invoice.number}</strong>
                    </td>
                    <td>{getDocumentTypeName(invoice.document_type)}</td>
                    <td>{invoice.customer_name}</td>
                    <td>{formatDate(invoice.issue_date)}</td>
                    <td>{formatCurrency(invoice.total)}</td>
                    <td>
                      <span className={`badge ${getStatusBadge(invoice.status)}`}>
                        {invoice.status}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Acceso rápido - RF-077 */}
      <div className="quick-access-section">
        <h3>Acceso Rápido</h3>
        <div className="quick-access-grid">
          <Link to="/dashboard/billing" className="quick-access-card">
            <span className="quick-access-icon">💰</span>
            <h4>Facturación</h4>
            <p>Ver comprobantes electrónicos</p>
          </Link>

          <Link to="/dashboard/orders" className="quick-access-card">
            <span className="quick-access-icon">📋</span>
            <h4>Órdenes</h4>
            <p>Ver órdenes y ventas</p>
          </Link>

          <Link to="/dashboard/patients" className="quick-access-card">
            <span className="quick-access-icon">👥</span>
            <h4>Pacientes</h4>
            <p>Consultar clientes</p>
          </Link>
        </div>
      </div>

      {/* Información sobre conciliación - RF-057, RF-058 */}
      <div className="info-section">
        <p className="info-message">
          ℹ️ <strong>Próximamente:</strong> Módulo de conciliación automática diaria para comparar órdenes, comprobantes y pagos.
          Incluirá reportes de cierre de caja y detección de discrepancias.
        </p>
      </div>
    </div>
  );
};

export default ContadorDashboard;
