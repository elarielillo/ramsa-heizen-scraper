"""
Script principal para ejecutar el sistema completo de scraping y enriquecimiento
"""
import sys
from pathlib import Path

# Agregar el directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent))

from loguru import logger
from datetime import datetime
from typing import Dict, List
import json

# Importar módulos del proyecto
from database.models import (
    init_database, get_session, 
    Empresa, Producto, Resena, Lead, PostSocial
)
from scrapers.web_scraper import RamsaWebScraper, HeizenWebScraper
from scrapers.marketplace_scraper import MercadoLibreScraper, RelatedBusinessScraper
from enrichment.ai_enricher import AIEnricher
from utils.exporter import DataExporter
from config.settings import COMPANY_INFO, LOGS_DIR, EXPORTS_DIR

# Configurar logging
logger.add(
    LOGS_DIR / "scraping_{time}.log",
    rotation="10 MB",
    retention="30 days",
    level="INFO"
)


class RamsaHeizenScraper:
    """Clase principal que orquesta todo el proceso de scraping"""
    
    def __init__(self, use_ai_enrichment: bool = True):
        """
        Inicializar el scraper
        
        Args:
            use_ai_enrichment: Si usar enriquecimiento con IA
        """
        self.use_ai = use_ai_enrichment
        
        # Inicializar componentes
        logger.info("🚀 Inicializando sistema de scraping Ramsa & Heizen...")
        
        # Base de datos
        init_database()
        self.session = get_session()
        
        # Scrapers
        self.ramsa_scraper = RamsaWebScraper()
        self.heizen_scraper = HeizenWebScraper()
        self.ml_scraper = MercadoLibreScraper()
        self.lead_scraper = RelatedBusinessScraper()
        
        # Enriquecimiento con IA
        if self.use_ai:
            try:
                self.ai_enricher = AIEnricher()
                logger.info("✅ Enriquecedor de IA inicializado")
            except ValueError as e:
                logger.warning(f"⚠️ No se pudo inicializar IA: {e}")
                self.use_ai = False
                self.ai_enricher = None
        else:
            self.ai_enricher = None
        
        # Exportador
        self.exporter = DataExporter()
        
        logger.info("✅ Sistema inicializado correctamente")
    
    def run_full_scraping(self) -> Dict:
        """
        Ejecutar el proceso completo de scraping
        
        Returns:
            Diccionario con estadísticas del proceso
        """
        logger.info("=" * 80)
        logger.info("INICIANDO SCRAPING COMPLETO")
        logger.info("=" * 80)
        
        stats = {
            'productos': 0,
            'empresas': 0,
            'leads': 0,
            'resenas': 0,
            'errores': []
        }
        
        # 1. Scrapear empresas principales (Ramsa y Heizen)
        logger.info("\n📍 PASO 1: Scrapeando información de empresas principales...")
        empresas_principales = self._scrape_main_companies()
        stats['empresas'] += len(empresas_principales)
        
        # 2. Scrapear productos de sitios web
        logger.info("\n📦 PASO 2: Scrapeando productos de sitios web...")
        productos_web = self._scrape_products_from_websites()
        stats['productos'] += len(productos_web)
        
        # 3. Scrapear productos de MercadoLibre
        logger.info("\n🛒 PASO 3: Scrapeando productos de MercadoLibre...")
        productos_ml = self._scrape_products_from_mercadolibre()
        stats['productos'] += len(productos_ml)
        
        # 4. Generar leads de empresas relacionadas
        logger.info("\n🎯 PASO 4: Generando leads de empresas relacionadas...")
        leads = self._generate_leads()
        stats['leads'] += len(leads)
        
        # 5. Enriquecer datos con IA (si está habilitado)
        if self.use_ai and self.ai_enricher:
            logger.info("\n🤖 PASO 5: Enriqueciendo datos con IA...")
            self._enrich_data_with_ai(productos_web + productos_ml, leads)
        else:
            logger.info("\n⏭️ PASO 5: Enriquecimiento con IA deshabilitado")
        
        # 6. Guardar en base de datos
        logger.info("\n💾 PASO 6: Guardando datos en base de datos...")
        self._save_to_database(empresas_principales, productos_web + productos_ml, leads)
        
        # 7. Exportar a Excel
        logger.info("\n📊 PASO 7: Exportando datos a Excel...")
        self._export_data()
        
        logger.info("\n" + "=" * 80)
        logger.info("SCRAPING COMPLETADO")
        logger.info(f"Estadísticas finales: {json.dumps(stats, indent=2)}")
        logger.info("=" * 80)
        
        return stats
    
    def _scrape_main_companies(self) -> List[Dict]:
        """Scrapear información de Ramsa y Heizen"""
        empresas = []
        
        # Ramsa
        logger.info("Scrapeando información de Ramsa...")
        ramsa_contact = self.ramsa_scraper.scrape_contact_info()
        ramsa_data = {
            **COMPANY_INFO['ramsa'],
            **ramsa_contact,
            'tipo': 'principal'
        }
        empresas.append(ramsa_data)
        logger.info(f"✅ Ramsa: {ramsa_data}")
        
        # Heizen
        logger.info("Scrapeando información de Heizen...")
        heizen_contact = self.heizen_scraper.scrape_contact_info(
            self.heizen_scraper.base_urls[0]
        )
        heizen_data = {
            **COMPANY_INFO['heizen'],
            **heizen_contact,
            'tipo': 'principal'
        }
        empresas.append(heizen_data)
        logger.info(f"✅ Heizen: {heizen_data}")
        
        return empresas
    
    def _scrape_products_from_websites(self) -> List[Dict]:
        """Scrapear productos de sitios web"""
        productos = []
        
        # Productos de Ramsa
        logger.info("Scrapeando productos de Ramsa...")
        try:
            ramsa_products = self.ramsa_scraper.scrape_products()
            productos.extend(ramsa_products)
            logger.info(f"✅ Productos Ramsa: {len(ramsa_products)}")
        except Exception as e:
            logger.error(f"❌ Error scrapeando Ramsa: {e}")
        
        # Productos de Heizen
        logger.info("Scrapeando productos de Heizen...")
        try:
            heizen_data = self.heizen_scraper.scrape_all_sites()
            productos.extend(heizen_data['productos'])
            logger.info(f"✅ Productos Heizen: {len(heizen_data['productos'])}")
        except Exception as e:
            logger.error(f"❌ Error scrapeando Heizen: {e}")
        
        return productos
    
    def _scrape_products_from_mercadolibre(self) -> List[Dict]:
        """Scrapear productos de MercadoLibre"""
        productos = []
        
        keywords = [
            "calefon electrico",
            "calefon gas",
            "calefactor",
            "juguetes infantiles"
        ]
        
        for keyword in keywords:
            try:
                logger.info(f"Buscando en MercadoLibre: {keyword}")
                products = self.ml_scraper.search_products(keyword, max_results=20)
                productos.extend(products)
                logger.info(f"✅ Encontrados {len(products)} productos para '{keyword}'")
            except Exception as e:
                logger.error(f"❌ Error en MercadoLibre con '{keyword}': {e}")
        
        return productos
    
    def _generate_leads(self) -> List[Dict]:
        """Generar leads de empresas relacionadas"""
        try:
            leads = self.lead_scraper.generate_all_leads()
            logger.info(f"✅ Leads generados: {len(leads)}")
            return leads
        except Exception as e:
            logger.error(f"❌ Error generando leads: {e}")
            return []
    
    def _enrich_data_with_ai(self, productos: List[Dict], leads: List[Dict]):
        """Enriquecer datos usando IA"""
        
        # Enriquecer productos
        logger.info(f"Enriqueciendo {len(productos)} productos...")
        for i, producto in enumerate(productos[:20], 1):  # Limitar a 20 para demo
            try:
                logger.info(f"  Enriqueciendo producto {i}/20: {producto.get('nombre', 'Sin nombre')}")
                
                enriched = self.ai_enricher.enrich_product_description(
                    nombre=producto.get('nombre', ''),
                    descripcion_original=producto.get('descripcion', ''),
                    especificaciones=producto.get('especificaciones')
                )
                
                producto['descripcion_enriquecida'] = enriched.get('descripcion_enriquecida')
                producto['palabras_clave'] = enriched.get('palabras_clave', [])
                producto['categoria_ia'] = enriched.get('categoria_sugerida')
                producto['beneficios'] = enriched.get('beneficios', [])
                
            except Exception as e:
                logger.error(f"    ❌ Error enriqueciendo producto: {e}")
        
        # Enriquecer leads
        logger.info(f"Enriqueciendo {len(leads)} leads...")
        for i, lead in enumerate(leads[:10], 1):  # Limitar a 10 para demo
            try:
                logger.info(f"  Scoring lead {i}/10: {lead.get('nombre_empresa', 'Sin nombre')}")
                
                scoring = self.ai_enricher.score_lead_quality(lead)
                
                lead['score_calidad'] = scoring.get('score_calidad', 50)
                lead['nivel_prioridad'] = scoring.get('nivel_prioridad', 'medio')
                lead['similitud_ramsa_heizen'] = scoring.get('similitud_ramsa_heizen', 0.5)
                lead['razon_lead'] = scoring.get('razon_lead', '')
                
            except Exception as e:
                logger.error(f"    ❌ Error evaluando lead: {e}")
    
    def _save_to_database(
        self, 
        empresas: List[Dict], 
        productos: List[Dict], 
        leads: List[Dict]
    ):
        """Guardar datos en la base de datos"""
        
        # Guardar empresas
        for empresa_data in empresas:
            empresa = Empresa(**{k: v for k, v in empresa_data.items() if hasattr(Empresa, k)})
            self.session.merge(empresa)
        
        # Guardar productos
        for producto_data in productos:
            # Convertir campos JSON
            if 'especificaciones' in producto_data and isinstance(producto_data['especificaciones'], dict):
                producto_data['especificaciones'] = producto_data['especificaciones']
            
            producto = Producto(**{k: v for k, v in producto_data.items() if hasattr(Producto, k)})
            self.session.add(producto)
        
        # Guardar leads
        for lead_data in leads:
            lead = Lead(**{k: v for k, v in lead_data.items() if hasattr(Lead, k)})
            self.session.add(lead)
        
        # Commit
        try:
            self.session.commit()
            logger.info("✅ Datos guardados en base de datos")
        except Exception as e:
            self.session.rollback()
            logger.error(f"❌ Error guardando en base de datos: {e}")
    
    def _export_data(self):
        """Exportar datos a Excel y otros formatos"""
        
        # Obtener datos de la base de datos
        productos = [
            {
                'nombre': p.nombre,
                'categoria': p.categoria,
                'precio': p.precio,
                'descripcion': p.descripcion,
                'descripcion_enriquecida': p.descripcion_enriquecida,
                'fuente': p.fuente,
                'url_producto': p.url_producto,
                'fecha_creacion': p.fecha_creacion
            }
            for p in self.session.query(Producto).all()
        ]
        
        empresas = [
            {
                'nombre': e.nombre,
                'tipo': e.tipo,
                'telefono': e.telefono,
                'email': e.email,
                'website': e.website,
                'direccion': e.direccion,
                'ciudad': e.ciudad
            }
            for e in self.session.query(Empresa).all()
        ]
        
        leads = [
            {
                'nombre_empresa': l.nombre_empresa,
                'tipo_negocio': l.tipo_negocio,
                'telefono': l.telefono,
                'email': l.email,
                'website': l.website,
                'score_calidad': l.score_calidad,
                'nivel_prioridad': l.nivel_prioridad,
                'fuente_lead': l.fuente_lead,
                'razon_lead': l.razon_lead
            }
            for l in self.session.query(Lead).all()
        ]
        
        # Exportar a Excel
        excel_path = self.exporter.export_to_excel(
            productos=productos,
            empresas=empresas,
            resenas=[],
            leads=leads,
            posts_sociales=[]
        )
        logger.info(f"✅ Excel exportado: {excel_path}")
        
        # Generar reporte resumen
        report_path = self.exporter.export_summary_report(
            productos=productos,
            empresas=empresas,
            resenas=[],
            leads=leads
        )
        logger.info(f"✅ Reporte generado: {report_path}")
        
        return excel_path, report_path
    
    def cleanup(self):
        """Limpiar recursos"""
        if self.session:
            self.session.close()


def main():
    """Función principal"""
    print("""
    ╔══════════════════════════════════════════════════════════════╗
    ║   SISTEMA DE SCRAPING Y ENRIQUECIMIENTO DE DATOS            ║
    ║   Ramsa Importaciones & Heizen Ecuador                      ║
    ╚══════════════════════════════════════════════════════════════╝
    """)
    
    # Preguntar si usar IA
    use_ai = input("\n¿Usar enriquecimiento con IA? (s/n) [s]: ").lower()
    use_ai = use_ai != 'n'
    
    if use_ai:
        print("\n⚠️  NOTA: El enriquecimiento con IA requiere ANTHROPIC_API_KEY")
        print("    Configúralo en un archivo .env o como variable de entorno\n")
    
    # Crear instancia del scraper
    scraper = RamsaHeizenScraper(use_ai_enrichment=use_ai)
    
    try:
        # Ejecutar scraping
        stats = scraper.run_full_scraping()
        
        print("\n" + "=" * 80)
        print("✅ PROCESO COMPLETADO EXITOSAMENTE")
        print("=" * 80)
        print(f"\n📊 Estadísticas:")
        print(f"   - Productos scrapeados: {stats['productos']}")
        print(f"   - Empresas procesadas: {stats['empresas']}")
        print(f"   - Leads generados: {stats['leads']}")
        print(f"\n📁 Archivos generados en: {EXPORTS_DIR}")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Proceso interrumpido por el usuario")
    except Exception as e:
        print(f"\n\n❌ Error durante el proceso: {e}")
        logger.exception("Error crítico en el proceso principal")
    finally:
        scraper.cleanup()
        print("\n👋 Sistema finalizado")


if __name__ == "__main__":
    main()
