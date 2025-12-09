/**
 * useOrders Hook
 * Hook personalizado para gestión de órdenes
 */
import { useState, useEffect } from 'react';
import { orderService, catalogService } from '../services';

export const useOrders = () => {
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [pagination, setPagination] = useState({
    total: 0,
    page: 1,
    page_size: 50,
  });

  /**
   * Cargar lista de órdenes
   */
  const fetchOrders = async (params = {}) => {
    setLoading(true);
    setError(null);

    try {
      const data = await orderService.getAll(params);
      setOrders(data.orders || []);
      setPagination({
        total: data.total || 0,
        page: data.page || 1,
        page_size: data.page_size || 50,
      });
    } catch (err) {
      setError(err.message || 'Error al cargar órdenes');
      console.error('Error fetching orders:', err);
    } finally {
      setLoading(false);
    }
  };

  /**
   * Obtener orden por ID
   */
  const fetchOrderById = async (id) => {
    setLoading(true);
    setError(null);

    try {
      const order = await orderService.getById(id);
      return { success: true, data: order };
    } catch (err) {
      setError(err.message || 'Error al cargar orden');
      return { success: false, error: err.message };
    } finally {
      setLoading(false);
    }
  };

  /**
   * Crear nueva orden
   */
  const createOrder = async (orderData) => {
    setLoading(true);
    setError(null);

    try {
      const newOrder = await orderService.create(orderData);
      await fetchOrders(); // Recargar lista
      return { success: true, data: newOrder };
    } catch (err) {
      setError(err.message || 'Error al crear orden');
      return { success: false, error: err.message };
    } finally {
      setLoading(false);
    }
  };

  /**
   * Actualizar orden
   */
  const updateOrder = async (id, orderData) => {
    setLoading(true);
    setError(null);

    try {
      const updatedOrder = await orderService.update(id, orderData);
      await fetchOrders(); // Recargar lista
      return { success: true, data: updatedOrder };
    } catch (err) {
      setError(err.message || 'Error al actualizar orden');
      return { success: false, error: err.message };
    } finally {
      setLoading(false);
    }
  };

  /**
   * Actualizar estado de orden
   */
  const updateOrderStatus = async (id, status) => {
    setLoading(true);
    setError(null);

    try {
      const updatedOrder = await orderService.updateStatus(id, status);
      await fetchOrders(); // Recargar lista
      return { success: true, data: updatedOrder };
    } catch (err) {
      setError(err.message || 'Error al actualizar estado');
      return { success: false, error: err.message };
    } finally {
      setLoading(false);
    }
  };

  /**
   * Agregar pagos a orden
   */
  const addPayments = async (id, payments) => {
    setLoading(true);
    setError(null);

    try {
      const updatedOrder = await orderService.addPayments(id, payments);
      return { success: true, data: updatedOrder };
    } catch (err) {
      setError(err.message || 'Error al agregar pago');
      return { success: false, error: err.message };
    } finally {
      setLoading(false);
    }
  };

  /**
   * Anular orden
   */
  const cancelOrder = async (id) => {
    setLoading(true);
    setError(null);

    try {
      await orderService.cancel(id);
      await fetchOrders(); // Recargar lista
      return { success: true };
    } catch (err) {
      setError(err.message || 'Error al anular orden');
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
      const stats = await orderService.getStatistics(params);
      return { success: true, data: stats };
    } catch (err) {
      setError(err.message || 'Error al cargar estadísticas');
      return { success: false, error: err.message };
    } finally {
      setLoading(false);
    }
  };

  return {
    orders,
    loading,
    error,
    pagination,
    fetchOrders,
    fetchOrderById,
    createOrder,
    updateOrder,
    updateOrderStatus,
    addPayments,
    cancelOrder,
    fetchStatistics,
  };
};

/**
 * useCatalog Hook
 * Hook para gestión del catálogo de servicios
 */
export const useCatalog = () => {
  const [services, setServices] = useState([]);
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  /**
   * Cargar servicios del catálogo
   */
  const fetchServices = async (params = {}) => {
    setLoading(true);
    setError(null);

    try {
      // Por defecto, solo servicios activos
      const queryParams = {
        is_active: true,
        ...params,
      };

      const data = await catalogService.getAllServices(queryParams);
      setServices(data.services || []);
    } catch (err) {
      setError(err.message || 'Error al cargar servicios');
      console.error('Error fetching services:', err);
    } finally {
      setLoading(false);
    }
  };

  /**
   * Cargar categorías
   */
  const fetchCategories = async () => {
    setLoading(true);
    setError(null);

    try {
      const data = await catalogService.getAllCategories();
      setCategories(data.categories || []);
    } catch (err) {
      setError(err.message || 'Error al cargar categorías');
      console.error('Error fetching categories:', err);
    } finally {
      setLoading(false);
    }
  };

  return {
    services,
    categories,
    loading,
    error,
    fetchServices,
    fetchCategories,
  };
};
