"""
Configuración central del sistema de scraping Ramsa/Heizen
"""
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Directorios del proyecto
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
EXPORTS_DIR = BASE_DIR / "exports"
LOGS_DIR = BASE_DIR / "logs"

# Crear directorios si no existen
for dir_path in [DATA_DIR, EXPORTS_DIR, LOGS_DIR]:
    dir_path.mkdir(exist_ok=True)

# Configuración de la base de datos
DATABASE_PATH = DATA_DIR / "ramsa_heizen.db"

# URLs objetivo
TARGET_URLS = {
    "ramsa": {
        "website": "https://ramsaimportaciones.com",
        "facebook": "https://www.facebook.com/1604408203019697",
        "mercadolibre": "https://eshops.mercadolibre.com.ec/ramsa+importaciones"
    },
    "heizen": {
        "website": "https://calefonecuador.com",
        "website_alt": "https://calefoneselectricos.info",
        "website_alt2": "https://www.calefonagas.com"
    }
}

# Información de contacto conocida
COMPANY_INFO = {
    "ramsa": {
        "nombre": "Ramsa Importaciones",
        "ubicacion": "Av. América N96-191 y Naciones Unidas, Edificio Izurieta Hnos. Local 1, Quito - Ecuador",
        "telefono": "+593982234833",
        "whatsapp": "0982234833",
        "email": None,
        "ruc": "1711842557001"
    },
    "heizen": {
        "nombre": "Heizen Ecuador",
        "ubicacion": "Av. América N36-191 y Av. Naciones Unidas, Edificio Izurieta Hermanos local 1, Quito - Ecuador",
        "telefono": "(02) 243-4381",
        "whatsapp": "0982234822",
        "celular": "0982234822",
        "telefono_adicional": "1700-434936",
        "email": "heizen-ecuador@hotmail.com"
    }
}

# API Keys
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY", "")

# Configuración de scraping
SCRAPING_CONFIG = {
    "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "timeout": 30,
    "max_retries": 3,
    "delay_between_requests": 2,  # segundos
    "use_selenium": True,  # Para sitios con JavaScript
}

# Categorías de productos
PRODUCT_CATEGORIES = [
    "Calefones Eléctricos",
    "Calefones a Gas",
    "Calefactores",
    "Termotanques",
    "Juguetes Infantiles",
    "Artículos para Hogar",
    "Piscinas",
    "Productos Varios"
]

# Configuración de enriquecimiento con IA
AI_ENRICHMENT_CONFIG = {
    "model": "claude-sonnet-4-20250514",
    "max_tokens": 2000,
    "temperature": 0.7,
}

# Términos de búsqueda para empresas relacionadas
RELATED_BUSINESS_KEYWORDS = [
    "calefones Ecuador",
    "calefactores Quito",
    "importadora hogar Ecuador",
    "distribuidora electrodomésticos Quito",
    "juguetes Ecuador mayorista",
    "productos hogar importados Ecuador"
]

# Configuración de logging
LOGGING_CONFIG = {
    "level": "INFO",
    "format": "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>",
    "rotation": "10 MB",
    "retention": "30 days"
}

# Límites de scraping (para evitar bloqueos)
RATE_LIMITS = {
    "requests_per_minute": 20,
    "concurrent_requests": 5,
    "backoff_factor": 2
}

# Configuración de exportación
EXPORT_CONFIG = {
    "excel_engine": "openpyxl",
    "include_charts": True,
    "auto_filter": True,
    "freeze_panes": (1, 0)  # Congelar fila de encabezados
}
