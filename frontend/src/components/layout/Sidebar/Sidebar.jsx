/**
 * Sidebar Component
 * Menú lateral de navegación
 */
import { NavLink } from 'react-router-dom';
import { useAuth } from '../../../hooks/useAuth';
import './Sidebar.css';

const Sidebar = () => {
  const { hasAnyPermission, hasRole } = useAuth(); // Obtenemos también el usuario para ver sus permisos

  const menuItems = [
    {
      path: '/dashboard',
      icon: '📊',
      label: 'Dashboard',
      permissions: null, // Todos los usuarios
    },
    {
      path: '/dashboard/usuarios',
      icon: '🔑',
      label: 'Gestión de usuarios',
      permissions: null, // Oculto por defecto, se maneja con hasRole
      show: () => hasRole('Administrador General'),
    },
    {
      path: '/dashboard/catalog',
      icon: '💉',
      label: 'Catálogo',
      permissions: null, // Todos los usuarios pueden ver el catálogo
    },
    {
      path: '/dashboard/patients',
      icon: '👥',
      label: 'Pacientes',
      permissions: ["patients:read"],
    },
    {
      path: '/dashboard/orders',
      icon: '📋',
      label: 'Órdenes',
      permissions: ['orders:read'],
    },
    {
      path: '/dashboard/billing',
      icon: '💰',
      label: 'Facturación',
      permissions: ['billing:read'],
    },
    {
      path: '/dashboard/reports',
      icon: '📈',
      label: 'Reportes',
      permissions: null, // Todos los usuarios pueden ver reportes
      show: () => hasRole('Contador') || hasRole('Supervisor de Sede') || hasRole('Administrador General'),
    },
    {
      path: '/dashboard/reconciliation',
      icon: '🔄',
      label: 'Conciliación',
      permissions: null,
      show: () => hasRole('Contador') || hasRole('Supervisor de Sede') || hasRole('Administrador General'),
    },
  ];

  return (
    <aside className="sidebar">
      <nav className="sidebar-nav">
        {menuItems.map((item) => {
          // Si hay una función `show`, usarla para determinar la visibilidad
          if (item.show && !item.show()) {
            return null;
          }

          // Si el item requiere permisos específicos, verificar
          if (item.permissions && !hasAnyPermission(item.permissions)) {
            return null;
          }

          return (
            <NavLink
              key={item.path}
              to={item.path}
              className={({ isActive }) => (isActive ? 'nav-item active' : 'nav-item')}
              end={item.path === '/dashboard'}
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
