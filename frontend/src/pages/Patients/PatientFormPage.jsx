/**
 * PatientFormPage Component
 * Formulario para crear/editar pacientes
 */
import { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { usePatients } from '../../hooks/usePatients';
import { patientService } from '../../services';
import './PatientFormPage.css';

const PatientFormPage = () => {
  const navigate = useNavigate();
  const { id } = useParams();
  const isEditMode = Boolean(id);

  const { createPatient, updatePatient } = usePatients();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const [formData, setFormData] = useState({
    document_type: 'DNI',
    document_number: '',
    first_name: '',
    last_name: '',
    business_name: '',
    email: '',
    phone: '',
    address: '',
  });

  // Cargar datos del paciente si estamos editando
  useEffect(() => {
    if (isEditMode) {
      loadPatientData();
    }
  }, [id]);

  const loadPatientData = async () => {
    setLoading(true);
    try {
      const patient = await patientService.getById(id);
      setFormData({
        document_type: patient.document_type || 'DNI',
        document_number: patient.document_number || '',
        first_name: patient.first_name || '',
        last_name: patient.last_name || '',
        business_name: patient.business_name || '',
        email: patient.email || '',
        phone: patient.phone || '',
        address: patient.address || '',
      });
    } catch (err) {
      setError('Error al cargar datos del paciente');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    // Validación básica
    if (!formData.document_number) {
      setError('El número de documento es obligatorio');
      setLoading(false);
      return;
    }

    if (formData.document_type === 'RUC' && !formData.business_name) {
      setError('La razón social es obligatoria para RUC');
      setLoading(false);
      return;
    }

    if (formData.document_type !== 'RUC' && (!formData.first_name || !formData.last_name)) {
      setError('El nombre y apellido son obligatorios');
      setLoading(false);
      return;
    }

    try {
      // Preparar datos según tipo de documento
      const dataToSend = {
        document_type: formData.document_type,
        document_number: formData.document_number,
        email: formData.email || null,
        phone: formData.phone || null,
        address: formData.address || null,
      };

      // Si es RUC, enviar business_name y omitir nombres personales
      if (formData.document_type === 'RUC') {
        dataToSend.business_name = formData.business_name;
      } else {
        // Si NO es RUC, enviar nombres personales y omitir business_name
        dataToSend.first_name = formData.first_name;
        dataToSend.last_name = formData.last_name;
      }

      let result;
      if (isEditMode) {
        result = await updatePatient(id, dataToSend);
      } else {
        result = await createPatient(dataToSend);
      }

      if (result.success) {
        alert(isEditMode ? 'Paciente actualizado correctamente' : 'Paciente creado correctamente');
        navigate('/dashboard/patients');
      } else {
        // Manejar errores de validación
        const errorMsg = typeof result.error === 'string'
          ? result.error
          : 'Error al guardar paciente. Revisa los datos ingresados.';
        setError(errorMsg);
        console.error('Error al guardar:', result);
      }
    } catch (err) {
      setError(err.message || 'Error al procesar la solicitud');
    } finally {
      setLoading(false);
    }
  };

  const isRUC = formData.document_type === 'RUC';

  if (loading && isEditMode && !formData.document_number) {
    return (
      <div className="loading-container">
        <p>Cargando datos del paciente...</p>
      </div>
    );
  }

  return (
    <div className="patient-form-page">
      <div className="form-header">
        <h1>{isEditMode ? 'Editar Paciente' : 'Nuevo Paciente'}</h1>
        <button onClick={() => navigate('/dashboard/patients')} className="btn btn-outline">
          ← Volver
        </button>
      </div>

      {error && (
        <div className="alert alert-error">
          {error}
        </div>
      )}

      <form onSubmit={handleSubmit} className="patient-form">
        <div className="form-section">
          <h3>Datos de Identificación</h3>

          <div className="form-row">
            <div className="form-group">
              <label htmlFor="document_type">Tipo de Documento *</label>
              <select
                id="document_type"
                name="document_type"
                value={formData.document_type}
                onChange={handleChange}
                required
                disabled={loading}
              >
                <option value="DNI">DNI</option>
                <option value="RUC">RUC</option>
                <option value="CE">Carnet de Extranjería</option>
                <option value="PASAPORTE">Pasaporte</option>
              </select>
            </div>

            <div className="form-group">
              <label htmlFor="document_number">N° de Documento *</label>
              <input
                type="text"
                id="document_number"
                name="document_number"
                value={formData.document_number}
                onChange={handleChange}
                placeholder={isRUC ? '20123456789' : '12345678'}
                required
                disabled={loading}
                maxLength={isRUC ? 11 : 20}
              />
            </div>
          </div>
        </div>

        <div className="form-section">
          <h3>{isRUC ? 'Datos de la Empresa' : 'Datos Personales'}</h3>

          {isRUC ? (
            <div className="form-group">
              <label htmlFor="business_name">Razón Social *</label>
              <input
                type="text"
                id="business_name"
                name="business_name"
                value={formData.business_name}
                onChange={handleChange}
                placeholder="Ej: Laboratorios Médicos S.A.C."
                required
                disabled={loading}
              />
            </div>
          ) : (
            <div className="form-row">
              <div className="form-group">
                <label htmlFor="first_name">Nombres *</label>
                <input
                  type="text"
                  id="first_name"
                  name="first_name"
                  value={formData.first_name}
                  onChange={handleChange}
                  placeholder="Juan"
                  required
                  disabled={loading}
                />
              </div>

              <div className="form-group">
                <label htmlFor="last_name">Apellidos *</label>
                <input
                  type="text"
                  id="last_name"
                  name="last_name"
                  value={formData.last_name}
                  onChange={handleChange}
                  placeholder="Pérez García"
                  required
                  disabled={loading}
                />
              </div>
            </div>
          )}
        </div>

        <div className="form-section">
          <h3>Datos de Contacto</h3>

          <div className="form-row">
            <div className="form-group">
              <label htmlFor="email">Email</label>
              <input
                type="email"
                id="email"
                name="email"
                value={formData.email}
                onChange={handleChange}
                placeholder="ejemplo@correo.com"
                disabled={loading}
              />
            </div>

            <div className="form-group">
              <label htmlFor="phone">Teléfono</label>
              <input
                type="tel"
                id="phone"
                name="phone"
                value={formData.phone}
                onChange={handleChange}
                placeholder="+51987654321"
                disabled={loading}
              />
            </div>
          </div>

          <div className="form-group">
            <label htmlFor="address">Dirección</label>
            <textarea
              id="address"
              name="address"
              value={formData.address}
              onChange={handleChange}
              placeholder="Av. Los Álamos 123, Lima"
              rows="3"
              disabled={loading}
            />
          </div>
        </div>

        <div className="form-actions">
          <button
            type="button"
            onClick={() => navigate('/dashboard/patients')}
            className="btn btn-outline"
            disabled={loading}
          >
            Cancelar
          </button>
          <button
            type="submit"
            className="btn btn-primary"
            disabled={loading}
          >
            {loading ? 'Guardando...' : isEditMode ? 'Actualizar' : 'Crear Paciente'}
          </button>
        </div>
      </form>
    </div>
  );
};

export default PatientFormPage;
