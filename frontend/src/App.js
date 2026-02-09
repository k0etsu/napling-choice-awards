import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Link, useLocation } from 'react-router-dom';
import { Navbar, Container, Nav } from 'react-bootstrap';
import 'bootstrap/dist/css/bootstrap.min.css';
import './index.css';
import './App.css';
import Home from './components/Home';
import Admin from './components/Admin';
import Results from './components/Results';

function AppContent() {
  const [isDarkMode, setIsDarkMode] = useState(() => {
    const savedTheme = localStorage.getItem('darkMode');
    return savedTheme === 'true';
  });
  const [showScrollTop, setShowScrollTop] = useState(false);
  const [navbarExpanded, setNavbarExpanded] = useState(false);
  const location = useLocation();

  useEffect(() => {
    localStorage.setItem('darkMode', isDarkMode);
    if (isDarkMode) {
      document.body.classList.add('dark-mode');
    } else {
      document.body.classList.remove('dark-mode');
    }
  }, [isDarkMode]);

  useEffect(() => {
    const handleScroll = () => {
      setShowScrollTop(window.scrollY > 300);
    };

    const handleResize = () => {
      setShowScrollTop(window.scrollY > 300 && window.innerWidth < 992);
    };

    window.addEventListener('scroll', handleScroll);
    window.addEventListener('resize', handleResize);

    // Initial check
    handleScroll();
    handleResize();

    return () => {
      window.removeEventListener('scroll', handleScroll);
      window.removeEventListener('resize', handleResize);
    };
  }, []);

  const toggleDarkMode = () => {
    setIsDarkMode(!isDarkMode);
  };

  const scrollToTop = () => {
    window.scrollTo({
      top: 0,
      behavior: 'smooth'
    });
  };

  const handleHomeClick = () => {
    setNavbarExpanded(false);
  };

  const handleNavCollapse = () => {
    setNavbarExpanded(false);
  };

  return (
    <div className="App">
      <Navbar
        bg={isDarkMode ? "dark" : "light"}
        variant={isDarkMode ? "dark" : "light"}
        expand="lg"
        sticky="top"
        className="navbar-custom"
        expanded={navbarExpanded}
        onToggle={setNavbarExpanded}
      >
        <Container>
          <Navbar.Brand as={Link} to="/" onClick={handleHomeClick}>
            Napling Choice Awards
          </Navbar.Brand>
          <Navbar.Toggle aria-controls="basic-navbar-nav" />
          <Navbar.Collapse id="basic-navbar-nav">
            <Nav className="me-auto">
              <Nav.Link as={Link} to="/results" onClick={handleNavCollapse}>Results</Nav.Link>
              <Nav.Link as={Link} to="/admin" onClick={handleNavCollapse}>Admin</Nav.Link>
            </Nav>
            <Nav className="ms-auto">
              <Nav.Link
                onClick={toggleDarkMode}
                className="theme-toggle-navbar"
                title={isDarkMode ? 'Switch to light mode' : 'Switch to dark mode'}
              >
                {isDarkMode ? '🌙' : '☀️'}
              </Nav.Link>
            </Nav>
          </Navbar.Collapse>
        </Container>
      </Navbar>

      <main>
        <Container>
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/results" element={<Results />} />
            <Route path="/admin" element={<Admin />} />
          </Routes>
        </Container>
      </main>

      {/* Scroll to top button */}
      <button
        className={`scroll-to-top ${showScrollTop ? 'show' : ''}`}
        onClick={scrollToTop}
        title="Scroll to top"
        aria-label="Scroll to top"
      >
        ↑
      </button>

      <footer className="footer mt-auto py-3">
        <Container>
          <p className="text-center mb-0">
            © {new Date().getFullYear()} Napling Choice Awards. All rights reserved.
          </p>
        </Container>
      </footer>
    </div>
  );
}

function App() {
  return (
    <Router>
      <AppContent />
    </Router>
  );
}

export default App;
