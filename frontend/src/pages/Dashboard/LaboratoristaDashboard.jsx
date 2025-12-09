/**
 * LaboratoristaDashboard Component
 * Dashboard para el rol Laboratorista
 * RF-065 a RF-070: Enfocado en órdenes pendientes de procesamiento y sincronización con laboratorio
 */
import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { orderService } from '../../services';
import api from '../../services/api';
import './Dashboard.css';

const LaboratoristaDashboard = () => {
  const [loading, setLoading] = useState(true);
  const [pendingOrders, setPendingOrders] = useState([]);
  const [labSyncStats, setLabSyncStats] = useState({
    successful: 0,
    failed: 0,
    pending: 0,
  });

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    setLoading(true);
    try {
      // Cargar órdenes pendientes de procesar (EN_PROCESO)
      const ordersData = await orderService.getAll({
        status: 'EN_PROCESO',
        limit: 10,
      });
      setPendingOrders(ordersData.items || []);

      // Cargar estadísticas de sincronización de laboratorio - RF-069
      try {
        const response = await api.get('/api/v1/lab-sync/statistics');
        setLabSyncStats(response.data || { successful: 0, failed: 0, pending: 0 });
      } catch (err) {
        console.warn('Estadísticas de lab-sync no disponibles:', err);
      }
    } catch (err) {
      console.error('Error al cargar datos:', err);
    } finally {
      setLoading(false);
    }
  };

  const formatCurrency = (amount) => {
    return `S/ ${parseFloat(amount).toFixed(2)}`;
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('es-PE', { day: '2-digit', month: '2-digit', year: 'numeric' });
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
      <h2>Panel de Laboratorio</h2>
      <p className="dashboard-subtitle">Gestión de órdenes y sincronización con laboratorio</p>

      {/* Estadísticas de sincronización - RF-069 */}
      <div className="kpi-grid-compact">
        <div className="kpi-card kpi-success">
          <div className="kpi-icon">✅</div>
          <div className="kpi-content">
            <h3>Sincronizadas</h3>
            <p className="kpi-value">{labSyncStats.successful || 0}</p>
            <p className="kpi-label">Exitosas</p>
          </div>
        </div>

        <div className="kpi-card kpi-danger">
          <div className="kpi-icon">❌</div>
          <div className="kpi-content">
            <h3>Fallidas</h3>
            <p className="kpi-value">{labSyncStats.failed || 0}</p>
            <p className="kpi-label">Requieren atención</p>
          </div>
        </div>

        <div className="kpi-card kpi-warning">
          <div className="kpi-icon">⏳</div>
          <div className="kpi-content">
            <h3>Pendientes</h3>
            <p className="kpi-value">{labSyncStats.pending || 0}</p>
            <p className="kpi-label">Por sincronizar</p>
          </div>
        </div>
      </div>

      {/* Órdenes pendientes de procesar - RF-065, RF-066 */}
      <div className="pending-section">
        <div className="section-header">
          <h3>Órdenes en Proceso</h3>
          <Link to="/dashboard/orders?status=EN_PROCESO" className="btn btn-outline btn-sm">
            Ver todas →
          </Link>
        </div>

        {pendingOrders.length === 0 ? (
          <div className="empty-state">
            <p className="empty-icon">✅</p>
            <p className="empty-message">No hay órdenes pendientes de procesar</p>
          </div>
        ) : (
          <div className="table-responsive">
            <table className="dashboard-table">
              <thead>
                <tr>
                  <th>N° Orden</th>
                  <th>Paciente</th>
                  <th>Fecha</th>
                  <th>Servicios</th>
                  <th>Total</th>
                  <th>Acciones</th>
                </tr>
              </thead>
              <tbody>
                {pendingOrders.map((order) => (
                  <tr key={order.id}>
                    <td>
                      <strong>{order.order_number}</strong>
                    </td>
                    <td>{order.patient_name || 'N/A'}</td>
                    <td>{formatDate(order.created_at)}</td>
                    <td>
                      {order.items?.length || 0} servicio(s)
                    </td>
                    <td>{formatCurrency(order.total_amount)}</td>
                    <td>
                      <Link
                        to={`/dashboard/orders/${order.id}`}
                        className="btn btn-sm btn-primary"
                      >
                        Ver Detalle
                      </Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Acceso rápido - RF-070 */}
      <div className="quick-access-section">
        <h3>Acceso Rápido</h3>
        <div className="quick-access-grid">
          <Link to="/dashboard/orders" className="quick-access-card">
            <span className="quick-access-icon">📋</span>
            <h4>Todas las Órdenes</h4>
            <p>Ver listado completo</p>
          </Link>

          <Link to="/dashboard/catalog" className="quick-access-card">
            <span className="quick-access-icon">💉</span>
            <h4>Catálogo</h4>
            <p>Consultar servicios</p>
          </Link>

          <Link to="/dashboard/patients" className="quick-access-card">
            <span className="quick-access-icon">👥</span>
            <h4>Pacientes</h4>
            <p>Información de pacientes</p>
          </Link>
        </div>
      </div>

      {/* Información sobre integración - RF-067, RF-068 */}
      <div className="info-section">
        <p className="info-message">
          ℹ️ <strong>Sincronización:</strong> Las órdenes se sincronizan automáticamente con el sistema de laboratorio.
          Puedes consultar el log de sincronizaciones y forzar reintentos manuales desde el detalle de cada orden.
        </p>
      </div>
    </div>
  );
};

export default LaboratoristaDashboard;
