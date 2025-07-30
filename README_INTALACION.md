# Sistema de Inventario INEI - Censos Nacionales 2025

## 🚀 Instalación y Configuración

### Requisitos Previos

- **Node.js** (versión 16 o superior)
- **Python** (versión 3.8 o superior)
- **MongoDB** (local o en la nube)
- **Git**

### 1. Estructura del Proyecto

```
proyecto-inventario-inei/
├── backend/
│   ├── server.py
│   ├── requirements.txt
│   ├── .env
│   └── README.md
├── frontend/
│   ├── src/
│   │   ├── App.js
│   │   ├── App.css
│   │   └── index.js
│   ├── public/
│   ├── package.json
│   ├── .env
│   └── README.md
└── README.md
```

### 2. Configuración del Backend

#### 2.1 Navegar al directorio backend
```bash
cd backend
```

#### 2.2 Crear entorno virtual
```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

#### 2.3 Instalar dependencias
```bash
pip install -r requirements.txt
```

#### 2.4 Configurar variables de entorno
Crear archivo `.env` en el directorio backend:
```env
MONGO_URL=mongodb://localhost:27017
DB_NAME=inei_inventario
```

#### 2.5 Ejecutar el servidor
```bash
uvicorn server:app --host 0.0.0.0 --port 8001 --reload
```

### 3. Configuración del Frontend

#### 3.1 Navegar al directorio frontend
```bash
cd frontend
```

#### 3.2 Instalar dependencias
```bash
npm install
# o
yarn install
```

#### 3.3 Configurar variables de entorno
Crear archivo `.env` en el directorio frontend:
```env
REACT_APP_BACKEND_URL=http://localhost:8001
```

#### 3.4 Ejecutar la aplicación
```bash
npm start
# o
yarn start
```

### 4. Configuración de MongoDB

#### 4.1 MongoDB Local
```bash
# Instalar MongoDB
# En Ubuntu/Debian:
sudo apt-get install mongodb

# En macOS:
brew install mongodb

# En Windows:
# Descargar e instalar desde https://www.mongodb.com/try/download/community
```

#### 4.2 MongoDB en la Nube (MongoDB Atlas)
1. Crear cuenta en [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)
2. Crear cluster gratuito
3. Obtener string de conexión
4. Actualizar `MONGO_URL` en `.env`

### 5. Funcionalidades del Sistema

#### 5.1 Dashboard Principal
- Estadísticas en tiempo real
- Gráficos de equipos por tipo
- Historial de reparaciones

#### 5.2 Registro de Responsables
- Validación de DNI (8 dígitos)
- Dropdowns para email (@gmail.com, @yahoo.com, etc.)
- Checkboxes para accesorios
- Control de estado y robos

#### 5.3 Búsqueda Avanzada
- Filtros múltiples
- Búsqueda por texto
- Filtros por estado y robo

#### 5.4 Inventario Completo
- Tabla con todos los registros
- Edición inline
- Eliminación individual o masiva
- Exportación a Excel (.xlsx)
- Importación desde Excel

#### 5.5 Historial de Reparaciones
- Registro de equipos en reparación
- Estados de reparación
- Motivos y fechas

### 6. Exportación/Importación Excel

#### 6.1 Formato de Exportación
El sistema exporta archivos Excel (.xlsx) con las siguientes columnas:
- ID, Persona, DNI, Dispositivo
- Control Patrimonial, Modelo, Número de Serie
- IMEI, Funda Tablet, Plan de Datos, Power Tech
- Teléfono, Correo Personal, Fecha de Entrega
- Estado, Robado, Motivo Reparación

#### 6.2 Formato de Importación
Para importar datos, usar el mismo formato de Excel exportado.

### 7. Despliegue en Producción

#### 7.1 Backend
```bash
# Usar gunicorn para producción
pip install gunicorn
gunicorn server:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8001
```

#### 7.2 Frontend
```bash
# Construir para producción
npm run build
# o
yarn build

# Servir archivos estáticos con nginx o Apache
```

### 8. Configuración de Base de Datos

#### 8.1 Colecciones MongoDB
- `inventory`: Registros principales de inventario
- `repairs`: Historial de reparaciones

#### 8.2 Índices Recomendados
```javascript
// En MongoDB shell
db.inventory.createIndex({ "dni": 1 }, { unique: true })
db.inventory.createIndex({ "dispositivo": 1 })
db.inventory.createIndex({ "estado": 1 })
db.repairs.createIndex({ "fecha_reparacion": -1 })
```

### 9. Solución de Problemas

#### 9.1 Errores Comunes
- **Puerto ocupado**: Cambiar puerto en configuración
- **MongoDB no conecta**: Verificar que MongoDB esté ejecutándose
- **CORS errors**: Verificar configuración de CORS en backend

#### 9.2 Logs
- Backend: Logs en consola al ejecutar uvicorn
- Frontend: Logs en consola del navegador (F12)

### 10. Seguridad

#### 10.1 Recomendaciones
- Usar HTTPS en producción
- Configurar autenticación si es necesario
- Validar todos los inputs
- Usar variables de entorno para secretos

### 11. Mantenimiento

#### 11.1 Backup de Base de Datos
```bash
# Backup MongoDB
mongodump --db inei_inventario --out backup/

# Restaurar MongoDB
mongorestore --db inei_inventario backup/inei_inventario/
```

#### 11.2 Actualizaciones
- Mantener dependencias actualizadas
- Revisar logs regularmente
- Monitorear rendimiento

### 12. Soporte

Para soporte técnico o consultas:
- Revisar logs de error
- Verificar configuración de variables de entorno
- Comprobar conectividad a MongoDB

---

## 📋 Características Implementadas

✅ **Tema oscuro** con acentos celestes (#00bcd4)
✅ **Dashboard con estadísticas** en tiempo real
✅ **Registro de responsables** con validación completa
✅ **Búsqueda avanzada** con múltiples filtros
✅ **Inventario completo** con edición y eliminación
✅ **Historial de reparaciones** editable
✅ **Exportación Excel** (.xlsx real)
✅ **Importación Excel** para carga masiva
✅ **Email con dominios** predefinidos
✅ **Control de robos** y estados
✅ **Validación de DNI** (8 dígitos)
✅ **Interfaz responsive** para móviles
✅ **API REST completa** con FastAPI
✅ **Base de datos MongoDB** con validaciones

## 🎯 Sistema Listo para Producción

El sistema está completamente funcional y listo para usar en entorno de producción del INEI - Censos Nacionales 2025.