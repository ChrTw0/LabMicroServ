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
import PatientOrdersListPage from '../pages/Orders/PatientOrdersListPage'; // Importar la nueva página
import OrderFormPage from '../pages/Orders/OrderFormPage';
import OrderDetailPage from '../pages/Orders/OrderDetailPage';
import CatalogoPage from '../pages/Catalog/CatalogoPage';
import OrderGenerateInvoicePage from '../pages/Orders/OrderGenerateInvoicePage'; // <-- 1. Importar la nueva página
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
  // Si el usuario es un paciente, muestra su listado de órdenes.
  // De lo contrario, muestra la gestión de órdenes para otros roles.
  return hasRole('Paciente') ? <PatientOrdersListPage /> : <OrdersListPage />;
};

export const AppRouter = () => {
  const { isAuthenticated } = useAuth();

  return (
    <BrowserRouter>
      <Routes>
        {/* Ruta pública: Catálogo (página de inicio) */}
        <Route
          path="/"
          element={isAuthenticated ? <Navigate to="/dashboard" replace /> : <InicioPage />}
        />

        {/* Ruta pública: Login */}
        <Route
          path="/login"
          element={isAuthenticated ? <Navigate to="/dashboard" replace /> : <LoginPage />}
        />

        {/* Rutas protegidas con Layout */}
        <Route
          path="/dashboard" // Cambiamos el path base para que no entre en conflicto con la raíz pública
          element={
            <PrivateRoute>
              <Layout />
            </PrivateRoute>
          }
        >
          {/* Dashboard */}
          {/* <Route index element={<DashboardPage />} /> */}
          <Route path="" element={<DashboardPage />} />

          {/* Profile */}
          <Route path="profile" element={<ProfilePage />} />

          {/* User Management */}
          <Route path="usuarios" element={<PrivateRoute requiredRoles={['Administrador General']}><UsersListPage /></PrivateRoute>} />
          <Route path="usuarios/new" element={<PrivateRoute requiredRoles={['Administrador General']}><UserFormPage /></PrivateRoute>} />
          <Route path="usuarios/:id/edit" element={<PrivateRoute requiredRoles={['Administrador General']}><UserFormPage /></PrivateRoute>} />
          <Route path="roles" element={<PrivateRoute requiredRoles={['Administrador General']}><RolesListPage /></PrivateRoute>} />
          <Route path="roles/:id/edit" element={<PrivateRoute requiredRoles={['Administrador General']}><RoleFormPage /></PrivateRoute>} />

          {/* Catálogo de Servicios */}
          <Route path="catalog" element={<CatalogoPage />} />
          <Route path="catalog/new" element={<PrivateRoute requiredPermissions={['catalog:write']}><CatalogoFormPage /></PrivateRoute>} />
          <Route path="catalog/:id/edit" element={<PrivateRoute requiredPermissions={['catalog:write']}><CatalogoFormPage /></PrivateRoute>} />
          <Route path="catalog/:id/price-history" element={<PriceHistoryPage />} />
          <Route path="catalog/categories" element={<PrivateRoute requiredPermissions={['catalog:write']}><CategoriesPage /></PrivateRoute>} />

          {/* Pacientes */}
          <Route path="patients" element={<PrivateRoute requiredPermissions={['patients:read']}><PatientsListPage /></PrivateRoute>} />
          <Route path="patients/new" element={<PrivateRoute requiredPermissions={['patients:write']}><PatientFormPage /></PrivateRoute>} />
          <Route path="patients/:id/edit" element={<PrivateRoute requiredPermissions={['patients:write']}><PatientFormPage /></PrivateRoute>} />

          {/* Órdenes */}
          <Route path="orders" element={<OrdersPageWrapper />} />
          <Route path="orders/new" element={<OrderFormPage />} />
          <Route path="orders/:id" element={<OrderDetailPage />} />
          <Route path="orders/:id/edit" element={<OrderFormPage />} />
          <Route path="orders/:id/generate-invoice" element={<OrderGenerateInvoicePage />} />

          {/* Facturación */}
          <Route path="billing" element={<PrivateRoute requiredPermissions={['billing:read']}><BillingListPage /></PrivateRoute>} />
          <Route path="billing/new" element={<PrivateRoute requiredPermissions={['billing:write']}><InvoiceFormPage /></PrivateRoute>} />
          <Route path="billing/:id" element={<PrivateRoute requiredPermissions={['billing:read']}><InvoiceDetailPage /></PrivateRoute>} />

          {/* Reportes - RF-074 a RF-082 */}
          <Route path="reports" element={<ReportsPage />} />

          {/* Conciliación - RF-056 a RF-064 */}
          <Route path="reconciliation" element={<PrivateRoute requiredRoles={['Contador', 'Supervisor de Sede', 'Administrador General']}><ReconciliationPage /></PrivateRoute>} />

          {/* 404 */}
          <Route path="*" element={<NotFoundPage />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
};
