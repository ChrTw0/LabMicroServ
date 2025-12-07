/**
 * PatientsListPage Component
 * Página de listado de pacientes con búsqueda y acciones
 */
import { useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { usePatients } from '../../hooks/usePatients';
import './PatientsListPage.css';

const PatientsListPage = () => {
  const navigate = useNavigate();
  const { patients, loading, error, pagination, fetchPatients, deletePatient } = usePatients();
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    fetchPatients();
  }, []);

  const handleSearch = (e) => {
    e.preventDefault();
    fetchPatients({ search: searchTerm });
  };

  const handleDelete = async (id, patientName) => {
    if (window.confirm(`¿Estás seguro de eliminar al paciente ${patientName}?`)) {
      const result = await deletePatient(id);
      if (result.success) {
        alert('Paciente eliminado correctamente');
      } else {
        alert(`Error: ${result.error}`);
      }
    }
  };

  const getDocumentTypeBadge = (type) => {
    const badges = {
      DNI: 'badge-primary',
      RUC: 'badge-success',
      CE: 'badge-warning',
    };
    return badges[type] || 'badge-secondary';
  };

  if (loading && patients.length === 0) {
    return (
      <div className="loading-container">
        <p>Cargando pacientes...</p>
      </div>
    );
  }

  return (
    <div className="patients-list-page">
      <div className="page-header">
        <h1>Gestión de Pacientes</h1>
        <Link to="/patients/new" className="btn btn-primary">
          + Nuevo Paciente
        </Link>
      </div>

      {error && (
        <div className="alert alert-error">
          {error}
        </div>
      )}

      <div className="search-section">
        <form onSubmit={handleSearch} className="search-form">
          <input
            type="text"
            placeholder="Buscar por nombre, documento o email..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="search-input"
          />
          <button type="submit" className="btn btn-secondary">
            Buscar
          </button>
          {searchTerm && (
            <button
              type="button"
              onClick={() => {
                setSearchTerm('');
                fetchPatients();
              }}
              className="btn btn-outline"
            >
              Limpiar
            </button>
          )}
        </form>
      </div>

      <div className="patients-stats">
        <p>
          Mostrando <strong>{patients.length}</strong> de <strong>{pagination.total}</strong> pacientes
        </p>
      </div>

      <div className="table-container">
        <table className="patients-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Tipo Doc.</th>
              <th>N° Documento</th>
              <th>Nombre/Razón Social</th>
              <th>Email</th>
              <th>Teléfono</th>
              <th>Recurrente</th>
              <th>Visitas</th>
              <th>Acciones</th>
            </tr>
          </thead>
          <tbody>
            {patients.length === 0 ? (
              <tr>
                <td colSpan="9" className="text-center">
                  No se encontraron pacientes
                </td>
              </tr>
            ) : (
              patients.map((patient) => (
                <tr key={patient.id}>
                  <td>{patient.id}</td>
                  <td>
                    <span className={`badge ${getDocumentTypeBadge(patient.document_type)}`}>
                      {patient.document_type}
                    </span>
                  </td>
                  <td>{patient.document_number}</td>
                  <td>
                    {patient.document_type === 'RUC' ? (
                      <strong>{patient.business_name}</strong>
                    ) : (
                      `${patient.first_name} ${patient.last_name}`
                    )}
                  </td>
                  <td>{patient.email || '-'}</td>
                  <td>{patient.phone || '-'}</td>
                  <td>
                    {patient.is_recurrent ? (
                      <span className="badge badge-success">Sí</span>
                    ) : (
                      <span className="badge badge-secondary">No</span>
                    )}
                  </td>
                  <td>{patient.visit_count || 0}</td>
                  <td>
                    <div className="action-buttons">
                      <button
                        onClick={() => navigate(`/patients/${patient.id}/edit`)}
                        className="btn-icon btn-edit"
                        title="Editar"
                      >
                        ✏️
                      </button>
                      <button
                        onClick={() =>
                          handleDelete(
                            patient.id,
                            patient.business_name ||
                              `${patient.first_name} ${patient.last_name}`
                          )
                        }
                        className="btn-icon btn-delete"
                        title="Eliminar"
                      >
                        🗑️
                      </button>
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

export default PatientsListPage;
