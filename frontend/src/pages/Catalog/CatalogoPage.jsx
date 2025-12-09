/**
 * CatalogoPage Component
 * Página de gestión del catálogo de servicios/exámenes
 */
import { useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../../hooks/useAuth';
import { useCatalog } from '../../hooks/useOrders';
import CatalogoGrid from './CatalogoGrid';
import './CatalogoPage.css';

const CatalogoPage = () => {
  const navigate = useNavigate();
  const { services, categories, loading, error, fetchServices, fetchCategories } = useCatalog();
  const { hasAnyRole } = useAuth();

  const [searchTerm, setSearchTerm] = useState('');
  const [categoryFilter, setCategoryFilter] = useState('');
  const [statusFilter, setStatusFilter] = useState(''); // '', 'active', 'inactive'

  const isReadOnly = hasAnyRole(['Recepcionista', 'Laboratorista', 'Contador', 'Paciente']);

  useEffect(() => {
    fetchServices({ is_active: isReadOnly ? true : undefined }); // Read-only roles only see active services
    fetchCategories();
  }, [isReadOnly]);

  const handleSearch = (e) => {
    e.preventDefault();

    const params = {};
    if (searchTerm) params.search = searchTerm;
    if (categoryFilter) params.category_id = parseInt(categoryFilter);

    // Filtrar por estado activo/inactivo
    if (statusFilter === 'active') {
      params.is_active = true;
    } else if (statusFilter === 'inactive') {
      params.is_active = false;
    }

    fetchServices(params);
  };

  const handleClearFilters = () => {
    setSearchTerm('');
    setCategoryFilter('');
    setStatusFilter('');
    fetchServices({ is_active: isReadOnly ? true : undefined });
  };

  const getCategoryName = (categoryId) => {
    const category = categories.find((c) => c.id === categoryId);
    return category ? category.name : 'Sin categoría';
  };

  const formatCurrency = (amount) => {
    return `S/ ${parseFloat(amount).toFixed(2)}`;
  };

  if (loading && services.length === 0) {
    return (
      <div className="loading-container">
        <p>Cargando servicios...</p>
      </div>
    );
  }

  return (
    <div className="catalogo-page">
      <div className="page-header">
        <h1>Catálogo de Servicios</h1>
        {!isReadOnly && (
          <div className="header-actions">
            <Link to="/dashboard/catalog/categories" className="btn btn-outline">
              📋 Gestionar Categorías
            </Link>
            <Link to="/dashboard/catalog/new" className="btn btn-primary">
              + Nuevo Servicio
            </Link>
          </div>
        )}
      </div>

      {error && (
        <div className="alert alert-error">
          {error}
        </div>
      )}

      <div className="filters-section">
        <form onSubmit={handleSearch} className="filters-form">
          <input
            type="text"
            placeholder="Buscar por nombre o código..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="filter-input"
          />

          <select
            value={categoryFilter}
            onChange={(e) => setCategoryFilter(e.target.value)}
            className="filter-select"
          >
            <option value="">Todas las categorías</option>
            {categories.map((category) => (
              <option key={category.id} value={category.id}>
                {category.name}
              </option>
            ))}
          </select>

          {!isReadOnly && (
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="filter-select"
            >
              <option value="">Todos los estados</option>
              <option value="active">Activos</option>
              <option value="inactive">Inactivos</option>
            </select>
          )}

          <button type="submit" className="btn btn-secondary">
            Buscar
          </button>

          {(searchTerm || categoryFilter || statusFilter) && (
            <button
              type="button"
              onClick={handleClearFilters}
              className="btn btn-outline"
            >
              Limpiar
            </button>
          )}
        </form>
      </div>

      <div className="services-stats">
        <p>
          Mostrando <strong>{services.length}</strong> servicios
        </p>
      </div>
      
      {isReadOnly ? (
        <CatalogoGrid services={services} categories={categories} />
      ) : (
        <div className="table-container">
          <table className="services-table">
            <thead>
              <tr>
                <th>Código</th>
                <th>Nombre</th>
                <th>Categoría</th>
                <th>Precio Actual</th>
                <th>Estado</th>
                <th>Acciones</th>
              </tr>
            </thead>
            <tbody>
              {services.length === 0 ? (
                <tr>
                  <td colSpan="6" className="text-center">
                    No se encontraron servicios
                  </td>
                </tr>
              ) : (
                services.map((service) => (
                  <tr key={service.id}>
                    <td>
                      <strong>{service.code}</strong>
                    </td>
                    <td>{service.name}</td>
                    <td>{getCategoryName(service.category_id)}</td>
                    <td>
                      <strong className="price-highlight">
                        {formatCurrency(service.current_price || service.price)}
                      </strong>
                    </td>
                    <td>
                      <span className={`badge ${service.is_active ? 'badge-success' : 'badge-secondary'}`}>
                        {service.is_active ? 'Activo' : 'Inactivo'}
                      </span>
                    </td>
                    <td>
                      <div className="action-buttons">
                        <button
                          onClick={() => navigate(`/dashboard/catalog/${service.id}`)}
                          className="btn-icon btn-view"
                          title="Ver detalles"
                        >
                          👁️
                        </button>
                        <button
                          onClick={() => navigate(`/dashboard/catalog/${service.id}/price-history`)}
                          className="btn-icon btn-info"
                          title="Historial de precios"
                        >
                          📊
                        </button>
                        <button
                          onClick={() => navigate(`/dashboard/catalog/${service.id}/edit`)}
                          className="btn-icon btn-edit"
                          title="Editar"
                        >
                          ✏️
                        </button>
                      </div>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      )}

      {loading && (
        <div className="loading-overlay">
          <p>Cargando...</p>
        </div>
      )}
    </div>
  );
};

export default CatalogoPage;