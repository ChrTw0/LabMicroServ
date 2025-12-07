/**
 * AuthContext
 * Context para manejar la autenticación global de la aplicación
 */
import { createContext, useState, useEffect } from 'react';
import authService from '../services/authService';

export const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(null);
  const [loading, setLoading] = useState(true);
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  // Inicializar estado desde localStorage
  useEffect(() => {
    const initAuth = async () => {
      const storedToken = localStorage.getItem('access_token');
      const storedUser = localStorage.getItem('user');

      if (storedToken && storedUser) {
        try {
          // Verificar si el token sigue siendo válido
          await authService.verifyToken();
          setToken(storedToken);
          setUser(JSON.parse(storedUser));
          setIsAuthenticated(true);
        } catch (error) {
          // Token inválido, limpiar localStorage
          console.error('Token inválido:', error);
          localStorage.removeItem('access_token');
          localStorage.removeItem('user');
        }
      }

      setLoading(false);
    };

    initAuth();
  }, []);

  /**
   * Login de usuario
   */
  const login = async (email, password) => {
    try {
      const data = await authService.login(email, password);

      // Guardar token y usuario en localStorage
      localStorage.setItem('access_token', data.access_token);
      localStorage.setItem('user', JSON.stringify(data.user));

      // Actualizar estado
      setToken(data.access_token);
      setUser(data.user);
      setIsAuthenticated(true);

      return { success: true, user: data.user };
    } catch (error) {
      console.error('Error en login:', error);
      return { success: false, error: error.message };
    }
  };

  /**
   * Logout de usuario
   */
  const logout = () => {
    // Limpiar localStorage
    localStorage.removeItem('access_token');
    localStorage.removeItem('user');

    // Limpiar estado
    setToken(null);
    setUser(null);
    setIsAuthenticated(false);
  };

  /**
   * Actualizar información del usuario
   */
  const updateUser = async () => {
    try {
      const userData = await authService.getCurrentUser();
      setUser(userData);
      localStorage.setItem('user', JSON.stringify(userData));
      return { success: true, user: userData };
    } catch (error) {
      console.error('Error al actualizar usuario:', error);
      return { success: false, error: error.message };
    }
  };

  /**
   * Verificar si el usuario tiene un rol específico
   */
  const hasRole = (roleName) => {
    if (!user || !user.roles) return false;
    return user.roles.includes(roleName);
  };

  /**
   * Verificar si el usuario tiene alguno de los roles especificados
   */
  const hasAnyRole = (roleNames) => {
    if (!user || !user.roles) return false;
    return roleNames.some((roleName) => user.roles.includes(roleName));
  };

  const value = {
    user,
    token,
    loading,
    isAuthenticated,
    login,
    logout,
    updateUser,
    hasRole,
    hasAnyRole,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};
