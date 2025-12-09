/**
 * AdministradorGeneralDashboard Component
 * Dashboard principal para el rol Administrador General
 * RF-071 a RF-082: KPIs en tiempo real, ventas, órdenes, reportes
 */
import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { orderService, billingService } from '../../services';
import './Dashboard.css';

const AdministradorGeneralDashboard = () => {
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState({
    orders: { total: 0, today: 0, registrada: 0, en_proceso: 0, completada: 0 },
    billing: { total: 0, today: 0, accepted: 0, pending: 0 },
  });

  useEffect(() => {
    loadStatistics();
  }, []);

  const loadStatistics = async () => {
    setLoading(true);
    try {
      // Obtener fecha de hoy para filtrar "today"
      const today = new Date().toISOString().split('T')[0];

      // Cargar estadísticas de órdenes (todas)
      const ordersStats = await orderService.getStatistics();

      // Cargar estadísticas de órdenes de hoy
      const ordersTodayStats = await orderService.getStatistics({
        date_from: today,
        date_to: today
      });

      // Cargar estadísticas de facturación (todas)
      const billingStats = await billingService.getStatistics();

      // Cargar estadísticas de facturación de hoy
      const billingTodayStats = await billingService.getStatistics({
        date_from: today,
        date_to: today
      });

      // Transformar los datos del backend al formato esperado por el dashboard
      setStats({
        orders: {
          total: ordersStats?.total_orders || 0,
          today: ordersTodayStats?.total_orders || 0,
          registrada: ordersStats?.orders_by_status?.registrada || 0,
          en_proceso: ordersStats?.orders_by_status?.en_proceso || 0,
          completada: ordersStats?.orders_by_status?.completada || 0,
        },
        billing: {
          total: parseFloat(billingStats?.total_billed || 0),
          today: parseFloat(billingTodayStats?.total_billed || 0),
          accepted: billingStats?.invoices_by_status?.ACEPTADO || 0,
          pending: billingStats?.invoices_by_status?.PENDIENTE || 0,
        },
      });
    } catch (err) {
      console.error('Error al cargar estadísticas:', err);
    } finally {
      setLoading(false);
    }
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
      <h2>Panel de Administrador General</h2>
      <p className="dashboard-subtitle">Vista global del sistema - Todos los módulos y estadísticas</p>

      {/* KPIs principales - RF-071 */}
      <div className="kpi-grid">
        <div className="kpi-card kpi-primary">
          <div className="kpi-icon">📋</div>
          <div className="kpi-content">
            <h3>Órdenes Totales</h3>
            <p className="kpi-value">{stats.orders.total || 0}</p>
            <p className="kpi-label">Registradas en el sistema</p>
          </div>
        </div>

        <div className="kpi-card kpi-success">
          <div className="kpi-icon">✅</div>
          <div className="kpi-content">
            <h3>Completadas</h3>
            <p className="kpi-value">{stats.orders.completada || 0}</p>
            <p className="kpi-label">Órdenes finalizadas</p>
          </div>
        </div>

        <div className="kpi-card kpi-warning">
          <div className="kpi-icon">⏳</div>
          <div className="kpi-content">
            <h3>En Proceso</h3>
            <p className="kpi-value">{stats.orders.en_proceso || 0}</p>
            <p className="kpi-label">Órdenes activas</p>
          </div>
        </div>

        <div className="kpi-card kpi-info">
          <div className="kpi-icon">💰</div>
          <div className="kpi-content">
            <h3>Facturación Total</h3>
            <p className="kpi-value">S/ {parseFloat(stats.billing.total || 0).toFixed(2)}</p>
            <p className="kpi-label">Comprobantes emitidos</p>
          </div>
        </div>
      </div>

      {/* Estadísticas del día - RF-072, RF-073 */}
      <div className="stats-section">
        <h3>Actividad del Día</h3>
        <div className="stats-grid">
          <div className="stat-card">
            <h4>Órdenes Hoy</h4>
            <p className="stat-number">{stats.orders.today || 0}</p>
          </div>
          <div className="stat-card">
            <h4>Ventas Hoy</h4>
            <p className="stat-number">S/ {parseFloat(stats.billing.today || 0).toFixed(2)}</p>
          </div>
          <div className="stat-card">
            <h4>Comprobantes Aceptados</h4>
            <p className="stat-number">{stats.billing.accepted || 0}</p>
          </div>
          <div className="stat-card">
            <h4>Comprobantes Pendientes</h4>
            <p className="stat-number">{stats.billing.pending || 0}</p>
          </div>
        </div>
      </div>

      {/* Acceso rápido a módulos */}
      <div className="quick-access-section">
        <h3>Acceso Rápido</h3>
        <div className="quick-access-grid">
          <Link to="/dashboard/usuarios" className="quick-access-card">
            <span className="quick-access-icon">🔑</span>
            <h4>Gestión de Usuarios</h4>
            <p>Administrar usuarios y roles</p>
          </Link>

          <Link to="/dashboard/catalog" className="quick-access-card">
            <span className="quick-access-icon">💉</span>
            <h4>Catálogo de Servicios</h4>
            <p>Gestionar servicios y precios</p>
          </Link>

          <Link to="/dashboard/orders" className="quick-access-card">
            <span className="quick-access-icon">📋</span>
            <h4>Órdenes</h4>
            <p>Ver todas las órdenes</p>
          </Link>

          <Link to="/dashboard/billing" className="quick-access-card">
            <span className="quick-access-icon">💰</span>
            <h4>Facturación</h4>
            <p>Comprobantes electrónicos</p>
          </Link>

          <Link to="/dashboard/patients" className="quick-access-card">
            <span className="quick-access-icon">👥</span>
            <h4>Pacientes</h4>
            <p>Base de datos de pacientes</p>
          </Link>
        </div>
      </div>
    </div>
  );
};

export default AdministradorGeneralDashboard;
