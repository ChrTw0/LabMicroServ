/**
 * OrdersListPage Component
 * Página de listado de órdenes con búsqueda, filtros y acciones
 */
import { useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useOrders } from '../../hooks/useOrders';
import './OrdersListPage.css';

const OrdersListPage = () => {
  const navigate = useNavigate();
  const { orders, loading, error, pagination, fetchOrders, cancelOrder } = useOrders();

  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [dateFrom, setDateFrom] = useState('');
  const [dateTo, setDateTo] = useState('');

  useEffect(() => {
    fetchOrders();
  }, []);

  const handleSearch = (e) => {
    e.preventDefault();

    const params = {};
    if (searchTerm) params.search = searchTerm;
    if (statusFilter) params.status = statusFilter;
    if (dateFrom) params.date_from = dateFrom;
    if (dateTo) params.date_to = dateTo;

    fetchOrders(params);
  };

  const handleClearFilters = () => {
    setSearchTerm('');
    setStatusFilter('');
    setDateFrom('');
    setDateTo('');
    fetchOrders();
  };

  const handleCancel = async (id, orderNumber) => {
    if (window.confirm(`¿Estás seguro de anular la orden ${orderNumber}?`)) {
      const result = await cancelOrder(id);
      if (result.success) {
        alert('Orden anulada correctamente');
      } else {
        alert(`Error: ${result.error}`);
      }
    }
  };

  const getStatusBadge = (status) => {
    const badges = {
      REGISTRADA: 'badge-info',
      EN_PROCESO: 'badge-warning',
      COMPLETADA: 'badge-success',
      ANULADA: 'badge-danger',
    };
    return badges[status] || 'badge-secondary';
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

  if (loading && orders.length === 0) {
    return (
      <div className="loading-container">
        <p>Cargando órdenes...</p>
      </div>
    );
  }

  return (
    <div className="orders-list-page">
      <div className="page-header">
        <h1>Gestión de Órdenes</h1>
        <Link to="/dashboard/orders/new" className="btn btn-primary">
          + Nueva Orden
        </Link>
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
              placeholder="Buscar por número de orden..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="filter-input"
            />

            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="filter-select"
            >
              <option value="">Todos los estados</option>
              <option value="REGISTRADA">Registrada</option>
              <option value="EN_PROCESO">En Proceso</option>
              <option value="COMPLETADA">Completada</option>
              <option value="ANULADA">Anulada</option>
            </select>

            <input
              type="date"
              placeholder="Desde"
              value={dateFrom}
              onChange={(e) => setDateFrom(e.target.value)}
              className="filter-input-date"
            />

            <input
              type="date"
              placeholder="Hasta"
              value={dateTo}
              onChange={(e) => setDateTo(e.target.value)}
              className="filter-input-date"
            />

            <button type="submit" className="btn btn-secondary">
              Buscar
            </button>

            {(searchTerm || statusFilter || dateFrom || dateTo) && (
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

      <div className="orders-stats">
        <p>
          Mostrando <strong>{orders.length}</strong> de <strong>{pagination.total}</strong> órdenes
        </p>
      </div>

      <div className="table-container">
        <table className="orders-table">
          <thead>
            <tr>
              <th>N° Orden</th>
              <th>Paciente ID</th>
              <th>Sede</th>
              <th>Estado</th>
              <th>Total</th>
              <th>Fecha</th>
              <th>Acciones</th>
            </tr>
          </thead>
          <tbody>
            {orders.length === 0 ? (
              <tr>
                <td colSpan="7" className="text-center">
                  No se encontraron órdenes
                </td>
              </tr>
            ) : (
              orders.map((order) => (
                <tr key={order.id}>
                  <td>
                    <strong>{order.order_number}</strong>
                  </td>
                  <td>{order.patient_id}</td>
                  <td>Sede {order.location_id}</td>
                  <td>
                    <span className={`badge ${getStatusBadge(order.status)}`}>
                      {order.status}
                    </span>
                  </td>
                  <td>{formatCurrency(order.total)}</td>
                  <td>{formatDate(order.created_at)}</td>
                  <td>
                    <div className="action-buttons">
                      <button
                        onClick={() => navigate(`/dashboard/orders/${order.id}`)}
                        className="btn-icon btn-view"
                        title="Ver detalle"
                      >
                        👁️
                      </button>
                      {order.status !== 'ANULADA' && order.status !== 'COMPLETADA' && (
                        <button
                          onClick={() => navigate(`/dashboard/orders/${order.id}/edit`)}
                          className="btn-icon btn-edit"
                          title="Editar"
                        >
                          ✏️
                        </button>
                      )}
                      {order.status !== 'ANULADA' && (
                        <button
                          onClick={() => handleCancel(order.id, order.order_number)}
                          className="btn-icon btn-delete"
                          title="Anular"
                        >
                          🗑️
                        </button>
                      )}
                    </div>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {loading && (
        <div className="loading-overlay">
          <p>Cargando...</p>
        </div>
      )}
    </div>
  );
};

export default OrdersListPage;
