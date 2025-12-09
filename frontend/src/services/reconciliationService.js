/**
 * Reconciliation Service
 * Servicios relacionados con conciliación y cierre de caja
 */
import api from './api';
import { ENDPOINTS } from '../config/api.config';

const reconciliationService = {
  /**
   * Obtener lista de cierres diarios - RF-062
   * @param {Object} params - Parámetros de búsqueda (page, page_size, location_id, status, date_from, date_to)
   * @returns {Promise} - Lista de cierres
   */
  async getAllClosures(params = {}) {
    const response = await api.get(ENDPOINTS.RECONCILIATION.CLOSURES, { params });
    return response.data;
  },

  /**
   * Obtener cierre por ID con discrepancias
   * @param {number} id - ID del cierre
   * @returns {Promise} - Datos del cierre con discrepancias
   */
  async getClosureById(id) {
    const response = await api.get(ENDPOINTS.RECONCILIATION.CLOSURE_BY_ID(id));
    return response.data;
  },

  /**
   * Crear cierre diario y ejecutar conciliación - RF-056, RF-057, RF-058
   * @param {Object} closureData - Datos del cierre { location_id, closure_date, registered_total }
   * @returns {Promise} - Cierre creado con discrepancias detectadas
   */
  async createDailyClosure(closureData) {
    const response = await api.post(ENDPOINTS.RECONCILIATION.CLOSURES, closureData);
    return response.data;
  },

  /**
   * Cerrar cierre diario (cambiar estado a CLOSED)
   * @param {number} id - ID del cierre
   * @returns {Promise} - Cierre actualizado
   */
  async closeDailyClosure(id) {
    const response = await api.put(ENDPOINTS.RECONCILIATION.CLOSE(id));
    return response.data;
  },

  /**
   * Reabrir cierre cerrado - RF-063 (solo admin)
   * @param {number} id - ID del cierre
   * @param {string} reason - Justificación de la reapertura
   * @returns {Promise} - Cierre reabierto
   */
  async reopenClosure(id, reason) {
    const response = await api.post(ENDPOINTS.RECONCILIATION.REOPEN(id), { reason });
    return response.data;
  },

  /**
   * Obtener estadísticas de cierres
   * @param {Object} params - Parámetros de filtro
   * @returns {Promise} - Estadísticas
   */
  async getStatistics(params = {}) {
    const response = await api.get(ENDPOINTS.RECONCILIATION.STATISTICS, { params });
    return response.data;
  },

  /**
   * Generar reporte completo de conciliación - RF-057, RF-059
   * @param {Object} params - Parámetros (location_id, closure_date)
   * @returns {Promise} - Reporte con tabla comparativa
   */
  async getReconciliationReport(params = {}) {
    const response = await api.get(ENDPOINTS.RECONCILIATION.REPORT, { params });
    return response.data;
  },

  /**
   * Agregar discrepancia manual a un cierre
   * @param {number} closureId - ID del cierre
   * @param {string} description - Descripción de la discrepancia
   * @returns {Promise} - Discrepancia creada
   */
  async addDiscrepancy(closureId, description) {
    const response = await api.post(ENDPOINTS.RECONCILIATION.ADD_DISCREPANCY(closureId), {
      description,
    });
    return response.data;
  },

  /**
   * Marcar discrepancia como resuelta
   * @param {number} discrepancyId - ID de la discrepancia
   * @returns {Promise} - Discrepancia actualizada
   */
  async resolveDiscrepancy(discrepancyId) {
    const response = await api.put(ENDPOINTS.RECONCILIATION.RESOLVE_DISCREPANCY(discrepancyId));
    return response.data;
  },
};

export default reconciliationService;
