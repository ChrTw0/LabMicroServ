/**
 * Billing Service
 * Servicios relacionados con facturación y comprobantes electrónicos (SUNAT)
 */
import api from './api';
import { ENDPOINTS } from '../config/api.config';

const billingService = {
  /**
   * Obtener lista de facturas/comprobantes
   * @param {Object} params - Parámetros de búsqueda (search, status, date_from, date_to, etc.)
   * @returns {Promise} - Lista de comprobantes
   */
  async getAll(params = {}) {
    const response = await api.get(ENDPOINTS.INVOICES.LIST, { params });
    return response.data;
  },

  /**
   * Obtener comprobante por ID
   * @param {number} id - ID del comprobante
   * @returns {Promise} - Datos del comprobante
   */
  async getById(id) {
    const response = await api.get(ENDPOINTS.INVOICES.BY_ID(id));
    return response.data;
  },

  /**
   * Crear nuevo comprobante
   * @param {Object} invoiceData - Datos del comprobante
   * @returns {Promise} - Comprobante creado
   */
  async create(invoiceData) {
    const response = await api.post(ENDPOINTS.INVOICES.LIST, invoiceData);
    return response.data;
  },

  /**
   * Actualizar estado del comprobante
   * @param {number} id - ID del comprobante
   * @param {string} status - Nuevo estado
   * @returns {Promise} - Comprobante actualizado
   */
  async updateStatus(id, status) {
    const response = await api.put(ENDPOINTS.INVOICES.STATUS(id), { status });
    return response.data;
  },

  /**
   * Obtener XML UBL del comprobante
   * @param {number} id - ID del comprobante
   * @returns {Promise} - XML UBL
   */
  async getUBL(id) {
    const response = await api.get(ENDPOINTS.INVOICES.UBL(id));
    return response.data;
  },

  /**
   * Obtener CDR (Constancia de Recepción) de SUNAT
   * @param {number} id - ID del comprobante
   * @returns {Promise} - CDR de SUNAT
   */
  async getCDR(id) {
    const response = await api.get(ENDPOINTS.INVOICES.CDR(id));
    return response.data;
  },

  /**
   * Enviar comprobante a SUNAT
   * @param {number} id - ID del comprobante
   * @returns {Promise} - Resultado del envío
   */
  async sendToSUNAT(id) {
    const response = await api.post(`${ENDPOINTS.INVOICES.BY_ID(id)}/send`);
    return response.data;
  },

  /**
   * Anular comprobante
   * @param {number} id - ID del comprobante
   * @param {string} reason - Motivo de anulación
   * @returns {Promise} - Resultado de la anulación
   */
  async void(id, reason) {
    const response = await api.post(`${ENDPOINTS.INVOICES.BY_ID(id)}/void`, { reason });
    return response.data;
  },

  /**
   * Obtener estadísticas de facturación
   * @param {Object} params - Parámetros de filtro (date_from, date_to)
   * @returns {Promise} - Estadísticas
   */
  async getStatistics(params = {}) {
    const response = await api.get(ENDPOINTS.INVOICES.STATISTICS, { params });
    return response.data;
  },
};

export default billingService;
