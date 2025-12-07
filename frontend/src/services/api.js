/**
 * Axios Instance Configuration
 * Instancia de axios configurada con interceptors para JWT y manejo de errores
 */
import axios from 'axios';
import { API_CONFIG } from '../config/api.config';

// Crear instancia de axios
const api = axios.create({
  baseURL: API_CONFIG.BASE_URL,
  timeout: API_CONFIG.TIMEOUT,
  headers: API_CONFIG.HEADERS,
});

// Request Interceptor: Añadir JWT token a todas las peticiones
api.interceptors.request.use(
  (config) => {
    // Obtener token del localStorage
    const token = localStorage.getItem('access_token');

    // Si existe token, añadirlo al header Authorization
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }

    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response Interceptor: Manejar errores globalmente
api.interceptors.response.use(
  (response) => {
    // Si la respuesta es exitosa, retornarla tal cual
    return response;
  },
  (error) => {
    // Manejo de errores
    if (error.response) {
      // El servidor respondió con un código de error
      const { status, data } = error.response;

      switch (status) {
        case 401:
          // Token inválido o expirado - Logout automático
          console.error('Sesión expirada. Por favor, inicia sesión nuevamente.');
          localStorage.removeItem('access_token');
          localStorage.removeItem('user');
          // Redirigir a login (se manejará en AuthContext)
          window.location.href = '/login';
          break;

        case 403:
          // Sin permisos
          console.error('No tienes permisos para realizar esta acción.');
          break;

        case 404:
          // Recurso no encontrado
          console.error('Recurso no encontrado.');
          break;

        case 422:
          // Error de validación
          console.error('Error de validación:', data.detail);
          // Si detail es un array, extraer los mensajes
          if (Array.isArray(data.detail)) {
            const errorMessages = data.detail.map(err => err.msg || JSON.stringify(err)).join(', ');
            console.error('Detalles:', errorMessages);
          }
          break;

        case 500:
          // Error interno del servidor
          console.error('Error interno del servidor. Intenta nuevamente más tarde.');
          break;

        default:
          console.error('Error en la petición:', data.detail || 'Error desconocido');
      }

      // Retornar error con formato consistente
      return Promise.reject({
        status,
        message: data.detail || 'Error en la petición',
        errors: data.errors || null,
      });
    } else if (error.request) {
      // La petición se hizo pero no hubo respuesta
      console.error('No hay respuesta del servidor. Verifica tu conexión.');
      return Promise.reject({
        status: 0,
        message: 'No hay respuesta del servidor',
      });
    } else {
      // Error al configurar la petición
      console.error('Error al realizar la petición:', error.message);
      return Promise.reject({
        status: -1,
        message: error.message,
      });
    }
  }
);

export default api;
