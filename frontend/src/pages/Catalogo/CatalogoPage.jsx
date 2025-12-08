/**
 * CatalogoPage Component
 * Página de Inicio (Landing Page) del Laboratorio Clínico.
 */
import { useNavigate } from 'react-router-dom';
import './CatalogoPage.css';

const CatalogoPage = () => {
  const navigate = useNavigate();

  const handleRedirect = () => {
    navigate('/login');
  };

  return (
    <div className="catalogo-page">
      {/* TopNavBar */}
      <header className="catalogo-header">
        <div className="catalogo-header-content">
          <div className="logo-container">
            <div className="icon">🧪</div>
            <h2 className="title">Laboratorio Clínico</h2>
          </div>
          <div className="nav-links">
            <nav>
              <a href="#">Inicio</a>
              <a href="#">Servicios</a>
              <a href="#">Precios</a>
              <a href="#">Contacto</a>
              <a href="#">Ayuda</a>
            </nav>
            <button onClick={handleRedirect} className="login-button">
              <span>Iniciar Sesión</span>
            </button>
          </div>
          <div className="mobile-menu-button">
            <button>
              {/* Icono de menú, puedes usar un SVG o un span */}
              <span>☰</span>
            </button>
          </div>
        </div>
      </header>

      <main className="flex-1">
        {/* HeroSection */}
        <section className="hero-section">
          {/* El fondo con imagen se puede agregar aquí si es necesario */}
          <div>
            <h1 className="hero-title">Análisis clínicos precisos, resultados en tiempo récord</h1>
            <p className="hero-subtitle">Confíe en nuestro laboratorio certificado para diagnósticos confiables, con más de 100 pruebas disponibles.</p>
            <div className="hero-buttons">
              <button onClick={handleRedirect} className="btn btn-primary">
                <span>Generar Órdenes</span>
              </button>
              <button className="btn btn-secondary">
                <span>Contactar</span>
              </button>
            </div>
          </div>
        </section>

        {/* Services Section */}
        <section className="services-section">
          <div className="services-container">
            <h2 className="services-title">Nuestros Servicios</h2>
            <div className="services-grid">
              {/* Service Card 1 */}
              <div className="service-card">
                <div className="service-icon">🩸</div>
                <div className="service-content">
                  <h3>Hematología</h3>
                  <p>Hemograma, Plaquetas, VSG, Coagulación, Grupo Sanguíneo</p>
                </div>
                <div className="service-footer">
                  <button>
                    <span>Ver más</span>
                  </button>
                </div>
              </div>
              {/* Service Card 2 */}
              <div className="service-card">
                <div className="service-icon">🧪</div>
                <div className="service-content">
                  <h3>Bioquímica</h3>
                  <p>Glucosa, Colesterol, Triglicéridos, Función renal, Perfil hepático</p>
                </div>
                <div className="service-footer">
                  <button>
                    <span>Ver más</span>
                  </button>
                </div>
              </div>
              {/* Service Card 3 */}
              <div className="service-card">
                <div className="service-icon">🛡️</div>
                <div className="service-content">
                  <h3>Inmunología</h3>
                  <p>Anticuerpos, Marcadores tumorales, Alergias, Hormonas, Serología</p>
                </div>
                <div className="service-footer">
                  <button>
                    <span>Ver más</span>
                  </button>
                </div>
              </div>
              {/* Service Card 4 */}
              <div className="service-card">
                <div className="service-icon">🦠</div>
                <div className="service-content">
                  <h3>Microbiología</h3>
                  <p>Cultivos, Antibiogramas, Detección de patógenos, Uroanálisis</p>
                </div>
                <div className="service-footer">
                  <button>
                    <span>Ver más</span>
                  </button>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* Secondary CTA */}
        <section style={{ backgroundColor: '#1e40af', padding: '4rem 0', textAlign: 'center', color: 'white' }}>
          <div>
            <h2 style={{ fontSize: '1.875rem', fontWeight: '700' }}>¿Listo para agilizar sus diagnósticos?</h2>
            <p style={{ marginTop: '1rem', fontSize: '1.125rem', color: '#bfdbfe' }}>Acceda a su portal médico y genere órdenes en minutos.</p>
            <div style={{ marginTop: '2rem' }}>
              <button onClick={handleRedirect} className="btn btn-primary" style={{ backgroundColor: 'white', color: '#1e3fae', height: '3.5rem', padding: '0 1.75rem' }}>
                <span>Iniciar Sesión</span>
              </button>
            </div>
          </div>
        </section>
      </main>

      {/* El footer se puede añadir aquí con un estilo similar si es necesario */}
    </div>
  );
};

export default CatalogoPage;