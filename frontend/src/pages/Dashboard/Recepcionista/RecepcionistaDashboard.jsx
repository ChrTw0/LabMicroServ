import React from 'react';

const RecepcionistaDashboard = () => {
  return (
    <div className="dashboard-grid">
      
      <div className="dashboard-card">
        <div className="card-icon">👥</div>
        <div className="card-content">
          <h3>Pacientes</h3>
          <p className="card-number">--</p>
          <p className="card-description">Total de pacientes registrados</p>
        </div>
      </div>

      <div className="dashboard-card">
        <div className="card-icon">📋</div>
        <div className="card-content">
          <h3>Órdenes</h3>
          <p className="card-number">--</p>
          <p className="card-description">Órdenes pendientes</p>
        </div>
      </div>

    </div>
  );
};

export default RecepcionistaDashboard;
