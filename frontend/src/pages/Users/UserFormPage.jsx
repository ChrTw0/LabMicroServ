/**
 * UserFormPage Component
 * Form for creating and editing users
 */
import { useState, useEffect } from 'react';
import { useNavigate, useParams, Link } from 'react-router-dom';
import { userService } from '../../services';
import './UserFormPage.css';

const UserFormPage = () => {
  const navigate = useNavigate();
  const { id } = useParams();
  const isEditMode = Boolean(id);

  const [formData, setFormData] = useState({
    first_name: '',
    last_name: '',
    email: '',
    phone: '',
    password: '',
    location_id: 1,
    role_ids: [],
    is_active: true,
  });
  const [roles, setRoles] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [successInfo, setSuccessInfo] = useState('');
  const [successRoles, setSuccessRoles] = useState('');

  useEffect(() => {
    const fetchData = async () => {
      try {
        const rolesData = await userService.getRoles();
        setRoles(rolesData);

        if (isEditMode) {
          const userData = await userService.getById(id);
          setFormData({
            first_name: userData.first_name || '',
            last_name: userData.last_name || '',
            email: userData.email || '',
            phone: userData.phone || '',
            password: '', // Password is not sent for editing
            location_id: userData.location_id || 1,
            role_ids: userData.roles.map(roleName => {
                const role = rolesData.find(r => r.name === roleName);
                return role ? role.id : null;
            }).filter(roleId => roleId !== null),
            is_active: userData.is_active,
          });
        }
      } catch (err) {
        setError(err.message || 'Error al cargar los datos');
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, [id, isEditMode]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };
  
  const handleRoleChange = (e) => {
    const selectedIds = Array.from(e.target.selectedOptions, option => parseInt(option.value));
    setFormData(prev => ({ ...prev, role_ids: selectedIds }));
  };

  const handleInfoSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setSuccessInfo('');

    try {
        await userService.update(id, {
            first_name: formData.first_name,
            last_name: formData.last_name,
            phone: formData.phone,
            is_active: formData.is_active,
        });
        setSuccessInfo('Información personal actualizada correctamente.');
    } catch (err) {
        setError(err.message || 'Error al actualizar la información.');
    } finally {
        setLoading(false);
    }
  };

  const handleRolesSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setSuccessRoles('');

    if (formData.role_ids.length === 0) {
        setError('Debe seleccionar al menos un rol.');
        setLoading(false);
        return;
    }

    try {
        await userService.assignRoles(id, formData.role_ids);
        setSuccessRoles('Roles actualizados correctamente.');
    } catch (err) {
        setError(err.message || 'Error al actualizar los roles.');
    } finally {
        setLoading(false);
    }
  };

  const handleCreateSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    if (formData.role_ids.length === 0) {
        setError('Debe seleccionar al menos un rol.');
        setLoading(false);
        return;
    }

    try {
        await userService.create(formData);
        alert('Usuario creado correctamente');
        navigate('/dashboard/usuarios');
    } catch (err) {
        setError(err.message || 'Error al crear el usuario');
    } finally {
        setLoading(false);
    }
  };

  if (loading && !isEditMode) {
    return <div className="loading-container"><p>Cargando...</p></div>;
  }
  
  const editForm = (
    <>
      <form onSubmit={handleInfoSubmit} className="user-form">
        <div className="form-section">
          <h3>Detalles del Usuario</h3>
          {successInfo && <div className="alert alert-success">{successInfo}</div>}
          <div className="form-row">
            <div className="form-group">
              <label>Nombres *</label>
              <input type="text" name="first_name" value={formData.first_name} onChange={handleChange} required />
            </div>
            <div className="form-group">
              <label>Apellidos *</label>
              <input type="text" name="last_name" value={formData.last_name} onChange={handleChange} required />
            </div>
          </div>
          <div className="form-row">
            <div className="form-group">
              <label>Email *</label>
              <input type="email" name="email" value={formData.email} onChange={handleChange} required disabled={isEditMode} />
            </div>
            <div className="form-group">
              <label>Teléfono</label>
              <input type="tel" name="phone" value={formData.phone} onChange={handleChange} />
            </div>
          </div>
           <div className="form-group">
              <label>
                <input type="checkbox" name="is_active" checked={formData.is_active} onChange={e => setFormData(prev => ({...prev, is_active: e.target.checked}))} />
                Usuario Activo
              </label>
            </div>
        </div>
        <div className="form-actions">
          <button type="submit" className="btn btn-primary" disabled={loading}>
            {loading ? 'Guardando...' : 'Actualizar Información'}
          </button>
        </div>
      </form>

      <form onSubmit={handleRolesSubmit} className="user-form" style={{marginTop: '2rem'}}>
        <div className="form-section">
            <h3>Roles y Permisos</h3>
            {successRoles && <div className="alert alert-success">{successRoles}</div>}
            <div className="form-row">
                <div className="form-group">
                <label>Sede</label>
                <select name="location_id" value={formData.location_id} onChange={handleChange}>
                    <option value={1}>Sede Principal</option>
                    <option value={2}>Sede Secundaria</option>
                </select>
                </div>
                <div className="form-group">
                <label>Roles *</label>
                <select name="role_ids" value={formData.role_ids} onChange={handleRoleChange} multiple required>
                    {roles.map(role => (
                    <option key={role.id} value={role.id}>{role.name}</option>
                    ))}
                </select>
                </div>
            </div>
        </div>
        <div className="form-actions">
          <button type="submit" className="btn btn-primary" disabled={loading}>
            {loading ? 'Guardando...' : 'Actualizar Roles'}
          </button>
        </div>
      </form>
    </>
  );

  const createForm = (
      <form onSubmit={handleCreateSubmit} className="user-form">
        <div className="form-section">
          <h3>Detalles del Usuario</h3>
          <div className="form-row">
            <div className="form-group">
              <label>Nombres *</label>
              <input type="text" name="first_name" value={formData.first_name} onChange={handleChange} required />
            </div>
            <div className="form-group">
              <label>Apellidos *</label>
              <input type="text" name="last_name" value={formData.last_name} onChange={handleChange} required />
            </div>
          </div>
          <div className="form-row">
            <div className="form-group">
              <label>Email *</label>
              <input type="email" name="email" value={formData.email} onChange={handleChange} required disabled={isEditMode} />
            </div>
            <div className="form-group">
              <label>Teléfono</label>
              <input type="tel" name="phone" value={formData.phone} onChange={handleChange} />
            </div>
          </div>
          {!isEditMode && (
            <div className="form-group">
              <label>Contraseña *</label>
              <input type="password" name="password" value={formData.password} onChange={handleChange} required />
            </div>
          )}
        </div>

        <div className="form-section">
          <h3>Roles y Permisos</h3>
          <div className="form-row">
            <div className="form-group">
              <label>Sede</label>
              <select name="location_id" value={formData.location_id} onChange={handleChange}>
                <option value={1}>Sede Principal</option>
                <option value={2}>Sede Secundaria</option>
              </select>
            </div>
            <div className="form-group">
              <label>Roles *</label>
              <select name="role_ids" value={formData.role_ids} onChange={handleRoleChange} multiple required>
                {roles.map(role => (
                  <option key={role.id} value={role.id}>{role.name}</option>
                ))}
              </select>
            </div>
          </div>
           <div className="form-group">
              <label>
                <input type="checkbox" name="is_active" checked={formData.is_active} onChange={e => setFormData(prev => ({...prev, is_active: e.target.checked}))} />
                Usuario Activo
              </label>
            </div>
        </div>

        <div className="form-actions">
          <button type="submit" className="btn btn-primary" disabled={loading}>
            {loading ? 'Guardando...' : 'Crear Usuario'}
          </button>
        </div>
      </form>
  );

  return (
    <div className="user-form-page">
      <div className="form-header">
        <h1>{isEditMode ? 'Editar Usuario' : 'Nuevo Usuario'}</h1>
        <Link to="/dashboard/usuarios" className="btn btn-outline">
          ← Volver a la lista
        </Link>
      </div>

      {error && <div className="alert alert-error">{error}</div>}

      {isEditMode ? editForm : createForm}
    </div>
  );
};

export default UserFormPage;
