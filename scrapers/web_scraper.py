"""
Scrapers para extraer datos de sitios web de Ramsa y Heizen
"""
import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
from urllib.parse import urljoin, urlparse
import time
from loguru import logger
from config.settings import SCRAPING_CONFIG, TARGET_URLS
from fake_useragent import UserAgent


class BaseScraper:
    """Clase base para todos los scrapers"""
    
    def __init__(self):
        self.ua = UserAgent()
        self.session = requests.Session()
        self.timeout = SCRAPING_CONFIG["timeout"]
        self.max_retries = SCRAPING_CONFIG["max_retries"]
        self.delay = SCRAPING_CONFIG["delay_between_requests"]
    
    def get_headers(self) -> Dict[str, str]:
        """Obtener headers para las peticiones"""
        return {
            'User-Agent': self.ua.random,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'es-ES,es;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
        }
    
    def fetch_url(self, url: str, retries: int = 0) -> Optional[BeautifulSoup]:
        """
        Obtener contenido HTML de una URL
        
        Args:
            url: URL a scrapear
            retries: Número de reintento actual
            
        Returns:
            Objeto BeautifulSoup o None si falla
        """
        try:
            time.sleep(self.delay)  # Rate limiting
            
            response = self.session.get(
                url,
                headers=self.get_headers(),
                timeout=self.timeout
            )
            response.raise_for_status()
            
            logger.info(f"✅ Descargado: {url}")
            return BeautifulSoup(response.content, 'lxml')
            
        except requests.exceptions.RequestException as e:
            if retries < self.max_retries:
                logger.warning(f"⚠️ Error en {url}. Reintentando... ({retries + 1}/{self.max_retries})")
                time.sleep(self.delay * (retries + 1))  # Backoff exponencial
                return self.fetch_url(url, retries + 1)
            else:
                logger.error(f"❌ Error definitivo en {url}: {e}")
                return None
    
    def extract_text(self, element, selector: str, default: str = "") -> str:
        """Extraer texto de un elemento de forma segura"""
        try:
            found = element.select_one(selector)
            return found.get_text(strip=True) if found else default
        except Exception:
            return default
    
    def extract_attribute(self, element, selector: str, attribute: str, default: str = "") -> str:
        """Extraer atributo de un elemento de forma segura"""
        try:
            found = element.select_one(selector)
            return found.get(attribute, default) if found else default
        except Exception:
            return default


class RamsaWebScraper(BaseScraper):
    """Scraper específico para el sitio web de Ramsa Importaciones"""
    
    def __init__(self):
        super().__init__()
        self.base_url = TARGET_URLS["ramsa"]["website"]
    
    def scrape_products(self) -> List[Dict]:
        """
        Extraer todos los productos del sitio web de Ramsa
        
        Returns:
            Lista de diccionarios con información de productos
        """
        products = []
        
        # Páginas principales a scrapear
        categories_urls = [
            f"{self.base_url}/",
            f"{self.base_url}/calefactores/",
            f"{self.base_url}/juegos-infantiles/",
        ]
        
        for url in categories_urls:
            logger.info(f"Scrapeando categoría: {url}")
            soup = self.fetch_url(url)
            
            if not soup:
                continue
            
            # Buscar productos en la página
            product_elements = soup.select('.product, .woocommerce-loop-product__link, article.product')
            
            for product_elem in product_elements:
                try:
                    product_data = self._extract_product_data(product_elem)
                    if product_data:
                        products.append(product_data)
                except Exception as e:
                    logger.error(f"Error extrayendo producto: {e}")
                    continue
        
        logger.info(f"📦 Total productos encontrados en Ramsa: {len(products)}")
        return products
    
    def _extract_product_data(self, element) -> Optional[Dict]:
        """Extraer datos de un elemento de producto"""
        
        # Nombre del producto
        nombre = self.extract_text(element, 'h2.woocommerce-loop-product__title, .product-title, h2 a')
        if not nombre:
            nombre = self.extract_text(element, 'a')
        
        if not nombre:
            return None
        
        # URL del producto
        url_producto = self.extract_attribute(element, 'a', 'href')
        if url_producto:
            url_producto = urljoin(self.base_url, url_producto)
        
        # Precio
        precio_text = self.extract_text(element, '.price .amount, .woocommerce-Price-amount, .price')
        precio = self._parse_price(precio_text)
        
        # Imagen
        imagen_url = self.extract_attribute(element, 'img', 'src')
        if imagen_url:
            imagen_url = urljoin(self.base_url, imagen_url)
        
        # Descripción breve
        descripcion = self.extract_text(element, '.woocommerce-product-details__short-description, .product-excerpt')
        
        product_data = {
            'nombre': nombre,
            'url_producto': url_producto,
            'precio': precio,
            'imagen_url': imagen_url,
            'descripcion': descripcion,
            'fuente': 'website_ramsa',
            'empresa': 'ramsa'
        }
        
        # Obtener detalles adicionales si tenemos URL
        if url_producto:
            detalles = self._scrape_product_details(url_producto)
            product_data.update(detalles)
        
        return product_data
    
    def _scrape_product_details(self, url: str) -> Dict:
        """Obtener detalles completos de un producto"""
        soup = self.fetch_url(url)
        if not soup:
            return {}
        
        detalles = {}
        
        # Descripción completa
        descripcion_completa = self.extract_text(
            soup, 
            '.woocommerce-product-details__short-description, #tab-description, .product-description'
        )
        if descripcion_completa:
            detalles['descripcion_completa'] = descripcion_completa
        
        # Especificaciones técnicas
        especificaciones = {}
        specs_table = soup.select_one('.woocommerce-product-attributes, .shop_attributes')
        if specs_table:
            rows = specs_table.select('tr')
            for row in rows:
                label = self.extract_text(row, 'th, .label')
                value = self.extract_text(row, 'td, .value')
                if label and value:
                    especificaciones[label] = value
        
        if especificaciones:
            detalles['especificaciones'] = especificaciones
        
        # Imágenes adicionales
        imagenes_adicionales = []
        for img in soup.select('.woocommerce-product-gallery__image img, .product-images img'):
            img_url = img.get('src', '') or img.get('data-src', '')
            if img_url:
                imagenes_adicionales.append(urljoin(self.base_url, img_url))
        
        if imagenes_adicionales:
            detalles['imagenes_adicionales'] = imagenes_adicionales
        
        return detalles
    
    def _parse_price(self, price_text: str) -> Optional[float]:
        """Convertir texto de precio a float"""
        if not price_text:
            return None
        
        # Limpiar el texto
        price_text = price_text.replace('$', '').replace('USD', '').replace(',', '').strip()
        
        try:
            return float(price_text)
        except ValueError:
            return None
    
    def scrape_contact_info(self) -> Dict:
        """Extraer información de contacto del sitio"""
        soup = self.fetch_url(self.base_url)
        if not soup:
            return {}
        
        contact_info = {}
        
        # Buscar información de contacto en el footer o página de contacto
        footer = soup.select_one('footer, .footer, .site-footer')
        if footer:
            # Teléfono
            telefono = self.extract_text(footer, 'a[href^="tel:"], .phone, .telefono')
            if telefono:
                contact_info['telefono'] = telefono
            
            # Email
            email = self.extract_text(footer, 'a[href^="mailto:"], .email')
            if email:
                contact_info['email'] = email
            
            # Dirección
            direccion = self.extract_text(footer, '.address, .direccion, address')
            if direccion:
                contact_info['direccion'] = direccion
        
        logger.info(f"📞 Información de contacto extraída: {contact_info}")
        return contact_info


class HeizenWebScraper(BaseScraper):
    """Scraper específico para sitios web de Heizen"""
    
    def __init__(self):
        super().__init__()
        self.base_urls = [
            TARGET_URLS["heizen"]["website"],
            TARGET_URLS["heizen"]["website_alt"],
            TARGET_URLS["heizen"]["website_alt2"]
        ]
    
    def scrape_all_sites(self) -> Dict:
        """Scrapear todos los sitios de Heizen"""
        all_data = {
            'productos': [],
            'contacto': {},
            'servicios': []
        }
        
        for url in self.base_urls:
            logger.info(f"🔍 Scrapeando sitio Heizen: {url}")
            
            # Productos
            products = self.scrape_products(url)
            all_data['productos'].extend(products)
            
            # Contacto
            contact = self.scrape_contact_info(url)
            all_data['contacto'].update(contact)
        
        return all_data
    
    def scrape_products(self, base_url: str) -> List[Dict]:
        """Extraer productos de un sitio de Heizen"""
        products = []
        
        soup = self.fetch_url(base_url)
        if not soup:
            return products
        
        # Buscar productos
        product_elements = soup.select('.product, article.product, .woocommerce-loop-product__link')
        
        for elem in product_elements:
            try:
                product = self._extract_heizen_product(elem, base_url)
                if product:
                    products.append(product)
            except Exception as e:
                logger.error(f"Error extrayendo producto Heizen: {e}")
        
        logger.info(f"📦 Productos Heizen encontrados en {base_url}: {len(products)}")
        return products
    
    def _extract_heizen_product(self, element, base_url: str) -> Optional[Dict]:
        """Extraer datos de producto Heizen"""
        nombre = self.extract_text(element, 'h2, h3, .product-title, a')
        if not nombre:
            return None
        
        return {
            'nombre': nombre,
            'url_producto': urljoin(base_url, self.extract_attribute(element, 'a', 'href')),
            'precio': self._parse_price(self.extract_text(element, '.price, .amount')),
            'imagen_url': urljoin(base_url, self.extract_attribute(element, 'img', 'src')),
            'descripcion': self.extract_text(element, '.product-description, .excerpt'),
            'fuente': 'website_heizen',
            'empresa': 'heizen'
        }
    
    def _parse_price(self, price_text: str) -> Optional[float]:
        """Convertir texto de precio a float"""
        if not price_text:
            return None
        price_text = price_text.replace('$', '').replace('USD', '').replace(',', '').strip()
        try:
            return float(price_text)
        except ValueError:
            return None
    
    def scrape_contact_info(self, base_url: str) -> Dict:
        """Extraer información de contacto"""
        soup = self.fetch_url(base_url)
        if not soup:
            return {}
        
        contact = {}
        
        # Buscar en footer
        footer = soup.select_one('footer, .footer')
        if footer:
            telefono = self.extract_text(footer, 'a[href^="tel:"], .phone')
            if telefono:
                contact['telefono'] = telefono
            
            email = self.extract_text(footer, 'a[href^="mailto:"], .email')
            if email:
                contact['email'] = email
        
        return contact


# Ejemplo de uso
if __name__ == "__main__":
    logger.info("Iniciando scraping de Ramsa y Heizen...")
    
    # Scraper Ramsa
    ramsa_scraper = RamsaWebScraper()
    ramsa_products = ramsa_scraper.scrape_products()
    ramsa_contact = ramsa_scraper.scrape_contact_info()
    
    print(f"\n📊 Resultados Ramsa:")
    print(f"Productos: {len(ramsa_products)}")
    print(f"Contacto: {ramsa_contact}")
    
    # Scraper Heizen
    heizen_scraper = HeizenWebScraper()
    heizen_data = heizen_scraper.scrape_all_sites()
    
    print(f"\n📊 Resultados Heizen:")
    print(f"Productos: {len(heizen_data['productos'])}")
    print(f"Contacto: {heizen_data['contacto']}")
