/**
 * Role Service
 * Servicios para la gestión de roles
 */
import api from './api';

const roleService = {
  /**
   * Obtener lista de todos los roles
   */
  async getAll() {
    const response = await api.get('/api/v1/roles');
    return response.data;
  },

  /**
   * Obtener rol por ID
   */
  async getById(id) {
    const response = await api.get(`/api/v1/roles/${id}`);
    return response.data;
  },

  /**
   * Actualizar rol
   */
  async update(id, roleData) {
    const response = await api.put(`/api/v1/roles/${id}`, roleData);
    return response.data;
  },

  /**
   * Obtener todos los permisos disponibles
   */
  async getAvailablePermissions() {
    const response = await api.get('/api/v1/roles/available-permissions');
    return response.data;
  }
};

export default roleService;
