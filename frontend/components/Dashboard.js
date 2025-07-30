import React, { useState, useEffect } from 'react';
import { 
  Chart as ChartJS, 
  CategoryScale, 
  LinearScale, 
  BarElement, 
  ArcElement,
  Title, 
  Tooltip, 
  Legend 
} from 'chart.js';
import { Bar, Doughnut } from 'react-chartjs-2';
import { 
  FaBoxes, 
  FaCheckCircle, 
  FaExclamationTriangle, 
  FaTools,
  FaThief,
  FaUsers,
  FaDownload,
  FaBell,
  FaRefresh
} from 'react-icons/fa';
import axios from 'axios';
import { toast } from 'react-toastify';
import './Dashboard.css';

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend
);

const Dashboard = () => {
  const [stats, setStats] = useState(null);
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  const fetchStats = async () => {
    try {
      const response = await axios.get('/api/stats');
      setStats(response.data);
    } catch (error) {
      console.error('Error cargando estadísticas:', error);
      toast.error('Error cargando estadísticas');
    }
  };

  const fetchAlerts = async () => {
    try {
      const response = await axios.get('/api/notifications/alerts');
      setAlerts(response.data.alerts);
    } catch (error) {
      console.error('Error cargando alertas:', error);
    }
  };

  useEffect(() => {
    const loadData = async () => {
      setLoading(true);
      await Promise.all([fetchStats(), fetchAlerts()]);
      setLoading(false);
    };

    loadData();
    
    // Actualizar cada 30 segundos
    const interval = setInterval(loadData, 30000);
    return () => clearInterval(interval);
  }, []);

  const handleRefresh = async () => {
    setRefreshing(true);
    await Promise.all([fetchStats(), fetchAlerts()]);
    setRefreshing(false);
    toast.success('Datos actualizados');
  };

  const handleExportPDF = async () => {
    try {
      const response = await axios.get('/api/reports/inventory/pdf', {
        responseType: 'blob'
      });
      
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `inventario_inei_${new Date().toISOString().split('T')[0]}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      
      toast.success('Reporte PDF descargado exitosamente');
    } catch (error) {
      console.error('Error descargando PDF:', error);
      toast.error('Error descargando reporte PDF');
    }
  };

  if (loading) {
    return (
      <div className="dashboard-loading">
        <div className="loading-spinner"></div>
        <p>Cargando dashboard...</p>
      </div>
    );
  }

  // Datos para gráficos
  const deviceChartData = {
    labels: Object.keys(stats?.devices_by_type || {}),
    datasets: [{
      label: 'Cantidad',
      data: Object.values(stats?.devices_by_type || {}),
      backgroundColor: [
        '#00bcd4',
        '#4caf50',
        '#ff9800',
        '#f44336',
        '#9c27b0',
        '#2196f3'
      ],
      borderColor: '#ffffff',
      borderWidth: 2
    }]
  };

  const statusChartData = {
    labels: ['Buen Estado', 'Mal Estado', 'En Reparación'],
    datasets: [{
      data: [
        stats?.items_bien || 0,
        stats?.items_mal_estado || 0,
        stats?.items_en_reparacion || 0
      ],
      backgroundColor: ['#4caf50', '#f44336', '#ff9800'],
      borderColor: '#ffffff',
      borderWidth: 2
    }]
  };

  const statCards = [
    { 
      title: 'Total Items', 
      value: stats?.total_items || 0, 
      icon: FaBoxes, 
      color: 'blue',
      subtitle: 'Equipos registrados'
    },
    { 
      title: 'Buen Estado', 
      value: stats?.items_bien || 0, 
      icon: FaCheckCircle, 
      color: 'green',
      subtitle: 'Equipos funcionales'
    },
    { 
      title: 'Mal Estado', 
      value: stats?.items_mal_estado || 0, 
      icon: FaExclamationTriangle, 
      color: 'red',
      subtitle: 'Requieren atención'
    },
    { 
      title: 'En Reparación', 
      value: stats?.items_en_reparacion || 0, 
      icon: FaTools, 
      color: 'orange',
      subtitle: 'En proceso'
    },
    { 
      title: 'Robados', 
      value: stats?.items_robados || 0, 
      icon: FaThief, 
      color: 'purple',
      subtitle: 'Reportados como robados'
    },
    { 
      title: 'Usuarios', 
      value: stats?.active_users || 0, 
      icon: FaUsers, 
      color: 'cyan',
      subtitle: 'Usuarios activos'
    }
  ];

  return (
    <div className="dashboard">
      <div className="dashboard-header">
        <div className="header-title">
          <h1>Dashboard - Sistema de Inventario INEI</h1>
          <p>Censos Nacionales 2025 - Monitoreo en Tiempo Real</p>
        </div>
        
        <div className="header-actions">
          <button 
            className="btn btn-secondary"
            onClick={handleRefresh}
            disabled={refreshing}
          >
            <FaRefresh className={refreshing ? 'spinning' : ''} />
            {refreshing ? 'Actualizando...' : 'Actualizar'}
          </button>
          
          <button 
            className="btn btn-primary"
            onClick={handleExportPDF}
          >
            <FaDownload />
            Reporte PDF
          </button>
        </div>
      </div>

      {/* Alertas del Sistema */}
      {alerts.length > 0 && (
        <div className="alerts-section">
          <h3><FaBell /> Alertas del Sistema</h3>
          <div className="alerts-grid">
            {alerts.map((alert, index) => (
              <div key={index} className={`alert alert-${alert.type}`}>
                <p>{alert.message}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Tarjetas de Estadísticas */}
      <div className="stats-grid">
        {statCards.map((card, index) => {
          const Icon = card.icon;
          return (
            <div key={index} className={`stat-card ${card.color}`}>
              <div className="stat-icon">
                <Icon />
              </div>
              <div className="stat-content">
                <h3>{card.value.toLocaleString()}</h3>
                <p className="stat-title">{card.title}</p>
                <small className="stat-subtitle">{card.subtitle}</small>
              </div>
            </div>
          );
        })}
      </div>

      {/* Gráficos */}
      <div className="charts-section">
        <div className="chart-container">
          <h3>Equipos por Tipo</h3>
          <div className="chart-wrapper">
            <Bar 
              data={deviceChartData}
              options={{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                  legend: {
                    display: false
                  }
                },
                scales: {
                  y: {
                    beginAtZero: true,
                    ticks: {
                      color: '#ffffff'
                    },
                    grid: {
                      color: '#444'
                    }
                  },
                  x: {
                    ticks: {
                      color: '#ffffff'
                    },
                    grid: {
                      color: '#444'
                    }
                  }
                }
              }}
            />
          </div>
        </div>

        <div className="chart-container">
          <h3>Estado de Equipos</h3>
          <div className="chart-wrapper">
            <Doughnut 
              data={statusChartData}
              options={{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                  legend: {
                    position: 'bottom',
                    labels: {
                      color: '#ffffff'
                    }
                  }
                }
              }}
            />
          </div>
        </div>
      </div>

      {/* Actividades Recientes */}
      <div className="recent-activities">
        <h3>Actividades Recientes</h3>
        <div className="activities-list">
          {stats?.recent_activities?.slice(0, 5).map((activity, index) => (
            <div key={index} className="activity-item">
              <div className="activity-info">
                <strong>{activity.username}</strong>
                <span className="activity-action">{activity.action}</span>
                <span className="activity-resource">{activity.resource_type}</span>
              </div>
              <div className="activity-time">
                {new Date(activity.timestamp).toLocaleString()}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Estado del Sistema */}
      <div className="system-health">
        <h3>Estado del Sistema</h3>
        <div className="health-grid">
          <div className="health-item">
            <span className="health-label">Base de Datos:</span>
            <span className={`health-status ${stats?.system_health?.database_connected ? 'online' : 'offline'}`}>
              {stats?.system_health?.database_connected ? 'Conectada' : 'Desconectada'}
            </span>
          </div>
          <div className="health-item">
            <span className="health-label">Último Backup:</span>
            <span className="health-value">
              {stats?.system_health?.last_backup ? 
                new Date(stats.system_health.last_backup).toLocaleString() : 
                'No disponible'
              }
            </span>
          </div>
          <div className="health-item">
            <span className="health-label">Uso de Disco:</span>
            <span className="health-value">{stats?.system_health?.disk_usage || 'N/A'}</span>
          </div>
          <div className="health-item">
            <span className="health-label">Tiempo Activo:</span>
            <span className="health-value">{stats?.system_health?.uptime || 'N/A'}</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard; 