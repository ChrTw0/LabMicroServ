/**
 * Sidebar Component
 * Menú lateral de navegación
 */
import { NavLink } from 'react-router-dom';
import { useAuth } from '../../../hooks/useAuth';
import './Sidebar.css';

const Sidebar = () => {
  const { hasAnyRole } = useAuth();

  const menuItems = [
    {
      path: '/dashboard',
      icon: '📊',
      label: 'Dashboard',
      roles: null, // Todos los usuarios
    },
    {
      path: '/patients',
      icon: '👥',
      label: 'Pacientes',
      roles: ['Administrador General', 'Recepcionista'],
    },
    {
      path: '/orders',
      icon: '📋',
      label: 'Órdenes',
      roles: ['Administrador General', 'Recepcionista', 'Laboratorista'],
    },
    {
      path: '/billing',
      icon: '💰',
      label: 'Facturación',
      roles: ['Administrador General', 'Recepcionista', 'Supervisor de Sede'],
    },
  ];

  return (
    <aside className="sidebar">
      <nav className="sidebar-nav">
        {menuItems.map((item) => {
          // Si el item requiere roles específicos, verificar
          if (item.roles && !hasAnyRole(item.roles)) {
            return null;
          }

          return (
            <NavLink
              key={item.path}
              to={item.path}
              className={({ isActive }) => (isActive ? 'nav-item active' : 'nav-item')}
            >
              <span className="nav-icon">{item.icon}</span>
              <span className="nav-label">{item.label}</span>
            </NavLink>
          );
        })}
      </nav>
    </aside>
  );
};

export default Sidebar;
