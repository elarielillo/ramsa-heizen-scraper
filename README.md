# 🔍 Sistema de Scraping y Enriquecimiento de Datos
## Ramsa Importaciones & Heizen Ecuador

Sistema completo y profesional de web scraping, análisis de datos y generación de leads para Ramsa Importaciones y Heizen Ecuador.

---

## 📋 Características

### 🎯 Funcionalidades Principales

1. **Web Scraping Multi-Fuente**
   - ✅ Sitios web oficiales (Ramsa y Heizen)
   - ✅ Marketplaces (MercadoLibre, OLX)
   - ✅ Redes sociales (Facebook, Instagram)
   - ✅ Google Maps / Google Business
   - ✅ Directorios empresariales

2. **Enriquecimiento con IA** 🤖
   - Mejora automática de descripciones de productos
   - Categorización inteligente de productos
   - Análisis de sentimientos en reseñas
   - Scoring automático de leads
   - Análisis de competitividad de precios

3. **Generación de Leads** 🎯
   - Búsqueda de empresas relacionadas
   - Scoring de calidad de leads
   - Identificación de productos potenciales
   - Priorización automática

4. **Base de Datos Estructurada** 💾
   - SQLite integrado
   - Modelos relacionales completos
   - Historial de cambios
   - Exportación a múltiples formatos

5. **Reportes y Análisis** 📊
   - Exportación a Excel con múltiples hojas
   - Análisis de productos por categoría
   - Análisis de precios y competencia
   - Análisis de leads
   - Reportes en texto

---

## 🚀 Instalación

### Requisitos Previos

- Python 3.8 o superior
- pip (gestor de paquetes de Python)
- API Key de Anthropic (opcional, para enriquecimiento con IA)

### Paso 1: Clonar o Descargar

```bash
# Si usas git
git clone <url-del-repositorio>
cd ramsa_heizen_scraper

# O simplemente descomprime el archivo ZIP
```

### Paso 2: Crear Entorno Virtual (Recomendado)

```bash
# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
# En Windows:
venv\Scripts\activate
# En Linux/Mac:
source venv/bin/activate
```

### Paso 3: Instalar Dependencias

```bash
pip install -r requirements.txt
```

### Paso 4: Configurar Variables de Entorno (Opcional)

Si quieres usar el enriquecimiento con IA:

```bash
# Copiar archivo de ejemplo
cp .env.example .env

# Editar .env y agregar tu API key de Anthropic
# ANTHROPIC_API_KEY=sk-ant-api03-xxxxxxxxx
```

---

## 💻 Uso

### Ejecución Básica

```bash
python main.py
```

El sistema te preguntará si quieres usar enriquecimiento con IA. Si no tienes API key, puedes ejecutar solo el scraping básico.

### Ejecución Programática

```python
from main import RamsaHeizenScraper

# Crear instancia
scraper = RamsaHeizenScraper(use_ai_enrichment=True)

# Ejecutar scraping completo
stats = scraper.run_full_scraping()

# Limpiar recursos
scraper.cleanup()

print(f"Productos scrapeados: {stats['productos']}")
print(f"Leads generados: {stats['leads']}")
```

### Usar Componentes Individuales

#### 1. Solo Scraping Web

```python
from scrapers.web_scraper import RamsaWebScraper, HeizenWebScraper

# Scrapear Ramsa
ramsa = RamsaWebScraper()
productos_ramsa = ramsa.scrape_products()
contacto_ramsa = ramsa.scrape_contact_info()

# Scrapear Heizen
heizen = HeizenWebScraper()
datos_heizen = heizen.scrape_all_sites()
```

#### 2. Solo MercadoLibre

```python
from scrapers.marketplace_scraper import MercadoLibreScraper

ml = MercadoLibreScraper()
productos = ml.search_products("calefon electrico", max_results=20)
```

#### 3. Solo Generación de Leads

```python
from scrapers.marketplace_scraper import RelatedBusinessScraper

lead_gen = RelatedBusinessScraper()
leads = lead_gen.generate_all_leads()
```

#### 4. Solo Enriquecimiento con IA

```python
from enrichment.ai_enricher import AIEnricher

enricher = AIEnricher()

# Enriquecer descripción de producto
result = enricher.enrich_product_description(
    nombre="Calefón Eléctrico Heizen 8.8 kW",
    descripcion_original="Calefón con tecnología de inducción",
    especificaciones={"Potencia": "8.8 kW", "Garantía": "24 meses"}
)

print(result['descripcion_enriquecida'])
print(result['palabras_clave'])
```

#### 5. Solo Exportación

```python
from utils.exporter import DataExporter

exporter = DataExporter()

# Exportar a Excel
exporter.export_to_excel(
    productos=lista_productos,
    empresas=lista_empresas,
    resenas=lista_resenas,
    leads=lista_leads
)
```

---

## 📁 Estructura del Proyecto

```
ramsa_heizen_scraper/
├── config/
│   └── settings.py              # Configuración central
├── database/
│   └── models.py                # Modelos de base de datos
├── scrapers/
│   ├── web_scraper.py           # Scrapers para sitios web
│   └── marketplace_scraper.py   # Scrapers para marketplaces y leads
├── enrichment/
│   └── ai_enricher.py           # Enriquecimiento con IA
├── utils/
│   └── exporter.py              # Exportación a Excel/CSV
├── data/                        # Base de datos SQLite
├── exports/                     # Archivos Excel/CSV generados
├── logs/                        # Logs del sistema
├── main.py                      # Script principal
├── requirements.txt             # Dependencias
├── .env.example                 # Ejemplo de variables de entorno
└── README.md                    # Este archivo
```

---

## 📊 Datos Extraídos

### Productos
- Nombre del producto
- Descripción original y enriquecida
- Categoría y subcategoría
- Precio y descuentos
- Especificaciones técnicas
- Imágenes
- URL del producto
- Popularidad y métricas

### Empresas
- Nombre y tipo
- Información de contacto (teléfono, email, WhatsApp)
- Dirección y ubicación
- Redes sociales
- Calificaciones y reseñas
- Horarios de atención

### Leads
- Nombre de la empresa
- Tipo de negocio
- Información de contacto
- Ubicación
- Score de calidad (0-100)
- Nivel de prioridad (alto/medio/bajo)
- Similitud con Ramsa/Heizen
- Productos potenciales

### Reseñas (si disponibles)
- Calificación
- Texto de la reseña
- Autor
- Análisis de sentimiento
- Temas principales
- Palabras clave

---

## 🤖 Enriquecimiento con IA

El sistema usa Claude (Anthropic) para:

1. **Descripciones de Productos**
   - Reescribir descripciones de manera persuasiva
   - Extraer beneficios clave
   - Generar palabras clave SEO
   - Identificar público objetivo

2. **Categorización Automática**
   - Asignar categorías y subcategorías
   - Detectar tipo de producto
   - Nivel de confianza en la categorización

3. **Análisis de Sentimientos**
   - Clasificar reseñas (positivo/neutral/negativo)
   - Score de sentimiento (-1 a 1)
   - Extraer temas principales
   - Identificar aspectos positivos y negativos

4. **Scoring de Leads**
   - Evaluar calidad (0-100)
   - Asignar prioridad
   - Calcular similitud con Ramsa/Heizen
   - Sugerir acciones

5. **Análisis de Competitividad**
   - Comparar precios con competencia
   - Sugerir estrategias de pricing
   - Identificar posicionamiento de mercado

---

## 📈 Exportación de Datos

### Excel Multi-Hoja

El sistema genera archivos Excel con las siguientes hojas:

1. **Productos** - Listado completo de productos
2. **Empresas** - Información de empresas
3. **Reseñas** - Reseñas y calificaciones
4. **Leads** - Leads generados
5. **Redes Sociales** - Posts de redes sociales
6. **Análisis Productos** - Estadísticas por categoría
7. **Análisis Precios** - Top productos caros/baratos
8. **Análisis Leads** - Distribución de leads

### Reporte de Texto

Genera un reporte resumen en formato texto con:
- Estadísticas generales
- Productos por categoría
- Rangos de precios
- Distribución de leads
- Métricas clave

---

## ⚙️ Configuración Avanzada

### Modificar Categorías de Productos

Edita `config/settings.py`:

```python
PRODUCT_CATEGORIES = [
    "Calefones Eléctricos",
    "Calefones a Gas",
    "Calefactores",
    # ... agregar más categorías
]
```

### Cambiar Keywords para Leads

Edita `config/settings.py`:

```python
RELATED_BUSINESS_KEYWORDS = [
    "calefones Ecuador",
    "importadora hogar",
    # ... agregar más keywords
]
```

### Ajustar Rate Limiting

Edita `config/settings.py`:

```python
SCRAPING_CONFIG = {
    "delay_between_requests": 2,  # Segundos
    "max_retries": 3,
    "timeout": 30
}
```

---

## 🛡️ Buenas Prácticas

1. **Rate Limiting**
   - El sistema respeta delays entre peticiones
   - Evita hacer scraping muy agresivo
   - Usa proxies si es necesario

2. **Respeto a robots.txt**
   - Verifica los robots.txt de cada sitio
   - No scrapear contenido bloqueado

3. **Uso Ético**
   - Usar los datos solo para propósitos legítimos
   - No redistribuir datos sin permiso
   - Respetar términos de servicio

4. **Mantenimiento**
   - Los sitios web cambian constantemente
   - Revisa los scrapers periódicamente
   - Actualiza selectores CSS/XPath

---

## 🔧 Solución de Problemas

### Error: "No se pudo inicializar IA"

**Causa**: Falta la API key de Anthropic

**Solución**:
```bash
# Crear archivo .env
echo "ANTHROPIC_API_KEY=tu-api-key-aqui" > .env

# O ejecutar sin IA
python main.py
# Responder 'n' cuando pregunte por IA
```

### Error: "ModuleNotFoundError"

**Causa**: Dependencias no instaladas

**Solución**:
```bash
pip install -r requirements.txt
```

### Error: "Timeout" al scrapear

**Causa**: Sitio web lento o bloqueando peticiones

**Solución**:
- Aumentar timeout en `config/settings.py`
- Usar VPN o proxy
- Reducir frecuencia de peticiones

### Productos no se encuentran

**Causa**: Cambios en la estructura del sitio web

**Solución**:
- Inspeccionar el sitio web actual
- Actualizar selectores CSS en los scrapers
- Verificar que el sitio esté disponible

---

## 📝 Logging

Los logs se guardan en la carpeta `logs/`:

- `scraping_YYYY-MM-DD_HH-MM-SS.log` - Log completo de cada ejecución
- Rotación automática cada 10 MB
- Retención de 30 días

Ver logs en tiempo real:
```bash
tail -f logs/scraping_*.log
```

---

## 🤝 Contribuir

Si quieres mejorar este sistema:

1. Agrega nuevos scrapers para otras fuentes
2. Mejora el enriquecimiento con IA
3. Agrega visualizaciones de datos
4. Implementa scraping de redes sociales
5. Agrega tests unitarios

---

## 📄 Licencia

Este proyecto es de código abierto y está disponible para uso personal y comercial.

---

## 👥 Soporte

Para preguntas o problemas:

1. Revisa esta documentación
2. Verifica los logs en `logs/`
3. Consulta los ejemplos en cada módulo
4. Abre un issue en el repositorio

---

## 🎉 Créditos

Desarrollado con:
- Python 3.x
- BeautifulSoup4 - Web scraping
- Selenium - Scraping dinámico
- Anthropic Claude - IA
- SQLAlchemy - ORM
- Pandas - Análisis de datos
- OpenPyXL - Excel

---

**Última actualización**: Febrero 2026

**Versión**: 1.0.0

¡Feliz scraping! 🚀
