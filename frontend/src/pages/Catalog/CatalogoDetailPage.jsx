/**
 * CatalogoDetailPage Component
 * Muestra los detalles de un servicio en modo de solo lectura
 */
import { useEffect, useState } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { catalogService } from '../../services';
import './CatalogoDetailPage.css';

const CatalogoDetailPage = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [service, setService] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadService();
  }, [id]);

  const loadService = async () => {
    setLoading(true);
    try {
      const serviceData = await catalogService.getServiceById(id);
      setService(serviceData);
    } catch (err) {
      setError('Error al cargar los datos del servicio');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const formatCurrency = (amount) => {
    return `S/ ${parseFloat(amount).toFixed(2)}`;
  };

  if (loading) {
    return <div className="loading-container"><p>Cargando servicio...</p></div>;
  }

  if (error) {
    return <div className="error-container">{error}</div>;
  }

  if (!service) {
    return <div className="error-container">Servicio no encontrado</div>;
  }

  return (
    <div className="catalogo-detail-page">
      <div className="page-header">
        <h1>{service.name}</h1>
        <Link to="/dashboard/catalog" className="btn btn-outline">
          ← Volver al Catálogo
        </Link>
      </div>
      <div className="detail-card">
        <div className="detail-section">
          <h3>Información General</h3>
          <div className="detail-row">
            <span className="detail-label">Código:</span>
            <span className="detail-value">{service.code}</span>
          </div>
          <div className="detail-row">
            <span className="detail-label">Categoría:</span>
            <span className="detail-value">{service.category_name}</span>
          </div>
          <div className="detail-row">
            <span className="detail-label">Precio Actual:</span>
            <span className="detail-value price">{formatCurrency(service.current_price)}</span>
          </div>
          <div className="detail-row">
            <span className="detail-label">Estado:</span>
            <span className={`badge ${service.is_active ? 'badge-success' : 'badge-secondary'}`}>
              {service.is_active ? 'Activo' : 'Inactivo'}
            </span>
          </div>
        </div>
        {service.description && (
          <div className="detail-section">
            <h3>Descripción</h3>
            <p>{service.description}</p>
          </div>
        )}
        <div className="detail-actions">
            <button
                onClick={() => navigate(`/dashboard/catalog/${service.id}/price-history`)}
                className="btn btn-secondary"
            >
                Ver Historial de Precios
            </button>
            <button
                onClick={() => navigate(`/dashboard/catalog/${service.id}/edit`)}
                className="btn btn-primary"
            >
                Editar Servicio
            </button>
        </div>
      </div>
    </div>
  );
};

export default CatalogoDetailPage;
