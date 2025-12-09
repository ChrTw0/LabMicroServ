/**
 * PacienteDashboard Component
 * Dashboard para el rol Paciente
 * RF-012: Enfocado en ver sus propias órdenes y resultados
 */
import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../../hooks/useAuth';
import { orderService } from '../../services';
import './Dashboard.css';

const PacienteDashboard = () => {
  const { user } = useAuth();
  const [loading, setLoading] = useState(true);
  const [myOrders, setMyOrders] = useState([]);
  const [stats, setStats] = useState({
    total: 0,
    completadas: 0,
    en_proceso: 0,
  });

  useEffect(() => {
    loadMyOrders();
  }, []);

  const loadMyOrders = async () => {
    setLoading(true);
    try {
      // Cargar órdenes del paciente
      // Nota: Esto requeriría filtrar por patient_id del usuario actual
      // Por ahora cargamos todas las órdenes (el backend debería filtrar por paciente)
      const ordersData = await orderService.getAll({ limit: 10 });
      const orders = ordersData.items || [];

      setMyOrders(orders);

      // Calcular estadísticas
      const completadas = orders.filter((o) => o.status === 'COMPLETADA').length;
      const en_proceso = orders.filter((o) => o.status === 'EN_PROCESO').length;

      setStats({
        total: orders.length,
        completadas,
        en_proceso,
      });
    } catch (err) {
      console.error('Error al cargar órdenes:', err);
    } finally {
      setLoading(false);
    }
  };

  const formatCurrency = (amount) => {
    return `S/ ${parseFloat(amount).toFixed(2)}`;
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('es-PE', {
      day: '2-digit',
      month: 'long',
      year: 'numeric',
    });
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

  const getStatusText = (status) => {
    const texts = {
      REGISTRADA: 'Registrada',
      EN_PROCESO: 'En Proceso',
      COMPLETADA: 'Completada',
      ANULADA: 'Anulada',
    };
    return texts[status] || status;
  };

  if (loading) {
    return (
      <div className="dashboard-loading">
        <p>Cargando tus órdenes...</p>
      </div>
    );
  }

  return (
    <div className="role-dashboard patient-dashboard">
      <h2>Mi Panel</h2>
      <p className="dashboard-subtitle">Bienvenido, {user?.first_name} {user?.last_name}</p>

      {/* Resumen de órdenes - RF-012 */}
      <div className="patient-summary">
        <div className="summary-card summary-primary">
          <div className="summary-icon">📋</div>
          <div className="summary-content">
            <h3>Mis Órdenes</h3>
            <p className="summary-value">{stats.total}</p>
            <p className="summary-label">Total registradas</p>
          </div>
        </div>

        <div className="summary-card summary-info">
          <div className="summary-icon">⏳</div>
          <div className="summary-content">
            <h3>En Proceso</h3>
            <p className="summary-value">{stats.en_proceso}</p>
            <p className="summary-label">Pendientes</p>
          </div>
        </div>

        <div className="summary-card summary-success">
          <div className="summary-icon">✅</div>
          <div className="summary-content">
            <h3>Completadas</h3>
            <p className="summary-value">{stats.completadas}</p>
            <p className="summary-label">Finalizadas</p>
          </div>
        </div>
      </div>

      {/* Historial de órdenes - RF-012 */}
      <div className="orders-section">
        <div className="section-header">
          <h3>Mis Órdenes</h3>
          <Link to="/dashboard/orders" className="btn btn-outline btn-sm">
            Ver todas →
          </Link>
        </div>

        {myOrders.length === 0 ? (
          <div className="empty-state">
            <p className="empty-icon">📋</p>
            <p className="empty-message">No tienes órdenes registradas</p>
          </div>
        ) : (
          <div className="orders-list">
            {myOrders.map((order) => (
              <div key={order.id} className="order-card">
                <div className="order-header">
                  <div>
                    <h4>{order.order_number}</h4>
                    <p className="order-date">{formatDate(order.created_at)}</p>
                  </div>
                  <span className={`badge ${getStatusBadge(order.status)}`}>
                    {getStatusText(order.status)}
                  </span>
                </div>

                <div className="order-body">
                  <div className="order-info">
                    <p>
                      <strong>Servicios:</strong> {order.items?.length || 0} análisis
                    </p>
                    <p>
                      <strong>Total:</strong> {formatCurrency(order.total_amount)}
                    </p>
                    <p>
                      <strong>Saldo:</strong> {formatCurrency(order.balance || 0)}
                    </p>
                  </div>

                  {order.status === 'COMPLETADA' && (
                    <div className="order-status-message success-message">
                      ✅ Tus resultados están listos
                    </div>
                  )}

                  {order.status === 'EN_PROCESO' && (
                    <div className="order-status-message info-message">
                      ⏳ Tu orden está siendo procesada
                    </div>
                  )}

                  {order.status === 'REGISTRADA' && (
                    <div className="order-status-message warning-message">
                      📝 Orden registrada, esperando proceso
                    </div>
                  )}
                </div>

                <div className="order-footer">
                  <Link
                    to={`/dashboard/orders/${order.id}`}
                    className="btn btn-sm btn-primary"
                  >
                    Ver Detalle
                  </Link>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Acceso rápido */}
      <div className="quick-access-section">
        <h3>Acceso Rápido</h3>
        <div className="quick-access-grid">
          <Link to="/dashboard/orders" className="quick-access-card">
            <span className="quick-access-icon">📋</span>
            <h4>Mis Órdenes</h4>
            <p>Ver todas mis órdenes</p>
          </Link>

          <Link to="/dashboard/catalog" className="quick-access-card">
            <span className="quick-access-icon">💉</span>
            <h4>Catálogo</h4>
            <p>Servicios disponibles</p>
          </Link>

          <Link to="/dashboard/profile" className="quick-access-card">
            <span className="quick-access-icon">👤</span>
            <h4>Mi Perfil</h4>
            <p>Ver y editar mi información</p>
          </Link>
        </div>
      </div>
    </div>
  );
};

export default PacienteDashboard;
