/**
 * InvoiceFormPage Component
 * Formulario para crear comprobante electrónico desde una orden
 */
import { useEffect, useState } from 'react';
import { useNavigate, useSearchParams, Link } from 'react-router-dom';
import { useBilling } from '../../hooks/useBilling';
import { orderService, patientService } from '../../services';
import './InvoiceFormPage.css';

const InvoiceFormPage = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const orderId = searchParams.get('order_id');

  const { loading: billingLoading, createInvoice } = useBilling();

  const [loading, setLoading] = useState(true);
  const [order, setOrder] = useState(null);
  const [patient, setPatient] = useState(null);

  const [formData, setFormData] = useState({
    document_type: '03', // Por defecto Boleta
    customer_document_type: 'DNI',
    customer_document: '',
    customer_name: '',
    customer_address: '',
    customer_email: '',
    issue_date: new Date().toISOString().split('T')[0],
  });

  useEffect(() => {
    if (orderId) {
      loadOrderData();
    } else {
      alert('Debe especificar una orden para generar el comprobante');
      navigate('/dashboard/orders');
    }
  }, [orderId]);

  const loadOrderData = async () => {
    setLoading(true);
    try {
      // Cargar orden
      const orderData = await orderService.getById(orderId);
      setOrder(orderData);

      // Cargar paciente
      const patientData = await patientService.getById(orderData.patient_id);
      setPatient(patientData);

      // Pre-llenar datos del cliente
      const isRUC = patientData.document_type === 'RUC';
      setFormData({
        document_type: isRUC ? '01' : '03', // Factura para RUC, Boleta para DNI
        customer_document_type: patientData.document_type,
        customer_document: patientData.document_number,
        customer_name: isRUC
          ? patientData.business_name
          : `${patientData.first_name} ${patientData.last_name}`,
        customer_address: patientData.address || '',
        customer_email: patientData.email || '',
        issue_date: new Date().toISOString().split('T')[0],
      });
    } catch (err) {
      alert(`Error al cargar datos: ${err.message}`);
      navigate('/dashboard/orders');
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData({
      ...formData,
      [name]: value,
    });
  };

  const calculateTotals = () => {
    if (!order || !order.items) return { subtotal: 0, igv: 0, total: 0 };

    const subtotal = order.items.reduce((sum, item) => sum + parseFloat(item.subtotal), 0);
    const igv = subtotal * 0.18; // 18% IGV
    const total = subtotal + igv;

    return { subtotal, igv, total };
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    // Validaciones
    if (!formData.customer_document || !formData.customer_name) {
      alert('Complete los datos del cliente');
      return;
    }

    // Validar tipo de documento
    if (formData.document_type === '01' && formData.customer_document_type !== 'RUC') {
      alert('Para emitir una Factura, el cliente debe tener RUC');
      return;
    }

    const { subtotal, igv, total } = calculateTotals();

    // Preparar items
    const items = order.items.map((item) => ({
      description: item.service_name,
      quantity: item.quantity,
      unit_price: parseFloat(item.unit_price),
      subtotal: parseFloat(item.subtotal),
    }));

    // Preparar datos del comprobante
    const invoiceData = {
      order_id: parseInt(orderId),
      document_type: formData.document_type,
      issue_date: formData.issue_date,
      currency: 'PEN',
      customer_document_type: formData.customer_document_type,
      customer_document: formData.customer_document,
      customer_name: formData.customer_name,
      customer_address: formData.customer_address || null,
      customer_email: formData.customer_email || null,
      items: items,
      subtotal: subtotal,
      igv: igv,
      total: total,
    };

    const result = await createInvoice(invoiceData);

    if (result.success) {
      alert('Comprobante creado exitosamente');
      navigate(`/dashboard/billing/${result.data.id}`);
    } else {
      alert(`Error al crear comprobante: ${result.error}`);
    }
  };

  const formatCurrency = (amount) => {
    return `S/ ${parseFloat(amount).toFixed(2)}`;
  };

  if (loading) {
    return (
      <div className="loading-container">
        <p>Cargando datos de la orden...</p>
      </div>
    );
  }

  if (!order) {
    return (
      <div className="error-container">
        <p>Orden no encontrada</p>
        <Link to="/dashboard/orders" className="btn btn-primary">
          Volver a Órdenes
        </Link>
      </div>
    );
  }

  const { subtotal, igv, total } = calculateTotals();

  return (
    <div className="invoice-form-page">
      <div className="page-header">
        <div>
          <Link to={`/dashboard/orders/${orderId}`} className="btn-back">
            ← Volver a la Orden
          </Link>
          <h1>Generar Comprobante Electrónico</h1>
          <p className="order-info">Orden: {order.order_number}</p>
        </div>
      </div>

      <form onSubmit={handleSubmit}>
        <div className="form-grid">
          {/* Tipo de Comprobante */}
          <div className="form-card">
            <h2>Tipo de Comprobante</h2>
            <div className="form-group">
              <label>Tipo de Documento: *</label>
              <select
                name="document_type"
                value={formData.document_type}
                onChange={handleChange}
                className="form-control"
                required
              >
                <option value="01">01 - Factura Electrónica</option>
                <option value="03">03 - Boleta de Venta Electrónica</option>
              </select>
              <small className="form-hint">
                {formData.document_type === '01'
                  ? 'Requiere RUC del cliente'
                  : 'Para clientes con DNI o sin documento'}
              </small>
            </div>

            <div className="form-group">
              <label>Fecha de Emisión: *</label>
              <input
                type="date"
                name="issue_date"
                value={formData.issue_date}
                onChange={handleChange}
                className="form-control"
                required
              />
            </div>
          </div>

          {/* Datos del Cliente */}
          <div className="form-card">
            <h2>Datos del Cliente</h2>
            <div className="form-row">
              <div className="form-group">
                <label>Tipo de Documento: *</label>
                <select
                  name="customer_document_type"
                  value={formData.customer_document_type}
                  onChange={handleChange}
                  className="form-control"
                  required
                >
                  <option value="DNI">DNI</option>
                  <option value="RUC">RUC</option>
                  <option value="CE">Carnet de Extranjería</option>
                  <option value="PASSPORT">Pasaporte</option>
                </select>
              </div>

              <div className="form-group">
                <label>N° Documento: *</label>
                <input
                  type="text"
                  name="customer_document"
                  value={formData.customer_document}
                  onChange={handleChange}
                  className="form-control"
                  required
                />
              </div>
            </div>

            <div className="form-group">
              <label>
                {formData.customer_document_type === 'RUC'
                  ? 'Razón Social:'
                  : 'Nombres y Apellidos:'} *
              </label>
              <input
                type="text"
                name="customer_name"
                value={formData.customer_name}
                onChange={handleChange}
                className="form-control"
                required
              />
            </div>

            <div className="form-group">
              <label>Dirección:</label>
              <input
                type="text"
                name="customer_address"
                value={formData.customer_address}
                onChange={handleChange}
                className="form-control"
              />
            </div>

            <div className="form-group">
              <label>Email:</label>
              <input
                type="email"
                name="customer_email"
                value={formData.customer_email}
                onChange={handleChange}
                className="form-control"
              />
              <small className="form-hint">
                El comprobante será enviado a este email
              </small>
            </div>
          </div>

          {/* Detalle de la Orden */}
          <div className="form-card full-width">
            <h2>Detalle de Items</h2>
            <div className="table-container">
              <table className="items-table">
                <thead>
                  <tr>
                    <th>Servicio</th>
                    <th>Cantidad</th>
                    <th>Precio Unit.</th>
                    <th>Subtotal</th>
                  </tr>
                </thead>
                <tbody>
                  {order.items && order.items.map((item, index) => (
                    <tr key={index}>
                      <td>{item.service_name}</td>
                      <td>{item.quantity}</td>
                      <td>{formatCurrency(item.unit_price)}</td>
                      <td>{formatCurrency(item.subtotal)}</td>
                    </tr>
                  ))}
                </tbody>
                <tfoot>
                  <tr>
                    <td colSpan="3" className="text-right">Subtotal (Base Imponible):</td>
                    <td>{formatCurrency(subtotal)}</td>
                  </tr>
                  <tr>
                    <td colSpan="3" className="text-right">IGV (18%):</td>
                    <td>{formatCurrency(igv)}</td>
                  </tr>
                  <tr className="total-row">
                    <td colSpan="3" className="text-right"><strong>TOTAL:</strong></td>
                    <td><strong>{formatCurrency(total)}</strong></td>
                  </tr>
                </tfoot>
              </table>
            </div>
          </div>
        </div>

        {/* Acciones */}
        <div className="form-actions">
          <button
            type="submit"
            className="btn btn-primary btn-lg"
            disabled={billingLoading}
          >
            {billingLoading ? 'Generando...' : 'Generar Comprobante'}
          </button>
          <Link
            to={`/dashboard/orders/${orderId}`}
            className="btn btn-outline btn-lg"
          >
            Cancelar
          </Link>
        </div>
      </form>
    </div>
  );
};

export default InvoiceFormPage;
