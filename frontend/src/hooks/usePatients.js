/**
 * usePatients Hook
 * Hook personalizado para gestión de pacientes
 */
import { useState, useEffect } from 'react';
import { patientService } from '../services';

export const usePatients = () => {
  const [patients, setPatients] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [pagination, setPagination] = useState({
    total: 0,
    page: 1,
    page_size: 50,
  });

  /**
   * Cargar lista de pacientes
   */
  const fetchPatients = async (params = {}) => {
    setLoading(true);
    setError(null);

    try {
      // Por defecto, solo traer pacientes activos (no eliminados)
      const queryParams = {
        is_active: true,
        ...params,
      };

      const data = await patientService.getAll(queryParams);
      setPatients(data.patients || []);
      setPagination({
        total: data.total || 0,
        page: data.page || 1,
        page_size: data.page_size || 50,
      });
    } catch (err) {
      setError(err.message || 'Error al cargar pacientes');
      console.error('Error fetching patients:', err);
    } finally {
      setLoading(false);
    }
  };

  /**
   * Crear nuevo paciente
   */
  const createPatient = async (patientData) => {
    setLoading(true);
    setError(null);

    try {
      const newPatient = await patientService.create(patientData);
      await fetchPatients(); // Recargar lista
      return { success: true, data: newPatient };
    } catch (err) {
      setError(err.message || 'Error al crear paciente');
      return { success: false, error: err.message };
    } finally {
      setLoading(false);
    }
  };

  /**
   * Actualizar paciente
   */
  const updatePatient = async (id, patientData) => {
    setLoading(true);
    setError(null);

    try {
      const updatedPatient = await patientService.update(id, patientData);
      await fetchPatients(); // Recargar lista
      return { success: true, data: updatedPatient };
    } catch (err) {
      setError(err.message || 'Error al actualizar paciente');
      return { success: false, error: err.message };
    } finally {
      setLoading(false);
    }
  };

  /**
   * Eliminar paciente
   */
  const deletePatient = async (id) => {
    setLoading(true);
    setError(null);

    try {
      await patientService.delete(id);
      await fetchPatients(); // Recargar lista
      return { success: true };
    } catch (err) {
      setError(err.message || 'Error al eliminar paciente');
      return { success: false, error: err.message };
    } finally {
      setLoading(false);
    }
  };

  return {
    patients,
    loading,
    error,
    pagination,
    fetchPatients,
    createPatient,
    updatePatient,
    deletePatient,
  };
};
