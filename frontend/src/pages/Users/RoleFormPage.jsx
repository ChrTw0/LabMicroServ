/**
 * RoleFormPage Component
 * Form for editing role details and permissions
 */
import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { roleService } from '../../services';
import './RoleFormPage.css';

const RoleFormPage = () => {
    const { id } = useParams();

    const [formData, setFormData] = useState({
        name: '',
        description: '',
        permissions: [],
        is_active: true,
    });
    const [availablePermissions, setAvailablePermissions] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [success, setSuccess] = useState('');

    useEffect(() => {
        const fetchData = async () => {
            setLoading(true);
            try {
                const [roleData, permissionsData] = await Promise.all([
                    roleService.getById(id),
                    roleService.getAvailablePermissions(),
                ]);

                setAvailablePermissions(permissionsData);
                setFormData({
                    name: roleData.name || '',
                    description: roleData.description || '',
                    permissions: roleData.permissions ? JSON.parse(roleData.permissions) : [],
                    is_active: roleData.is_active,
                });

            } catch (err) {
                setError(err.message || 'Error al cargar los datos del rol');
            } finally {
                setLoading(false);
            }
        };
        fetchData();
    }, [id]);

    const handlePermissionChange = (e) => {
        const { value, checked } = e.target;
        setFormData(prev => {
            const newPermissions = checked
                ? [...prev.permissions, value]
                : prev.permissions.filter(p => p !== value);
            return { ...prev, permissions: newPermissions };
        });
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError(null);
        setSuccess('');

        // Ensure id is a number for the backend
        const roleIdNum = parseInt(id, 10);
        if (isNaN(roleIdNum)) {
            setError("ID de rol inválido.");
            setLoading(false);
            return;
        }

        console.log("Submitting update for role ID (parsed):", roleIdNum);
        console.log("Original ID from useParams:", id);
        
        const dataToSend = {
            description: formData.description,
            permissions: JSON.stringify(formData.permissions),
            is_active: formData.is_active,
        };
        console.log("Data to send:", dataToSend);

        try {
            await roleService.update(roleIdNum, dataToSend); // Use parsed ID
            setSuccess('Rol actualizado correctamente.');
        } catch (err) {
            let errorMessage = 'Error al actualizar el rol';
            if (err.message) {
                if (Array.isArray(err.message)) {
                    errorMessage = err.message.map(e => `${e.loc.join(' -> ')}: ${e.msg}`).join('; ');
                } else if (typeof err.message === 'string') {
                    errorMessage = err.message;
                } else { // Catch any other object errors
                    errorMessage = JSON.stringify(err.message);
                }
            }
            setError(errorMessage);
        } finally {
            setLoading(false);
        }
    };

    if (loading) {
        return <div className="loading-container"><p>Cargando...</p></div>;
    }

    return (
        <div className="role-form-page">
            <div className="form-header">
                <h1>Editar Rol</h1>
                <Link to="/dashboard/roles" className="btn btn-outline">
                    ← Volver a Roles
                </Link>
            </div>

            {error && <div className="alert alert-error">{error}</div>}
            {success && <div className="alert alert-success">{success}</div>}

            <form onSubmit={handleSubmit} className="role-form">
                <div className="form-section">
                    <h3>Detalles del Rol</h3>
                    <div className="form-group">
                        <label>Nombre del Rol</label>
                        <input type="text" value={formData.name} disabled />
                    </div>
                    <div className="form-group">
                        <label>Descripción</label>
                        <textarea
                            name="description"
                            value={formData.description}
                            onChange={e => setFormData(prev => ({ ...prev, description: e.target.value }))}
                        />
                    </div>
                    <div className="form-group">
                        <label>
                            <input
                                type="checkbox"
                                name="is_active"
                                checked={formData.is_active}
                                onChange={e => setFormData(prev => ({...prev, is_active: e.target.checked}))}
                            />
                            Rol Activo
                        </label>
                    </div>
                </div>

                <div className="form-section">
                    <h3>Permisos</h3>
                    <div className="permissions-grid">
                        {availablePermissions.map(perm => (
                            <div key={perm.id} className="permission-item">
                                <label>
                                    <input
                                        type="checkbox"
                                        value={perm.id}
                                        checked={formData.permissions.includes(perm.id)}
                                        onChange={handlePermissionChange}
                                    />
                                    {perm.name} ({perm.id})
                                </label>
                            </div>
                        ))}
                    </div>
                </div>

                <div className="form-actions">
                    <button type="submit" className="btn btn-primary" disabled={loading}>
                        {loading ? 'Guardando...' : 'Actualizar Rol'}
                    </button>
                </div>
            </form>
        </div>
    );
};

export default RoleFormPage;
