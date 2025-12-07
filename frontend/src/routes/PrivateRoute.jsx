/**
 * PrivateRoute Component
 * HOC para proteger rutas que requieren autenticación
 */
import { Navigate } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';

export const PrivateRoute = ({ children, requiredRoles = null }) => {
  const { isAuthenticated, loading, hasAnyRole } = useAuth();

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
    return <Navigate to="/login" replace />;
  }

  // Si se requieren roles específicos, verificar
  if (requiredRoles && !hasAnyRole(requiredRoles)) {
    return (
      <div style={{ padding: '2rem', textAlign: 'center' }}>
        <h2>Acceso Denegado</h2>
        <p>No tienes permisos para acceder a esta página.</p>
      </div>
    );
  }

  // Usuario autenticado y con permisos correctos
  return children;
};
