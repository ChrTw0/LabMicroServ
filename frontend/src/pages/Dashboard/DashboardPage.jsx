/**
 * DashboardPage Component
 * Página principal del dashboard
 */
import { useAuth } from '../../hooks/useAuth';
import './DashboardPage.css';

const DashboardPage = () => {
  const { user } = useAuth();

  return (
    <div className="dashboard-page">
      <h1>Dashboard</h1>
      <p className="welcome-message">
        Bienvenido, <strong>{user?.first_name} {user?.last_name}</strong>
      </p>

      <div className="dashboard-grid">
        <div className="dashboard-card">
          <div className="card-icon">👥</div>
          <div className="card-content">
            <h3>Pacientes</h3>
            <p className="card-number">--</p>
            <p className="card-description">Total de pacientes registrados</p>
          </div>
        </div>

        <div className="dashboard-card">
          <div className="card-icon">📋</div>
          <div className="card-content">
            <h3>Órdenes</h3>
            <p className="card-number">--</p>
            <p className="card-description">Órdenes pendientes</p>
          </div>
        </div>

        <div className="dashboard-card">
          <div className="card-icon">💰</div>
          <div className="card-content">
            <h3>Facturas</h3>
            <p className="card-number">--</p>
            <p className="card-description">Facturas del día</p>
          </div>
        </div>

        <div className="dashboard-card">
          <div className="card-icon">🧪</div>
          <div className="card-content">
            <h3>Servicios</h3>
            <p className="card-number">--</p>
            <p className="card-description">Servicios disponibles</p>
          </div>
        </div>
      </div>

      <div className="dashboard-info">
        <p>📌 Las estadísticas se implementarán en la siguiente fase.</p>
      </div>
    </div>
  );
};

export default DashboardPage;
