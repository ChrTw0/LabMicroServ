import React from 'react';

const ContadorDashboard = () => {
  return (
    <div className="dashboard-grid">

      <div className="dashboard-card">
        <div className="card-icon">💰</div>
        <div className="card-content">
          <h3>Facturas</h3>
          <p className="card-number">--</p>
          <p className="card-description">Facturas del día</p>
        </div>
      </div>

    </div>
  );
};

export default ContadorDashboard;
