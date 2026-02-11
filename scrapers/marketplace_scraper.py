"""
Scraper para MercadoLibre y generador de leads de empresas relacionadas
"""
import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
from loguru import logger
from scrapers.web_scraper import BaseScraper
from config.settings import RELATED_BUSINESS_KEYWORDS


class MercadoLibreScraper(BaseScraper):
    """Scraper para MercadoLibre Ecuador"""
    
    def __init__(self):
        super().__init__()
        self.base_url = "https://listado.mercadolibre.com.ec"
    
    def search_products(self, query: str, max_results: int = 50) -> List[Dict]:
        """
        Buscar productos en MercadoLibre
        
        Args:
            query: Término de búsqueda
            max_results: Máximo número de resultados
            
        Returns:
            Lista de productos encontrados
        """
        products = []
        search_url = f"{self.base_url}/{query.replace(' ', '-')}"
        
        logger.info(f"🔍 Buscando en MercadoLibre: {query}")
        
        soup = self.fetch_url(search_url)
        if not soup:
            return products
        
        # Buscar elementos de productos
        product_items = soup.select('.ui-search-result__content, .ui-search-result')
        
        for item in product_items[:max_results]:
            try:
                product = self._extract_ml_product(item)
                if product:
                    products.append(product)
            except Exception as e:
                logger.error(f"Error extrayendo producto ML: {e}")
        
        logger.info(f"📦 Productos ML encontrados: {len(products)}")
        return products
    
    def _extract_ml_product(self, element) -> Optional[Dict]:
        """Extraer datos de un producto de MercadoLibre"""
        
        # Nombre
        nombre = self.extract_text(element, '.ui-search-item__title, h2')
        if not nombre:
            return None
        
        # Precio
        precio_text = self.extract_text(element, '.price-tag-amount, .price-tag-fraction')
        precio = self._parse_ml_price(precio_text)
        
        # URL
        url = self.extract_attribute(element, 'a.ui-search-link', 'href')
        
        # Imagen
        imagen = self.extract_attribute(element, 'img', 'src') or self.extract_attribute(element, 'img', 'data-src')
        
        # Vendedor
        vendedor = self.extract_text(element, '.ui-search-item__brand-discoverability, .ui-search-official-store-label')
        
        # Calificación
        calificacion_elem = element.select_one('.ui-search-reviews__rating-number')
        calificacion = None
        if calificacion_elem:
            try:
                calificacion = float(calificacion_elem.get_text(strip=True))
            except:
                pass
        
        return {
            'nombre': nombre,
            'precio': precio,
            'url_producto': url,
            'imagen_url': imagen,
            'vendedor': vendedor,
            'calificacion': calificacion,
            'fuente': 'mercadolibre',
            'marketplace': 'MercadoLibre'
        }
    
    def _parse_ml_price(self, price_text: str) -> Optional[float]:
        """Parsear precio de MercadoLibre"""
        if not price_text:
            return None
        
        # Limpiar texto
        price_text = price_text.replace('$', '').replace('.', '').replace(',', '.').strip()
        
        try:
            return float(price_text)
        except ValueError:
            return None
    
    def scrape_seller_info(self, seller_name: str) -> Dict:
        """
        Obtener información de un vendedor específico
        
        Args:
            seller_name: Nombre del vendedor
            
        Returns:
            Información del vendedor
        """
        # Buscar tienda del vendedor
        search_url = f"https://eshops.mercadolibre.com.ec/{seller_name.replace(' ', '+')}"
        
        soup = self.fetch_url(search_url)
        if not soup:
            return {}
        
        seller_info = {
            'nombre': seller_name,
            'url_tienda': search_url
        }
        
        # Extraer información adicional si está disponible
        # Esto depende de la estructura de ML que puede cambiar
        
        return seller_info


class RelatedBusinessScraper(BaseScraper):
    """Scraper para encontrar empresas relacionadas a Ramsa/Heizen"""
    
    def __init__(self):
        super().__init__()
    
    def search_google_business(self, keyword: str, location: str = "Quito Ecuador") -> List[Dict]:
        """
        Buscar empresas en Google
        
        Args:
            keyword: Palabra clave de búsqueda
            location: Ubicación
            
        Returns:
            Lista de empresas encontradas
        """
        leads = []
        
        # Construir URL de búsqueda de Google
        search_query = f"{keyword} {location}"
        google_url = f"https://www.google.com/search?q={search_query.replace(' ', '+')}"
        
        logger.info(f"🔍 Buscando empresas: {search_query}")
        
        soup = self.fetch_url(google_url)
        if not soup:
            return leads
        
        # Extraer resultados de búsqueda
        # Nota: Google puede bloquear scraping, esto es solo demostrativo
        # En producción, usar Google Places API
        
        result_divs = soup.select('.g, .tF2Cxc')
        
        for result in result_divs[:10]:  # Primeros 10 resultados
            try:
                lead = self._extract_google_result(result)
                if lead:
                    leads.append(lead)
            except Exception as e:
                logger.error(f"Error extrayendo resultado de Google: {e}")
        
        logger.info(f"🎯 Leads encontrados para '{keyword}': {len(leads)}")
        return leads
    
    def _extract_google_result(self, element) -> Optional[Dict]:
        """Extraer información de un resultado de Google"""
        
        # Título/Nombre
        nombre = self.extract_text(element, 'h3, .DKV0Md')
        if not nombre:
            return None
        
        # URL
        url = self.extract_attribute(element, 'a', 'href')
        
        # Descripción/Snippet
        descripcion = self.extract_text(element, '.VwiC3b, .aCOpRe, .s3v9rd')
        
        return {
            'nombre_empresa': nombre,
            'website': url,
            'descripcion': descripcion,
            'fuente_lead': 'google_search'
        }
    
    def find_related_businesses_mercadolibre(self, category: str) -> List[Dict]:
        """
        Encontrar vendedores relacionados en MercadoLibre
        
        Args:
            category: Categoría de productos
            
        Returns:
            Lista de vendedores/leads
        """
        ml_scraper = MercadoLibreScraper()
        products = ml_scraper.search_products(category, max_results=50)
        
        # Extraer vendedores únicos
        vendors = {}
        for product in products:
            vendor_name = product.get('vendedor')
            if vendor_name and vendor_name not in vendors:
                vendors[vendor_name] = {
                    'nombre_empresa': vendor_name,
                    'tipo_negocio': 'vendedor_marketplace',
                    'productos_encontrados': 1,
                    'fuente_lead': 'mercadolibre'
                }
            elif vendor_name:
                vendors[vendor_name]['productos_encontrados'] += 1
        
        return list(vendors.values())
    
    def scrape_ecuadornegocios(self, keyword: str) -> List[Dict]:
        """
        Scrapear ecuadornegocios.com para encontrar empresas
        
        Args:
            keyword: Palabra clave
            
        Returns:
            Lista de empresas
        """
        leads = []
        base_url = "https://ecuadornegocios.com"
        search_url = f"{base_url}/buscar?q={keyword.replace(' ', '+')}"
        
        logger.info(f"🔍 Buscando en Ecuador Negocios: {keyword}")
        
        soup = self.fetch_url(search_url)
        if not soup:
            return leads
        
        # Extraer listados de empresas
        business_cards = soup.select('.business-card, .company-listing, .result-item')
        
        for card in business_cards[:20]:  # Limitar a 20 resultados
            try:
                lead = {
                    'nombre_empresa': self.extract_text(card, 'h2, h3, .company-name'),
                    'direccion': self.extract_text(card, '.address, .direccion'),
                    'telefono': self.extract_text(card, '.phone, .telefono, a[href^="tel:"]'),
                    'ciudad': self.extract_text(card, '.city, .ciudad'),
                    'tipo_negocio': self.extract_text(card, '.category, .categoria'),
                    'fuente_lead': 'ecuadornegocios'
                }
                
                if lead['nombre_empresa']:
                    leads.append(lead)
            except Exception as e:
                logger.error(f"Error extrayendo empresa: {e}")
        
        logger.info(f"🎯 Empresas encontradas en Ecuador Negocios: {len(leads)}")
        return leads
    
    def generate_all_leads(self) -> List[Dict]:
        """
        Generar todos los leads posibles de empresas relacionadas
        
        Returns:
            Lista consolidada de leads
        """
        all_leads = []
        
        logger.info("🚀 Iniciando generación de leads...")
        
        # 1. Buscar en MercadoLibre
        for keyword in RELATED_BUSINESS_KEYWORDS[:3]:  # Primeras 3 palabras clave
            ml_leads = self.find_related_businesses_mercadolibre(keyword)
            all_leads.extend(ml_leads)
        
        # 2. Buscar en Google (con precaución por rate limiting)
        for keyword in RELATED_BUSINESS_KEYWORDS[:2]:  # Solo 2 búsquedas
            try:
                google_leads = self.search_google_business(keyword)
                all_leads.extend(google_leads)
            except Exception as e:
                logger.warning(f"Error buscando en Google: {e}")
        
        # 3. Buscar en Ecuador Negocios
        for keyword in ["calefones quito", "importadora hogar"]:
            try:
                ec_leads = self.scrape_ecuadornegocios(keyword)
                all_leads.extend(ec_leads)
            except Exception as e:
                logger.warning(f"Error en Ecuador Negocios: {e}")
        
        # Eliminar duplicados basados en nombre
        unique_leads = {}
        for lead in all_leads:
            nombre = lead.get('nombre_empresa', '')
            if nombre and nombre not in unique_leads:
                unique_leads[nombre] = lead
        
        final_leads = list(unique_leads.values())
        logger.info(f"✅ Total de leads únicos generados: {len(final_leads)}")
        
        return final_leads


# Ejemplo de uso
if __name__ == "__main__":
    # Test MercadoLibre
    ml_scraper = MercadoLibreScraper()
    productos = ml_scraper.search_products("calefon electrico", max_results=10)
    print(f"\n📦 Productos MercadoLibre: {len(productos)}")
    if productos:
        print(f"Ejemplo: {productos[0]}")
    
    # Test generador de leads
    lead_generator = RelatedBusinessScraper()
    leads = lead_generator.generate_all_leads()
    print(f"\n🎯 Leads generados: {len(leads)}")
    if leads:
        print(f"Ejemplo: {leads[0]}")
