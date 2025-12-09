/**
 * RecepcionistaDashboard Component
 * Dashboard para el rol Recepcionista
 * RF-023 a RF-035: Enfocado en creación rápida de órdenes y atención de pacientes
 */
import { useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { orderService } from '../../services';
import './Dashboard.css';

const RecepcionistaDashboard = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [recentOrders, setRecentOrders] = useState([]);
  const [stats, setStats] = useState({
    today: 0,
    registrada: 0,
    en_proceso: 0,
  });

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    setLoading(true);
    try {
      // Cargar estadísticas del día
      const statsData = await orderService.getStatistics();
      setStats({
        today: statsData.today || 0,
        registrada: statsData.registrada || 0,
        en_proceso: statsData.en_proceso || 0,
      });

      // Cargar últimas órdenes del día
      const today = new Date().toISOString().split('T')[0];
      const ordersData = await orderService.getAll({
        from_date: today,
        to_date: today,
        limit: 5,
      });
      setRecentOrders(ordersData.items || []);
    } catch (err) {
      console.error('Error al cargar datos:', err);
    } finally {
      setLoading(false);
    }
  };

  const formatCurrency = (amount) => {
    return `S/ ${parseFloat(amount).toFixed(2)}`;
  };

  const getStatusBadge = (status) => {
    const badges = {
      REGISTRADA: 'badge-warning',
      EN_PROCESO: 'badge-info',
      COMPLETADA: 'badge-success',
      ANULADA: 'badge-danger',
    };
    return badges[status] || 'badge-secondary';
  };

  if (loading) {
    return (
      <div className="dashboard-loading">
        <p>Cargando datos...</p>
      </div>
    );
  }

  return (
    <div className="role-dashboard">
      <h2>Panel de Recepción</h2>
      <p className="dashboard-subtitle">Atención de pacientes y gestión de órdenes</p>

      {/* Acción principal - RF-023 */}
      <div className="main-action-section">
        <button
          className="btn btn-primary btn-large"
          onClick={() => navigate('/dashboard/orders/new')}
        >
          ➕ Nueva Orden
        </button>
        <p className="action-hint">Registrar solicitud de análisis de paciente</p>
      </div>

      {/* KPIs del día - RF-072 */}
      <div className="kpi-grid-compact">
        <div className="kpi-card kpi-info">
          <div className="kpi-icon">📋</div>
          <div className="kpi-content">
            <h3>Órdenes Hoy</h3>
            <p className="kpi-value">{stats.today}</p>
          </div>
        </div>

        <div className="kpi-card kpi-warning">
          <div className="kpi-icon">📝</div>
          <div className="kpi-content">
            <h3>Registradas</h3>
            <p className="kpi-value">{stats.registrada}</p>
          </div>
        </div>

        <div className="kpi-card kpi-primary">
          <div className="kpi-icon">⏳</div>
          <div className="kpi-content">
            <h3>En Proceso</h3>
            <p className="kpi-value">{stats.en_proceso}</p>
          </div>
        </div>
      </div>

      {/* Últimas órdenes - RF-034 */}
      <div className="recent-section">
        <div className="section-header">
          <h3>Últimas Órdenes del Día</h3>
          <Link to="/dashboard/orders" className="btn btn-outline btn-sm">
            Ver todas →
          </Link>
        </div>

        {recentOrders.length === 0 ? (
          <p className="empty-message">No hay órdenes registradas hoy</p>
        ) : (
          <div className="table-responsive">
            <table className="dashboard-table">
              <thead>
                <tr>
                  <th>N° Orden</th>
                  <th>Paciente</th>
                  <th>Estado</th>
                  <th>Total</th>
                  <th>Acciones</th>
                </tr>
              </thead>
              <tbody>
                {recentOrders.map((order) => (
                  <tr key={order.id}>
                    <td>
                      <strong>{order.order_number}</strong>
                    </td>
                    <td>{order.patient_name || 'N/A'}</td>
                    <td>
                      <span className={`badge ${getStatusBadge(order.status)}`}>
                        {order.status}
                      </span>
                    </td>
                    <td>{formatCurrency(order.total_amount)}</td>
                    <td>
                      <Link
                        to={`/dashboard/orders/${order.id}`}
                        className="btn btn-sm btn-outline"
                      >
                        Ver
                      </Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Acceso rápido */}
      <div className="quick-access-section">
        <h3>Acceso Rápido</h3>
        <div className="quick-access-grid">
          <Link to="/dashboard/patients" className="quick-access-card">
            <span className="quick-access-icon">👥</span>
            <h4>Pacientes</h4>
            <p>Buscar o registrar pacientes</p>
          </Link>

          <Link to="/dashboard/catalog" className="quick-access-card">
            <span className="quick-access-icon">💉</span>
            <h4>Catálogo</h4>
            <p>Ver servicios disponibles</p>
          </Link>

          <Link to="/dashboard/orders" className="quick-access-card">
            <span className="quick-access-icon">📋</span>
            <h4>Órdenes</h4>
            <p>Ver todas las órdenes</p>
          </Link>
        </div>
      </div>
    </div>
  );
};

export default RecepcionistaDashboard;
