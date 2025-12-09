/**
 * Order Service
 * Servicios relacionados con órdenes de servicio
 */
import api from './api';
import { ENDPOINTS } from '../config/api.config';

const orderService = {
  /**
   * Obtener lista de órdenes
   * @param {Object} params - Parámetros de búsqueda (page, page_size, search, status, etc.)
   * @returns {Promise} - Lista de órdenes
   */
  async getAll(params = {}) {
    const response = await api.get(ENDPOINTS.ORDERS.LIST, { params });
    return response.data;
  },

  /**
   * Obtener orden por ID
   * @param {number} id - ID de la orden
   * @returns {Promise} - Datos de la orden con items y pagos
   */
  async getById(id) {
    const response = await api.get(ENDPOINTS.ORDERS.BY_ID(id));
    return response.data;
  },

  /**
   * Buscar orden por número
   * @param {string} orderNumber - Número de orden
   * @returns {Promise} - Datos de la orden
   */
  async getByNumber(orderNumber) {
    const response = await api.get(ENDPOINTS.ORDERS.BY_NUMBER(orderNumber));
    return response.data;
  },

  /**
   * Crear nueva orden
   * @param {Object} orderData - Datos de la orden
   * @returns {Promise} - Orden creada
   */
  async create(orderData) {
    const response = await api.post(ENDPOINTS.ORDERS.LIST, orderData);
    return response.data;
  },

  /**
   * Actualizar orden
   * @param {number} id - ID de la orden
   * @param {Object} orderData - Datos actualizados
   * @returns {Promise} - Orden actualizada
   */
  async update(id, orderData) {
    const response = await api.put(ENDPOINTS.ORDERS.BY_ID(id), orderData);
    return response.data;
  },

  /**
   * Actualizar estado de orden
   * @param {number} id - ID de la orden
   * @param {string} status - Nuevo estado (REGISTRADA, EN_PROCESO, COMPLETADA, ANULADA)
   * @returns {Promise} - Orden actualizada
   */
  async updateStatus(id, status) {
    const response = await api.put(ENDPOINTS.ORDERS.STATUS(id), { status });
    return response.data;
  },

  /**
   * Agregar pago(s) a una orden
   * @param {number} id - ID de la orden
   * @param {Array} payments - Array de pagos [{payment_method, amount}, ...]
   * @returns {Promise} - Orden actualizada con pagos
   */
  async addPayments(id, payments) {
    const response = await api.post(ENDPOINTS.ORDERS.PAYMENTS(id), { payments });
    return response.data;
  },

  /**
   * Anular orden
   * @param {number} id - ID de la orden
   * @returns {Promise} - Orden anulada
   */
  async cancel(id) {
    const response = await api.delete(ENDPOINTS.ORDERS.BY_ID(id));
    return response.data;
  },

  /**
   * Obtener estadísticas de órdenes
   * @param {Object} params - Parámetros (date_from, date_to)
   * @returns {Promise} - Estadísticas
   */
  async getStatistics(params = {}) {
    const response = await api.get(ENDPOINTS.ORDERS.STATISTICS, { params });
    return response.data;
  },
};

export default orderService;
