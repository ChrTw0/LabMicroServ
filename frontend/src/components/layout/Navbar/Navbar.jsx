/**
 * Navbar Component
 * Barra de navegación superior
 */
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../../hooks/useAuth';
import './Navbar.css';

const Navbar = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    if (window.confirm('¿Estás seguro de cerrar sesión?')) {
      logout();
    }
  };

  const handleProfileClick = () => {
    navigate('/dashboard/profile');
  };

  return (
    <nav className="navbar">
      <div className="navbar-brand">
        <h2>🧪 Laboratorio Clínico</h2>
      </div>

      <div className="navbar-user">
        <button className="user-profile-button" onClick={handleProfileClick}>
          <span className="user-name">
            {user?.first_name} {user?.last_name}
          </span>
        </button>
        {/* <span className="user-role">{user?.roles?.[0]}</span> */}
        <button onClick={handleLogout} className="btn-logout">
          Cerrar Sesión
        </button>
      </div>
    </nav>
  );
};

export default Navbar;
