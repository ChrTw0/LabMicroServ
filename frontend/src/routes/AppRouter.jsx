/**
 * AppRouter
 * Configuración de rutas de la aplicación
 */
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { PrivateRoute } from './PrivateRoute';
import { useAuth } from '../hooks/useAuth';

// Pages (las crearemos después)
import LoginPage from '../pages/Login/LoginPage';
import DashboardPage from '../pages/Dashboard/DashboardPage';
import PatientsListPage from '../pages/Patients/PatientsListPage';
import PatientFormPage from '../pages/Patients/PatientFormPage';
import OrdersListPage from '../pages/Orders/OrdersListPage';
import OrderFormPage from '../pages/Orders/OrderFormPage';
import BillingListPage from '../pages/Billing/BillingListPage';
import NotFoundPage from '../pages/NotFound/NotFoundPage';

// Layout
import Layout from '../components/layout/Layout/Layout';

export const AppRouter = () => {
  const { isAuthenticated } = useAuth();

  return (
    <BrowserRouter>
      <Routes>
        {/* Ruta pública: Login */}
        <Route
          path="/login"
          element={isAuthenticated ? <Navigate to="/dashboard" replace /> : <LoginPage />}
        />

        {/* Rutas protegidas con Layout */}
        <Route
          path="/"
          element={
            <PrivateRoute>
              <Layout />
            </PrivateRoute>
          }
        >
          {/* Dashboard */}
          <Route index element={<Navigate to="/dashboard" replace />} />
          <Route path="dashboard" element={<DashboardPage />} />

          {/* Pacientes */}
          <Route path="patients" element={<PatientsListPage />} />
          <Route path="patients/new" element={<PatientFormPage />} />
          <Route path="patients/:id/edit" element={<PatientFormPage />} />

          {/* Órdenes */}
          <Route path="orders" element={<OrdersListPage />} />
          <Route path="orders/new" element={<OrderFormPage />} />
          <Route path="orders/:id/edit" element={<OrderFormPage />} />

          {/* Facturación */}
          <Route path="billing" element={<BillingListPage />} />

          {/* 404 */}
          <Route path="*" element={<NotFoundPage />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
};
