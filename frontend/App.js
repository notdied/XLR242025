import React, { useState, useEffect, createContext, useContext } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate, useNavigate } from 'react-router-dom';
import axios from 'axios';
import { ToastContainer, toast } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import './App.css';

// Componentes
import LoginForm from './components/LoginForm';
import Dashboard from './components/Dashboard';
import InventoryManager from './components/InventoryManager';
import UserManagement from './components/UserManagement';
import AuditLogs from './components/AuditLogs';
import Navigation from './components/Navigation';
import LoadingSpinner from './components/LoadingSpinner';

// Context para autenticación
const AuthContext = createContext();

// Hook personalizado para autenticación
export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth debe ser usado dentro de AuthProvider');
  }
  return context;
};

// Configuración de axios
axios.defaults.baseURL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

// Interceptor para agregar token a todas las requests
axios.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Interceptor para manejar respuestas y errores
axios.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      toast.error('Sesión expirada. Por favor, inicie sesión nuevamente.');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Componente principal de la aplicación
function App() {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  // Verificar autenticación al cargar la app
  useEffect(() => {
    const checkAuth = async () => {
      try {
        const token = localStorage.getItem('token');
        const savedUser = localStorage.getItem('user');

        if (token && savedUser) {
          // Verificar que el token sea válido
          const response = await axios.get('/api/auth/me');
          setUser(JSON.parse(savedUser));
          setIsAuthenticated(true);
        }
      } catch (error) {
        console.error('Error verificando autenticación:', error);
        localStorage.removeItem('token');
        localStorage.removeItem('user');
      } finally {
        setLoading(false);
      }
    };

    checkAuth();
  }, []);

  // Función de login
  const login = async (credentials) => {
    try {
      const response = await axios.post('/api/auth/login', credentials);
      const { access_token, user: userData } = response.data;

      localStorage.setItem('token', access_token);
      localStorage.setItem('user', JSON.stringify(userData));
      
      setUser(userData);
      setIsAuthenticated(true);
      
      toast.success(`¡Bienvenido, ${userData.full_name}!`);
      return true;
    } catch (error) {
      const message = error.response?.data?.detail || 'Error al iniciar sesión';
      toast.error(message);
      throw error;
    }
  };

  // Función de logout
  const logout = async () => {
    try {
      await axios.post('/api/auth/logout');
    } catch (error) {
      console.error('Error al cerrar sesión:', error);
    } finally {
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      setUser(null);
      setIsAuthenticated(false);
      toast.info('Sesión cerrada exitosamente');
    }
  };

  // Componente de ruta protegida
  const ProtectedRoute = ({ children, requiredRole = null }) => {
    if (!isAuthenticated) {
      return <Navigate to="/login" replace />;
    }

    if (requiredRole && user?.role !== requiredRole) {
      toast.error('No tienes permisos para acceder a esta sección');
      return <Navigate to="/dashboard" replace />;
    }

    return children;
  };

  if (loading) {
    return <LoadingSpinner />;
  }

  const authValue = {
    user,
    isAuthenticated,
    login,
    logout
  };

  return (
    <AuthContext.Provider value={authValue}>
      <Router>
        <div className="App">
          {isAuthenticated && <Navigation />}
          
          <main className={`main-content ${isAuthenticated ? 'with-nav' : ''}`}>
            <Routes>
              <Route 
                path="/login" 
                element={
                  isAuthenticated ? 
                  <Navigate to="/dashboard" replace /> : 
                  <LoginForm />
                } 
              />
              
              <Route 
                path="/dashboard" 
                element={
                  <ProtectedRoute>
                    <Dashboard />
                  </ProtectedRoute>
                } 
              />
              
              <Route 
                path="/inventory" 
                element={
                  <ProtectedRoute>
                    <InventoryManager />
                  </ProtectedRoute>
                } 
              />
              
              <Route 
                path="/users" 
                element={
                  <ProtectedRoute requiredRole="admin">
                    <UserManagement />
                  </ProtectedRoute>
                } 
              />
              
              <Route 
                path="/audit" 
                element={
                  <ProtectedRoute requiredRole="admin">
                    <AuditLogs />
                  </ProtectedRoute>
                } 
              />
              
              <Route 
                path="/" 
                element={
                  isAuthenticated ? 
                  <Navigate to="/dashboard" replace /> : 
                  <Navigate to="/login" replace />
                } 
              />
            </Routes>
          </main>

          <ToastContainer
            position="top-right"
            autoClose={5000}
            hideProgressBar={false}
            newestOnTop={false}
            closeOnClick
            rtl={false}
            pauseOnFocusLoss
            draggable
            pauseOnHover
            theme="dark"
          />
        </div>
      </Router>
    </AuthContext.Provider>
  );
}

export default App;