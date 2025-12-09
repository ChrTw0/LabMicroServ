/**
 * OrderFormPage Component
 * Formulario para crear nueva orden con selección de servicios y registro de pagos
 */
import { useEffect, useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useOrders, useCatalog } from '../../hooks/useOrders';
import { usePatients } from '../../hooks/usePatients';
import './OrderFormPage.css';

const OrderFormPage = () => {
  const navigate = useNavigate();
  const { loading: ordersLoading, createOrder } = useOrders();
  const { services, loading: catalogLoading, fetchServices } = useCatalog();
  const { patients, loading: patientsLoading, fetchPatients } = usePatients();

  // Datos de la orden
  const [patientId, setPatientId] = useState('');
  const [locationId, setLocationId] = useState('1');
  const [searchPatient, setSearchPatient] = useState('');
  const [searchService, setSearchService] = useState('');

  // Items de la orden
  const [selectedServices, setSelectedServices] = useState([]);

  // Pagos
  const [payments, setPayments] = useState([
    { payment_method: 'EFECTIVO', amount: '' }
  ]);

  useEffect(() => {
    fetchServices();
    fetchPatients({ page_size: 100 });
  }, []);

  // Filtrar pacientes por búsqueda
  const filteredPatients = patients.filter((p) => {
    if (!searchPatient) return true;
    const search = searchPatient.toLowerCase();
    const fullName = `${p.first_name} ${p.last_name}`.toLowerCase();
    const businessName = (p.business_name || '').toLowerCase();
    const document = p.document_number;
    return fullName.includes(search) || businessName.includes(search) || document.includes(search);
  });

  // Filtrar servicios por búsqueda
  const filteredServices = services.filter((s) => {
    if (!searchService) return true;
    const search = searchService.toLowerCase();
    return s.name.toLowerCase().includes(search) || s.code.toLowerCase().includes(search);
  });

  // Agregar servicio a la orden
  const handleAddService = (service) => {
    const exists = selectedServices.find((s) => s.service_id === service.id);
    if (exists) {
      alert('El servicio ya fue agregado');
      return;
    }

    setSelectedServices([
      ...selectedServices,
      {
        service_id: service.id,
        service_name: service.name,
        unit_price: parseFloat(service.price),
        quantity: 1,
      },
    ]);
  };

  // Remover servicio
  const handleRemoveService = (serviceId) => {
    setSelectedServices(selectedServices.filter((s) => s.service_id !== serviceId));
  };

  // Actualizar cantidad de servicio
  const handleUpdateQuantity = (serviceId, quantity) => {
    const qty = parseInt(quantity) || 1;
    setSelectedServices(
      selectedServices.map((s) =>
        s.service_id === serviceId ? { ...s, quantity: qty } : s
      )
    );
  };

  // Calcular subtotal de un item
  const getItemSubtotal = (item) => {
    return item.unit_price * item.quantity;
  };

  // Calcular total de la orden
  const getOrderTotal = () => {
    return selectedServices.reduce((sum, item) => sum + getItemSubtotal(item), 0);
  };

  // Agregar nuevo pago
  const handleAddPayment = () => {
    setPayments([
      ...payments,
      { payment_method: 'EFECTIVO', amount: '' }
    ]);
  };

  // Remover pago
  const handleRemovePayment = (index) => {
    setPayments(payments.filter((_, i) => i !== index));
  };

  // Actualizar pago
  const handleUpdatePayment = (index, field, value) => {
    const updated = [...payments];
    updated[index] = { ...updated[index], [field]: value };
    setPayments(updated);
  };

  // Calcular total de pagos
  const getTotalPayments = () => {
    return payments.reduce((sum, payment) => {
      const amount = parseFloat(payment.amount) || 0;
      return sum + amount;
    }, 0);
  };

  // Validar y crear orden
  const handleSubmit = async (e) => {
    e.preventDefault();

    // Validaciones
    if (!patientId) {
      alert('Seleccione un paciente');
      return;
    }

    if (selectedServices.length === 0) {
      alert('Agregue al menos un servicio');
      return;
    }

    const total = getOrderTotal();
    const totalPaid = getTotalPayments();

    if (totalPaid > total) {
      alert('El total de pagos no puede exceder el total de la orden');
      return;
    }

    // Preparar items
    const items = selectedServices.map((service) => ({
      service_id: service.service_id,
      quantity: service.quantity,
    }));

    // Preparar datos de la orden
    const orderData = {
      patient_id: parseInt(patientId),
      location_id: parseInt(locationId),
      items: items,
    };

    // Crear la orden
    const result = await createOrder(orderData);

    if (result.success) {
      const newOrder = result.data;

      // Si hay pagos, registrarlos
      if (totalPaid > 0) {
        const validPayments = payments
          .filter((p) => parseFloat(p.amount) > 0)
          .map((p) => ({
            payment_method: p.payment_method,
            amount: parseFloat(p.amount),
          }));

        if (validPayments.length > 0) {
          // Redirigir al detalle para registrar pagos
          // (Como createOrder no retorna ID en algunos casos, navegamos a la lista)
          alert(`Orden creada exitosamente. Ahora registre los pagos.`);
          navigate(`/dashboard/orders/${newOrder.id}`);
          return;
        }
      }

      alert('Orden creada exitosamente');
      navigate('/dashboard/orders');
    } else {
      alert(`Error al crear orden: ${result.error}`);
    }
  };

  const formatCurrency = (amount) => {
    return `S/ ${parseFloat(amount).toFixed(2)}`;
  };

  const orderTotal = getOrderTotal();
  const totalPaid = getTotalPayments();
  const balance = orderTotal - totalPaid;
  const isLoading = ordersLoading || catalogLoading || patientsLoading;

  return (
    <div className="order-form-page">
      <div className="page-header">
        <div>
          <Link to="/dashboard/orders" className="btn-back">← Volver</Link>
          <h1>Nueva Orden</h1>
        </div>
      </div>

      <form onSubmit={handleSubmit}>
        <div className="form-grid">
          {/* Sección: Paciente */}
          <div className="form-card">
            <h2>1. Seleccionar Paciente</h2>
            <div className="form-group">
              <label>Buscar Paciente:</label>
              <input
                type="text"
                placeholder="Buscar por nombre, DNI o RUC..."
                value={searchPatient}
                onChange={(e) => setSearchPatient(e.target.value)}
                className="form-control"
              />
            </div>
            <div className="form-group">
              <label>Paciente: *</label>
              <select
                value={patientId}
                onChange={(e) => setPatientId(e.target.value)}
                className="form-control"
                required
              >
                <option value="">Seleccione un paciente</option>
                {filteredPatients.map((patient) => (
                  <option key={patient.id} value={patient.id}>
                    {patient.document_type === 'RUC'
                      ? `${patient.business_name} - ${patient.document_number}`
                      : `${patient.first_name} ${patient.last_name} - ${patient.document_number}`}
                  </option>
                ))}
              </select>
            </div>
            <div className="form-group">
              <label>Sede: *</label>
              <select
                value={locationId}
                onChange={(e) => setLocationId(e.target.value)}
                className="form-control"
                required
              >
                <option value="1">Sede 1 - Principal</option>
                <option value="2">Sede 2 - Sucursal</option>
              </select>
            </div>
          </div>

          {/* Sección: Servicios */}
          <div className="form-card full-width">
            <h2>2. Seleccionar Servicios</h2>
            <div className="form-group">
              <label>Buscar Servicio:</label>
              <input
                type="text"
                placeholder="Buscar por nombre o código..."
                value={searchService}
                onChange={(e) => setSearchService(e.target.value)}
                className="form-control"
              />
            </div>

            <div className="services-grid">
              {filteredServices.map((service) => (
                <div key={service.id} className="service-card">
                  <div className="service-info">
                    <strong>{service.name}</strong>
                    <span className="service-code">{service.code}</span>
                    <span className="service-price">{formatCurrency(service.price)}</span>
                  </div>
                  <button
                    type="button"
                    onClick={() => handleAddService(service)}
                    className="btn btn-sm btn-primary"
                  >
                    + Agregar
                  </button>
                </div>
              ))}
            </div>

            {selectedServices.length > 0 && (
              <div className="selected-services">
                <h3>Servicios Agregados</h3>
                <table className="items-table">
                  <thead>
                    <tr>
                      <th>Servicio</th>
                      <th>Precio Unit.</th>
                      <th>Cantidad</th>
                      <th>Subtotal</th>
                      <th>Acción</th>
                    </tr>
                  </thead>
                  <tbody>
                    {selectedServices.map((item) => (
                      <tr key={item.service_id}>
                        <td>{item.service_name}</td>
                        <td>{formatCurrency(item.unit_price)}</td>
                        <td>
                          <input
                            type="number"
                            min="1"
                            value={item.quantity}
                            onChange={(e) =>
                              handleUpdateQuantity(item.service_id, e.target.value)
                            }
                            className="quantity-input"
                          />
                        </td>
                        <td><strong>{formatCurrency(getItemSubtotal(item))}</strong></td>
                        <td>
                          <button
                            type="button"
                            onClick={() => handleRemoveService(item.service_id)}
                            className="btn-icon btn-delete"
                            title="Eliminar"
                          >
                            🗑️
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                  <tfoot>
                    <tr>
                      <td colSpan="3" className="text-right"><strong>TOTAL:</strong></td>
                      <td><strong>{formatCurrency(orderTotal)}</strong></td>
                      <td></td>
                    </tr>
                  </tfoot>
                </table>
              </div>
            )}
          </div>

          {/* Sección: Pagos */}
          {selectedServices.length > 0 && (
            <div className="form-card full-width">
              <h2>3. Registrar Pagos (Opcional)</h2>
              <p className="text-muted">
                Puede registrar uno o más pagos. Si no registra ninguno, la orden quedará con saldo pendiente.
              </p>

              {payments.map((payment, index) => (
                <div key={index} className="payment-row">
                  <select
                    value={payment.payment_method}
                    onChange={(e) =>
                      handleUpdatePayment(index, 'payment_method', e.target.value)
                    }
                    className="form-control"
                  >
                    <option value="EFECTIVO">Efectivo</option>
                    <option value="TARJETA">Tarjeta</option>
                    <option value="TRANSFERENCIA">Transferencia</option>
                    <option value="YAPE_PLIN">Yape/Plin</option>
                  </select>
                  <input
                    type="number"
                    step="0.01"
                    min="0"
                    placeholder="Monto"
                    value={payment.amount}
                    onChange={(e) =>
                      handleUpdatePayment(index, 'amount', e.target.value)
                    }
                    className="form-control"
                  />
                  {payments.length > 1 && (
                    <button
                      type="button"
                      onClick={() => handleRemovePayment(index)}
                      className="btn btn-outline"
                    >
                      Eliminar
                    </button>
                  )}
                </div>
              ))}

              <button
                type="button"
                onClick={handleAddPayment}
                className="btn btn-outline btn-sm"
              >
                + Agregar otro pago
              </button>

              <div className="payments-summary">
                <div className="summary-row">
                  <span>Total de la Orden:</span>
                  <strong>{formatCurrency(orderTotal)}</strong>
                </div>
                <div className="summary-row">
                  <span>Total a Pagar Ahora:</span>
                  <strong className="text-success">{formatCurrency(totalPaid)}</strong>
                </div>
                <div className="summary-row balance-row">
                  <span>Saldo Pendiente:</span>
                  <strong className={balance > 0 ? 'text-danger' : 'text-success'}>
                    {formatCurrency(balance)}
                  </strong>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Botones de acción */}
        <div className="form-actions">
          <button
            type="submit"
            className="btn btn-primary btn-lg"
            disabled={isLoading || selectedServices.length === 0}
          >
            {isLoading ? 'Creando...' : 'Crear Orden'}
          </button>
          <Link to="/dashboard/orders" className="btn btn-outline btn-lg">
            Cancelar
          </Link>
        </div>
      </form>
    </div>
  );
};

export default OrderFormPage;
