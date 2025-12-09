/**
 * OrderDetailPage Component
 * Página de detalle de orden con items, pagos y acciones
 */
import { useEffect, useState } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { useOrders } from '../../hooks/useOrders';
import './OrderDetailPage.css';

const OrderDetailPage = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const { loading, error, fetchOrderById, updateOrderStatus, addPayments } = useOrders();

  const [order, setOrder] = useState(null);
  const [showPaymentModal, setShowPaymentModal] = useState(false);
  const [paymentMethod, setPaymentMethod] = useState('EFECTIVO');
  const [paymentAmount, setPaymentAmount] = useState('');

  useEffect(() => {
    loadOrder();
  }, [id]);

  const loadOrder = async () => {
    const result = await fetchOrderById(id);
    if (result.success) {
      setOrder(result.data);
    } else {
      alert(`Error: ${result.error}`);
      navigate('/dashboard/orders');
    }
  };

  const handleStatusChange = async (newStatus) => {
    if (window.confirm(`¿Cambiar el estado a ${newStatus}?`)) {
      const result = await updateOrderStatus(id, newStatus);
      if (result.success) {
        alert('Estado actualizado correctamente');
        await loadOrder();
      } else {
        alert(`Error: ${result.error}`);
      }
    }
  };

  const handleAddPayment = async (e) => {
    e.preventDefault();

    const amount = parseFloat(paymentAmount);
    if (isNaN(amount) || amount <= 0) {
      alert('Ingrese un monto válido');
      return;
    }

    const balance = parseFloat(order.balance);
    if (amount > balance) {
      alert(`El monto no puede exceder el saldo pendiente de S/ ${balance.toFixed(2)}`);
      return;
    }

    const payments = [
      {
        payment_method: paymentMethod,
        amount: amount,
      },
    ];

    const result = await addPayments(id, payments);
    if (result.success) {
      alert('Pago registrado correctamente');
      setShowPaymentModal(false);
      setPaymentAmount('');
      await loadOrder();
    } else {
      alert(`Error: ${result.error}`);
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

  const getPaymentMethodBadge = (method) => {
    const badges = {
      EFECTIVO: 'badge-cash',
      TARJETA: 'badge-card',
      TRANSFERENCIA: 'badge-transfer',
      YAPE_PLIN: 'badge-digital',
    };
    return badges[method] || 'badge-secondary';
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

  if (loading || !order) {
    return (
      <div className="loading-container">
        <p>Cargando orden...</p>
      </div>
    );
  }

  const balance = parseFloat(order.balance);
  const totalPaid = parseFloat(order.total_paid);
  const total = parseFloat(order.total);
  const isPaid = balance <= 0;

  return (
    <div className="order-detail-page">
      <div className="page-header">
        <div>
          <Link to="/dashboard/orders" className="btn-back">← Volver</Link>
          <h1>Orden {order.order_number}</h1>
        </div>
        <span className={`badge ${getStatusBadge(order.status)}`}>
          {order.status}
        </span>
      </div>

      {error && (
        <div className="alert alert-error">
          {error}
        </div>
      )}

      <div className="detail-grid">
        {/* Información General */}
        <div className="detail-card">
          <h2>Información General</h2>
          <div className="detail-row">
            <span className="detail-label">N° Orden:</span>
            <span className="detail-value"><strong>{order.order_number}</strong></span>
          </div>
          <div className="detail-row">
            <span className="detail-label">Paciente ID:</span>
            <span className="detail-value">{order.patient_id}</span>
          </div>
          <div className="detail-row">
            <span className="detail-label">Sede:</span>
            <span className="detail-value">Sede {order.location_id}</span>
          </div>
          <div className="detail-row">
            <span className="detail-label">Estado:</span>
            <span className={`badge ${getStatusBadge(order.status)}`}>
              {order.status}
            </span>
          </div>
          <div className="detail-row">
            <span className="detail-label">Fecha de Registro:</span>
            <span className="detail-value">{formatDate(order.created_at)}</span>
          </div>
        </div>

        {/* Resumen Económico */}
        <div className="detail-card">
          <h2>Resumen Económico</h2>
          <div className="detail-row">
            <span className="detail-label">Subtotal:</span>
            <span className="detail-value">{formatCurrency(total)}</span>
          </div>
          <div className="detail-row">
            <span className="detail-label">Total Pagado:</span>
            <span className="detail-value text-success"><strong>{formatCurrency(totalPaid)}</strong></span>
          </div>
          <div className="detail-row balance-row">
            <span className="detail-label">Saldo Pendiente:</span>
            <span className={`detail-value ${balance > 0 ? 'text-danger' : 'text-success'}`}>
              <strong>{formatCurrency(balance)}</strong>
            </span>
          </div>
          {balance > 0 && order.status !== 'ANULADA' && (
            <button
              onClick={() => setShowPaymentModal(true)}
              className="btn btn-primary btn-block"
            >
              + Registrar Pago
            </button>
          )}
          {isPaid && (
            <div className="paid-badge">
              ✓ Pagado Completamente
            </div>
          )}
        </div>
      </div>

      {/* Items de la Orden */}
      <div className="detail-card">
        <h2>Servicios Solicitados</h2>
        <div className="table-container">
          <table className="items-table">
            <thead>
              <tr>
                <th>Servicio</th>
                <th>Precio Unitario</th>
                <th>Cantidad</th>
                <th>Subtotal</th>
              </tr>
            </thead>
            <tbody>
              {order.items && order.items.length > 0 ? (
                order.items.map((item, index) => (
                  <tr key={index}>
                    <td>{item.service_name}</td>
                    <td>{formatCurrency(item.unit_price)}</td>
                    <td>{item.quantity}</td>
                    <td><strong>{formatCurrency(item.subtotal)}</strong></td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan="4" className="text-center">No hay items registrados</td>
                </tr>
              )}
            </tbody>
            <tfoot>
              <tr>
                <td colSpan="3" className="text-right"><strong>TOTAL:</strong></td>
                <td><strong>{formatCurrency(total)}</strong></td>
              </tr>
            </tfoot>
          </table>
        </div>
      </div>

      {/* Pagos Registrados */}
      <div className="detail-card">
        <h2>Pagos Registrados</h2>
        {order.payments && order.payments.length > 0 ? (
          <div className="payments-list">
            {order.payments.map((payment, index) => (
              <div key={index} className="payment-item">
                <span className={`badge ${getPaymentMethodBadge(payment.payment_method)}`}>
                  {payment.payment_method}
                </span>
                <span className="payment-amount">{formatCurrency(payment.amount)}</span>
              </div>
            ))}
            <div className="payments-total">
              <strong>Total Pagado:</strong>
              <strong>{formatCurrency(totalPaid)}</strong>
            </div>
          </div>
        ) : (
          <p className="text-muted">No se han registrado pagos para esta orden.</p>
        )}
      </div>

      {/* Acciones */}
      {order.status !== 'ANULADA' && (
        <div className="actions-card">
          <h2>Acciones</h2>
          <div className="actions-buttons">
            {order.status === 'REGISTRADA' && (
              <button
                onClick={() => handleStatusChange('EN_PROCESO')}
                className="btn btn-secondary"
              >
                Marcar como En Proceso
              </button>
            )}
            {order.status === 'EN_PROCESO' && (
              <button
                onClick={() => handleStatusChange('COMPLETADA')}
                className="btn btn-success"
              >
                Marcar como Completada
              </button>
            )}
            <button
              onClick={() => navigate(`/dashboard/orders/${order.id}/generate-invoice`)}
              className="btn btn-primary"
              disabled={!isPaid || order.status !== 'COMPLETADA'}
            >
              Generar Factura/Boleta
            </button>
          </div>
        </div>
      )}

      {/* Modal de Registro de Pago */}
      {showPaymentModal && (
        <div className="modal-overlay" onClick={() => setShowPaymentModal(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <h2>Registrar Pago</h2>
            <form onSubmit={handleAddPayment}>
              <div className="form-group">
                <label>Método de Pago:</label>
                <select
                  value={paymentMethod}
                  onChange={(e) => setPaymentMethod(e.target.value)}
                  className="form-control"
                >
                  <option value="EFECTIVO">Efectivo</option>
                  <option value="TARJETA">Tarjeta</option>
                  <option value="TRANSFERENCIA">Transferencia</option>
                  <option value="YAPE_PLIN">Yape/Plin</option>
                </select>
              </div>
              <div className="form-group">
                <label>Monto:</label>
                <input
                  type="number"
                  step="0.01"
                  min="0.01"
                  max={balance}
                  value={paymentAmount}
                  onChange={(e) => setPaymentAmount(e.target.value)}
                  placeholder={`Máximo: S/ ${balance.toFixed(2)}`}
                  className="form-control"
                  required
                />
                <small className="form-hint">
                  Saldo pendiente: {formatCurrency(balance)}
                </small>
              </div>
              <div className="modal-actions">
                <button type="submit" className="btn btn-primary">
                  Registrar Pago
                </button>
                <button
                  type="button"
                  onClick={() => {
                    setShowPaymentModal(false);
                    setPaymentAmount('');
                  }}
                  className="btn btn-outline"
                >
                  Cancelar
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default OrderDetailPage;
