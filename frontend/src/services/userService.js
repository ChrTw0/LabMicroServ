/**
 * User Service
 * Servicios para la gestión de usuarios
 */
import api from './api';
import { ENDPOINTS } from '../config/api.config';

const userService = {
  /**
   * Obtener lista de usuarios
   * @param {Object} params - Parámetros de búsqueda (page, page_size, search, etc.)
   * @returns {Promise} - Lista de usuarios
   */
  async getAll(params = {}) {
    const response = await api.get(ENDPOINTS.USERS.LIST, { params });
    return response.data;
  },

  /**
   * Obtener usuario por ID
   * @param {number} id - ID del usuario
   * @returns {Promise} - Datos del usuario
   */
  async getById(id) {
    const response = await api.get(ENDPOINTS.USERS.BY_ID(id));
    return response.data;
  },

  /**
   * Crear nuevo usuario
   * @param {Object} userData - Datos del usuario
   * @returns {Promise} - Usuario creado
   */
  async create(userData) {
    const response = await api.post(ENDPOINTS.USERS.LIST, userData);
    return response.data;
  },

  /**
   * Actualizar usuario
   * @param {number} id - ID del usuario
   * @param {Object} userData - Datos a actualizar
   * @returns {Promise} - Usuario actualizado
   */
  async update(id, userData) {
    const response = await api.put(ENDPOINTS.USERS.BY_ID(id), userData);
    return response.data;
  },

  /**
   * Desactivar usuario (soft delete)
   * @param {number} id - ID del usuario
   * @returns {Promise}
   */
  async deactivate(id) {
    const response = await api.delete(ENDPOINTS.USERS.BY_ID(id));
    return response.data;
  },
  
  /**
   * Activar usuario
   * @param {number} id - ID del usuario
   * @returns {Promise}
   */
  async activate(id) {
      const response = await api.put(ENDPOINTS.USERS.ACTIVATE(id));
      return response.data;
  },

  /**
   * Asignar roles a un usuario
   * @param {number} id - ID del usuario
   * @param {Array<number>} roleIds - IDs de los roles
   * @returns {Promise}
   */
  async assignRoles(id, roleIds) {
    const response = await api.put(`${ENDPOINTS.USERS.BY_ID(id)}/roles`, { role_ids: roleIds });
    return response.data;
  },

  /**
   * Obtener todos los roles
   * @returns {Promise} - Lista de roles
   */
  async getRoles() {
      const response = await api.get('/api/v1/roles?active_only=true'); // Directly using path
      return response.data;
  }
};

export default userService;
