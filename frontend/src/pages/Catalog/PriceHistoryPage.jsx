/**
 * PriceHistoryPage Component
 * Vista del historial de cambios de precio de un servicio
 */
import { useEffect, useState } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { catalogService } from '../../services';
import './PriceHistoryPage.css';

const PriceHistoryPage = () => {
  const { id } = useParams();
  const navigate = useNavigate();

  const [service, setService] = useState(null);
  const [priceHistory, setPriceHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadData();
  }, [id]);

  const loadData = async () => {
    setLoading(true);
    setError(null);

    try {
      // Cargar servicio y su historial de precios
      const [serviceData, historyData] = await Promise.all([
        catalogService.getServiceById(id),
        catalogService.getPriceHistory(id),
      ]);

      setService(serviceData);
      setPriceHistory(historyData.price_history || []);
    } catch (err) {
      setError(err.message || 'Error al cargar el historial');
      console.error('Error loading price history:', err);
    } finally {
      setLoading(false);
    }
  };

  const formatCurrency = (amount) => {
    return `S/ ${parseFloat(amount).toFixed(2)}`;
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('es-PE', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const calculateChange = (newPrice, oldPrice) => {
    const change = parseFloat(newPrice) - parseFloat(oldPrice);
    const percentage = ((change / parseFloat(oldPrice)) * 100).toFixed(2);
    return { change, percentage };
  };

  const getPriceChangeClass = (change) => {
    if (change > 0) return 'price-increase';
    if (change < 0) return 'price-decrease';
    return '';
  };

  if (loading) {
    return (
      <div className="loading-container">
        <p>Cargando historial de precios...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="error-container">
        <div className="alert alert-error">
          {error}
        </div>
        <Link to="/dashboard/catalog" className="btn btn-primary">
          Volver al Catálogo
        </Link>
      </div>
    );
  }

  if (!service) {
    return (
      <div className="error-container">
        <p>Servicio no encontrado</p>
        <Link to="/dashboard/catalog" className="btn btn-primary">
          Volver al Catálogo
        </Link>
      </div>
    );
  }

  return (
    <div className="price-history-page">
      <div className="page-header">
        <div>
          <Link to="/dashboard/catalog" className="btn-back">← Volver al Catálogo</Link>
          <h1>Historial de Precios</h1>
        </div>
        <button
          onClick={() => navigate(`/dashboard/catalog/${id}/edit`)}
          className="btn btn-primary"
        >
          Editar Servicio
        </button>
      </div>

      {/* Información del Servicio */}
      <div className="service-info-card">
        <div className="service-header">
          <div>
            <h2>{service.name}</h2>
            <p className="service-code">{service.code}</p>
          </div>
          <div className="current-price">
            <span className="price-label">Precio Actual:</span>
            <span className="price-value">
              {formatCurrency(service.current_price || service.price)}
            </span>
          </div>
        </div>
        {service.description && (
          <p className="service-description">{service.description}</p>
        )}
      </div>

      {/* Historial de Cambios */}
      <div className="history-card">
        <h2>Historial de Cambios de Precio</h2>

        {priceHistory.length === 0 ? (
          <div className="empty-state">
            <p>No hay cambios de precio registrados para este servicio.</p>
            <p className="text-muted">
              El precio actual es el precio original del servicio.
            </p>
          </div>
        ) : (
          <div className="timeline">
            {priceHistory.map((record, index) => {
              const previousPrice = index < priceHistory.length - 1
                ? priceHistory[index + 1].new_price
                : record.old_price;

              const { change, percentage } = calculateChange(
                record.new_price,
                previousPrice
              );

              return (
                <div key={record.id} className="timeline-item">
                  <div className="timeline-marker">
                    <span className="timeline-dot"></span>
                    {index < priceHistory.length - 1 && (
                      <span className="timeline-line"></span>
                    )}
                  </div>
                  <div className="timeline-content">
                    <div className="timeline-header">
                      <span className="timeline-date">
                        {formatDate(record.changed_at)}
                      </span>
                    </div>
                    <div className="price-change-box">
                      <div className="price-row">
                        <span className="price-label-small">Precio anterior:</span>
                        <span className="price-old">
                          {formatCurrency(previousPrice)}
                        </span>
                      </div>
                      <div className="price-arrow">→</div>
                      <div className="price-row">
                        <span className="price-label-small">Precio nuevo:</span>
                        <span className={`price-new ${getPriceChangeClass(change)}`}>
                          {formatCurrency(record.new_price)}
                        </span>
                      </div>
                    </div>
                    <div className="price-change-info">
                      <span className={`change-badge ${getPriceChangeClass(change)}`}>
                        {change > 0 ? '+' : ''}{formatCurrency(change)}
                        {' '}
                        ({change > 0 ? '+' : ''}{percentage}%)
                      </span>
                    </div>
                  </div>
                </div>
              );
            })}

            {/* Precio Inicial */}
            <div className="timeline-item timeline-item-initial">
              <div className="timeline-marker">
                <span className="timeline-dot-initial"></span>
              </div>
              <div className="timeline-content">
                <div className="timeline-header">
                  <span className="timeline-date">Precio Inicial</span>
                </div>
                <div className="price-initial">
                  {formatCurrency(
                    priceHistory.length > 0
                      ? priceHistory[priceHistory.length - 1].old_price
                      : service.current_price || service.price
                  )}
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default PriceHistoryPage;
