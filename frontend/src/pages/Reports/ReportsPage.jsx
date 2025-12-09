/**
 * ReportsPage Component
 * Página de reportes con gráficos interactivos - RF-074 a RF-082
 */
import { useEffect, useState } from 'react';
import { useReports } from '../../hooks';
import {
  BarChart, Bar, LineChart, Line, PieChart, Pie, Cell,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer
} from 'recharts';
import jsPDF from 'jspdf';
import 'jspdf-autotable';
import * as XLSX from 'xlsx';
import './ReportsPage.css';

const ReportsPage = () => {
  const {
    loading,
    error,
    paymentMethodData,
    topServicesData,
    monthlyRevenueData,
    patientTypesData,
    salesByPeriodData,
    invoiceTypeData,
    fetchPaymentMethodReport,
    fetchTopServicesReport,
    fetchMonthlyRevenueReport,
    fetchPatientTypesReport,
    fetchSalesByPeriodReport,
    fetchInvoiceTypeReport,
  } = useReports();

  const [activeTab, setActiveTab] = useState('ventas'); // ventas, servicios, pacientes, facturacion
  const [filters, setFilters] = useState({
    dateFrom: '',
    dateTo: '',
    locationId: '',
    months: 12,
    limit: 10,
  });

  // Colores para gráficos
  const COLORS = ['#667eea', '#764ba2', '#f093fb', '#4facfe', '#00f2fe', '#43e97b', '#fa709a', '#fee140'];

  useEffect(() => {
    // Cargar reportes iniciales
    loadReports();
  }, []);

  // Debug: Ver los datos cuando cambien
  useEffect(() => {
    if (paymentMethodData.length > 0) {
      console.log('Payment Method Data:', paymentMethodData);
      console.log('Data types:', paymentMethodData.map(item => ({
        payment_method: typeof item.payment_method,
        total_amount: typeof item.total_amount,
        count: typeof item.count,
        percentage: typeof item.percentage
      })));
    }
  }, [paymentMethodData]);

  const loadReports = () => {
    // Construir parámetros solo con valores no vacíos
    const params = {};
    if (filters.dateFrom) params.date_from = filters.dateFrom;
    if (filters.dateTo) params.date_to = filters.dateTo;
    if (filters.locationId) params.location_id = parseInt(filters.locationId);

    // Reportes de ventas
    fetchPaymentMethodReport(params);
    fetchMonthlyRevenueReport({
      months: filters.months || 12,
      ...(filters.locationId && { location_id: parseInt(filters.locationId) })
    });

    // Reportes de servicios
    fetchTopServicesReport({
      limit: filters.limit || 10,
      ...params
    });

    // Reportes de pacientes
    fetchPatientTypesReport(params);

    // Reportes de facturación
    fetchSalesByPeriodReport({
      months: filters.months || 12,
      ...(filters.locationId && { location_id: parseInt(filters.locationId) })
    });
    fetchInvoiceTypeReport(params);
  };

  const handleFilterChange = (e) => {
    const { name, value } = e.target;
    setFilters((prev) => ({ ...prev, [name]: value }));
  };

  const handleApplyFilters = (e) => {
    e.preventDefault();
    loadReports();
  };

  const handleClearFilters = () => {
    setFilters({
      dateFrom: '',
      dateTo: '',
      locationId: '',
      months: 12,
      limit: 10,
    });
    setTimeout(() => loadReports(), 0);
  };

  // Formatear moneda
  const formatCurrency = (value) => {
    return `S/ ${parseFloat(value).toLocaleString('es-PE', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
  };

  // Exportar a PDF - RF-081, RF-064
  const exportToPDF = () => {
    const doc = new jsPDF();
    const currentDate = new Date().toLocaleDateString('es-PE');

    // Header
    doc.setFontSize(18);
    doc.text('Reporte de Análisis de Ventas', 14, 20);
    doc.setFontSize(10);
    doc.text(`Fecha de generación: ${currentDate}`, 14, 28);

    let yPosition = 35;

    // Reporte de métodos de pago
    if (activeTab === 'ventas' && paymentMethodData.length > 0) {
      doc.setFontSize(14);
      doc.text('Ventas por Método de Pago', 14, yPosition);
      yPosition += 5;

      const tableData = paymentMethodData.map((item) => [
        item.payment_method,
        formatCurrency(item.total_amount),
        item.count.toString(),
        `${item.percentage.toFixed(2)}%`,
      ]);

      doc.autoTable({
        startY: yPosition,
        head: [['Método de Pago', 'Total', 'Cantidad', 'Porcentaje']],
        body: tableData,
      });
    }

    // Top servicios
    if (activeTab === 'servicios' && topServicesData.length > 0) {
      doc.setFontSize(14);
      doc.text('Servicios Más Solicitados', 14, yPosition);
      yPosition += 5;

      const tableData = topServicesData.map((item) => [
        item.service_name,
        item.quantity_sold.toString(),
        formatCurrency(item.total_revenue),
        `${item.percentage.toFixed(2)}%`,
      ]);

      doc.autoTable({
        startY: yPosition,
        head: [['Servicio', 'Cantidad', 'Ingresos', 'Porcentaje']],
        body: tableData,
      });
    }

    doc.save(`reporte_${activeTab}_${currentDate}.pdf`);
  };

  // Exportar a Excel - RF-081
  const exportToExcel = () => {
    let dataToExport = [];
    let fileName = 'reporte';

    switch (activeTab) {
      case 'ventas':
        dataToExport = paymentMethodData.map((item) => ({
          'Método de Pago': item.payment_method,
          'Total': parseFloat(item.total_amount),
          'Cantidad': item.count,
          'Porcentaje': item.percentage,
        }));
        fileName = 'ventas_por_metodo_pago';
        break;
      case 'servicios':
        dataToExport = topServicesData.map((item) => ({
          'Servicio': item.service_name,
          'Cantidad Vendida': item.quantity_sold,
          'Ingresos Totales': parseFloat(item.total_revenue),
          'Porcentaje': item.percentage,
        }));
        fileName = 'servicios_mas_solicitados';
        break;
      case 'facturacion':
        dataToExport = salesByPeriodData.map((item) => ({
          'Periodo': item.period,
          'Ventas Totales': parseFloat(item.total_sales),
          'Total Facturas': item.total_invoices,
          'Total Impuestos': parseFloat(item.total_tax),
          'Valor Promedio': parseFloat(item.avg_invoice_value),
        }));
        fileName = 'ventas_por_periodo';
        break;
      default:
        break;
    }

    if (dataToExport.length === 0) {
      alert('No hay datos para exportar');
      return;
    }

    const worksheet = XLSX.utils.json_to_sheet(dataToExport);
    const workbook = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(workbook, worksheet, 'Reporte');
    XLSX.writeFile(workbook, `${fileName}_${new Date().toISOString().split('T')[0]}.xlsx`);
  };

  if (loading && !paymentMethodData.length) {
    return (
      <div className="loading-container">
        <p>Cargando reportes...</p>
      </div>
    );
  }

  return (
    <div className="reports-page">
      <div className="page-header">
        <h1>Reportes y Análisis</h1>
        <div className="export-buttons">
          <button onClick={exportToPDF} className="btn btn-secondary">
            📄 Exportar PDF
          </button>
          <button onClick={exportToExcel} className="btn btn-secondary">
            📊 Exportar Excel
          </button>
        </div>
      </div>

      {error && (
        <div className="alert alert-error">
          {typeof error === 'string' ? error : 'Ha ocurrido un error. Por favor, intenta nuevamente.'}
        </div>
      )}

      {/* Filtros - RF-080 */}
      <div className="filters-section">
        <form className="filters-form" onSubmit={handleApplyFilters}>
          <div className="filter-row">
            <input
              type="date"
              name="dateFrom"
              value={filters.dateFrom}
              onChange={handleFilterChange}
              className="filter-input-date"
              placeholder="Fecha desde"
            />
            <input
              type="date"
              name="dateTo"
              value={filters.dateTo}
              onChange={handleFilterChange}
              className="filter-input-date"
              placeholder="Fecha hasta"
            />
            <input
              type="number"
              name="locationId"
              value={filters.locationId}
              onChange={handleFilterChange}
              className="filter-input"
              placeholder="ID de Sede"
              min="1"
            />
            <button type="submit" className="btn btn-primary">
              Aplicar Filtros
            </button>
            <button type="button" onClick={handleClearFilters} className="btn btn-secondary">
              Limpiar
            </button>
          </div>
        </form>
      </div>

      {/* Tabs de navegación */}
      <div className="tabs-container">
        <button
          className={`tab ${activeTab === 'ventas' ? 'active' : ''}`}
          onClick={() => setActiveTab('ventas')}
        >
          Ventas y Pagos
        </button>
        <button
          className={`tab ${activeTab === 'servicios' ? 'active' : ''}`}
          onClick={() => setActiveTab('servicios')}
        >
          Servicios
        </button>
        <button
          className={`tab ${activeTab === 'pacientes' ? 'active' : ''}`}
          onClick={() => setActiveTab('pacientes')}
        >
          Pacientes
        </button>
        <button
          className={`tab ${activeTab === 'facturacion' ? 'active' : ''}`}
          onClick={() => setActiveTab('facturacion')}
        >
          Facturación
        </button>
      </div>

      {/* Contenido de tabs */}
      <div className="tab-content">
        {/* TAB: VENTAS Y PAGOS */}
        {activeTab === 'ventas' && (
          <div className="reports-grid">
            {/* Gráfico de métodos de pago - RF-077 */}
            <div className="report-card">
              <h3>Ventas por Método de Pago</h3>
              {loading ? (
                <div className="loading-container">
                  <p>Cargando datos...</p>
                </div>
              ) : Array.isArray(paymentMethodData) && paymentMethodData.length > 0 ? (
                <>
                  <ResponsiveContainer width="100%" height={350}>
                    <PieChart>
                      <Pie
                        data={paymentMethodData}
                        dataKey="total_amount"
                        nameKey="payment_method"
                        cx="50%"
                        cy="50%"
                        outerRadius={100}
                        fill="#8884d8"
                        label={(entry) => `${entry.payment_method}: ${entry.percentage.toFixed(1)}%`}
                        labelLine={true}
                      >
                        {paymentMethodData.map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                        ))}
                      </Pie>
                      <Tooltip
                        formatter={(value) => formatCurrency(value)}
                        contentStyle={{ backgroundColor: '#fff', border: '1px solid #ccc' }}
                      />
                      <Legend
                        verticalAlign="bottom"
                        height={36}
                        formatter={(value) => value}
                      />
                    </PieChart>
                  </ResponsiveContainer>
                </>
              ) : (
                <p className="no-data">
                  No hay datos de pagos disponibles.
                  {filters.dateFrom || filters.dateTo ? ' Intenta ajustar los filtros de fecha.' : ' Registra algunas órdenes con pagos para ver las estadísticas.'}
                </p>
              )}
            </div>

            {/* Gráfico de ingresos mensuales - RF-079 */}
            <div className="report-card full-width">
              <h3>Comparativa Mensual de Ingresos</h3>
              <div className="filter-inline">
                <label>
                  Meses a mostrar:
                  <input
                    type="number"
                    name="months"
                    value={filters.months}
                    onChange={handleFilterChange}
                    min="1"
                    max="24"
                    className="filter-input-small"
                  />
                </label>
              </div>
              {monthlyRevenueData.length > 0 ? (
                <ResponsiveContainer width="100%" height={300}>
                  <LineChart data={monthlyRevenueData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="month" />
                    <YAxis />
                    <Tooltip formatter={(value) => formatCurrency(value)} />
                    <Legend />
                    <Line type="monotone" dataKey="total_revenue" stroke="#667eea" strokeWidth={2} name="Ingresos" />
                    <Line type="monotone" dataKey="avg_order_value" stroke="#764ba2" strokeWidth={2} name="Valor Promedio" />
                  </LineChart>
                </ResponsiveContainer>
              ) : (
                <p className="no-data">No hay datos disponibles</p>
              )}
            </div>
          </div>
        )}

        {/* TAB: SERVICIOS */}
        {activeTab === 'servicios' && (
          <div className="reports-grid">
            {/* Gráfico de top servicios - RF-076 */}
            <div className="report-card full-width">
              <h3>Servicios Más Solicitados</h3>
              <div className="filter-inline">
                <label>
                  Top:
                  <input
                    type="number"
                    name="limit"
                    value={filters.limit}
                    onChange={handleFilterChange}
                    min="5"
                    max="20"
                    className="filter-input-small"
                  />
                </label>
              </div>
              {topServicesData.length > 0 ? (
                <ResponsiveContainer width="100%" height={400}>
                  <BarChart data={topServicesData} layout="vertical">
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis type="number" />
                    <YAxis dataKey="service_name" type="category" width={150} />
                    <Tooltip formatter={(value, name) => {
                      if (name === 'total_revenue') return formatCurrency(value);
                      return value;
                    }} />
                    <Legend />
                    <Bar dataKey="quantity_sold" fill="#667eea" name="Cantidad Vendida" />
                    <Bar dataKey="total_revenue" fill="#764ba2" name="Ingresos Totales" />
                  </BarChart>
                </ResponsiveContainer>
              ) : (
                <p className="no-data">No hay datos disponibles</p>
              )}
            </div>
          </div>
        )}

        {/* TAB: PACIENTES */}
        {activeTab === 'pacientes' && (
          <div className="reports-grid">
            {/* Gráfico de pacientes nuevos vs recurrentes - RF-078 */}
            <div className="report-card">
              <h3>Pacientes Nuevos vs Recurrentes</h3>
              {patientTypesData ? (
                <>
                  <ResponsiveContainer width="100%" height={300}>
                    <PieChart>
                      <Pie
                        data={[
                          { name: 'Nuevos', value: patientTypesData.new_patients },
                          { name: 'Recurrentes', value: patientTypesData.recurring_patients },
                        ]}
                        dataKey="value"
                        nameKey="name"
                        cx="50%"
                        cy="50%"
                        outerRadius={100}
                        label={(entry) => `${entry.name}: ${((entry.value / patientTypesData.total_patients) * 100).toFixed(1)}%`}
                      >
                        <Cell fill="#667eea" />
                        <Cell fill="#764ba2" />
                      </Pie>
                      <Tooltip />
                      <Legend />
                    </PieChart>
                  </ResponsiveContainer>
                  <div className="stats-summary">
                    <div className="stat-item">
                      <span className="stat-label">Total Pacientes:</span>
                      <span className="stat-value">{patientTypesData.total_patients}</span>
                    </div>
                    <div className="stat-item">
                      <span className="stat-label">Nuevos:</span>
                      <span className="stat-value">{patientTypesData.new_patients} ({patientTypesData.new_percentage.toFixed(1)}%)</span>
                    </div>
                    <div className="stat-item">
                      <span className="stat-label">Recurrentes:</span>
                      <span className="stat-value">{patientTypesData.recurring_patients} ({patientTypesData.recurring_percentage.toFixed(1)}%)</span>
                    </div>
                  </div>
                </>
              ) : (
                <p className="no-data">No hay datos disponibles</p>
              )}
            </div>
          </div>
        )}

        {/* TAB: FACTURACIÓN */}
        {activeTab === 'facturacion' && (
          <div className="reports-grid">
            {/* Gráfico de ventas por periodo - RF-075 */}
            <div className="report-card full-width">
              <h3>Ventas por Periodo</h3>
              {salesByPeriodData.length > 0 ? (
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={salesByPeriodData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="period" />
                    <YAxis />
                    <Tooltip formatter={(value) => formatCurrency(value)} />
                    <Legend />
                    <Bar dataKey="total_sales" fill="#667eea" name="Ventas Totales" />
                    <Bar dataKey="total_tax" fill="#764ba2" name="Impuestos (IGV)" />
                  </BarChart>
                </ResponsiveContainer>
              ) : (
                <p className="no-data">No hay datos disponibles</p>
              )}
            </div>

            {/* Gráfico de tipos de comprobante - RF-075 */}
            <div className="report-card">
              <h3>Ventas por Tipo de Comprobante</h3>
              {Array.isArray(invoiceTypeData) && invoiceTypeData.length > 0 ? (
                <>
                  <ResponsiveContainer width="100%" height={350}>
                    <PieChart>
                      <Pie
                        data={invoiceTypeData}
                        dataKey="total_amount"
                        nameKey="invoice_type"
                        cx="50%"
                        cy="50%"
                        outerRadius={100}
                        fill="#8884d8"
                        label={(entry) => `${entry.invoice_type}: ${entry.percentage.toFixed(1)}%`}
                        labelLine={true}
                      >
                        {invoiceTypeData.map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                        ))}
                      </Pie>
                      <Tooltip
                        formatter={(value) => formatCurrency(value)}
                        contentStyle={{ backgroundColor: '#fff', border: '1px solid #ccc' }}
                      />
                      <Legend
                        verticalAlign="bottom"
                        height={36}
                        formatter={(value) => value}
                      />
                    </PieChart>
                  </ResponsiveContainer>
                </>
              ) : (
                <p className="no-data">No hay datos disponibles</p>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default ReportsPage;
