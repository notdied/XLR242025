import React, { useState, useEffect } from "react";
import "./App.css";
import axios from "axios";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Robot Animation Component
const AnimatedRobot = () => {
  return (
    <div className="robot-container">
      <div className="robot">
        <div className="robot-head">
          <div className="robot-eyes">
            <div className="robot-eye"></div>
            <div className="robot-eye"></div>
          </div>
          <div className="robot-smile"></div>
        </div>
        <div className="robot-body">
          <div className="robot-arm left-arm"></div>
          <div className="robot-arm right-arm"></div>
        </div>
      </div>
    </div>
  );
};

const HomePage = () => {
  const [currentView, setCurrentView] = useState('home');

  console.log('HomePage currentView:', currentView);

  const handleNavigation = (view) => {
    console.log('Navigating to:', view);
    setCurrentView(view);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      {/* Header */}
      <header className="bg-white shadow-lg">
        <div className="container mx-auto px-4 py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <img 
                src="https://images.unsplash.com/photo-1735498905712-3d9d9011a419?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NDQ2NDF8MHwxfHNlYXJjaHwyfHxQZXJ1JTIwc3RhdGlzdGljc3xlbnwwfHx8fDE3NTM1NDc2Mzl8MA&ixlib=rb-4.1.0&q=85"
                alt="INEI Logo" 
                className="h-16 w-16 object-cover rounded"
              />
              <div>
                <h1 className="text-2xl font-bold text-gray-800">INEI - Censos Nacionales 2025</h1>
                <p className="text-gray-600">Operador Informático - Sede Arequipa 06 Socabaya</p>
              </div>
            </div>
            <div className="text-right">
              <img 
                src="https://images.unsplash.com/photo-1717700300409-9cfe51e29671?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2NzR8MHwxfHNlYXJjaHwxfHxQZXJ1JTIwbWFwfGVufDB8fHx8MTc1MzU0NzY1NHww&ixlib=rb-4.1.0&q=85"
                alt="Mapa Arequipa" 
                className="h-16 w-24 object-cover rounded shadow"
              />
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-8">
        {currentView === 'home' && <HomeView setCurrentView={handleNavigation} />}
        {currentView === 'register' && <RegisterView setCurrentView={handleNavigation} />}
        {currentView === 'search' && <SearchView setCurrentView={handleNavigation} />}
        {currentView === 'inventory' && <InventoryView setCurrentView={handleNavigation} />}
      </main>
    </div>
  );
};

const HomeView = ({ setCurrentView }) => {
  return (
    <div className="text-center">
      <AnimatedRobot />
      
      <div className="mt-8 mb-12">
        <h2 className="text-3xl font-bold text-gray-800 mb-4">
          ¡Bienvenido al Sistema de Inventariado!
        </h2>
        <p className="text-lg text-gray-600">
          Gestiona el inventario de equipos del censo de manera eficiente
        </p>
      </div>

      <div className="grid md:grid-cols-3 gap-8 max-w-4xl mx-auto">
        {/* Register Card */}
        <button 
          onClick={() => setCurrentView('register')}
          className="bg-white rounded-lg shadow-lg p-8 cursor-pointer transform hover:scale-105 transition-transform w-full text-center"
        >
          <div className="text-4xl mb-4">👥</div>
          <h3 className="text-xl font-semibold text-gray-800 mb-2">Registrar Responsable</h3>
          <p className="text-gray-600">Registrar nuevos responsables y sus equipos asignados</p>
        </button>

        {/* Search Card */}
        <button 
          onClick={() => setCurrentView('search')}
          className="bg-white rounded-lg shadow-lg p-8 cursor-pointer transform hover:scale-105 transition-transform w-full text-center"
        >
          <div className="text-4xl mb-4">🔍</div>
          <h3 className="text-xl font-semibold text-gray-800 mb-2">Búsqueda</h3>
          <p className="text-gray-600">Buscar y filtrar registros por diferentes criterios</p>
        </button>

        {/* Inventory Card */}
        <button 
          onClick={() => {
            console.log('Inventory button clicked');
            setCurrentView('inventory');
          }}
          className="bg-white rounded-lg shadow-lg p-8 cursor-pointer transform hover:scale-105 transition-transform w-full text-center"
        >
          <div className="text-4xl mb-4">📋</div>
          <h3 className="text-xl font-semibold text-gray-800 mb-2">Inventario</h3>
          <p className="text-gray-600">Ver todos los registros y gestionar el inventario</p>
        </button>
      </div>
    </div>
  );
};

const RegisterView = ({ setCurrentView }) => {
  const [formData, setFormData] = useState({
    persona: '',
    dni: '',
    dispositivo: '',
    control_patrimonial: '',
    modelo: '',
    numero_serie: '',
    imei: '',
    funda_tablet: false,
    plan_datos: false,
    power_tech: false,
    telefono: '',
    correo_personal: '',
    estado: 'bien'
  });
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const handleInputChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');

    // Validate DNI
    if (!/^\d{8}$/.test(formData.dni)) {
      setError('El DNI debe tener exactamente 8 dígitos numéricos');
      return;
    }

    try {
      await axios.post(`${API}/inventory`, formData);
      setSuccess('Responsable registrado exitosamente');
      setFormData({
        persona: '',
        dni: '',
        dispositivo: '',
        control_patrimonial: '',
        modelo: '',
        numero_serie: '',
        imei: '',
        funda_tablet: false,
        plan_datos: false,
        power_tech: false,
        telefono: '',
        correo_personal: '',
        estado: 'bien'
      });
    } catch (error) {
      if (error.response?.status === 400) {
        setError('Persona ya registrada');
      } else {
        setError('Error al registrar responsable');
      }
    }
  };

  return (
    <div className="max-w-4xl mx-auto">
      <div className="flex items-center mb-6">
        <button 
          onClick={() => setCurrentView('home')}
          className="text-blue-600 hover:text-blue-800 mr-4"
        >
          ← Volver al inicio
        </button>
        <h2 className="text-2xl font-bold text-gray-800">Registrar Responsable</h2>
      </div>

      <div className="bg-white rounded-lg shadow-lg p-8">
        {error && (
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
            {error}
          </div>
        )}
        {success && (
          <div className="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded mb-4">
            {success}
          </div>
        )}

        <form onSubmit={handleSubmit} className="grid md:grid-cols-2 gap-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Persona</label>
            <input
              type="text"
              name="persona"
              value={formData.persona}
              onChange={handleInputChange}
              required
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">DNI</label>
            <input
              type="text"
              name="dni"
              value={formData.dni}
              onChange={handleInputChange}
              required
              maxLength="8"
              pattern="\d{8}"
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Dispositivo</label>
            <input
              type="text"
              name="dispositivo"
              value={formData.dispositivo}
              onChange={handleInputChange}
              required
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Control Patrimonial</label>
            <input
              type="text"
              name="control_patrimonial"
              value={formData.control_patrimonial}
              onChange={handleInputChange}
              required
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Modelo</label>
            <input
              type="text"
              name="modelo"
              value={formData.modelo}
              onChange={handleInputChange}
              required
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Número de Serie</label>
            <input
              type="text"
              name="numero_serie"
              value={formData.numero_serie}
              onChange={handleInputChange}
              required
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">IMEI</label>
            <input
              type="text"
              name="imei"
              value={formData.imei}
              onChange={handleInputChange}
              required
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Teléfono</label>
            <input
              type="text"
              name="telefono"
              value={formData.telefono}
              onChange={handleInputChange}
              required
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Correo Personal</label>
            <input
              type="email"
              name="correo_personal"
              value={formData.correo_personal}
              onChange={handleInputChange}
              required
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Estado del Equipo</label>
            <select
              name="estado"
              value={formData.estado}
              onChange={handleInputChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="bien">Bien</option>
              <option value="mal estado">Mal Estado</option>
            </select>
          </div>

          <div className="md:col-span-2">
            <div className="grid md:grid-cols-3 gap-4">
              <label className="flex items-center">
                <input
                  type="checkbox"
                  name="funda_tablet"
                  checked={formData.funda_tablet}
                  onChange={handleInputChange}
                  className="mr-2"
                />
                Funda para Tablet
              </label>

              <label className="flex items-center">
                <input
                  type="checkbox"
                  name="plan_datos"
                  checked={formData.plan_datos}
                  onChange={handleInputChange}
                  className="mr-2"
                />
                Plan de Datos
              </label>

              <label className="flex items-center">
                <input
                  type="checkbox"
                  name="power_tech"
                  checked={formData.power_tech}
                  onChange={handleInputChange}
                  className="mr-2"
                />
                Power Tech
              </label>
            </div>
          </div>

          <div className="md:col-span-2">
            <button
              type="submit"
              className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              Registrar Responsable
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

const SearchView = ({ setCurrentView }) => {
  const [searchData, setSearchData] = useState({
    persona: '',
    dni: '',
    dispositivo: '',
    control_patrimonial: '',
    modelo: '',
    numero_serie: '',
    imei: '',
    telefono: '',
    correo_personal: ''
  });
  const [results, setResults] = useState([]);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setSearchData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSearch = async (e) => {
    e.preventDefault();
    try {
      const response = await axios.post(`${API}/inventory/search`, searchData);
      setResults(response.data);
    } catch (error) {
      console.error('Error searching:', error);
    }
  };

  return (
    <div className="max-w-6xl mx-auto">
      <div className="flex items-center mb-6">
        <button 
          onClick={() => setCurrentView('home')}
          className="text-blue-600 hover:text-blue-800 mr-4"
        >
          ← Volver al inicio
        </button>
        <h2 className="text-2xl font-bold text-gray-800">Búsqueda de Registros</h2>
      </div>

      <div className="bg-white rounded-lg shadow-lg p-8 mb-8">
        <form onSubmit={handleSearch} className="grid md:grid-cols-3 gap-4">
          <input
            type="text"
            name="persona"
            placeholder="Persona"
            value={searchData.persona}
            onChange={handleInputChange}
            className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <input
            type="text"
            name="dni"
            placeholder="DNI"
            value={searchData.dni}
            onChange={handleInputChange}
            className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <input
            type="text"
            name="dispositivo"
            placeholder="Dispositivo"
            value={searchData.dispositivo}
            onChange={handleInputChange}
            className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <input
            type="text"
            name="control_patrimonial"
            placeholder="Control Patrimonial"
            value={searchData.control_patrimonial}
            onChange={handleInputChange}
            className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <input
            type="text"
            name="modelo"
            placeholder="Modelo"
            value={searchData.modelo}
            onChange={handleInputChange}
            className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <input
            type="text"
            name="numero_serie"
            placeholder="Número de Serie"
            value={searchData.numero_serie}
            onChange={handleInputChange}
            className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <input
            type="text"
            name="imei"
            placeholder="IMEI"
            value={searchData.imei}
            onChange={handleInputChange}
            className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <input
            type="text"
            name="telefono"
            placeholder="Teléfono"
            value={searchData.telefono}
            onChange={handleInputChange}
            className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <input
            type="text"
            name="correo_personal"
            placeholder="Correo Personal"
            value={searchData.correo_personal}
            onChange={handleInputChange}
            className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <button
            type="submit"
            className="bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            🔍 Buscar
          </button>
        </form>
      </div>

      {results.length > 0 && (
        <div className="bg-white rounded-lg shadow-lg overflow-hidden">
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Persona</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">DNI</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Dispositivo</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Modelo</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Estado</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Fecha Entrega</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {results.map((item) => (
                  <tr key={item.id}>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{item.persona}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{item.dni}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{item.dispositivo}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{item.modelo}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{item.estado}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {new Date(item.fecha_entrega).toLocaleString('es-ES')}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
};

const InventoryView = ({ setCurrentView }) => {
  const [inventory, setInventory] = useState([]);
  
  useEffect(() => {
    loadInventory();
  }, []);

  const loadInventory = async () => {
    try {
      const response = await axios.get(`${API}/inventory`);
      setInventory(response.data);
    } catch (error) {
      console.error('Error loading inventory:', error);
    }
  };

  const handleDeletePerson = async (dni) => {
    if (window.confirm('¿Está seguro de eliminar todos los registros de esta persona?')) {
      try {
        await axios.delete(`${API}/inventory/${dni}`);
        loadInventory();
      } catch (error) {
        console.error('Error deleting person:', error);
      }
    }
  };

  const handleDeleteAll = async () => {
    if (window.confirm('¿Está seguro de eliminar TODOS los registros? Esta acción no se puede deshacer.')) {
      try {
        await axios.delete(`${API}/inventory`);
        loadInventory();
      } catch (error) {
        console.error('Error deleting all records:', error);
      }
    }
  };

  const handleExportExcel = async () => {
    try {
      const response = await axios.get(`${API}/inventory/export`);
      const data = response.data.data;
      
      // Convert to CSV format for download
      const headers = Object.keys(data[0] || {});
      const csvContent = [
        headers.join(','),
        ...data.map(row => headers.map(header => `"${row[header] || ''}"`).join(','))
      ].join('\n');
      
      const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
      const link = document.createElement('a');
      link.href = URL.createObjectURL(blob);
      link.download = `inventario_${new Date().toISOString().split('T')[0]}.csv`;
      link.click();
    } catch (error) {
      console.error('Error exporting data:', error);
    }
  };

  return (
    <div className="max-w-7xl mx-auto">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center">
          <button 
            onClick={() => setCurrentView('home')}
            className="text-blue-600 hover:text-blue-800 mr-4"
          >
            ← Volver al inicio
          </button>
          <h2 className="text-2xl font-bold text-gray-800">Inventario Completo</h2>
        </div>
        
        <div className="flex space-x-4">
          <button
            onClick={handleExportExcel}
            className="bg-green-600 text-white px-4 py-2 rounded-md hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500"
          >
            📊 Exportar Excel
          </button>
          <button
            onClick={handleDeleteAll}
            className="bg-red-600 text-white px-4 py-2 rounded-md hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-red-500"
          >
            🗑️ Eliminar Todo
          </button>
        </div>
      </div>

      <div className="bg-white rounded-lg shadow-lg overflow-hidden">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Persona</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">DNI</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Dispositivo</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Control Pat.</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Modelo</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">N° Serie</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">IMEI</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Funda</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Plan Datos</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Power Tech</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Teléfono</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Correo</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Fecha Entrega</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Estado</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Acciones</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {inventory.map((item) => (
                <tr key={item.id}>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{item.persona}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{item.dni}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{item.dispositivo}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{item.control_patrimonial}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{item.modelo}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{item.numero_serie}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{item.imei}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {item.funda_tablet ? '✅' : '❌'}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {item.plan_datos ? '✅' : '❌'}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {item.power_tech ? '✅' : '❌'}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{item.telefono}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{item.correo_personal}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {new Date(item.fecha_entrega).toLocaleString('es-ES')}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    <span className={`px-2 py-1 rounded-full text-xs ${
                      item.estado === 'bien' 
                        ? 'bg-green-100 text-green-800' 
                        : 'bg-red-100 text-red-800'
                    }`}>
                      {item.estado}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    <button
                      onClick={() => handleDeletePerson(item.dni)}
                      className="text-red-600 hover:text-red-900"
                    >
                      🗑️
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        
        {inventory.length === 0 && (
          <div className="text-center py-8 text-gray-500">
            No hay registros en el inventario
          </div>
        )}
      </div>
    </div>
  );
};

function App() {
  return (
    <div className="App">
      <HomePage />
    </div>
  );
}

export default App;