/**
 * Catalog Service
 * Servicios relacionados con el catálogo de servicios/exámenes
 */
import api from './api';
import { ENDPOINTS } from '../config/api.config';

const catalogService = {
  /**
   * Obtener lista de servicios del catálogo
   * @param {Object} params - Parámetros de búsqueda (search, category_id, is_active, etc.)
   * @returns {Promise} - Lista de servicios
   */
  async getAllServices(params = {}) {
    const response = await api.get(ENDPOINTS.SERVICES.LIST, { params });
    return response.data;
  },

  /**
   * Obtener servicio por ID
   * @param {number} id - ID del servicio
   * @returns {Promise} - Datos del servicio
   */
  async getServiceById(id) {
    const response = await api.get(ENDPOINTS.SERVICES.BY_ID(id));
    return response.data;
  },

  /**
   * Crear nuevo servicio
   * @param {Object} serviceData - Datos del servicio
   * @returns {Promise} - Servicio creado
   */
  async createService(serviceData) {
    const response = await api.post(ENDPOINTS.SERVICES.LIST, serviceData);
    return response.data;
  },

  /**
   * Actualizar servicio
   * @param {number} id - ID del servicio
   * @param {Object} serviceData - Datos actualizados
   * @returns {Promise} - Servicio actualizado
   */
  async updateService(id, serviceData) {
    const response = await api.put(ENDPOINTS.SERVICES.BY_ID(id), serviceData);
    return response.data;
  },

  /**
   * Actualizar precio de servicio
   * @param {number} id - ID del servicio
   * @param {number} price - Nuevo precio
   * @returns {Promise} - Servicio actualizado
   */
  async updatePrice(id, price) {
    const response = await api.put(ENDPOINTS.SERVICES.PRICE(id), { new_price: price });
    return response.data;
  },

  /**
   * Obtener historial de precios
   * @param {number} id - ID del servicio
   * @returns {Promise} - Historial de cambios de precio
   */
  async getPriceHistory(id) {
    const response = await api.get(ENDPOINTS.SERVICES.PRICE_HISTORY(id));
    return response.data;
  },

  /**
   * Obtener lista de categorías
   * @returns {Promise} - Lista de categorías
   */
  async getAllCategories() {
    const response = await api.get(ENDPOINTS.CATEGORIES.LIST);
    return response.data;
  },

  /**
   * Crear nueva categoría
   * @param {Object} categoryData - Datos de la categoría
   * @returns {Promise} - Categoría creada
   */
  async createCategory(categoryData) {
    const response = await api.post(ENDPOINTS.CATEGORIES.LIST, categoryData);
    return response.data;
  },

  /**
   * Actualizar categoría
   * @param {number} id - ID de la categoría
   * @param {Object} categoryData - Datos actualizados
   * @returns {Promise} - Categoría actualizada
   */
  async updateCategory(id, categoryData) {
    const response = await api.put(ENDPOINTS.CATEGORIES.BY_ID(id), categoryData);
    return response.data;
  },

  /**
   * Eliminar categoría
   * @param {number} id - ID de la categoría
   * @returns {Promise} - Resultado de la eliminación
   */
  async deleteCategory(id) {
    const response = await api.delete(ENDPOINTS.CATEGORIES.BY_ID(id));
    return response.data;
  },
};

export default catalogService;
