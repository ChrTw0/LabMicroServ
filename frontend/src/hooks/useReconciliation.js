/**
 * useReconciliation Hook
 * Hook personalizado para manejar conciliación y cierre de caja
 */
import { useState } from 'react';
import { reconciliationService } from '../services';

export const useReconciliation = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [closures, setClosures] = useState([]);
  const [currentClosure, setCurrentClosure] = useState(null);
  const [statistics, setStatistics] = useState(null);
  const [reconciliationReport, setReconciliationReport] = useState(null);
  const [pagination, setPagination] = useState({
    page: 1,
    page_size: 10,
    total: 0,
    pages: 0,
  });

  /**
   * Obtener lista de cierres diarios - RF-062
   */
  const fetchClosures = async (params = {}) => {
    try {
      setLoading(true);
      setError(null);
      const data = await reconciliationService.getAllClosures(params);

      // Asegurarse de que closures siempre sea un array
      if (Array.isArray(data)) {
        setClosures(data);
      } else if (data.closures && Array.isArray(data.closures)) {
        // El backend devuelve: { total, page, page_size, closures: [...] }
        setClosures(data.closures);
        setPagination({
          page: data.page,
          page_size: data.page_size,
          total: data.total,
          pages: Math.ceil(data.total / data.page_size)
        });
      } else if (data.items && Array.isArray(data.items)) {
        // Fallback para otros formatos
        setClosures(data.items);
        if (data.pagination) {
          setPagination(data.pagination);
        }
      } else {
        console.warn('Unexpected response format for closures:', data);
        setClosures([]);
      }
      return { success: true, data };
    } catch (err) {
      // Mejorar el manejo de errores de validación
      let errorMessage = 'Error al cargar cierres';
      if (err.message) {
        errorMessage = err.message;
      } else if (err.errors) {
        errorMessage = JSON.stringify(err.errors);
      }
      setError(errorMessage);
      setClosures([]); // Asegurar que closures sea un array vacío en caso de error
      console.error('Error fetching closures:', err);
      return { success: false, error: errorMessage };
    } finally {
      setLoading(false);
    }
  };

  /**
   * Obtener cierre por ID con discrepancias
   */
  const fetchClosureById = async (id) => {
    try {
      setLoading(true);
      setError(null);
      const data = await reconciliationService.getClosureById(id);
      setCurrentClosure(data);
      return { success: true, data };
    } catch (err) {
      const errorMessage = err.message || 'Error al cargar cierre';
      setError(errorMessage);
      console.error('Error fetching closure:', err);
      return { success: false, error: errorMessage };
    } finally {
      setLoading(false);
    }
  };

  /**
   * Crear cierre diario y ejecutar conciliación - RF-056, RF-057, RF-058
   */
  const createDailyClosure = async (closureData) => {
    try {
      setLoading(true);
      setError(null);
      const data = await reconciliationService.createDailyClosure(closureData);
      setCurrentClosure(data);
      // Actualizar la lista de cierres
      setClosures((prev) => [data, ...prev]);
      return { success: true, data };
    } catch (err) {
      const errorMessage = err.message || 'Error al crear cierre';
      setError(errorMessage);
      console.error('Error creating closure:', err);
      return { success: false, error: errorMessage };
    } finally {
      setLoading(false);
    }
  };

  /**
   * Cerrar cierre diario (cambiar estado a CLOSED)
   */
  const closeDailyClosure = async (id) => {
    try {
      setLoading(true);
      setError(null);
      const data = await reconciliationService.closeDailyClosure(id);
      setCurrentClosure(data);
      // Actualizar la lista de cierres
      setClosures((prev) =>
        prev.map((closure) => (closure.id === id ? data : closure))
      );
      return { success: true, data };
    } catch (err) {
      const errorMessage = err.message || 'Error al cerrar cierre';
      setError(errorMessage);
      console.error('Error closing closure:', err);
      return { success: false, error: errorMessage };
    } finally {
      setLoading(false);
    }
  };

  /**
   * Reabrir cierre cerrado - RF-063 (solo admin)
   */
  const reopenClosure = async (id, reason) => {
    try {
      setLoading(true);
      setError(null);
      const data = await reconciliationService.reopenClosure(id, reason);
      setCurrentClosure(data);
      // Actualizar la lista de cierres
      setClosures((prev) =>
        prev.map((closure) => (closure.id === id ? data : closure))
      );
      return { success: true, data };
    } catch (err) {
      const errorMessage = err.message || 'Error al reabrir cierre';
      setError(errorMessage);
      console.error('Error reopening closure:', err);
      return { success: false, error: errorMessage };
    } finally {
      setLoading(false);
    }
  };

  /**
   * Obtener estadísticas de cierres
   */
  const fetchStatistics = async (params = {}) => {
    try {
      setLoading(true);
      setError(null);
      const data = await reconciliationService.getStatistics(params);
      setStatistics(data);
      return { success: true, data };
    } catch (err) {
      const errorMessage = err.message || 'Error al cargar estadísticas';
      setError(errorMessage);
      console.error('Error fetching statistics:', err);
      return { success: false, error: errorMessage };
    } finally {
      setLoading(false);
    }
  };

  /**
   * Generar reporte completo de conciliación - RF-057, RF-059
   */
  const fetchReconciliationReport = async (params = {}) => {
    try {
      setLoading(true);
      setError(null);
      const data = await reconciliationService.getReconciliationReport(params);
      setReconciliationReport(data);
      return { success: true, data };
    } catch (err) {
      const errorMessage = err.message || 'Error al generar reporte de conciliación';
      setError(errorMessage);
      console.error('Error fetching reconciliation report:', err);
      return { success: false, error: errorMessage };
    } finally {
      setLoading(false);
    }
  };

  /**
   * Agregar discrepancia manual a un cierre
   */
  const addDiscrepancy = async (closureId, description) => {
    try {
      setLoading(true);
      setError(null);
      const data = await reconciliationService.addDiscrepancy(closureId, description);
      // Actualizar el cierre actual si es el mismo
      if (currentClosure && currentClosure.id === closureId) {
        setCurrentClosure((prev) => ({
          ...prev,
          discrepancies: [...(prev.discrepancies || []), data],
        }));
      }
      return { success: true, data };
    } catch (err) {
      const errorMessage = err.message || 'Error al agregar discrepancia';
      setError(errorMessage);
      console.error('Error adding discrepancy:', err);
      return { success: false, error: errorMessage };
    } finally {
      setLoading(false);
    }
  };

  /**
   * Marcar discrepancia como resuelta
   */
  const resolveDiscrepancy = async (discrepancyId) => {
    try {
      setLoading(true);
      setError(null);
      const data = await reconciliationService.resolveDiscrepancy(discrepancyId);
      // Actualizar el cierre actual
      if (currentClosure && currentClosure.discrepancies) {
        setCurrentClosure((prev) => ({
          ...prev,
          discrepancies: prev.discrepancies.map((disc) =>
            disc.id === discrepancyId ? data : disc
          ),
        }));
      }
      return { success: true, data };
    } catch (err) {
      const errorMessage = err.message || 'Error al resolver discrepancia';
      setError(errorMessage);
      console.error('Error resolving discrepancy:', err);
      return { success: false, error: errorMessage };
    } finally {
      setLoading(false);
    }
  };

  return {
    // State
    loading,
    error,
    closures,
    currentClosure,
    statistics,
    reconciliationReport,
    pagination,

    // Actions
    fetchClosures,
    fetchClosureById,
    createDailyClosure,
    closeDailyClosure,
    reopenClosure,
    fetchStatistics,
    fetchReconciliationReport,
    addDiscrepancy,
    resolveDiscrepancy,
  };
};
