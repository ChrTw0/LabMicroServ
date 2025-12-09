/**
 * useReports Hook
 * Hook personalizado para manejar reportes de órdenes y facturación
 */
import { useState } from 'react';
import { reportService } from '../services';

export const useReports = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // States para cada reporte
  const [paymentMethodData, setPaymentMethodData] = useState([]);
  const [topServicesData, setTopServicesData] = useState([]);
  const [monthlyRevenueData, setMonthlyRevenueData] = useState([]);
  const [patientTypesData, setPatientTypesData] = useState(null);
  const [salesByPeriodData, setSalesByPeriodData] = useState([]);
  const [invoiceTypeData, setInvoiceTypeData] = useState([]);

  /**
   * Obtener reporte de ventas por método de pago - RF-077
   */
  const fetchPaymentMethodReport = async (params = {}) => {
    try {
      setLoading(true);
      setError(null);
      const data = await reportService.getPaymentMethodReport(params);
      // Asegurar que siempre sea un array
      setPaymentMethodData(Array.isArray(data) ? data : []);
      return { success: true, data };
    } catch (err) {
      const errorMessage = err.message || 'Error al cargar reporte de métodos de pago';
      setError(errorMessage);
      setPaymentMethodData([]); // Array vacío en caso de error
      console.error('Error fetching payment method report:', err);
      return { success: false, error: errorMessage };
    } finally {
      setLoading(false);
    }
  };

  /**
   * Obtener reporte de servicios más solicitados - RF-076
   */
  const fetchTopServicesReport = async (params = {}) => {
    try {
      setLoading(true);
      setError(null);
      const data = await reportService.getTopServicesReport(params);
      setTopServicesData(data);
      return { success: true, data };
    } catch (err) {
      const errorMessage = err.message || 'Error al cargar reporte de servicios';
      setError(errorMessage);
      console.error('Error fetching top services report:', err);
      return { success: false, error: errorMessage };
    } finally {
      setLoading(false);
    }
  };

  /**
   * Obtener comparativa mensual de ventas - RF-079
   */
  const fetchMonthlyRevenueReport = async (params = {}) => {
    try {
      setLoading(true);
      setError(null);
      const data = await reportService.getMonthlyRevenueReport(params);
      setMonthlyRevenueData(data);
      return { success: true, data };
    } catch (err) {
      const errorMessage = err.message || 'Error al cargar reporte mensual';
      setError(errorMessage);
      console.error('Error fetching monthly revenue report:', err);
      return { success: false, error: errorMessage };
    } finally {
      setLoading(false);
    }
  };

  /**
   * Obtener reporte de pacientes nuevos vs recurrentes - RF-078
   */
  const fetchPatientTypesReport = async (params = {}) => {
    try {
      setLoading(true);
      setError(null);
      const data = await reportService.getPatientTypesReport(params);
      setPatientTypesData(data);
      return { success: true, data };
    } catch (err) {
      const errorMessage = err.message || 'Error al cargar reporte de pacientes';
      setError(errorMessage);
      console.error('Error fetching patient types report:', err);
      return { success: false, error: errorMessage };
    } finally {
      setLoading(false);
    }
  };

  /**
   * Obtener reporte de ventas por periodo - RF-075
   */
  const fetchSalesByPeriodReport = async (params = {}) => {
    try {
      setLoading(true);
      setError(null);
      const data = await reportService.getSalesByPeriodReport(params);
      setSalesByPeriodData(data);
      return { success: true, data };
    } catch (err) {
      const errorMessage = err.message || 'Error al cargar reporte de ventas por periodo';
      setError(errorMessage);
      console.error('Error fetching sales by period report:', err);
      return { success: false, error: errorMessage };
    } finally {
      setLoading(false);
    }
  };

  /**
   * Obtener reporte de ventas por tipo de comprobante - RF-075
   */
  const fetchInvoiceTypeReport = async (params = {}) => {
    try {
      setLoading(true);
      setError(null);
      const data = await reportService.getInvoiceTypeReport(params);
      setInvoiceTypeData(data);
      return { success: true, data };
    } catch (err) {
      const errorMessage = err.message || 'Error al cargar reporte por tipo de comprobante';
      setError(errorMessage);
      console.error('Error fetching invoice type report:', err);
      return { success: false, error: errorMessage };
    } finally {
      setLoading(false);
    }
  };

  return {
    // State
    loading,
    error,
    paymentMethodData,
    topServicesData,
    monthlyRevenueData,
    patientTypesData,
    salesByPeriodData,
    invoiceTypeData,

    // Actions
    fetchPaymentMethodReport,
    fetchTopServicesReport,
    fetchMonthlyRevenueReport,
    fetchPatientTypesReport,
    fetchSalesByPeriodReport,
    fetchInvoiceTypeReport,
  };
};
