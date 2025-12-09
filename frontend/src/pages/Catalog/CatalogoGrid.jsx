/**
 * CatalogoGrid Component
 * Muestra los servicios en una vista de mosaico/grid
 */
import React from 'react';
import './CatalogoGrid.css';

const CatalogoGrid = ({ services, categories }) => {
  const getCategoryName = (categoryId) => {
    const category = categories.find((c) => c.id === categoryId);
    return category ? category.name : 'Sin categoría';
  };

  const formatCurrency = (amount) => {
    return `S/ ${parseFloat(amount).toFixed(2)}`;
  };

  return (
    <div className="catalogo-grid">
      {services.map((service) => (
        <div key={service.id} className="service-card-grid">
          <div className="service-card-header">
            <h3>{service.name}</h3>
            <span className={`badge ${service.is_active ? 'badge-success' : 'badge-secondary'}`}>
              {service.is_active ? 'Activo' : 'Inactivo'}
            </span>
          </div>
          <div className="service-card-body">
            <p className="service-code">{service.code}</p>
            <p className="service-category">{getCategoryName(service.category_id)}</p>
            <p className="service-description">{service.description}</p>
          </div>
          <div className="service-card-footer">
            <strong className="price-highlight">
              {formatCurrency(service.current_price || service.price)}
            </strong>
          </div>
        </div>
      ))}
    </div>
  );
};

export default CatalogoGrid;
