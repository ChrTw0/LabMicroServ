/**
 * DashboardPage Component
 * Página principal del dashboard que renderiza el dashboard correspondiente al rol del usuario.
 */
import { useAuth } from '../../hooks/useAuth';
import {
  AdministradorGeneralDashboard,
  RecepcionistaDashboard,
  SupervisorSedeDashboard,
  LaboratoristaDashboard,
  ContadorDashboard,
  PacienteDashboard,
} from '.';
import './DashboardPage.css';

const roleDashboards = {
  'Administrador General': <AdministradorGeneralDashboard />,
  'Recepcionista': <RecepcionistaDashboard />,
  'Supervisor de Sede': <SupervisorSedeDashboard />,
  'Laboratorista': <LaboratoristaDashboard />,
  'Contador': <ContadorDashboard />,
  'Paciente': <PacienteDashboard />,
};

const DashboardPage = () => {
  const { user } = useAuth();
  
  // Asumimos que el usuario tiene un solo rol principal
  const userRole = user?.roles?.[0]; 

  const DashboardComponent = userRole ? roleDashboards[userRole] : null;

  return (
    <div className="dashboard-page">
      <h1>Dashboard</h1>
      <p className="welcome-message">
        Bienvenido, <strong>{user?.first_name} {user?.last_name}</strong>
      </p>
      {DashboardComponent ? DashboardComponent : <div>Rol de usuario no definido o dashboard no encontrado.</div>}
    </div>
  );
};

export default DashboardPage;
