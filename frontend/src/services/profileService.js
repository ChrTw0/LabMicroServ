/**
 * Profile Service
 * Servicios para la gestión del perfil del usuario (F-03)
 */
import api from './api';
import { ENDPOINTS } from '../config/api.config';

const profileService = {
  /**
   * Obtener el perfil del usuario autenticado
   * @returns {Promise} - Datos del perfil del usuario
   */
  async getProfile() {
    const response = await api.get(ENDPOINTS.PROFILE.GET);
    return response.data;
  },

  /**
   * Actualizar el perfil del usuario autenticado
   * @param {Object} profileData - Datos a actualizar (first_name, last_name, phone, email)
   * @returns {Promise} - Perfil actualizado
   */
  async updateProfile(profileData) {
    const response = await api.put(ENDPOINTS.PROFILE.UPDATE, profileData);
    return response.data;
  },

  /**
   * Cambiar la contraseña del usuario autenticado
   * @param {string} currentPassword - Contraseña actual
   * @param {string} newPassword - Nueva contraseña
   * @returns {Promise}
   */
  async changePassword(currentPassword, newPassword) {
    const response = await api.put(ENDPOINTS.PROFILE.CHANGE_PASSWORD, {
      current_password: currentPassword,
      new_password: newPassword,
    });
    return response.data;
  },
};

export default profileService;
