/**
 * API Configuration
 * Configuración centralizada para el API Gateway
 */

export const API_CONFIG = {
  // URL base del API Gateway
  BASE_URL: import.meta.env.VITE_API_URL || 'http://localhost:8000',

  // Timeout por defecto (30 segundos)
  TIMEOUT: 30000,

  // Headers por defecto
  HEADERS: {
    'Content-Type': 'application/json',
  },
};

// Endpoints organizados por servicio
export const ENDPOINTS = {
  // Authentication
  AUTH: {
    LOGIN: '/api/v1/auth/login',
    REGISTER: '/api/v1/auth/register',
    ME: '/api/v1/auth/me',
    CHANGE_PASSWORD: '/api/v1/auth/change-password',
    VERIFY_TOKEN: '/api/v1/auth/verify-token',
  },

  // Users
  USERS: {
    LIST: '/api/v1/users',
    BY_ID: (id) => `/api/v1/users/${id}`,
    ACTIVATE: (id) => `/api/v1/users/${id}/activate`,
    DEACTIVATE: (id) => `/api/v1/users/${id}/deactivate`,
  },

  // Patients
  PATIENTS: {
    LIST: '/api/v1/patients',
    BY_ID: (id) => `/api/v1/patients/${id}`,
    HISTORY: (id) => `/api/v1/patients/${id}/history`,
    NOTES: (id) => `/api/v1/patients/${id}/notes`,
  },

  // Orders
  ORDERS: {
    LIST: '/api/v1/orders',
    BY_ID: (id) => `/api/v1/orders/${id}`,
    BY_NUMBER: (orderNumber) => `/api/v1/orders/number/${orderNumber}`,
    STATUS: (id) => `/api/v1/orders/${id}/status`,
    PAYMENTS: (id) => `/api/v1/orders/${id}/payments`,
    STATISTICS: '/api/v1/orders/statistics',
  },

  // Services/Catalog
  SERVICES: {
    LIST: '/api/v1/services',
    BY_ID: (id) => `/api/v1/services/${id}`,
    PRICE: (id) => `/api/v1/services/${id}/price`,
    PRICE_HISTORY: (id) => `/api/v1/services/${id}/price-history`,
  },

  // Categories
  CATEGORIES: {
    LIST: '/api/v1/categories',
    BY_ID: (id) => `/api/v1/categories/${id}`,
  },

  // Billing/Invoices
  INVOICES: {
    LIST: '/api/v1/invoices',
    BY_ID: (id) => `/api/v1/invoices/${id}`,
    STATUS: (id) => `/api/v1/invoices/${id}/status`,
    UBL: (id) => `/api/v1/invoices/${id}/ubl`,
    CDR: (id) => `/api/v1/invoices/${id}/cdr`,
    STATISTICS: '/api/v1/invoices/statistics',
  },

  // Configuration
  CONFIGURATION: {
    LOCATIONS: '/api/v1/configuration/locations',
    LOCATION_BY_ID: (id) => `/api/v1/configuration/locations/${id}`,
    COMPANY: '/api/v1/configuration/company',
    COMPANY_BY_ID: (id) => `/api/v1/configuration/company/${id}`,
    SETTINGS: '/api/v1/configuration/settings',
    SETTING_BY_KEY: (key) => `/api/v1/configuration/settings/${key}`,
  },

  // Lab Sync
  LAB_SYNC: {
    LIST: '/api/v1/lab-sync',
    BY_ID: (id) => `/api/v1/lab-sync/${id}`,
    BY_ORDER: (orderId) => `/api/v1/lab-sync/order/${orderId}`,
    RETRY: (id) => `/api/v1/lab-sync/${id}/retry`,
    STATISTICS: '/api/v1/lab-sync/statistics',
  },

  // Profile
  PROFILE: {
    GET: '/api/v1/profile',
    UPDATE: '/api/v1/profile',
    CHANGE_PASSWORD: '/api/v1/profile/password',
  },

  // Reports
  REPORTS: {
    // Order Reports
    PAYMENT_METHODS: '/api/v1/orders/reports/by-payment-method',
    TOP_SERVICES: '/api/v1/orders/reports/top-services',
    MONTHLY_REVENUE: '/api/v1/orders/reports/monthly-revenue',
    PATIENT_TYPES: '/api/v1/orders/reports/patient-types',
    // Billing Reports
    SALES_BY_PERIOD: '/api/v1/invoices/reports/sales-by-period',
    INVOICE_TYPES: '/api/v1/invoices/reports/by-invoice-type',
  },

  // Reconciliation
  RECONCILIATION: {
    CLOSURES: '/api/v1/reconciliation/closures',
    CLOSURE_BY_ID: (id) => `/api/v1/reconciliation/closures/${id}`,
    CLOSE: (id) => `/api/v1/reconciliation/closures/${id}/close`,
    REOPEN: (id) => `/api/v1/reconciliation/closures/${id}/reopen`,
    STATISTICS: '/api/v1/reconciliation/closures/statistics',
    REPORT: '/api/v1/reconciliation/report',
    ADD_DISCREPANCY: (closureId) => `/api/v1/reconciliation/closures/${closureId}/discrepancies`,
    RESOLVE_DISCREPANCY: (discrepancyId) => `/api/v1/reconciliation/discrepancies/${discrepancyId}/resolve`,
  },
};
