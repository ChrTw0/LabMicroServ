/**
 * CategoriesPage Component
 * Gestión de categorías de servicios
 */
import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { useCatalog } from '../../hooks/useOrders';
import { catalogService } from '../../services';
import './CategoriesPage.css';

const CategoriesPage = () => {
  const { categories, loading, error, fetchCategories } = useCatalog();

  const [showModal, setShowModal] = useState(false);
  const [editingCategory, setEditingCategory] = useState(null);
  const [formData, setFormData] = useState({
    name: '',
    description: '',
  });
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    fetchCategories();
  }, []);

  const handleOpenModal = (category = null) => {
    if (category) {
      setEditingCategory(category);
      setFormData({
        name: category.name,
        description: category.description || '',
      });
    } else {
      setEditingCategory(null);
      setFormData({
        name: '',
        description: '',
      });
    }
    setShowModal(true);
  };

  const handleCloseModal = () => {
    setShowModal(false);
    setEditingCategory(null);
    setFormData({ name: '', description: '' });
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData({
      ...formData,
      [name]: value,
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!formData.name.trim()) {
      alert('El nombre es obligatorio');
      return;
    }

    setSubmitting(true);

    try {
      const categoryData = {
        name: formData.name.trim(),
        description: formData.description.trim() || null,
      };

      if (editingCategory) {
        // Actualizar categoría
        await catalogService.updateCategory(editingCategory.id, categoryData);
        alert('Categoría actualizada correctamente');
      } else {
        // Crear nueva categoría
        await catalogService.createCategory(categoryData);
        alert('Categoría creada correctamente');
      }

      handleCloseModal();
      await fetchCategories();
    } catch (err) {
      alert(`Error: ${err.message}`);
    } finally {
      setSubmitting(false);
    }
  };

  const handleDelete = async (categoryId, categoryName) => {
    if (!window.confirm(`¿Está seguro de eliminar la categoría "${categoryName}"?`)) {
      return;
    }

    try {
      await catalogService.deleteCategory(categoryId);
      alert('Categoría eliminada correctamente');
      await fetchCategories();
    } catch (err) {
      alert(`Error al eliminar: ${err.message}`);
    }
  };

  if (loading && categories.length === 0) {
    return (
      <div className="loading-container">
        <p>Cargando categorías...</p>
      </div>
    );
  }

  return (
    <div className="categories-page">
      <div className="page-header">
        <div>
          <Link to="/dashboard/catalog" className="btn-back">← Volver al Catálogo</Link>
          <h1>Gestión de Categorías</h1>
        </div>
        <button onClick={() => handleOpenModal()} className="btn btn-primary">
          + Nueva Categoría
        </button>
      </div>

      {error && (
        <div className="alert alert-error">
          {error}
        </div>
      )}

      <div className="categories-grid">
        {categories.length === 0 ? (
          <div className="empty-state">
            <p>No hay categorías registradas</p>
            <button onClick={() => handleOpenModal()} className="btn btn-primary">
              Crear Primera Categoría
            </button>
          </div>
        ) : (
          categories.map((category) => (
            <div key={category.id} className="category-card">
              <div className="category-header">
                <h3>{category.name}</h3>
                <div className="category-actions">
                  <button
                    onClick={() => handleOpenModal(category)}
                    className="btn-icon btn-edit"
                    title="Editar"
                  >
                    ✏️
                  </button>
                  <button
                    onClick={() => handleDelete(category.id, category.name)}
                    className="btn-icon btn-delete"
                    title="Eliminar"
                  >
                    🗑️
                  </button>
                </div>
              </div>
              {category.description && (
                <p className="category-description">{category.description}</p>
              )}
              <div className="category-footer">
                <span className="category-id">ID: {category.id}</span>
              </div>
            </div>
          ))
        )}
      </div>

      {/* Modal de Crear/Editar */}
      {showModal && (
        <div className="modal-overlay" onClick={handleCloseModal}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <h2>{editingCategory ? 'Editar Categoría' : 'Nueva Categoría'}</h2>
            <form onSubmit={handleSubmit}>
              <div className="form-group">
                <label>Nombre: *</label>
                <input
                  type="text"
                  name="name"
                  value={formData.name}
                  onChange={handleChange}
                  placeholder="Ej: Hematología"
                  className="form-control"
                  required
                  autoFocus
                />
              </div>
              <div className="form-group">
                <label>Descripción:</label>
                <textarea
                  name="description"
                  value={formData.description}
                  onChange={handleChange}
                  placeholder="Descripción de la categoría..."
                  className="form-control"
                  rows="3"
                />
              </div>
              <div className="modal-actions">
                <button
                  type="submit"
                  className="btn btn-primary"
                  disabled={submitting}
                >
                  {submitting ? 'Guardando...' : editingCategory ? 'Actualizar' : 'Crear'}
                </button>
                <button
                  type="button"
                  onClick={handleCloseModal}
                  className="btn btn-outline"
                  disabled={submitting}
                >
                  Cancelar
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {loading && (
        <div className="loading-overlay">
          <p>Cargando...</p>
        </div>
      )}
    </div>
  );
};

export default CategoriesPage;
