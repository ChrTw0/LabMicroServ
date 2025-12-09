/**
 * Report Service
 * Servicios relacionados con reportes de órdenes y facturación
 */
import api from './api';
import { ENDPOINTS } from '../config/api.config';

const reportService = {
  /**
   * Obtener reporte de ventas por método de pago - RF-077
   * @param {Object} params - Parámetros de filtro (date_from, date_to, location_id)
   * @returns {Promise} - Estadísticas por método de pago
   */
  async getPaymentMethodReport(params = {}) {
    const response = await api.get(ENDPOINTS.REPORTS.PAYMENT_METHODS, { params });
    return response.data;
  },

  /**
   * Obtener reporte de servicios más solicitados - RF-076
   * @param {Object} params - Parámetros de filtro (date_from, date_to, location_id, limit)
   * @returns {Promise} - Top servicios más vendidos
   */
  async getTopServicesReport(params = {}) {
    const response = await api.get(ENDPOINTS.REPORTS.TOP_SERVICES, { params });
    return response.data;
  },

  /**
   * Obtener comparativa mensual de ventas - RF-079
   * @param {Object} params - Parámetros de filtro (months, location_id)
   * @returns {Promise} - Ingresos mensuales
   */
  async getMonthlyRevenueReport(params = {}) {
    const response = await api.get(ENDPOINTS.REPORTS.MONTHLY_REVENUE, { params });
    return response.data;
  },

  /**
   * Obtener reporte de pacientes nuevos vs recurrentes - RF-078
   * @param {Object} params - Parámetros de filtro (date_from, date_to, location_id)
   * @returns {Promise} - Estadísticas de pacientes
   */
  async getPatientTypesReport(params = {}) {
    const response = await api.get(ENDPOINTS.REPORTS.PATIENT_TYPES, { params });
    return response.data;
  },

  /**
   * Obtener reporte de ventas por periodo - RF-075
   * @param {Object} params - Parámetros de filtro (months, location_id)
   * @returns {Promise} - Ventas mensuales
   */
  async getSalesByPeriodReport(params = {}) {
    const response = await api.get(ENDPOINTS.REPORTS.SALES_BY_PERIOD, { params });
    return response.data;
  },

  /**
   * Obtener reporte de ventas por tipo de comprobante - RF-075
   * @param {Object} params - Parámetros de filtro (date_from, date_to, location_id)
   * @returns {Promise} - Estadísticas por tipo de comprobante (BOLETA/FACTURA)
   */
  async getInvoiceTypeReport(params = {}) {
    const response = await api.get(ENDPOINTS.REPORTS.INVOICE_TYPES, { params });
    return response.data;
  },
};

export default reportService;
