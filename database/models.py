"""
Modelos de base de datos para el sistema de scraping
"""
from sqlalchemy import (
    create_engine, Column, Integer, String, Float, Text, 
    DateTime, Boolean, ForeignKey, JSON
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
from config.settings import DATABASE_PATH

Base = declarative_base()

class Empresa(Base):
    """Modelo para empresas (Ramsa, Heizen, y relacionadas)"""
    __tablename__ = 'empresas'
    
    id = Column(Integer, primary_key=True)
    nombre = Column(String(200), nullable=False)
    tipo = Column(String(50))  # 'principal' o 'relacionada'
    categoria = Column(String(100))
    
    # Información de contacto
    telefono = Column(String(50))
    whatsapp = Column(String(50))
    email = Column(String(100))
    website = Column(String(255))
    
    # Ubicación
    direccion = Column(Text)
    ciudad = Column(String(100))
    provincia = Column(String(100))
    pais = Column(String(50), default='Ecuador')
    latitud = Column(Float)
    longitud = Column(Float)
    
    # Datos adicionales
    ruc = Column(String(20))
    descripcion = Column(Text)
    horario = Column(Text)
    
    # Redes sociales
    facebook_url = Column(String(255))
    instagram_url = Column(String(255))
    twitter_url = Column(String(255))
    
    # Métricas
    calificacion = Column(Float)
    numero_resenas = Column(Integer, default=0)
    
    # Metadatos
    fecha_creacion = Column(DateTime, default=datetime.now)
    fecha_actualizacion = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    activo = Column(Boolean, default=True)
    
    # Relaciones
    productos = relationship("Producto", back_populates="empresa")
    resenas = relationship("Resena", back_populates="empresa")
    posts_sociales = relationship("PostSocial", back_populates="empresa")


class Producto(Base):
    """Modelo para productos de las empresas"""
    __tablename__ = 'productos'
    
    id = Column(Integer, primary_key=True)
    empresa_id = Column(Integer, ForeignKey('empresas.id'))
    
    # Información básica
    nombre = Column(String(255), nullable=False)
    descripcion = Column(Text)
    categoria = Column(String(100))
    subcategoria = Column(String(100))
    marca = Column(String(100))
    modelo = Column(String(100))
    
    # Precio
    precio = Column(Float)
    precio_original = Column(Float)
    moneda = Column(String(10), default='USD')
    descuento_porcentaje = Column(Float)
    precio_oferta = Column(Boolean, default=False)
    
    # Especificaciones técnicas (JSON)
    especificaciones = Column(JSON)
    
    # Disponibilidad
    stock_disponible = Column(Boolean, default=True)
    cantidad_stock = Column(Integer)
    
    # Imágenes y URLs
    url_producto = Column(String(500))
    imagen_url = Column(String(500))
    imagenes_adicionales = Column(JSON)  # Lista de URLs
    
    # Métricas
    vistas = Column(Integer, default=0)
    ventas = Column(Integer, default=0)
    popularidad_score = Column(Float)
    
    # Enriquecimiento con IA
    descripcion_enriquecida = Column(Text)
    tags_ia = Column(JSON)  # Tags generados por IA
    categoria_ia = Column(String(100))  # Categoría sugerida por IA
    
    # Marketplace
    fuente = Column(String(50))  # 'website', 'mercadolibre', 'olx', etc.
    id_externo = Column(String(100))  # ID en la plataforma externa
    
    # Metadatos
    fecha_creacion = Column(DateTime, default=datetime.now)
    fecha_actualizacion = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    activo = Column(Boolean, default=True)
    
    # Relaciones
    empresa = relationship("Empresa", back_populates="productos")


class Resena(Base):
    """Modelo para reseñas de clientes"""
    __tablename__ = 'resenas'
    
    id = Column(Integer, primary_key=True)
    empresa_id = Column(Integer, ForeignKey('empresas.id'))
    
    # Información de la reseña
    calificacion = Column(Float, nullable=False)  # 1-5 estrellas
    titulo = Column(String(255))
    texto = Column(Text)
    
    # Autor
    autor_nombre = Column(String(100))
    autor_verificado = Column(Boolean, default=False)
    
    # Análisis con IA
    sentimiento = Column(String(20))  # 'positivo', 'neutral', 'negativo'
    sentimiento_score = Column(Float)  # -1 a 1
    temas_principales = Column(JSON)  # Lista de temas extraídos
    palabras_clave = Column(JSON)
    
    # Fuente
    fuente = Column(String(50))  # 'google', 'facebook', 'mercadolibre', etc.
    url_fuente = Column(String(500))
    
    # Metadatos
    fecha_publicacion = Column(DateTime)
    fecha_creacion = Column(DateTime, default=datetime.now)
    
    # Relaciones
    empresa = relationship("Empresa", back_populates="resenas")


class PostSocial(Base):
    """Modelo para posts de redes sociales"""
    __tablename__ = 'posts_sociales'
    
    id = Column(Integer, primary_key=True)
    empresa_id = Column(Integer, ForeignKey('empresas.id'))
    
    # Información del post
    plataforma = Column(String(50))  # 'facebook', 'instagram', 'twitter'
    tipo_post = Column(String(50))  # 'imagen', 'video', 'texto', 'enlace'
    contenido = Column(Text)
    url_post = Column(String(500))
    
    # Engagement
    likes = Column(Integer, default=0)
    comentarios = Column(Integer, default=0)
    compartidos = Column(Integer, default=0)
    vistas = Column(Integer, default=0)
    engagement_rate = Column(Float)
    
    # Análisis con IA
    temas = Column(JSON)
    productos_mencionados = Column(JSON)
    sentimiento_audiencia = Column(String(20))
    
    # Multimedia
    imagenes_urls = Column(JSON)
    video_url = Column(String(500))
    
    # Metadatos
    fecha_publicacion = Column(DateTime)
    fecha_creacion = Column(DateTime, default=datetime.now)
    
    # Relaciones
    empresa = relationship("Empresa", back_populates="posts_sociales")


class TendenciaProducto(Base):
    """Modelo para tendencias de productos en el tiempo"""
    __tablename__ = 'tendencias_productos'
    
    id = Column(Integer, primary_key=True)
    categoria = Column(String(100))
    nombre_producto = Column(String(255))
    
    # Métricas de tendencia
    busquedas = Column(Integer, default=0)
    menciones_sociales = Column(Integer, default=0)
    ventas_estimadas = Column(Integer, default=0)
    popularidad_score = Column(Float)
    
    # Análisis de precios
    precio_promedio = Column(Float)
    precio_minimo = Column(Float)
    precio_maximo = Column(Float)
    variacion_precio = Column(Float)
    
    # Competencia
    numero_competidores = Column(Integer)
    saturacion_mercado = Column(Float)
    
    # Período
    fecha_inicio = Column(DateTime)
    fecha_fin = Column(DateTime)
    periodo = Column(String(20))  # 'diario', 'semanal', 'mensual'
    
    # Metadatos
    fecha_creacion = Column(DateTime, default=datetime.now)


class Lead(Base):
    """Modelo para leads de empresas relacionadas"""
    __tablename__ = 'leads'
    
    id = Column(Integer, primary_key=True)
    
    # Información básica
    nombre_empresa = Column(String(200), nullable=False)
    tipo_negocio = Column(String(100))
    industria = Column(String(100))
    
    # Contacto
    telefono = Column(String(50))
    email = Column(String(100))
    website = Column(String(255))
    
    # Ubicación
    direccion = Column(Text)
    ciudad = Column(String(100))
    provincia = Column(String(100))
    
    # Scoring
    score_calidad = Column(Float)  # 0-100
    nivel_prioridad = Column(String(20))  # 'alto', 'medio', 'bajo'
    
    # Análisis con IA
    similitud_ramsa_heizen = Column(Float)  # 0-1
    productos_potenciales = Column(JSON)
    razon_lead = Column(Text)  # Por qué es un buen lead
    
    # Estado
    estado = Column(String(50), default='nuevo')  # 'nuevo', 'contactado', 'calificado', 'descartado'
    notas = Column(Text)
    
    # Fuente
    fuente_lead = Column(String(100))  # 'google_maps', 'mercadolibre', 'web_search', etc.
    url_fuente = Column(String(500))
    
    # Metadatos
    fecha_creacion = Column(DateTime, default=datetime.now)
    fecha_actualizacion = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    
# Inicialización de la base de datos
def init_database():
    """Crear todas las tablas en la base de datos"""
    engine = create_engine(f'sqlite:///{DATABASE_PATH}')
    Base.metadata.create_all(engine)
    return engine


def get_session():
    """Obtener una sesión de base de datos"""
    engine = create_engine(f'sqlite:///{DATABASE_PATH}')
    Session = sessionmaker(bind=engine)
    return Session()


if __name__ == "__main__":
    # Crear base de datos si se ejecuta directamente
    print(f"Creando base de datos en: {DATABASE_PATH}")
    init_database()
    print("✅ Base de datos creada exitosamente!")
