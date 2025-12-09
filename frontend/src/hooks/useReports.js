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
      // Asegurar que siempre sea un array y transformar valores numéricos
      const normalizedData = Array.isArray(data) ? data.map(item => ({
        ...item,
        total_amount: parseFloat(item.total_amount) || 0,
        count: parseInt(item.count) || 0,
        percentage: parseFloat(item.percentage) || 0
      })) : [];
      setPaymentMethodData(normalizedData);
      return { success: true, data: normalizedData };
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
      // Asegurar que siempre sea un array y transformar valores numéricos
      const normalizedData = Array.isArray(data) ? data.map(item => ({
        ...item,
        quantity_sold: parseInt(item.quantity_sold) || 0,
        total_revenue: parseFloat(item.total_revenue) || 0,
        percentage: parseFloat(item.percentage) || 0
      })) : [];
      setTopServicesData(normalizedData);
      return { success: true, data: normalizedData };
    } catch (err) {
      const errorMessage = err.message || 'Error al cargar reporte de servicios';
      setError(errorMessage);
      setTopServicesData([]);
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
      // Asegurar que siempre sea un array y transformar valores numéricos
      const normalizedData = Array.isArray(data) ? data.map(item => ({
        ...item,
        total_revenue: parseFloat(item.total_revenue) || 0,
        total_orders: parseInt(item.total_orders) || 0
      })) : [];
      setMonthlyRevenueData(normalizedData);
      return { success: true, data: normalizedData };
    } catch (err) {
      const errorMessage = err.message || 'Error al cargar reporte mensual';
      setError(errorMessage);
      setMonthlyRevenueData([]);
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
      // Asegurar que siempre sea un array y transformar valores numéricos
      const normalizedData = Array.isArray(data) ? data.map(item => ({
        ...item,
        total_sales: parseFloat(item.total_sales) || 0,
        total_invoices: parseInt(item.total_invoices) || 0,
        total_tax: parseFloat(item.total_tax) || 0,
        avg_invoice_value: parseFloat(item.avg_invoice_value) || 0
      })) : [];
      setSalesByPeriodData(normalizedData);
      return { success: true, data: normalizedData };
    } catch (err) {
      const errorMessage = err.message || 'Error al cargar reporte de ventas por periodo';
      setError(errorMessage);
      setSalesByPeriodData([]);
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
      // Asegurar que siempre sea un array y transformar valores numéricos
      const normalizedData = Array.isArray(data) ? data.map(item => ({
        ...item,
        total_amount: parseFloat(item.total_amount) || 0,
        count: parseInt(item.count) || 0,
        percentage: parseFloat(item.percentage) || 0
      })) : [];
      setInvoiceTypeData(normalizedData);
      return { success: true, data: normalizedData };
    } catch (err) {
      const errorMessage = err.message || 'Error al cargar reporte por tipo de comprobante';
      setError(errorMessage);
      setInvoiceTypeData([]);
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
