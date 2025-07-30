import React, { useState } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '../App';
import { 
  FaHome, 
  FaBoxes, 
  FaUsers, 
  FaHistory, 
  FaSignOutAlt,
  FaUserCircle,
  FaBars,
  FaTimes,
  FaBell,
  FaCog
} from 'react-icons/fa';
import './Navigation.css';

const Navigation = () => {
  const { user, logout } = useAuth();
  const location = useLocation();
  const navigate = useNavigate();
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [showUserMenu, setShowUserMenu] = useState(false);

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  const toggleMenu = () => {
    setIsMenuOpen(!isMenuOpen);
  };

  const navItems = [
    { path: '/dashboard', icon: FaHome, label: 'Dashboard', roles: ['admin', 'operator', 'readonly'] },
    { path: '/inventory', icon: FaBoxes, label: 'Inventario', roles: ['admin', 'operator', 'readonly'] },
    { path: '/users', icon: FaUsers, label: 'Usuarios', roles: ['admin'] },
    { path: '/audit', icon: FaHistory, label: 'Auditoría', roles: ['admin'] }
  ];

  const visibleNavItems = navItems.filter(item => 
    item.roles.includes(user?.role)
  );

  return (
    <nav className="navigation">
      <div className="nav-header">
        <div className="nav-brand">
          <img src="/logo-inei-small.png" alt="INEI" className="nav-logo" />
          <span className="nav-title">INEI Inventory</span>
        </div>
        
        <button className="nav-toggle" onClick={toggleMenu}>
          {isMenuOpen ? <FaTimes /> : <FaBars />}
        </button>
      </div>

      <div className={`nav-content ${isMenuOpen ? 'open' : ''}`}>
        <ul className="nav-menu">
          {visibleNavItems.map((item) => {
            const Icon = item.icon;
            const isActive = location.pathname === item.path;
            
            return (
              <li key={item.path}>
                <Link
                  to={item.path}
                  className={`nav-link ${isActive ? 'active' : ''}`}
                  onClick={() => setIsMenuOpen(false)}
                >
                  <Icon className="nav-icon" />
                  <span>{item.label}</span>
                </Link>
              </li>
            );
          })}
        </ul>

        <div className="nav-user">
          <div className="user-info">
            <div 
              className="user-avatar"
              onClick={() => setShowUserMenu(!showUserMenu)}
            >
              <FaUserCircle />
            </div>
            
            {showUserMenu && (
              <div className="user-menu">
                <div className="user-details">
                  <h4>{user?.full_name}</h4>
                  <p>{user?.email}</p>
                  <span className={`role-badge ${user?.role}`}>
                    {user?.role?.toUpperCase()}
                  </span>
                </div>
                
                <div className="user-actions">
                  <button className="user-menu-item">
                    <FaCog /> Configuración
                  </button>
                  <button className="user-menu-item logout" onClick={handleLogout}>
                    <FaSignOutAlt /> Cerrar Sesión
                  </button>
                </div>
              </div>
            )}
          </div>
          
          <div className="nav-footer">
            <p className="sede-info">{user?.sede}</p>
            <p className="version-info">v2.0.0</p>
          </div>
        </div>
      </div>
    </nav>
  );
};

export default Navigation;