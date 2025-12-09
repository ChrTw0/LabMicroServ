/**
 * RolesListPage Component
 * Page for listing and managing system roles
 */
import { useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { roleService } from '../../services';
import './RolesListPage.css';

const RolesListPage = () => {
    const navigate = useNavigate();
    const [roles, setRoles] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        const fetchRoles = async () => {
            setLoading(true);
            try {
                const rolesData = await roleService.getAll();
                setRoles(rolesData);
            } catch (err) {
                setError(err.message || 'Error al cargar los roles');
            } finally {
                setLoading(false);
            }
        };
        fetchRoles();
    }, []);

    if (loading) {
        return <div className="loading-container"><p>Cargando roles...</p></div>;
    }

    return (
        <div className="roles-list-page">
            <div className="page-header">
                <div>
                    <Link to="/dashboard/usuarios" className="btn-back">← Volver a Usuarios</Link>
                    <h1>Gestión de Roles</h1>
                </div>
            </div>

            {error && <div className="alert alert-error">{error}</div>}

            <div className="roles-grid">
                {roles.length === 0 ? (
                    <div className="empty-state">
                        <p>No se encontraron roles.</p>
                    </div>
                ) : (
                    roles.map(role => (
                        <div key={role.id} className="role-card">
                            <div className="role-header">
                                <h3>{role.name}</h3>
                                <div className="role-actions">
                                    <button
                                        onClick={() => navigate(`/dashboard/roles/${role.id}/edit`)}
                                        className="btn-icon btn-edit"
                                        title="Editar Permisos"
                                    >
                                        ✏️
                                    </button>
                                </div>
                            </div>
                            <p className="role-description">{role.description}</p>
                            <div className="role-footer">
                                <span className="role-id">ID: {role.id}</span>
                            </div>
                        </div>
                    ))
                )}
            </div>
        </div>
    );
};

export default RolesListPage;
