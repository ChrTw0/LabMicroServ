/**
 * Patient Service
 * Servicios relacionados con pacientes
 */
import api from './api';
import { ENDPOINTS } from '../config/api.config';

const patientService = {
  /**
   * Obtener lista de pacientes
   * @param {Object} params - Parámetros de búsqueda (page, page_size, search, etc.)
   * @returns {Promise} - Lista de pacientes
   */
  async getAll(params = {}) {
    const response = await api.get(ENDPOINTS.PATIENTS.LIST, { params });
    return response.data;
  },

  /**
   * Obtener paciente por ID
   * @param {number} id - ID del paciente
   * @returns {Promise} - Datos del paciente
   */
  async getById(id) {
    const response = await api.get(ENDPOINTS.PATIENTS.BY_ID(id));
    return response.data;
  },

  /**
   * Crear nuevo paciente
   * @param {Object} patientData - Datos del paciente
   * @returns {Promise} - Paciente creado
   */
  async create(patientData) {
    const response = await api.post(ENDPOINTS.PATIENTS.LIST, patientData);
    return response.data;
  },

  /**
   * Actualizar paciente
   * @param {number} id - ID del paciente
   * @param {Object} patientData - Datos actualizados
   * @returns {Promise} - Paciente actualizado
   */
  async update(id, patientData) {
    const response = await api.put(ENDPOINTS.PATIENTS.BY_ID(id), patientData);
    return response.data;
  },

  /**
   * Eliminar paciente (soft delete)
   * @param {number} id - ID del paciente
   * @returns {Promise}
   */
  async delete(id) {
    const response = await api.delete(ENDPOINTS.PATIENTS.BY_ID(id));
    return response.data;
  },

  /**
   * Obtener historial de cambios del paciente
   * @param {number} id - ID del paciente
   * @returns {Promise} - Historial de cambios
   */
  async getHistory(id) {
    const response = await api.get(ENDPOINTS.PATIENTS.HISTORY(id));
    return response.data;
  },

  /**
   * Obtener notas del paciente
   * @param {number} id - ID del paciente
   * @returns {Promise} - Notas del paciente
   */
  async getNotes(id) {
    const response = await api.get(ENDPOINTS.PATIENTS.NOTES(id));
    return response.data;
  },

  /**
   * Agregar nota al paciente
   * @param {number} id - ID del paciente
   * @param {Object} noteData - Datos de la nota
   * @returns {Promise} - Nota creada
   */
  async addNote(id, noteData) {
    const response = await api.post(ENDPOINTS.PATIENTS.NOTES(id), noteData);
    return response.data;
  },
};

export default patientService;
