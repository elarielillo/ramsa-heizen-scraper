"""
Script DEMO - Ejecución simplificada sin API keys
Muestra el funcionamiento básico del sistema de scraping
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from scrapers.web_scraper import RamsaWebScraper, HeizenWebScraper
from scrapers.marketplace_scraper import MercadoLibreScraper, RelatedBusinessScraper
from utils.exporter import DataExporter
from database.models import init_database, get_session, Empresa, Producto, Lead
import json
from datetime import datetime

def demo_web_scraping():
    """Demo de scraping de sitios web"""
    print("\n" + "="*80)
    print("🌐 DEMO 1: Web Scraping de Ramsa y Heizen")
    print("="*80)
    
    # Ramsa
    print("\n📍 Scrapeando Ramsa Importaciones...")
    ramsa = RamsaWebScraper()
    
    print("   - Obteniendo información de contacto...")
    contacto = ramsa.scrape_contact_info()
    print(f"   ✅ Contacto: {json.dumps(contacto, indent=6, ensure_ascii=False)}")
    
    print("\n   - Scrapeando productos...")
    productos_ramsa = ramsa.scrape_products()
    print(f"   ✅ Productos encontrados: {len(productos_ramsa)}")
    
    if productos_ramsa:
        print("\n   📦 Ejemplo de producto:")
        ejemplo = productos_ramsa[0]
        print(f"      Nombre: {ejemplo.get('nombre', 'N/A')}")
        print(f"      Precio: ${ejemplo.get('precio', 'N/A')}")
        print(f"      URL: {ejemplo.get('url_producto', 'N/A')}")
    
    # Heizen
    print("\n📍 Scrapeando Heizen Ecuador...")
    heizen = HeizenWebScraper()
    datos_heizen = heizen.scrape_all_sites()
    
    print(f"   ✅ Productos encontrados: {len(datos_heizen['productos'])}")
    print(f"   ✅ Contacto: {json.dumps(datos_heizen['contacto'], indent=6, ensure_ascii=False)}")
    
    return productos_ramsa + datos_heizen['productos']


def demo_mercadolibre():
    """Demo de scraping de MercadoLibre"""
    print("\n" + "="*80)
    print("🛒 DEMO 2: Scraping de MercadoLibre")
    print("="*80)
    
    ml = MercadoLibreScraper()
    
    keywords = ["calefon electrico", "calefactor"]
    todos_productos = []
    
    for keyword in keywords:
        print(f"\n🔍 Buscando: '{keyword}'")
        productos = ml.search_products(keyword, max_results=10)
        print(f"   ✅ Encontrados: {len(productos)} productos")
        
        if productos:
            ejemplo = productos[0]
            print(f"\n   📦 Ejemplo:")
            print(f"      Nombre: {ejemplo.get('nombre', 'N/A')}")
            print(f"      Precio: ${ejemplo.get('precio', 'N/A')}")
            print(f"      Vendedor: {ejemplo.get('vendedor', 'N/A')}")
        
        todos_productos.extend(productos)
    
    return todos_productos


def demo_lead_generation():
    """Demo de generación de leads"""
    print("\n" + "="*80)
    print("🎯 DEMO 3: Generación de Leads")
    print("="*80)
    
    lead_gen = RelatedBusinessScraper()
    
    print("\n🔍 Buscando empresas relacionadas...")
    
    # Buscar en MercadoLibre
    print("\n   - Buscando vendedores en MercadoLibre...")
    ml_leads = lead_gen.find_related_businesses_mercadolibre("calefones")
    print(f"   ✅ Leads de MercadoLibre: {len(ml_leads)}")
    
    if ml_leads:
        print(f"\n   🏢 Ejemplo de lead:")
        ejemplo = ml_leads[0]
        print(f"      Empresa: {ejemplo.get('nombre_empresa', 'N/A')}")
        print(f"      Productos: {ejemplo.get('productos_encontrados', 0)}")
    
    # Buscar en Google (simulado para demo - puede fallar)
    print("\n   - Buscando en Google (puede tomar tiempo)...")
    try:
        google_leads = lead_gen.search_google_business("calefones quito")
        print(f"   ✅ Leads de Google: {len(google_leads)}")
    except Exception as e:
        print(f"   ⚠️ Google bloqueó la búsqueda (esperado): {e}")
        google_leads = []
    
    return ml_leads + google_leads


def demo_database():
    """Demo de guardado en base de datos"""
    print("\n" + "="*80)
    print("💾 DEMO 4: Base de Datos")
    print("="*80)
    
    print("\n🗄️ Inicializando base de datos...")
    init_database()
    session = get_session()
    
    # Crear empresa de ejemplo
    print("\n   - Guardando empresa de ejemplo...")
    empresa = Empresa(
        nombre="Ramsa Importaciones",
        tipo="principal",
        telefono="+593982234833",
        email="info@ramsa.com",
        website="https://ramsaimportaciones.com",
        ciudad="Quito",
        provincia="Pichincha"
    )
    session.add(empresa)
    session.commit()
    print("   ✅ Empresa guardada")
    
    # Crear producto de ejemplo
    print("\n   - Guardando producto de ejemplo...")
    producto = Producto(
        empresa_id=empresa.id,
        nombre="Calefón Eléctrico Heizen 8.8 kW",
        categoria="Calefones Eléctricos",
        precio=450.00,
        descripcion="Calefón eléctrico con tecnología de inducción",
        fuente="demo"
    )
    session.add(producto)
    session.commit()
    print("   ✅ Producto guardado")
    
    # Consultar datos
    print("\n   - Consultando base de datos...")
    total_empresas = session.query(Empresa).count()
    total_productos = session.query(Producto).count()
    total_leads = session.query(Lead).count()
    
    print(f"\n   📊 Estadísticas de la base de datos:")
    print(f"      Empresas: {total_empresas}")
    print(f"      Productos: {total_productos}")
    print(f"      Leads: {total_leads}")
    
    session.close()


def demo_export(productos):
    """Demo de exportación"""
    print("\n" + "="*80)
    print("📊 DEMO 5: Exportación de Datos")
    print("="*80)
    
    exporter = DataExporter()
    
    # Preparar datos mínimos
    empresas = [
        {
            'nombre': 'Ramsa Importaciones',
            'telefono': '+593982234833',
            'website': 'https://ramsaimportaciones.com',
            'ciudad': 'Quito'
        },
        {
            'nombre': 'Heizen Ecuador',
            'telefono': '(02) 243-4381',
            'website': 'https://calefonecuador.com',
            'ciudad': 'Quito'
        }
    ]
    
    leads = [
        {
            'nombre_empresa': 'Ejemplo Lead 1',
            'telefono': '0999999999',
            'fuente_lead': 'demo',
            'score_calidad': 75,
            'nivel_prioridad': 'alto'
        }
    ]
    
    print("\n📁 Exportando a Excel...")
    excel_path = exporter.export_to_excel(
        productos=productos[:20] if len(productos) > 20 else productos,
        empresas=empresas,
        resenas=[],
        leads=leads
    )
    print(f"   ✅ Excel generado: {excel_path}")
    
    print("\n📄 Generando reporte resumen...")
    report_path = exporter.export_summary_report(
        productos=productos,
        empresas=empresas,
        resenas=[],
        leads=leads
    )
    print(f"   ✅ Reporte generado: {report_path}")
    
    return excel_path, report_path


def main():
    """Función principal del demo"""
    print("""
    ╔════════════════════════════════════════════════════════════════╗
    ║                         DEMO MODE                              ║
    ║     Sistema de Scraping - Ramsa & Heizen                      ║
    ║                                                                ║
    ║  Este demo muestra las funcionalidades básicas sin API keys   ║
    ╚════════════════════════════════════════════════════════════════╝
    """)
    
    input("\nPresiona ENTER para comenzar el demo...")
    
    try:
        # Demo 1: Web Scraping
        productos_web = demo_web_scraping()
        input("\n✅ Demo 1 completado. Presiona ENTER para continuar...")
        
        # Demo 2: MercadoLibre
        productos_ml = demo_mercadolibre()
        input("\n✅ Demo 2 completado. Presiona ENTER para continuar...")
        
        # Demo 3: Generación de Leads
        leads = demo_lead_generation()
        input("\n✅ Demo 3 completado. Presiona ENTER para continuar...")
        
        # Demo 4: Base de Datos
        demo_database()
        input("\n✅ Demo 4 completado. Presiona ENTER para continuar...")
        
        # Demo 5: Exportación
        todos_productos = productos_web + productos_ml
        excel_path, report_path = demo_export(todos_productos)
        
        # Resumen final
        print("\n" + "="*80)
        print("✅ DEMO COMPLETADO EXITOSAMENTE")
        print("="*80)
        print(f"\n📊 Resumen:")
        print(f"   - Productos scrapeados: {len(todos_productos)}")
        print(f"   - Leads generados: {len(leads)}")
        print(f"\n📁 Archivos generados:")
        print(f"   - Excel: {excel_path}")
        print(f"   - Reporte: {report_path}")
        print(f"\n💡 Para usar el sistema completo con IA:")
        print(f"   1. Configura ANTHROPIC_API_KEY en .env")
        print(f"   2. Ejecuta: python main.py")
        
    except KeyboardInterrupt:
        print("\n\n⚠️ Demo interrumpido por el usuario")
    except Exception as e:
        print(f"\n\n❌ Error durante el demo: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n👋 Demo finalizado")


if __name__ == "__main__":
    main()
