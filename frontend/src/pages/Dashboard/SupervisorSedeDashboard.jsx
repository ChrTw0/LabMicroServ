/**
 * SupervisorSedeDashboard Component
 * Dashboard para el rol Supervisor de Sede
 * RF-059, RF-072: Enfocado en control operativo de la sede, ventas y conciliación
 */
import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { orderService, billingService } from '../../services';
import './Dashboard.css';

const SupervisorSedeDashboard = () => {
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState({
    orders: { total: 0, today: 0, registrada: 0, en_proceso: 0, completada: 0, anulada: 0 },
    billing: { total: 0, today: 0 },
  });

  useEffect(() => {
    loadStatistics();
  }, []);

  const loadStatistics = async () => {
    setLoading(true);
    try {
      // Cargar estadísticas de órdenes
      const ordersStats = await orderService.getStatistics();

      // Cargar estadísticas de facturación
      const billingStats = await billingService.getStatistics();

      setStats({
        orders: ordersStats || { total: 0, today: 0, registrada: 0, en_proceso: 0, completada: 0, anulada: 0 },
        billing: billingStats || { total: 0, today: 0 },
      });
    } catch (err) {
      console.error('Error al cargar estadísticas:', err);
    } finally {
      setLoading(false);
    }
  };

  const formatCurrency = (amount) => {
    return `S/ ${parseFloat(amount).toFixed(2)}`;
  };

  if (loading) {
    return (
      <div className="dashboard-loading">
        <p>Cargando estadísticas...</p>
      </div>
    );
  }

  return (
    <div className="role-dashboard">
      <h2>Panel de Supervisor de Sede</h2>
      <p className="dashboard-subtitle">Control operativo y supervisión de la sede</p>

      {/* Resumen del día - RF-072, RF-073 */}
      <div className="summary-section">
        <h3>Resumen del Día</h3>
        <div className="summary-grid">
          <div className="summary-card summary-primary">
            <h4>Órdenes del Día</h4>
            <p className="summary-value">{stats.orders.today || 0}</p>
            <p className="summary-label">Total registradas hoy</p>
          </div>

          <div className="summary-card summary-success">
            <h4>Ventas del Día</h4>
            <p className="summary-value">{formatCurrency(stats.billing.today || 0)}</p>
            <p className="summary-label">Ingresos generados</p>
          </div>
        </div>
      </div>

      {/* Estados de órdenes - RF-072 */}
      <div className="status-section">
        <h3>Estado de Órdenes</h3>
        <div className="status-grid">
          <div className="status-card status-warning">
            <div className="status-icon">📝</div>
            <div className="status-content">
              <h4>Registradas</h4>
              <p className="status-value">{stats.orders.registrada || 0}</p>
            </div>
          </div>

          <div className="status-card status-info">
            <div className="status-icon">⏳</div>
            <div className="status-content">
              <h4>En Proceso</h4>
              <p className="status-value">{stats.orders.en_proceso || 0}</p>
            </div>
          </div>

          <div className="status-card status-success">
            <div className="status-icon">✅</div>
            <div className="status-content">
              <h4>Completadas</h4>
              <p className="status-value">{stats.orders.completada || 0}</p>
            </div>
          </div>

          <div className="status-card status-danger">
            <div className="status-icon">❌</div>
            <div className="status-content">
              <h4>Anuladas</h4>
              <p className="status-value">{stats.orders.anulada || 0}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Estadísticas generales */}
      <div className="stats-section">
        <h3>Estadísticas Generales</h3>
        <div className="stats-grid">
          <div className="stat-card">
            <h4>Total Órdenes</h4>
            <p className="stat-number">{stats.orders.total || 0}</p>
            <p className="stat-label">Registradas en el sistema</p>
          </div>

          <div className="stat-card">
            <h4>Facturación Total</h4>
            <p className="stat-number">{formatCurrency(stats.billing.total || 0)}</p>
            <p className="stat-label">Comprobantes emitidos</p>
          </div>
        </div>
      </div>

      {/* Acceso rápido - RF-074, RF-075 */}
      <div className="quick-access-section">
        <h3>Gestión de Sede</h3>
        <div className="quick-access-grid">
          <Link to="/dashboard/orders" className="quick-access-card">
            <span className="quick-access-icon">📋</span>
            <h4>Órdenes</h4>
            <p>Ver y filtrar órdenes</p>
          </Link>

          <Link to="/dashboard/billing" className="quick-access-card">
            <span className="quick-access-icon">💰</span>
            <h4>Facturación</h4>
            <p>Comprobantes emitidos</p>
          </Link>

          <Link to="/dashboard/patients" className="quick-access-card">
            <span className="quick-access-icon">👥</span>
            <h4>Pacientes</h4>
            <p>Base de datos de pacientes</p>
          </Link>

          <Link to="/dashboard/catalog" className="quick-access-card">
            <span className="quick-access-icon">💉</span>
            <h4>Catálogo</h4>
            <p>Servicios y precios</p>
          </Link>
        </div>
      </div>

      {/* Nota sobre conciliación - RF-056 a RF-064 */}
      <div className="info-section">
        <p className="info-message">
          ℹ️ <strong>Próximamente:</strong> Reportes de cierre de caja y conciliación automática diaria
        </p>
      </div>
    </div>
  );
};

export default SupervisorSedeDashboard;
