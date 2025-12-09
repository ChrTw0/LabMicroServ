/**
 * PrivateRoute Component
 * HOC para proteger rutas que requieren autenticación y permisos/roles específicos
 */
import { Navigate } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';

export const PrivateRoute = ({ children, requiredRoles = null, requiredPermissions = null }) => {
  const { isAuthenticated, loading, hasAnyRole, hasAnyPermission } = useAuth();

  // Mostrar loading mientras se verifica la autenticación
  if (loading) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh' }}>
        <p>Cargando...</p>
      </div>
    );
  }

  // Si no está autenticado, redirigir a login
  if (!isAuthenticated) {
    return <Navigate to="/" replace />;
  }

  // Si se requieren roles específicos, verificar
  if (requiredRoles && !hasAnyRole(requiredRoles)) {
    return (
      <div style={{ padding: '2rem', textAlign: 'center' }}>
        <h2>Acceso Denegado</h2>
        <p>No tienes los roles necesarios para acceder a esta página.</p>
      </div>
    );
  }

  // Si se requieren permisos específicos, verificar
  if (requiredPermissions && !hasAnyPermission(requiredPermissions)) {
    return (
      <div style={{ padding: '2rem', textAlign: 'center' }}>
        <h2>Acceso Denegado</h2>
        <p>No tienes los permisos necesarios para acceder a esta página.</p>
      </div>
    );
  }

  // Usuario autenticado y con permisos/roles correctos
  return children;
};
