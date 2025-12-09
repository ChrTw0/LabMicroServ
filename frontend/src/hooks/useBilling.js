/**
 * useBilling Hook
 * Hook para gestión de facturación y comprobantes electrónicos
 */
import { useState } from 'react';
import { billingService } from '../services';

export const useBilling = () => {
  const [invoices, setInvoices] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [pagination, setPagination] = useState({
    total: 0,
    page: 1,
    page_size: 50,
  });

  /**
   * Cargar lista de facturas/comprobantes
   */
  const fetchInvoices = async (params = {}) => {
    setLoading(true);
    setError(null);

    try {
      const data = await billingService.getAll(params);
      setInvoices(data.invoices || []);
      setPagination({
        total: data.total || 0,
        page: data.page || 1,
        page_size: data.page_size || 50,
      });
    } catch (err) {
      setError(err.message || 'Error al cargar comprobantes');
      console.error('Error fetching invoices:', err);
    } finally {
      setLoading(false);
    }
  };

  /**
   * Obtener comprobante por ID
   */
  const fetchInvoiceById = async (id) => {
    setLoading(true);
    setError(null);

    try {
      const invoice = await billingService.getById(id);
      return { success: true, data: invoice };
    } catch (err) {
      setError(err.message || 'Error al cargar comprobante');
      return { success: false, error: err.message };
    } finally {
      setLoading(false);
    }
  };

  /**
   * Crear nuevo comprobante
   */
  const createInvoice = async (invoiceData) => {
    setLoading(true);
    setError(null);

    try {
      const newInvoice = await billingService.create(invoiceData);
      await fetchInvoices(); // Recargar lista
      return { success: true, data: newInvoice };
    } catch (err) {
      setError(err.message || 'Error al crear comprobante');
      return { success: false, error: err.message };
    } finally {
      setLoading(false);
    }
  };

  /**
   * Actualizar estado del comprobante
   */
  const updateInvoiceStatus = async (id, status) => {
    setLoading(true);
    setError(null);

    try {
      const updatedInvoice = await billingService.updateStatus(id, status);
      await fetchInvoices(); // Recargar lista
      return { success: true, data: updatedInvoice };
    } catch (err) {
      setError(err.message || 'Error al actualizar estado');
      return { success: false, error: err.message };
    } finally {
      setLoading(false);
    }
  };

  /**
   * Enviar comprobante a SUNAT
   */
  const sendToSUNAT = async (id) => {
    setLoading(true);
    setError(null);

    try {
      const result = await billingService.sendToSUNAT(id);
      await fetchInvoices(); // Recargar lista
      return { success: true, data: result };
    } catch (err) {
      setError(err.message || 'Error al enviar a SUNAT');
      return { success: false, error: err.message };
    } finally {
      setLoading(false);
    }
  };

  /**
   * Anular comprobante
   */
  const voidInvoice = async (id, reason) => {
    setLoading(true);
    setError(null);

    try {
      const result = await billingService.void(id, reason);
      await fetchInvoices(); // Recargar lista
      return { success: true, data: result };
    } catch (err) {
      setError(err.message || 'Error al anular comprobante');
      return { success: false, error: err.message };
    } finally {
      setLoading(false);
    }
  };

  /**
   * Obtener XML UBL
   */
  const getUBL = async (id) => {
    setLoading(true);
    setError(null);

    try {
      const ubl = await billingService.getUBL(id);
      return { success: true, data: ubl };
    } catch (err) {
      setError(err.message || 'Error al obtener UBL');
      return { success: false, error: err.message };
    } finally {
      setLoading(false);
    }
  };

  /**
   * Obtener CDR de SUNAT
   */
  const getCDR = async (id) => {
    setLoading(true);
    setError(null);

    try {
      const cdr = await billingService.getCDR(id);
      return { success: true, data: cdr };
    } catch (err) {
      setError(err.message || 'Error al obtener CDR');
      return { success: false, error: err.message };
    } finally {
      setLoading(false);
    }
  };

  /**
   * Obtener estadísticas
   */
  const fetchStatistics = async (params = {}) => {
    setLoading(true);
    setError(null);

    try {
      const stats = await billingService.getStatistics(params);
      return { success: true, data: stats };
    } catch (err) {
      setError(err.message || 'Error al cargar estadísticas');
      return { success: false, error: err.message };
    } finally {
      setLoading(false);
    }
  };

  return {
    invoices,
    loading,
    error,
    pagination,
    fetchInvoices,
    fetchInvoiceById,
    createInvoice,
    updateInvoiceStatus,
    sendToSUNAT,
    voidInvoice,
    getUBL,
    getCDR,
    fetchStatistics,
  };
};
