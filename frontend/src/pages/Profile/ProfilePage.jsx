import { useState, useEffect } from 'react';
import { useAuth } from '../../hooks/useAuth';
import profileService from '../../services/profileService';
import './ProfilePage.css';

const ProfilePage = () => {
  const { user, updateUser } = useAuth();
  const [formData, setFormData] = useState({
    first_name: '',
    last_name: '',
    email: '',
    phone: '',
  });
  const [passwordData, setPasswordData] = useState({
    current_password: '',
    new_password: '',
  });

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  useEffect(() => {
    if (user) {
      setFormData({
        first_name: user.first_name || '',
        last_name: user.last_name || '',
        email: user.email || '',
        phone: user.phone || '',
      });
    }
  }, [user]);

  const handleFormChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handlePasswordChange = (e) => {
    const { name, value } = e.target;
    setPasswordData((prev) => ({ ...prev, [name]: value }));
  };

  const handleProfileSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setSuccess('');

    try {
      await profileService.updateProfile(formData);
      await updateUser(); // Actualiza el contexto global
      setSuccess('Perfil actualizado exitosamente.');
    } catch (err) {
      setError(err.message || 'Error al actualizar el perfil.');
    } finally {
      setLoading(false);
    }
  };

  const handlePasswordSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setSuccess('');

    if (passwordData.new_password.length < 8) {
      setError('La nueva contraseña debe tener al menos 8 caracteres.');
      setLoading(false);
      return;
    }

    try {
      await profileService.changePassword(
        passwordData.current_password,
        passwordData.new_password
      );
      setSuccess('Contraseña cambiada exitosamente.');
      setPasswordData({ current_password: '', new_password: '' });
    } catch (err) {
      setError(err.message || 'Error al cambiar la contraseña.');
    } finally {
      setLoading(false);
    }
  };

  if (!user) {
    return (
      <div className="loading-container">
        <p>Cargando perfil...</p>
      </div>
    );
  }

  return (
    <div className="profile-page">
      <div className="profile-header">
        <h1>Mi Perfil</h1>
      </div>

      {error && <div className="alert alert-error">{error}</div>}
      {success && <div className="alert alert-success">{success}</div>}

      <div className="profile-form-container">
        <form onSubmit={handleProfileSubmit}>
          <div className="form-section">
            <h3>Información Personal</h3>
            <div className="form-row">
              <div className="form-group">
                <label htmlFor="first_name">Nombres</label>
                <input
                  type="text"
                  id="first_name"
                  name="first_name"
                  value={formData.first_name}
                  onChange={handleFormChange}
                  disabled={loading}
                  required
                />
              </div>
              <div className="form-group">
                <label htmlFor="last_name">Apellidos</label>
                <input
                  type="text"
                  id="last_name"
                  name="last_name"
                  value={formData.last_name}
                  onChange={handleFormChange}
                  disabled={loading}
                  required
                />
              </div>
            </div>
            <div className="form-row">
              <div className="form-group">
                <label htmlFor="email">Email</label>
                <input
                  type="email"
                  id="email"
                  name="email"
                  value={formData.email}
                  onChange={handleFormChange}
                  disabled={loading}
                  required
                />
              </div>
              <div className="form-group">
                <label htmlFor="phone">Teléfono</label>
                <input
                  type="tel"
                  id="phone"
                  name="phone"
                  value={formData.phone || ''}
                  onChange={handleFormChange}
                  disabled={loading}
                />
              </div>
            </div>
             <div className="roles-section">
                <label>Roles Asignados</label>
                <div className="roles-list">
                    {user.roles?.map(role => (
                        <span key={role} className="role-badge">{role}</span>
                    ))}
                </div>
            </div>
          </div>
          <div className="form-actions">
            <button type="submit" className="btn btn-primary" disabled={loading}>
              {loading ? 'Guardando...' : 'Guardar Cambios'}
            </button>
          </div>
        </form>
      </div>

      <div className="profile-form-container" style={{ marginTop: '2rem' }}>
        <form onSubmit={handlePasswordSubmit}>
          <div className="form-section">
            <h3>Cambiar Contraseña</h3>
            <div className="form-row">
              <div className="form-group">
                <label htmlFor="current_password">Contraseña Actual</label>
                <input
                  type="password"
                  id="current_password"
                  name="current_password"
                  value={passwordData.current_password}
                  onChange={handlePasswordChange}
                  disabled={loading}
                  required
                />
              </div>
              <div className="form-group">
                <label htmlFor="new_password">Nueva Contraseña</label>
                <input
                  type="password"
                  id="new_password"
                  name="new_password"
                  value={passwordData.new_password}
                  onChange={handlePasswordChange}
                  disabled={loading}
                  required
                />
              </div>
            </div>
          </div>
          <div className="form-actions">
            <button type="submit" className="btn btn-primary" disabled={loading}>
              {loading ? 'Cambiando...' : 'Cambiar Contraseña'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default ProfilePage;
