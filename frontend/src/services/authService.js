/**
 * Authentication Service
 * Servicios relacionados con autenticación
 */
import api from './api';
import { ENDPOINTS } from '../config/api.config';

const authService = {
  /**
   * Login de usuario
   * @param {string} email - Email del usuario
   * @param {string} password - Contraseña
   * @returns {Promise} - Token y datos del usuario
   */
  async login(email, password) {
    const response = await api.post(ENDPOINTS.AUTH.LOGIN, {
      email,
      password,
    });
    return response.data;
  },

  /**
   * Obtener información del usuario actual
   * @returns {Promise} - Datos del usuario autenticado
   */
  async getCurrentUser() {
    const response = await api.get(ENDPOINTS.AUTH.ME);
    return response.data;
  },

  /**
   * Verificar si el token es válido
   * @returns {Promise} - Validez del token
   */
  async verifyToken() {
    const response = await api.post(ENDPOINTS.AUTH.VERIFY_TOKEN);
    return response.data;
  },

  /**
   * Cambiar contraseña
   * @param {string} currentPassword - Contraseña actual
   * @param {string} newPassword - Nueva contraseña
   * @returns {Promise}
   */
  async changePassword(currentPassword, newPassword) {
    const response = await api.post(ENDPOINTS.AUTH.CHANGE_PASSWORD, {
      current_password: currentPassword,
      new_password: newPassword,
    });
    return response.data;
  },

  /**
   * Registrar nuevo usuario (requiere autenticación)
   * @param {Object} userData - Datos del nuevo usuario
   * @returns {Promise}
   */
  async register(userData) {
    const response = await api.post(ENDPOINTS.AUTH.REGISTER, userData);
    return response.data;
  },
};

export default authService;
