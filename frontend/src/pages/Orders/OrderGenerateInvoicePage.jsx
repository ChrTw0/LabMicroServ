import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import billingService from '../../services/billingService'; // Necesitaremos crear este servicio
import './OrderGenerateInvoicePage.css';

const OrderGenerateInvoicePage = () => {
  const { id: orderId } = useParams(); // Obtiene el ID de la orden desde la URL
  const navigate = useNavigate();
  const { register, handleSubmit, watch, formState: { errors } } = useForm();

  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const invoiceType = watch('invoice_type', 'BOLETA');

  useEffect(() => {
    if (!orderId) {
      setError('No se ha especificado una orden para facturar.');
    }
  }, [orderId]);

  const onSubmit = async (data) => {
    if (!orderId) {
      setError('Error: ID de la orden no encontrado.');
      return;
    }

    setIsLoading(true);
    setError('');

    try {
      const payload = {
        order_id: orderId,
        invoice_type: data.invoice_type,
      };

      // Llamada al endpoint: POST /api/v1/invoices
      const newInvoice = await billingService.create(payload);

      // Si todo sale bien, redirigir al detalle de la factura recién creada
      navigate(`/dashboard/billing/${newInvoice.id}`);

    } catch (err) {
      console.error('Error al generar el comprobante:', err);
      setError(err.message || 'Ocurrió un error al comunicarse con el servicio de facturación.');
    } finally {
      setIsLoading(false);
    }
  };

  if (!orderId && !error) {
    return <div>Cargando...</div>;
  }

  return (
    <div className="invoice-form-container">
      <div className="invoice-form-card">
        <h1 className="invoice-form-title">Generar Comprobante</h1>
        <p className="invoice-form-subtitle">
          Estás a punto de generar un comprobante para la orden: <strong>{orderId}</strong>
        </p>

        {error && <div className="alert alert-error">{error}</div>}

        <form onSubmit={handleSubmit(onSubmit)}>
          <div className="form-group">
            <label htmlFor="invoice_type">Tipo de Comprobante</label>
            <select
              id="invoice_type"
              {...register('invoice_type', { required: 'Debe seleccionar un tipo de comprobante' })}
              className="form-control"
            >
              <option value="BOLETA">Boleta Electrónica</option>
              <option value="FACTURA">Factura Electrónica</option>
            </select>
            {errors.invoice_type && <span className="error-message">{errors.invoice_type.message}</span>}
          </div>

          <div className="invoice-type-info">
            {invoiceType === 'BOLETA' && (
              <p>Se emitirá una <strong>Boleta</strong>. El sistema usará el DNI del paciente asociado a la orden.</p>
            )}
            {invoiceType === 'FACTURA' && (
              <p>Se emitirá una <strong>Factura</strong>. El sistema usará el RUC del paciente. Asegúrate de que el paciente tenga RUC registrado.</p>
            )}
          </div>

          <div className="form-actions">
            <button
              type="button"
              className="btn btn-secondary"
              onClick={() => navigate(`/dashboard/orders/${orderId}`)} // Volver al detalle de la orden
              disabled={isLoading}
            >
              Cancelar
            </button>
            <button
              type="submit"
              className="btn btn-primary"
              disabled={isLoading}
            >
              {isLoading ? 'Generando...' : 'Confirmar y Generar'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default OrderGenerateInvoicePage;