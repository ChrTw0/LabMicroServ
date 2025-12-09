/**
 * UsersListPage Component
 * Page for listing and managing system users
 */
import { useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { userService } from '../../services';
import './UsersListPage.css';

const UsersListPage = () => {
  const navigate = useNavigate();
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [pagination, setPagination] = useState({ total: 0, page: 1, page_size: 50 });
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState(''); // 'true', 'false', or ''

  useEffect(() => {
    fetchUsers(1);
  }, []);

  const fetchUsers = async (page = 1) => {
    setLoading(true);
    setError(null);
    try {
      const params = { page, page_size: 50 };
      if (searchTerm) params.search = searchTerm;
      if (statusFilter !== '') params.is_active = statusFilter === 'true';
      
      const data = await userService.getAll(params);
      setUsers(data.users || []);
      setPagination({ total: data.total, page: data.page, page_size: data.page_size });
    } catch (err) {
      setError(err.message || 'Error al cargar usuarios');
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = (e) => {
    e.preventDefault();
    fetchUsers(1);
  };

  const handleDeactivate = async (userId, userName) => {
    if (window.confirm(`¿Está seguro de que desea desactivar al usuario ${userName}?`)) {
      try {
        await userService.deactivate(userId);
        alert('Usuario desactivado correctamente.');
        fetchUsers(pagination.page);
      } catch (err) {
        alert(`Error al desactivar: ${err.message}`);
      }
    }
  };

  const handleActivate = async (userId, userName) => {
    if (window.confirm(`¿Está seguro de que desea activar al usuario ${userName}?`)) {
        try {
            await userService.activate(userId);
            alert('Usuario activado correctamente.');
            fetchUsers(pagination.page);
        } catch (err) {
            alert(`Error al activar: ${err.message}`);
        }
    }
  };

  if (loading && users.length === 0) {
    return <div className="loading-container"><p>Cargando usuarios...</p></div>;
  }

  return (
    <div className="users-list-page">
      <div className="page-header">
        <h1>Gestión de Usuarios</h1>
        <div className="header-actions">
          <Link to="/dashboard/roles" className="btn btn-outline">
            Gestionar Roles
          </Link>
          <Link to="/dashboard/usuarios/new" className="btn btn-primary">
            + Nuevo Usuario
          </Link>
        </div>
      </div>

      {error && <div className="alert alert-error">{error}</div>}

      <div className="filters-section">
        <form onSubmit={handleSearch} className="filters-form">
          <input
            type="text"
            placeholder="Buscar por nombre o email..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="search-input"
          />
          <select 
            value={statusFilter} 
            onChange={(e) => setStatusFilter(e.target.value)}
            className="filter-select"
          >
            <option value="">Todos los estados</option>
            <option value="true">Activo</option>
            <option value="false">Inactivo</option>
          </select>
          <button type="submit" className="btn btn-secondary">Buscar</button>
        </form>
      </div>

      <div className="users-stats">
        <p>
          Mostrando <strong>{users.length}</strong> de <strong>{pagination.total}</strong> usuarios
        </p>
      </div>

      <div className="table-container">
        <table className="users-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Nombre</th>
              <th>Email</th>
              <th>Roles</th>
              <th>Estado</th>
              <th>Acciones</th>
            </tr>
          </thead>
          <tbody>
            {users.length === 0 ? (
              <tr>
                <td colSpan="6" className="text-center">No se encontraron usuarios.</td>
              </tr>
            ) : (
              users.map((user) => (
                <tr key={user.id}>
                  <td>{user.id}</td>
                  <td>{user.first_name} {user.last_name}</td>
                  <td>{user.email}</td>
                  <td>
                    <div className="roles-list">
                      {user.roles.map(role => <span key={role}>{role}</span>)}
                    </div>
                  </td>
                  <td>
                    <span className={`badge ${user.is_active ? 'badge-success' : 'badge-danger'}`}>
                      {user.is_active ? 'Activo' : 'Inactivo'}
                    </span>
                  </td>
                  <td>
                    <div className="action-buttons">
                      <button
                        onClick={() => navigate(`/dashboard/usuarios/${user.id}/edit`)}
                        className="btn-icon btn-edit"
                        title="Editar"
                      >
                        ✏️
                      </button>
                      {user.is_active ? (
                        <button
                          onClick={() => handleDeactivate(user.id, `${user.first_name} ${user.last_name}`)}
                          className="btn-icon btn-delete"
                          title="Desactivar"
                        >
                          🗑️
                        </button>
                      ) : (
                        <button
                          onClick={() => handleActivate(user.id, `${user.first_name} ${user.last_name}`)}
                          className="btn-icon"
                          title="Activar"
                        >
                          ✅
                        </button>
                      )}
                    </div>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {loading && <div className="loading-overlay"><p>Cargando...</p></div>}
    </div>
  );
};

export default UsersListPage;
