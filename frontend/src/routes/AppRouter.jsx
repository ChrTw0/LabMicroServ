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
import BillingListPage from '../pages/Billing/BillingListPage';
import NotFoundPage from '../pages/NotFound/NotFoundPage';
import InicioPage from '../pages/Inicio/InicioPage';

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
          <Route index element={<DashboardPage />} />
          {/* <Route path="dashboard" element={<DashboardPage />} /> */}


          {/* Catálogo */}
          {/* <Route path="servicios" element={<CatalogoPage />}/> */}

          {/* Pacientes */}
          {/* TODO: Proteger estas rutas con `hasPermission` */}
          <Route path="patients" element={<PatientsListPage />} />
          <Route path="patients/new" element={<PatientFormPage />} />
          <Route path="patients/:id/edit" element={<PatientFormPage />} />

          {/* Órdenes */}
          <Route path="orders" element={<OrdersPageWrapper />} />
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
