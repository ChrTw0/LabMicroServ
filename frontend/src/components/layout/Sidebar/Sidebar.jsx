/**
 * Sidebar Component
 * Menú lateral de navegación
 */
import { NavLink } from 'react-router-dom';
import { useAuth } from '../../../hooks/useAuth';
import './Sidebar.css';

const Sidebar = () => {
  const { /* user, */ hasAnyPermission } = useAuth(); // Obtenemos también el usuario para ver sus permisos

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
      permissions: null, // Todos los usuarios (provisional)
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
  ];

  return (
    <aside className="sidebar">
      <nav className="sidebar-nav">
        {menuItems.map((item) => {
          // --- INICIO: Bloque de depuración ---
/*           if (item.permissions) {
            const userHasAccess = hasAnyPermission(item.permissions);
            console.log(`[Sidebar] Verificando acceso para: "${item.label}"`);
            console.log(`  - Permisos requeridos:`, item.permissions);
            console.log(`  - Permisos del usuario:`, user);
            console.log(`  - ¿Tiene acceso?: ${userHasAccess}`);
          } */
          // --- FIN: Bloque de depuración ---

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
