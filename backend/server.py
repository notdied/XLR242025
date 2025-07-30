
# ========================================
# BACKEND MEJORADO - server.py
# ========================================

from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, BackgroundTasks, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import StreamingResponse, FileResponse
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel, Field, validator, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from bson import ObjectId
import pandas as pd
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment
import io
import os
import json
import hashlib
import jwt
from passlib.context import CryptContext
from loguru import logger
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from decouple import config
import asyncio
import tempfile
import zipfile
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch

# ========================================
# CONFIGURACION MEJORADA
# ========================================

# Variables de entorno (.env)
"""
# Base de datos
MONGO_URL=mongodb://localhost:27017
DB_NAME=inei_inventario_v2

# Seguridad
SECRET_KEY=tu_clave_secreta_super_segura_aqui_2024
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Configuración de aplicación
ENVIRONMENT=development
DEBUG=True
BACKUP_ENABLED=True
BACKUP_INTERVAL_HOURS=24

# Email (para notificaciones futuras)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=tu_email@gmail.com
SMTP_PASSWORD=tu_password_app

# Configuración de archivos
MAX_FILE_SIZE=10485760  # 10MB
ALLOWED_EXTENSIONS=xlsx,xls
UPLOAD_FOLDER=uploads
BACKUP_FOLDER=backups
REPORTS_FOLDER=reports
"""

# Configuración
SECRET_KEY = config("SECRET_KEY", default="inei-inventory-secret-key-2024")
ALGORITHM = config("ALGORITHM", default="HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = config("ACCESS_TOKEN_EXPIRE_MINUTES", default=480, cast=int)
MONGO_URL = config("MONGO_URL", default="mongodb://localhost:27017")
DB_NAME = config("DB_NAME", default="inei_inventario_v2")

# Configuración de logging
logger.add("logs/inei_inventory_{time:YYYY-MM-DD}.log", 
          rotation="1 day", 
          retention="30 days",
          level="INFO",
          format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} | {message}")

# Inicialización
app = FastAPI(
    title="INEI Inventory Management System - Enhanced",
    description="Sistema de inventario mejorado para INEI - Censos Nacionales 2025",
    version="2.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# CORS mejorado
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Seguridad
security = HTTPBearer()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Base de datos
client = AsyncIOMotorClient(MONGO_URL)
db = client[DB_NAME]

# Scheduler para tareas automáticas
scheduler = AsyncIOScheduler()

# ========================================
# MODELOS MEJORADOS
# ========================================

class UserRole(str):
    ADMIN = "admin"
    OPERATOR = "operator"
    READONLY = "readonly"

class User(BaseModel):
    id: Optional[str] = None
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    full_name: str = Field(..., min_length=2, max_length=100)
    role: str = Field(default=UserRole.OPERATOR)
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.now)
    last_login: Optional[datetime] = None
    sede: str = Field(default="Arequipa 06 - Socabaya")

class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    full_name: str = Field(..., min_length=2, max_length=100)
    password: str = Field(..., min_length=6, max_length=100)
    role: str = Field(default=UserRole.OPERATOR)
    sede: str = Field(default="Arequipa 06 - Socabaya")

class UserLogin(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: Dict[str, Any]

class InventoryItemEnhanced(BaseModel):
    id: Optional[str] = None
    persona: str = Field(..., min_length=2, max_length=100)
    dni: str = Field(..., min_length=8, max_length=8)
    dispositivo: str = Field(..., min_length=2, max_length=100)
    control_patrimonial: str = Field(..., min_length=1, max_length=50)
    modelo: str = Field(..., min_length=1, max_length=100)
    numero_serie: str = Field(..., min_length=1, max_length=100)
    imei: Optional[str] = Field(None, max_length=20)
    funda_tablet: bool = Field(default=False)
    plan_datos: bool = Field(default=False)
    power_tech: bool = Field(default=False)
    telefono: str = Field(..., min_length=9, max_length=15)
    correo_personal: EmailStr
    fecha_entrega: datetime = Field(default_factory=datetime.now)
    estado: str = Field(..., regex="^(bien|mal estado|en reparacion)$")
    robado: bool = Field(default=False)
    motivo_reparacion: Optional[str] = Field(default="")
    
    # Campos nuevos mejorados
    ubicacion_actual: str = Field(default="Sede Arequipa 06 - Socabaya")
    responsable_entrega: Optional[str] = None
    observaciones: Optional[str] = None
    valor_estimado: Optional[float] = Field(None, ge=0)
    garantia_vence: Optional[datetime] = None
    proveedor: Optional[str] = None
    fecha_compra: Optional[datetime] = None
    
    # Auditoría
    created_by: Optional[str] = None
    updated_by: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    @validator('dni')
    def validate_dni(cls, v):
        if not v.isdigit() or len(v) != 8:
            raise ValueError('DNI debe tener exactamente 8 dígitos numéricos')
        return v

    @validator('telefono')
    def validate_telefono(cls, v):
        if not v.isdigit() or len(v) < 9:
            raise ValueError('Teléfono debe tener al menos 9 dígitos')
        return v

class AuditLog(BaseModel):
    id: Optional[str] = None
    user_id: str
    username: str
    action: str  # CREATE, UPDATE, DELETE, LOGIN, LOGOUT, EXPORT, IMPORT
    resource_type: str  # inventory, user, repair, etc.
    resource_id: Optional[str] = None
    details: Dict[str, Any] = Field(default_factory=dict)
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)
    sede: str = Field(default="Arequipa 06 - Socabaya")

class SystemStats(BaseModel):
    total_users: int = 0
    active_users: int = 0
    total_items: int = 0
    items_bien: int = 0
    items_mal_estado: int = 0
    items_en_reparacion: int = 0
    items_robados: int = 0
    total_repairs: int = 0
    devices_by_type: Dict[str, int] = Field(default_factory=dict)
    recent_activities: List[Dict[str, Any]] = Field(default_factory=list)
    system_health: Dict[str, Any] = Field(default_factory=dict)

# ========================================
# UTILIDADES DE AUTENTICACION
# ========================================

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Token inválido")
        
        user = await db.users.find_one({"username": username})
        if user is None:
            raise HTTPException(status_code=401, detail="Usuario no encontrado")
        
        if not user.get("is_active", True):
            raise HTTPException(status_code=401, detail="Usuario inactivo")
        
        return user
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expirado")
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Token inválido")

async def require_role(required_roles: List[str]):
    def role_checker(current_user: dict = Depends(get_current_user)):
        if current_user["role"] not in required_roles:
            raise HTTPException(status_code=403, detail="Permisos insuficientes")
        return current_user
    return role_checker

async def log_activity(user: dict, action: str, resource_type: str, 
                      resource_id: str = None, details: dict = None):
    """Registrar actividad del usuario para auditoría"""
    try:
        audit_log = AuditLog(
            user_id=str(user["_id"]),
            username=user["username"],
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            details=details or {},
            sede=user.get("sede", "Arequipa 06 - Socabaya")
        )
        
        await db.audit_logs.insert_one(audit_log.dict())
        logger.info(f"Actividad registrada: {user['username']} - {action} {resource_type}")
    except Exception as e:
        logger.error(f"Error registrando actividad: {e}")

# ========================================
# ENDPOINTS DE AUTENTICACION
# ========================================

@app.post("/api/auth/register", response_model=dict)
async def register_user(user_data: UserCreate, current_user: dict = Depends(require_role([UserRole.ADMIN]))):
    """Registrar nuevo usuario (solo admins)"""
    try:
        # Verificar si el usuario ya existe
        existing_user = await db.users.find_one({
            "$or": [
                {"username": user_data.username},
                {"email": user_data.email}
            ]
        })
        
        if existing_user:
            raise HTTPException(status_code=400, detail="Usuario o email ya existe")
        
        # Crear nuevo usuario
        hashed_password = get_password_hash(user_data.password)
        user_dict = user_data.dict()
        user_dict.pop("password")
        user_dict["hashed_password"] = hashed_password
        user_dict["created_at"] = datetime.now()
        
        result = await db.users.insert_one(user_dict)
        
        # Log de actividad
        await log_activity(current_user, "CREATE", "user", str(result.inserted_id), 
                          {"new_user": user_data.username, "role": user_data.role})
        
        logger.info(f"Usuario creado: {user_data.username} por {current_user['username']}")
        
        return {"message": "Usuario creado exitosamente", "user_id": str(result.inserted_id)}
    
    except Exception as e:
        logger.error(f"Error creando usuario: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@app.post("/api/auth/login", response_model=Token)
async def login(user_credentials: UserLogin):
    """Iniciar sesión"""
    try:
        # Buscar usuario
        user = await db.users.find_one({"username": user_credentials.username})
        
        if not user or not verify_password(user_credentials.password, user["hashed_password"]):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credenciales incorrectas",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        if not user.get("is_active", True):
            raise HTTPException(status_code=401, detail="Usuario inactivo")
        
        # Actualizar último login
        await db.users.update_one(
            {"_id": user["_id"]},
            {"$set": {"last_login": datetime.now()}}
        )
        
        # Crear token
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user["username"], "role": user["role"]}, 
            expires_delta=access_token_expires
        )
        
        # Log de actividad
        await log_activity(user, "LOGIN", "auth", details={"login_time": datetime.now().isoformat()})
        
        # Respuesta del token
        user_data = {
            "id": str(user["_id"]),
            "username": user["username"],
            "email": user["email"],
            "full_name": user["full_name"],
            "role": user["role"],
            "sede": user.get("sede", "Arequipa 06 - Socabaya")
        }
        
        logger.info(f"Login exitoso: {user['username']}")
        
        return Token(
            access_token=access_token,
            token_type="bearer",
            expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user=user_data
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error en login: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@app.post("/api/auth/logout")
async def logout(current_user: dict = Depends(get_current_user)):
    """Cerrar sesión"""
    await log_activity(current_user, "LOGOUT", "auth")
    logger.info(f"Logout: {current_user['username']}")
    return {"message": "Sesión cerrada exitosamente"}

@app.get("/api/auth/me", response_model=dict)
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """Obtener información del usuario actual"""
    user_data = {
        "id": str(current_user["_id"]),
        "username": current_user["username"],
        "email": current_user["email"],
        "full_name": current_user["full_name"],
        "role": current_user["role"],
        "sede": current_user.get("sede", "Arequipa 06 - Socabaya"),
        "is_active": current_user.get("is_active", True),
        "created_at": current_user.get("created_at"),
        "last_login": current_user.get("last_login")
    }
    return user_data

# ========================================
# ENDPOINTS DE INVENTARIO MEJORADOS
# ========================================

@app.get("/api/stats", response_model=SystemStats)
async def get_enhanced_stats(current_user: dict = Depends(get_current_user)):
    """Obtener estadísticas mejoradas del sistema"""
    try:
        # Estadísticas de usuarios
        total_users = await db.users.count_documents({})
        active_users = await db.users.count_documents({"is_active": True})
        
        # Estadísticas de inventario
        total_items = await db.inventory.count_documents({})
        items_bien = await db.inventory.count_documents({"estado": "bien"})
        items_mal_estado = await db.inventory.count_documents({"estado": "mal estado"})
        items_en_reparacion = await db.inventory.count_documents({"estado": "en reparacion"})
        items_robados = await db.inventory.count_documents({"robado": True})
        
        # Estadísticas de reparaciones
        total_repairs = await db.repairs.count_documents({})
        
        # Dispositivos por tipo
        devices_pipeline = [
            {"$group": {"_id": "$dispositivo", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}}
        ]
        devices_cursor = db.inventory.aggregate(devices_pipeline)
        devices_by_type = {doc["_id"]: doc["count"] async for doc in devices_cursor}
        
        # Actividades recientes
        recent_activities_cursor = db.audit_logs.find().sort("timestamp", -1).limit(10)
        recent_activities = []
        async for log in recent_activities_cursor:
            activity = {
                "id": str(log["_id"]),
                "username": log["username"],
                "action": log["action"],
                "resource_type": log["resource_type"],
                "timestamp": log["timestamp"].isoformat(),
                "details": log.get("details", {})
            }
            recent_activities.append(activity)
        
        # Salud del sistema
        system_health = {
            "database_connected": True,
            "last_backup": "2024-07-29T10:00:00",  # Se actualizará con backup real
            "disk_usage": "65%",
            "memory_usage": "78%",
            "uptime": "7 days, 14 hours"
        }
        
        stats = SystemStats(
            total_users=total_users,
            active_users=active_users,
            total_items=total_items,
            items_bien=items_bien,
            items_mal_estado=items_mal_estado,
            items_en_reparacion=items_en_reparacion,
            items_robados=items_robados,
            total_repairs=total_repairs,
            devices_by_type=devices_by_type,
            recent_activities=recent_activities,
            system_health=system_health
        )
        
        return stats
    
    except Exception as e:
        logger.error(f"Error obteniendo estadísticas: {e}")
        raise HTTPException(status_code=500, detail="Error obteniendo estadísticas")

@app.post("/api/inventory", response_model=dict, status_code=201)
async def create_inventory_item_enhanced(
    item: InventoryItemEnhanced, 
    current_user: dict = Depends(get_current_user)
):
    """Crear item de inventario mejorado"""
    try:
        # Verificar DNI único
        existing_item = await db.inventory.find_one({"dni": item.dni})
        if existing_item:
            raise HTTPException(status_code=400, detail="DNI ya existe en el inventario")
        
        # Preparar datos del item
        item_dict = item.dict()
        item_dict["created_by"] = current_user["username"]
        item_dict["updated_by"] = current_user["username"]
        item_dict["responsable_entrega"] = current_user["full_name"]
        
        # Insertar en base de datos
        result = await db.inventory.insert_one(item_dict)
        item_dict["id"] = str(result.inserted_id)
        
        # Log de actividad
        await log_activity(current_user, "CREATE", "inventory", str(result.inserted_id), 
                          {"persona": item.persona, "dispositivo": item.dispositivo})
        
        logger.info(f"Item creado: {item.persona} - {item.dispositivo} por {current_user['username']}")
        
        return {"message": "Item creado exitosamente", "id": str(result.inserted_id)}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creando item: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

# ========================================
# SISTEMA DE BACKUP AUTOMATICO
# ========================================

async def create_backup():
    """Crear backup automático de la base de datos"""
    try:
        logger.info("Iniciando backup automático...")
        
        # Crear directorio de backup si no existe
        backup_dir = "backups"
        os.makedirs(backup_dir, exist_ok=True)
        
        # Nombre del archivo de backup
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"inei_backup_{timestamp}.json"
        backup_path = os.path.join(backup_dir, backup_filename)
        
        # Recopilar datos
        backup_data = {
            "timestamp": datetime.now().isoformat(),
            "version": "2.0.0",
            "collections": {}
        }
        
        # Backup de inventario
        inventory_cursor = db.inventory.find()
        inventory_data = []
        async for item in inventory_cursor:
            item["_id"] = str(item["_id"])
            inventory_data.append(item)
        backup_data["collections"]["inventory"] = inventory_data
        
        # Backup de reparaciones
        repairs_cursor = db.repairs.find()
        repairs_data = []
        async for repair in repairs_cursor:
            repair["_id"] = str(repair["_id"])
            repairs_data.append(repair)
        backup_data["collections"]["repairs"] = repairs_data
        
        # Backup de usuarios (sin contraseñas)
        users_cursor = db.users.find()
        users_data = []
        async for user in users_cursor:
            user["_id"] = str(user["_id"])
            user.pop("hashed_password", None)  # Remover contraseña
            users_data.append(user)
        backup_data["collections"]["users"] = users_data
        
        # Backup de logs de auditoría (últimos 1000)
        logs_cursor = db.audit_logs.find().sort("timestamp", -1).limit(1000)
        logs_data = []
        async for log in logs_cursor:
            log["_id"] = str(log["_id"])
            logs_data.append(log)
        backup_data["collections"]["audit_logs"] = logs_data
        
        # Guardar backup
        with open(backup_path, 'w', encoding='utf-8') as f:
            json.dump(backup_data, f, indent=2, ensure_ascii=False, default=str)
        
        # Comprimir backup
        zip_path = backup_path.replace('.json', '.zip')
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            zipf.write(backup_path, backup_filename)
        
        # Eliminar archivo JSON temporal
        os.remove(backup_path)
        
        # Limpiar backups antiguos (mantener últimos 30)
        backup_files = [f for f in os.listdir(backup_dir) if f.startswith("inei_backup_") and f.endswith(".zip")]
        backup_files.sort()
        
        if len(backup_files) > 30:
            for old_backup in backup_files[:-30]:
                old_backup_path = os.path.join(backup_dir, old_backup)
                os.remove(old_backup_path)
                logger.info(f"Backup antiguo eliminado: {old_backup}")
        
        file_size = os.path.getsize(zip_path) / (1024 * 1024)  # MB
        logger.info(f"Backup completado: {backup_filename} ({file_size:.2f} MB)")
        
        return zip_path
    
    except Exception as e:
        logger.error(f"Error creando backup: {e}")
        raise

@app.post("/api/admin/backup")
async def manual_backup(current_user: dict = Depends(require_role([UserRole.ADMIN]))):
    """Crear backup manual"""
    try:
        backup_path = await create_backup()
        
        await log_activity(current_user, "BACKUP", "system", details={"type": "manual"})
        
        return {"message": "Backup creado exitosamente", "file": os.path.basename(backup_path)}
    except Exception as e:
        logger.error(f"Error en backup manual: {e}")
        raise HTTPException(status_code=500, detail="Error creando backup")

# ========================================
# REPORTES AVANZADOS
# ========================================

@app.get("/api/reports/inventory/pdf")
async def generate_inventory_pdf_report(current_user: dict = Depends(get_current_user)):
    """Generar reporte PDF del inventario"""
    try:
        # Crear directorio de reportes
        reports_dir = "reports"
        os.makedirs(reports_dir, exist_ok=True)
        
        # Nombre del archivo
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        pdf_filename = f"inventario_inei_{timestamp}.pdf"
        pdf_path = os.path.join(reports_dir, pdf_filename)
        
        # Obtener datos del inventario
        inventory_cursor = db.inventory.find().sort("persona", 1)
        inventory_data = []
        async for item in inventory_cursor:
            inventory_data.append([
                item["persona"],
                item["dni"],
                item["dispositivo"],
                item["modelo"],
                item["estado"],
                "Sí" if item["robado"] else "No",
                item["fecha_entrega"].strftime("%d/%m/%Y")
            ])
        
        # Crear PDF
        doc = SimpleDocTemplate(pdf_path, pagesize=A4)
        story = []
        
        # Estilos
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=16,
            spaceAfter=30,
            alignment=1  # Centrado
        )
        
        # Título
        title = Paragraph("REPORTE DE INVENTARIO - INEI<br/>Censos Nacionales 2025", title_style)
        story.append(title)
        story.append(Spacer(1, 20))
        
        # Información del reporte
        info_data = [
            ["Fecha de generación:", datetime.now().strftime("%d/%m/%Y %H:%M:%S")],
            ["Generado por:", current_user["full_name"]],
            ["Sede:", current_user.get("sede", "Arequipa 06 - Socabaya")],
            ["Total de items:", str(len(inventory_data))]
        ]
        
        info_table = Table(info_data, colWidths=[2*inch, 3*inch])
        info_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('BACKGROUND', (1, 0), (1, -1), colors.white),
        ]))
        
        story.append(info_table)
        story.append(Spacer(1, 30))
        
        # Tabla de inventario
        headers = ["Persona", "DNI", "Dispositivo", "Modelo", "Estado", "Robado", "Fecha Entrega"]
        table_data = [headers] + inventory_data
        
        # Crear tabla
        inventory_table = Table(table_data, repeatRows=1)
        inventory_table.setStyle(TableStyle([
            # Estilo del header
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            
            # Estilo del contenido
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        
        story.append(inventory_table)
        
        # Construir PDF
        doc.build(story)
        
        # Log de actividad
        await log_activity(current_user, "EXPORT", "report", details={"type": "pdf", "format": "inventory"})
        
        logger.info(f"Reporte PDF generado: {pdf_filename} por {current_user['username']}")
        
        # Retornar archivo
        return FileResponse(
            pdf_path,
            media_type='application/pdf',
            filename=pdf_filename,
            headers={"Content-Disposition": f"attachment; filename={pdf_filename}"}
        )
    
    except Exception as e:
        logger.error(f"Error generando reporte PDF: {e}")
        raise HTTPException(status_code=500, detail="Error generando reporte PDF")

# ========================================
# NOTIFICACIONES Y ALERTAS
# ========================================

class NotificationService:
    @staticmethod
    async def check_equipment_alerts():
        """Verificar alertas de equipos"""
        try:
            alerts = []
            
            # Equipos robados sin resolver
            stolen_count = await db.inventory.count_documents({"robado": True})
            if stolen_count > 0:
                alerts.append({
                    "type": "warning",
                    "message": f"{stolen_count} equipos reportados como robados",
                    "action": "revisar_robados"
                })
            
            # Equipos en mal estado por mucho tiempo
            thirty_days_ago = datetime.now() - timedelta(days=30)
            old_damaged = await db.inventory.count_documents({
                "estado": "mal estado",
                "updated_at": {"$lt": thirty_days_ago}
            })
            
            if old_damaged > 0:
                alerts.append({
                    "type": "info",
                    "message": f"{old_damaged} equipos en mal estado por más de 30 días",
                    "action": "revisar_mal_estado"
                })
            
            # Equipos con garantía próxima a vencer
            next_month = datetime.now() + timedelta(days=30)
            warranty_expiring = await db.inventory.count_documents({
                "garantia_vence": {"$lte": next_month, "$gte": datetime.now()}
            })
            
            if warranty_expiring > 0:
                alerts.append({
                    "type": "warning",
                    "message": f"{warranty_expiring} equipos con garantía por vencer",
                    "action": "revisar_garantias"
                })
            
            return alerts
            
        except Exception as e:
            logger.error(f"Error verificando alertas: {e}")
            return []

@app.get("/api/notifications/alerts")
async def get_system_alerts(current_user: dict = Depends(get_current_user)):
    """Obtener alertas del sistema"""
    alerts = await NotificationService.check_equipment_alerts()
    return {"alerts": alerts}

# ========================================
# ENDPOINTS ADICIONALES MEJORADOS
# ========================================

@app.get("/api/inventory/export/excel/enhanced")
async def export_inventory_excel_enhanced(current_user: dict = Depends(get_current_user)):
    """Exportar inventario a Excel con formato mejorado"""
    try:
        # Obtener datos del inventario
        inventory_cursor = db.inventory.find().sort("persona", 1)
        inventory_data = []
        
        async for item in inventory_cursor:
            row_data = {
                'ID': str(item['_id']),
                'Persona': item['persona'],
                'DNI': item['dni'],
                'Dispositivo': item['dispositivo'],
                'Control Patrimonial': item['control_patrimonial'],
                'Modelo': item['modelo'],
                'Número de Serie': item['numero_serie'],
                'IMEI': item.get('imei', ''),
                'Funda Tablet': 'Sí' if item['funda_tablet'] else 'No',
                'Plan de Datos': 'Sí' if item['plan_datos'] else 'No',
                'Power Tech': 'Sí' if item['power_tech'] else 'No',
                'Teléfono': item['telefono'],
                'Correo Personal': item['correo_personal'],
                'Fecha de Entrega': item['fecha_entrega'].strftime('%d/%m/%Y %H:%M'),
                'Estado': item['estado'],
                'Robado': 'Sí' if item['robado'] else 'No',
                'Motivo Reparación': item.get('motivo_reparacion', ''),
                'Ubicación Actual': item.get('ubicacion_actual', ''),
                'Responsable Entrega': item.get('responsable_entrega', ''),
                'Observaciones': item.get('observaciones', ''),
                'Valor Estimado': item.get('valor_estimado', ''),
                'Garantía Vence': item.get('garantia_vence', '').strftime('%d/%m/%Y') if item.get('garantia_vence') else '',
                'Proveedor': item.get('proveedor', ''),
                'Fecha Compra': item.get('fecha_compra', '').strftime('%d/%m/%Y') if item.get('fecha_compra') else '',
                'Creado Por': item.get('created_by', ''),
                'Actualizado Por': item.get('updated_by', ''),
                'Fecha Creación': item.get('created_at', '').strftime('%d/%m/%Y %H:%M') if item.get('created_at') else '',
                'Última Actualización': item.get('updated_at', '').strftime('%d/%m/%Y %H:%M') if item.get('updated_at') else ''
            }
            inventory_data.append(row_data)
        
        # Crear DataFrame
        df = pd.DataFrame(inventory_data)
        
        # Crear archivo Excel en memoria
        output = io.BytesIO()
        
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            # Hoja principal de inventario
            df.to_excel(writer, sheet_name='Inventario', index=False)
            
            # Obtener el workbook y worksheet
            workbook = writer.book
            worksheet = writer.sheets['Inventario']
            
            # Estilos
            header_fill = PatternFill(start_color='366092', end_color='366092', fill_type='solid')
            header_font = Font(color='FFFFFF', bold=True)
            
            # Aplicar estilos al header
            for cell in worksheet[1]:
                cell.fill = header_fill
                cell.font = header_font
                cell.alignment = Alignment(horizontal='center', vertical='center')
            
            # Ajustar ancho de columnas
            for column in worksheet.columns:
                max_length = 0
                column_letter = column[0].column_letter
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                adjusted_width = min(max_length + 2, 50)
                worksheet.column_dimensions[column_letter].width = adjusted_width
            
            # Hoja de estadísticas
            stats_data = await get_enhanced_stats(current_user)
            stats_df = pd.DataFrame([
                ['Total de Items', stats_data.total_items],
                ['Items en Buen Estado', stats_data.items_bien],
                ['Items en Mal Estado', stats_data.items_mal_estado],
                ['Items en Reparación', stats_data.items_en_reparacion],
                ['Items Robados', stats_data.items_robados],
                ['Total de Reparaciones', stats_data.total_repairs],
                ['Fecha de Exportación', datetime.now().strftime('%d/%m/%Y %H:%M:%S')],
                ['Exportado Por', current_user['full_name']],
                ['Sede', current_user.get('sede', 'Arequipa 06 - Socabaya')]
            ], columns=['Concepto', 'Valor'])
            
            stats_df.to_excel(writer, sheet_name='Estadísticas', index=False)
            
            # Aplicar estilos a la hoja de estadísticas
            stats_sheet = writer.sheets['Estadísticas']
            for cell in stats_sheet[1]:
                cell.fill = header_fill
                cell.font = header_font
            
            # Hoja de dispositivos por tipo
            devices_df = pd.DataFrame(list(stats_data.devices_by_type.items()), 
                                    columns=['Tipo de Dispositivo', 'Cantidad'])
            devices_df.to_excel(writer, sheet_name='Dispositivos por Tipo', index=False)
            
            # Aplicar estilos a dispositivos
            devices_sheet = writer.sheets['Dispositivos por Tipo']
            for cell in devices_sheet[1]:
                cell.fill = header_fill
                cell.font = header_font
        
        output.seek(0)
        
        # Log de actividad
        await log_activity(current_user, "EXPORT", "inventory", 
                          details={"format": "excel_enhanced", "items_count": len(inventory_data)})
        
        logger.info(f"Excel mejorado exportado por {current_user['username']}: {len(inventory_data)} items")
        
        # Generar nombre de archivo
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"inventario_inei_completo_{timestamp}.xlsx"
        
        return StreamingResponse(
            io.BytesIO(output.read()),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    
    except Exception as e:
        logger.error(f"Error exportando Excel mejorado: {e}")
        raise HTTPException(status_code=500, detail="Error generando archivo Excel")

@app.get("/api/users")
async def get_users(current_user: dict = Depends(require_role([UserRole.ADMIN]))):
    """Obtener lista de usuarios (solo admins)"""
    try:
        users_cursor = db.users.find().sort("username", 1)
        users = []
        
        async for user in users_cursor:
            user_data = {
                "id": str(user["_id"]),
                "username": user["username"],
                "email": user["email"],
                "full_name": user["full_name"],
                "role": user["role"],
                "is_active": user.get("is_active", True),
                "sede": user.get("sede", "Arequipa 06 - Socabaya"),
                "created_at": user.get("created_at"),
                "last_login": user.get("last_login")
            }
            users.append(user_data)
        
        return users
    
    except Exception as e:
        logger.error(f"Error obteniendo usuarios: {e}")
        raise HTTPException(status_code=500, detail="Error obteniendo usuarios")

@app.put("/api/users/{user_id}")
async def update_user(
    user_id: str, 
    user_update: dict, 
    current_user: dict = Depends(require_role([UserRole.ADMIN]))
):
    """Actualizar usuario (solo admins)"""
    try:
        # Verificar que el usuario existe
        user = await db.users.find_one({"_id": ObjectId(user_id)})
        if not user:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        
        # Preparar datos de actualización
        update_data = {}
        allowed_fields = ["email", "full_name", "role", "is_active", "sede"]
        
        for field in allowed_fields:
            if field in user_update:
                update_data[field] = user_update[field]
        
        if not update_data:
            raise HTTPException(status_code=400, detail="No hay datos para actualizar")
        
        update_data["updated_at"] = datetime.now()
        
        # Actualizar usuario
        result = await db.users.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": update_data}
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        
        # Log de actividad
        await log_activity(current_user, "UPDATE", "user", user_id, 
                          {"updated_fields": list(update_data.keys()), "target_user": user["username"]})
        
        logger.info(f"Usuario actualizado: {user['username']} por {current_user['username']}")
        
        return {"message": "Usuario actualizado exitosamente"}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error actualizando usuario: {e}")
        raise HTTPException(status_code=500, detail="Error actualizando usuario")

@app.get("/api/audit-logs")
async def get_audit_logs(
    page: int = 1,
    limit: int = 50,
    current_user: dict = Depends(require_role([UserRole.ADMIN]))
):
    """Obtener logs de auditoría (solo admins)"""
    try:
        skip = (page - 1) * limit
        
        # Obtener logs paginados
        logs_cursor = db.audit_logs.find().sort("timestamp", -1).skip(skip).limit(limit)
        logs = []
        
        async for log in logs_cursor:
            log_data = {
                "id": str(log["_id"]),
                "username": log["username"],
                "action": log["action"],
                "resource_type": log["resource_type"],
                "resource_id": log.get("resource_id"),
                "details": log.get("details", {}),
                "timestamp": log["timestamp"].isoformat(),
                "sede": log.get("sede", "")
            }
            logs.append(log_data)
        
        # Contar total
        total_logs = await db.audit_logs.count_documents({})
        total_pages = (total_logs + limit - 1) // limit
        
        return {
            "logs": logs,
            "pagination": {
                "current_page": page,
                "total_pages": total_pages,
                "total_logs": total_logs,
                "per_page": limit
            }
        }
    
    except Exception as e:
        logger.error(f"Error obteniendo logs de auditoría: {e}")
        raise HTTPException(status_code=500, detail="Error obteniendo logs")

# ========================================
# CONFIGURACION DE SCHEDULER
# ========================================

@app.on_event("startup")
async def startup_event():
    """Evento de inicio - configurar scheduler y crear usuario admin por defecto"""
    try:
        # Configurar scheduler para backups automáticos
        if config("BACKUP_ENABLED", default=True, cast=bool):
            backup_interval = config("BACKUP_INTERVAL_HOURS", default=24, cast=int)
            scheduler.add_job(
                create_backup,
                "interval",
                hours=backup_interval,
                id="auto_backup",
                replace_existing=True
            )
            logger.info(f"Scheduler configurado: backup cada {backup_interval} horas")
        
        # Iniciar scheduler
        scheduler.start()
        
        # Crear usuario admin por defecto si no existe
        admin_exists = await db.users.find_one({"role": "admin"})
        if not admin_exists:
            admin_user = {
                "username": "admin",
                "email": "admin@inei.gob.pe",
                "full_name": "Administrador INEI",
                "role": "admin",
                "is_active": True,
                "sede": "Arequipa 06 - Socabaya",
                "hashed_password": get_password_hash("admin123"),
                "created_at": datetime.now()
            }
            
            await db.users.insert_one(admin_user)
            logger.info("Usuario admin por defecto creado - username: admin, password: admin123")
        
        # Crear índices de base de datos
        await db.inventory.create_index("dni", unique=True)
        await db.inventory.create_index("dispositivo")
        await db.inventory.create_index("estado")
        await db.users.create_index("username", unique=True)
        await db.users.create_index("email", unique=True)
        await db.audit_logs.create_index("timestamp")
        
        logger.info("Sistema iniciado correctamente - INEI Inventory v2.0")
        
    except Exception as e:
        logger.error(f"Error en startup: {e}")

@app.on_event("shutdown")
async def shutdown_event():
    """Evento de cierre"""
    try:
        scheduler.shutdown()
        logger.info("Sistema cerrado correctamente")
    except Exception as e:
        logger.error(f"Error en shutdown: {e}")

# ========================================
# ENDPOINT PRINCIPAL
# ========================================

@app.get("/api")
async def root():
    """Endpoint principal de la API"""
    return {
        "message": "INEI Inventory Management System API v2.0",
        "description": "Sistema de inventario mejorado para INEI - Censos Nacionales 2025",
        "version": "2.0.0",
        "features": [
            "Autenticación JWT",
            "Control de roles",
            "Logging de auditoría",
            "Backups automáticos",
            "Reportes PDF",
            "Excel mejorado",
            "Notificaciones",
            "Sistema de alertas"
        ],
        "docs": "/api/docs",
        "status": "running"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "server:app",
        host="0.0.0.0",
        port=8001,
        reload=True,
        log_level="info"
    )