/**
 * NotFoundPage Component
 * Página de error 404
 */
import { Link } from 'react-router-dom';
import './NotFoundPage.css';

const NotFoundPage = () => {
  return (
    <div className="not-found-page">
      <h1>404</h1>
      <p>Página no encontrada</p>
      <Link to="/dashboard" className="btn btn-primary">
        Volver al Dashboard
      </Link>
    </div>
  );
};

export default NotFoundPage;
