# 🚀 Guía Rápida de Inicio

## ⚡ Instalación Rápida (5 minutos)

### 1. Requisitos
```bash
# Verificar Python
python --version  # Debe ser 3.8 o superior
```

### 2. Instalar Dependencias
```bash
pip install -r requirements.txt
```

### 3. Ejecutar Demo (Sin API keys necesarias)
```bash
python demo.py
```

---

## 🎯 Uso Básico

### Opción 1: Demo Simplificado (Recomendado para empezar)
```bash
python demo.py
```
**Qué hace:**
- ✅ Scrapea Ramsa y Heizen
- ✅ Busca en MercadoLibre
- ✅ Genera leads
- ✅ Crea base de datos
- ✅ Exporta a Excel

**NO requiere:** API keys

---

### Opción 2: Sistema Completo (Con IA)

#### Paso 1: Configurar API Key
```bash
# Crear archivo .env
cp .env.example .env

# Editar .env y agregar tu API key
nano .env  # o usar tu editor favorito
```

Agregar:
```
ANTHROPIC_API_KEY=sk-ant-api03-tu-api-key-aqui
```

#### Paso 2: Ejecutar
```bash
python main.py
```

Cuando pregunte "¿Usar enriquecimiento con IA? (s/n)", responder: **s**

**Qué hace adicional:**
- 🤖 Mejora descripciones de productos
- 🎯 Categoriza automáticamente
- 📊 Analiza sentimientos
- ⭐ Califica leads automáticamente

---

## 📊 Archivos Generados

Después de ejecutar, encontrarás:

```
exports/
├── ramsa_heizen_data_20260210_143022.xlsx    # Excel con múltiples hojas
└── reporte_resumen_20260210_143022.txt       # Reporte en texto

data/
└── ramsa_heizen.db                           # Base de datos SQLite

logs/
└── scraping_2026-02-10_14-30-22.log         # Logs detallados
```

---

## 🔍 Ejemplos Rápidos

### Solo scrapear Ramsa
```python
from scrapers.web_scraper import RamsaWebScraper

ramsa = RamsaWebScraper()
productos = ramsa.scrape_products()
print(f"Productos: {len(productos)}")
```

### Solo buscar en MercadoLibre
```python
from scrapers.marketplace_scraper import MercadoLibreScraper

ml = MercadoLibreScraper()
productos = ml.search_products("calefon", max_results=20)
print(f"Encontrados: {len(productos)}")
```

### Solo generar leads
```python
from scrapers.marketplace_scraper import RelatedBusinessScraper

lead_gen = RelatedBusinessScraper()
leads = lead_gen.generate_all_leads()
print(f"Leads: {len(leads)}")
```

### Solo enriquecer con IA
```python
from enrichment.ai_enricher import AIEnricher

enricher = AIEnricher()
result = enricher.enrich_product_description(
    nombre="Calefón Eléctrico",
    descripcion_original="Calefón con inducción"
)
print(result['descripcion_enriquecida'])
```

---

## ❓ Solución Rápida de Problemas

### ❌ Error: "No module named 'requests'"
```bash
pip install -r requirements.txt
```

### ❌ Error: "No se pudo inicializar IA"
**Opción 1:** Ejecutar sin IA
```bash
python main.py
# Responder 'n' cuando pregunte
```

**Opción 2:** Configurar API key
```bash
echo "ANTHROPIC_API_KEY=tu-key" > .env
```

### ❌ Error: "Timeout"
Aumentar timeout en `config/settings.py`:
```python
SCRAPING_CONFIG = {
    "timeout": 60,  # Cambiar a 60 segundos
}
```

### ❌ No encuentra productos
- Verificar que los sitios estén disponibles
- Los sitios web pueden cambiar su estructura
- Revisar logs en `logs/`

---

## 📚 Próximos Pasos

1. ✅ Ejecutar demo.py
2. ✅ Revisar archivos Excel generados
3. ✅ Explorar la base de datos
4. 📖 Leer README.md completo
5. 🔧 Personalizar configuración
6. 🚀 Ejecutar sistema completo

---

## 🆘 Ayuda

- 📖 Documentación completa: `README.md`
- 📝 Logs detallados: `logs/`
- 💬 Ejemplos de código: Cada módulo tiene ejemplos al final

---

## ⏱️ Tiempo Estimado de Ejecución

| Modo | Tiempo | Datos |
|------|--------|-------|
| Demo | 2-5 min | ~50 productos |
| Completo sin IA | 5-10 min | ~100-200 productos |
| Completo con IA | 10-20 min | ~100-200 productos enriquecidos |

---

¡Listo para comenzar! 🚀

```bash
python demo.py
```
