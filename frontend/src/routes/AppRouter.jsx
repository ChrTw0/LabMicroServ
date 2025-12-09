/**
 * AppRouter
 * Configuración de rutas de la aplicación
 */
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { PrivateRoute } from './PrivateRoute';
import { useAuth } from '../hooks/useAuth';

// Pages
import LoginPage from '../pages/Login/LoginPage';
import DashboardPage from '../pages/Dashboard/DashboardPage';
import PatientsListPage from '../pages/Patients/PatientsListPage';
import PatientFormPage from '../pages/Patients/PatientFormPage';
import OrdersListPage from '../pages/Orders/OrdersListPage';
import PatientOrdersListPage from '../pages/Orders/PatientOrdersListPage';
import OrderFormPage from '../pages/Orders/OrderFormPage';
import OrderDetailPage from '../pages/Orders/OrderDetailPage';
import OrderGenerateInvoicePage from '../pages/Orders/OrderGenerateInvoicePage';
import CatalogoPage from '../pages/Catalog/CatalogoPage';
import CatalogoDetailPage from '../pages/Catalog/CatalogoDetailPage';
import CatalogoFormPage from '../pages/Catalog/CatalogoFormPage';
import CategoriesPage from '../pages/Catalog/CategoriesPage';
import PriceHistoryPage from '../pages/Catalog/PriceHistoryPage';
import BillingListPage from '../pages/Billing/BillingListPage';
import InvoiceDetailPage from '../pages/Billing/InvoiceDetailPage';
import InvoiceFormPage from '../pages/Billing/InvoiceFormPage';
import ReportsPage from '../pages/Reports/ReportsPage';
import ReconciliationPage from '../pages/Reconciliation/ReconciliationPage';
import { UsersListPage, UserFormPage, RolesListPage, RoleFormPage } from '../pages/Users';
import NotFoundPage from '../pages/NotFound/NotFoundPage';
import InicioPage from '../pages/Inicio/InicioPage';
import ProfilePage from '../pages/Profile/ProfilePage';

// Layout
import Layout from '../components/layout/Layout/Layout';

// Wrapper para la página de Órdenes
const OrdersPageWrapper = () => {
  const { hasRole } = useAuth();
  return hasRole('Paciente') ? <PatientOrdersListPage /> : <OrdersListPage />;
};

export const AppRouter = () => {
  const { isAuthenticated } = useAuth();

  return (
    <BrowserRouter>
      <Routes>
        <Route
          path="/"
          element={isAuthenticated ? <Navigate to="/dashboard" replace /> : <InicioPage />}
        />

        <Route
          path="/login"
          element={isAuthenticated ? <Navigate to="/dashboard" replace /> : <LoginPage />}
        />

        <Route
          path="/dashboard"
          element={
            <PrivateRoute>
              <Layout />
            </PrivateRoute>
          }
        >
          <Route path="" element={<DashboardPage />} />

          <Route path="profile" element={<ProfilePage />} />

          {/* Gestión de Usuarios y Roles (solo Administrador General) */}
          <Route path="usuarios" element={<PrivateRoute requiredRoles={['Administrador General']}><UsersListPage /></PrivateRoute>} />
          <Route path="usuarios/new" element={<PrivateRoute requiredRoles={['Administrador General']}><UserFormPage /></PrivateRoute>} />
          <Route path="usuarios/:id/edit" element={<PrivateRoute requiredRoles={['Administrador General']}><UserFormPage /></PrivateRoute>} />
          <Route path="roles" element={<PrivateRoute requiredRoles={['Administrador General']}><RolesListPage /></PrivateRoute>} />
          <Route path="roles/:id/edit" element={<PrivateRoute requiredRoles={['Administrador General']}><RoleFormPage /></PrivateRoute>} />

          {/* Catálogo de Servicios */}
          <Route path="catalog" element={<CatalogoPage />} /> {/* Vista principal del catálogo (mosaico/tabla) */}
          <Route path="catalog/new" element={<PrivateRoute requiredPermissions={['catalog:write']}><CatalogoFormPage /></PrivateRoute>} />
          <Route path="catalog/:id" element={<CatalogoDetailPage />} /> {/* Vista de detalle del servicio */}
          <Route path="catalog/:id/edit" element={<PrivateRoute requiredPermissions={['catalog:write']}><CatalogoFormPage /></PrivateRoute>} />
          <Route path="catalog/:id/price-history" element={<PriceHistoryPage />} />
          <Route path="catalog/categories" element={<PrivateRoute requiredPermissions={['catalog:write']}><CategoriesPage /></PrivateRoute>} />

          {/* Gestión de Pacientes (permisos de lectura/escritura) */}
          <Route path="patients" element={<PrivateRoute requiredPermissions={['patients:read']}><PatientsListPage /></PrivateRoute>} />
          <Route path="patients/new" element={<PrivateRoute requiredPermissions={['patients:write']}><PatientFormPage /></PrivateRoute>} />
          <Route path="patients/:id/edit" element={<PrivateRoute requiredPermissions={['patients:write']}><PatientFormPage /></PrivateRoute>} />

          {/* Gestión de Órdenes (permisos de lectura/escritura) */}
          <Route path="orders" element={<PrivateRoute requiredPermissions={['orders:read']}><OrdersPageWrapper /></PrivateRoute>} />
          <Route path="orders/new" element={<PrivateRoute requiredPermissions={['orders:write']}><OrderFormPage /></PrivateRoute>} />
          <Route path="orders/:id" element={<PrivateRoute requiredPermissions={['orders:read']}><OrderDetailPage /></PrivateRoute>} />
          <Route path="orders/:id/edit" element={<PrivateRoute requiredPermissions={['orders:write']}><OrderFormPage /></PrivateRoute>} />
          <Route path="orders/:id/generate-invoice" element={<PrivateRoute requiredPermissions={['billing:write']}><OrderGenerateInvoicePage /></PrivateRoute>} />

          {/* Facturación (permisos de lectura/escritura) */}
          <Route path="billing" element={<PrivateRoute requiredPermissions={['billing:read']}><BillingListPage /></PrivateRoute>} />
          <Route path="billing/new" element={<PrivateRoute requiredPermissions={['billing:write']}><InvoiceFormPage /></PrivateRoute>} />
          <Route path="billing/:id" element={<PrivateRoute requiredPermissions={['billing:read']}><InvoiceDetailPage /></PrivateRoute>} />

          {/* Reportes (permisos de lectura) */}
          <Route path="reports" element={<PrivateRoute requiredPermissions={['reports:read']}><ReportsPage /></PrivateRoute>} />

          {/* Conciliación (roles específicos) */}
          <Route path="reconciliation" element={<PrivateRoute requiredRoles={['Contador', 'Administrador General']}><ReconciliationPage /></PrivateRoute>} />

          {/* 404 */}
          <Route path="*" element={<NotFoundPage />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
};
