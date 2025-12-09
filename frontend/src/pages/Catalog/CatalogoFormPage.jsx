/**
 * CatalogoFormPage Component
 * Formulario para crear/editar servicios del catálogo
 */
import { useEffect, useState } from 'react';
import { useNavigate, useParams, Link } from 'react-router-dom';
import { useCatalog } from '../../hooks/useOrders';
import { catalogService } from '../../services';
import './CatalogoFormPage.css';

const CatalogoFormPage = () => {
  const navigate = useNavigate();
  const { id } = useParams();
  const isEditMode = Boolean(id);

  const { categories, loading: categoriesLoading, fetchCategories } = useCatalog();

  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState({
    code: '',
    name: '',
    description: '',
    category_id: '',
    price: '',
    is_active: true,
  });

  useEffect(() => {
    fetchCategories();

    if (isEditMode) {
      loadService();
    }
  }, [id]);

  const loadService = async () => {
    setLoading(true);
    try {
      const service = await catalogService.getServiceById(id);
      setFormData({
        code: service.code,
        name: service.name,
        description: service.description || '',
        category_id: service.category_id || '',
        price: service.current_price || service.price,
        is_active: service.is_active,
      });
    } catch (err) {
      alert(`Error al cargar servicio: ${err.message}`);
      navigate('/dashboard/catalog');
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData({
      ...formData,
      [name]: type === 'checkbox' ? checked : value,
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    // Validaciones
    if (!formData.code || !formData.name || !formData.price) {
      alert('Por favor complete todos los campos obligatorios');
      return;
    }

    const price = parseFloat(formData.price);
    if (isNaN(price) || price <= 0) {
      alert('El precio debe ser un número mayor a 0');
      return;
    }

    setLoading(true);

    try {
      const serviceData = {
        code: formData.code.trim(),
        name: formData.name.trim(),
        description: formData.description.trim() || null,
        category_id: formData.category_id ? parseInt(formData.category_id) : null,
        is_active: formData.is_active,
      };

      if (isEditMode) {
        // Actualizar servicio
        await catalogService.updateService(id, serviceData);

        // Si el precio cambió, actualizarlo también
        const currentService = await catalogService.getServiceById(id);
        const currentPrice = parseFloat(currentService.current_price || currentService.price);

        if (price !== currentPrice) {
          await catalogService.updatePrice(id, price);
        }

        alert('Servicio actualizado correctamente');
      } else {
        // Crear servicio nuevo
        const newServiceData = {
          ...serviceData,
          price: price,
        };
        await catalogService.createService(newServiceData);
        alert('Servicio creado correctamente');
      }

      navigate('/dashboard/catalog');
    } catch (err) {
      alert(`Error: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  if (loading && isEditMode) {
    return (
      <div className="loading-container">
        <p>Cargando servicio...</p>
      </div>
    );
  }

  return (
    <div className="catalogo-form-page">
      <div className="page-header">
        <div>
          <Link to="/dashboard/catalog" className="btn-back">← Volver</Link>
          <h1>{isEditMode ? 'Editar Servicio' : 'Nuevo Servicio'}</h1>
        </div>
      </div>

      <form onSubmit={handleSubmit}>
        <div className="form-card">
          <h2>Información del Servicio</h2>

          <div className="form-row">
            <div className="form-group">
              <label>Código: *</label>
              <input
                type="text"
                name="code"
                value={formData.code}
                onChange={handleChange}
                placeholder="Ej: HEM001"
                className="form-control"
                required
              />
              <small className="form-hint">Código único del servicio</small>
            </div>

            <div className="form-group">
              <label>Categoría:</label>
              <select
                name="category_id"
                value={formData.category_id}
                onChange={handleChange}
                className="form-control"
              >
                <option value="">Sin categoría</option>
                {categories.map((category) => (
                  <option key={category.id} value={category.id}>
                    {category.name}
                  </option>
                ))}
              </select>
            </div>
          </div>

          <div className="form-group">
            <label>Nombre: *</label>
            <input
              type="text"
              name="name"
              value={formData.name}
              onChange={handleChange}
              placeholder="Ej: Hemograma Completo"
              className="form-control"
              required
            />
          </div>

          <div className="form-group">
            <label>Descripción:</label>
            <textarea
              name="description"
              value={formData.description}
              onChange={handleChange}
              placeholder="Descripción detallada del servicio..."
              className="form-control"
              rows="4"
            />
          </div>

          <div className="form-row">
            <div className="form-group">
              <label>Precio: *</label>
              <input
                type="number"
                step="0.01"
                min="0"
                name="price"
                value={formData.price}
                onChange={handleChange}
                placeholder="0.00"
                className="form-control"
                required
              />
              <small className="form-hint">Precio en soles (S/)</small>
              {isEditMode && (
                <small className="form-hint-warning">
                  ⚠️ Cambiar el precio creará un registro en el historial
                </small>
              )}
            </div>

            <div className="form-group">
              <label className="checkbox-label">
                <input
                  type="checkbox"
                  name="is_active"
                  checked={formData.is_active}
                  onChange={handleChange}
                  className="checkbox-input"
                />
                <span>Servicio activo</span>
              </label>
              <small className="form-hint">
                Solo los servicios activos aparecerán en el catálogo de órdenes
              </small>
            </div>
          </div>
        </div>

        <div className="form-actions">
          <button
            type="submit"
            className="btn btn-primary btn-lg"
            disabled={loading || categoriesLoading}
          >
            {loading ? 'Guardando...' : isEditMode ? 'Actualizar Servicio' : 'Crear Servicio'}
          </button>
          <Link to="/dashboard/catalog" className="btn btn-outline btn-lg">
            Cancelar
          </Link>
        </div>
      </form>
    </div>
  );
};

export default CatalogoFormPage;
