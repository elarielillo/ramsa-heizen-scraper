"""
Sistema de enriquecimiento de datos usando Claude AI
"""
import json
from anthropic import Anthropic
from typing import Dict, List, Optional, Any
from config.settings import ANTHROPIC_API_KEY, AI_ENRICHMENT_CONFIG
from loguru import logger


class AIEnricher:
    """Clase para enriquecer datos usando Claude AI"""
    
    def __init__(self, api_key: str = ANTHROPIC_API_KEY):
        """
        Inicializar el enriquecedor de IA
        
        Args:
            api_key: API key de Anthropic
        """
        if not api_key:
            raise ValueError("Se requiere ANTHROPIC_API_KEY")
        
        self.client = Anthropic(api_key=api_key)
        self.model = AI_ENRICHMENT_CONFIG["model"]
        self.max_tokens = AI_ENRICHMENT_CONFIG["max_tokens"]
        self.temperature = AI_ENRICHMENT_CONFIG["temperature"]
    
    def _call_claude(self, prompt: str, system_prompt: str = "") -> str:
        """
        Llamar a Claude API
        
        Args:
            prompt: Prompt del usuario
            system_prompt: Prompt del sistema
            
        Returns:
            Respuesta de Claude
        """
        try:
            messages = [{"role": "user", "content": prompt}]
            
            response = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                system=system_prompt if system_prompt else "",
                messages=messages
            )
            
            return response.content[0].text
            
        except Exception as e:
            logger.error(f"Error llamando a Claude API: {e}")
            return ""
    
    def enrich_product_description(
        self, 
        nombre: str, 
        descripcion_original: str = "",
        especificaciones: Dict = None
    ) -> Dict[str, Any]:
        """
        Enriquecer descripción de producto
        
        Args:
            nombre: Nombre del producto
            descripcion_original: Descripción original del producto
            especificaciones: Especificaciones técnicas
            
        Returns:
            Diccionario con descripción enriquecida y metadatos
        """
        system_prompt = """Eres un experto en marketing de productos para el hogar en Ecuador. 
Tu tarea es crear descripciones de productos atractivas, informativas y orientadas a la venta.
Debes usar un tono persuasivo pero profesional, resaltando beneficios clave."""
        
        especificaciones_texto = ""
        if especificaciones:
            especificaciones_texto = "\n".join([f"- {k}: {v}" for k, v in especificaciones.items()])
        
        prompt = f"""
Producto: {nombre}
Descripción original: {descripcion_original if descripcion_original else "No disponible"}
Especificaciones técnicas:
{especificaciones_texto if especificaciones_texto else "No disponibles"}

Por favor:
1. Crea una descripción mejorada y persuasiva del producto (2-3 párrafos)
2. Extrae 5-7 palabras clave relevantes
3. Sugiere una categoría apropiada
4. Identifica los beneficios principales (3-5 puntos)

Responde en formato JSON:
{{
    "descripcion_enriquecida": "...",
    "palabras_clave": ["..."],
    "categoria_sugerida": "...",
    "beneficios": ["..."],
    "publico_objetivo": "..."
}}
"""
        
        response = self._call_claude(prompt, system_prompt)
        
        try:
            # Limpiar la respuesta en caso de que venga con markdown
            cleaned_response = response.strip()
            if cleaned_response.startswith("```json"):
                cleaned_response = cleaned_response[7:]
            if cleaned_response.endswith("```"):
                cleaned_response = cleaned_response[:-3]
            
            result = json.loads(cleaned_response.strip())
            logger.info(f"Producto '{nombre}' enriquecido exitosamente")
            return result
        except json.JSONDecodeError as e:
            logger.error(f"Error parseando respuesta JSON: {e}")
            return {
                "descripcion_enriquecida": descripcion_original,
                "palabras_clave": [],
                "categoria_sugerida": "General",
                "beneficios": [],
                "publico_objetivo": "General"
            }
    
    def categorize_product(
        self, 
        nombre: str, 
        descripcion: str = ""
    ) -> Dict[str, str]:
        """
        Categorizar producto automáticamente
        
        Args:
            nombre: Nombre del producto
            descripcion: Descripción del producto
            
        Returns:
            Diccionario con categoría y subcategoría
        """
        system_prompt = """Eres un experto en clasificación de productos para tiendas de Ecuador.
Categoriza productos de manera precisa según su naturaleza y uso."""
        
        prompt = f"""
Producto: {nombre}
Descripción: {descripcion}

Categorías disponibles:
- Calefones Eléctricos
- Calefones a Gas
- Calefactores
- Termotanques
- Juguetes Infantiles
- Artículos para Hogar
- Piscinas
- Productos Varios

Asigna este producto a la categoría más apropiada y sugiere una subcategoría.

Responde en formato JSON:
{{
    "categoria": "...",
    "subcategoria": "...",
    "confianza": 0.95
}}
"""
        
        response = self._call_claude(prompt, system_prompt)
        
        try:
            cleaned_response = response.strip()
            if cleaned_response.startswith("```json"):
                cleaned_response = cleaned_response[7:]
            if cleaned_response.endswith("```"):
                cleaned_response = cleaned_response[:-3]
            
            result = json.loads(cleaned_response.strip())
            return result
        except json.JSONDecodeError:
            return {"categoria": "Productos Varios", "subcategoria": "General", "confianza": 0.5}
    
    def analyze_review_sentiment(
        self, 
        review_text: str
    ) -> Dict[str, Any]:
        """
        Analizar sentimiento de una reseña
        
        Args:
            review_text: Texto de la reseña
            
        Returns:
            Diccionario con análisis de sentimiento
        """
        system_prompt = """Eres un experto en análisis de sentimientos de reseñas de clientes.
Analiza el tono, sentimiento y temas clave de cada reseña."""
        
        prompt = f"""
Reseña del cliente:
"{review_text}"

Analiza esta reseña y extrae:
1. Sentimiento general (positivo/neutral/negativo)
2. Score de sentimiento (-1 a 1)
3. Temas principales mencionados
4. Palabras clave
5. Aspectos positivos mencionados
6. Aspectos negativos mencionados

Responde en formato JSON:
{{
    "sentimiento": "positivo",
    "sentimiento_score": 0.8,
    "temas_principales": ["calidad", "precio", "entrega"],
    "palabras_clave": ["..."],
    "aspectos_positivos": ["..."],
    "aspectos_negativos": ["..."],
    "resumen": "..."
}}
"""
        
        response = self._call_claude(prompt, system_prompt)
        
        try:
            cleaned_response = response.strip()
            if cleaned_response.startswith("```json"):
                cleaned_response = cleaned_response[7:]
            if cleaned_response.endswith("```"):
                cleaned_response = cleaned_response[:-3]
            
            result = json.loads(cleaned_response.strip())
            return result
        except json.JSONDecodeError:
            return {
                "sentimiento": "neutral",
                "sentimiento_score": 0.0,
                "temas_principales": [],
                "palabras_clave": [],
                "aspectos_positivos": [],
                "aspectos_negativos": [],
                "resumen": review_text[:100]
            }
    
    def analyze_social_post(
        self, 
        post_content: str, 
        platform: str = "facebook"
    ) -> Dict[str, Any]:
        """
        Analizar post de redes sociales
        
        Args:
            post_content: Contenido del post
            platform: Plataforma ('facebook', 'instagram', etc.)
            
        Returns:
            Diccionario con análisis del post
        """
        system_prompt = """Eres un experto en análisis de redes sociales y marketing digital.
Analiza posts para extraer insights valiosos."""
        
        prompt = f"""
Post de {platform}:
"{post_content}"

Analiza este post y extrae:
1. Temas principales
2. Productos mencionados (si hay)
3. Llamado a la acción (CTA) si existe
4. Tono del mensaje
5. Estrategia de marketing evidente

Responde en formato JSON:
{{
    "temas": ["..."],
    "productos_mencionados": ["..."],
    "cta_presente": true/false,
    "tipo_cta": "...",
    "tono": "...",
    "estrategia": "...",
    "hashtags_sugeridos": ["..."]
}}
"""
        
        response = self._call_claude(prompt, system_prompt)
        
        try:
            cleaned_response = response.strip()
            if cleaned_response.startswith("```json"):
                cleaned_response = cleaned_response[7:]
            if cleaned_response.endswith("```"):
                cleaned_response = cleaned_response[:-3]
            
            result = json.loads(cleaned_response.strip())
            return result
        except json.JSONDecodeError:
            return {
                "temas": [],
                "productos_mencionados": [],
                "cta_presente": False,
                "tipo_cta": "",
                "tono": "neutral",
                "estrategia": "",
                "hashtags_sugeridos": []
            }
    
    def score_lead_quality(
        self, 
        lead_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Evaluar calidad de un lead
        
        Args:
            lead_info: Información del lead
            
        Returns:
            Diccionario con scoring del lead
        """
        system_prompt = """Eres un experto en calificación de leads para ventas B2B.
Evalúa la calidad y potencial de cada lead basándote en la información disponible."""
        
        lead_str = json.dumps(lead_info, indent=2, ensure_ascii=False)
        
        prompt = f"""
Información del lead:
{lead_str}

Evalúa este lead considerando:
1. Similitud con Ramsa/Heizen (productos similares, ubicación, mercado)
2. Potencial de negocio
3. Información de contacto disponible
4. Presencia online

Asigna un score de calidad (0-100) y nivel de prioridad.

Responde en formato JSON:
{{
    "score_calidad": 85,
    "nivel_prioridad": "alto",
    "similitud_ramsa_heizen": 0.8,
    "productos_potenciales": ["..."],
    "razon_lead": "...",
    "accion_recomendada": "..."
}}
"""
        
        response = self._call_claude(prompt, system_prompt)
        
        try:
            cleaned_response = response.strip()
            if cleaned_response.startswith("```json"):
                cleaned_response = cleaned_response[7:]
            if cleaned_response.endswith("```"):
                cleaned_response = cleaned_response[:-3]
            
            result = json.loads(cleaned_response.strip())
            return result
        except json.JSONDecodeError:
            return {
                "score_calidad": 50,
                "nivel_prioridad": "medio",
                "similitud_ramsa_heizen": 0.5,
                "productos_potenciales": [],
                "razon_lead": "Lead requiere más información",
                "accion_recomendada": "Investigar más"
            }
    
    def analyze_price_competitiveness(
        self, 
        producto: str,
        precio_actual: float,
        precios_competencia: List[float]
    ) -> Dict[str, Any]:
        """
        Analizar competitividad de precios
        
        Args:
            producto: Nombre del producto
            precio_actual: Precio actual del producto
            precios_competencia: Lista de precios de la competencia
            
        Returns:
            Análisis de competitividad
        """
        if not precios_competencia:
            return {
                "posicion_mercado": "desconocida",
                "recomendacion": "Recopilar más datos de competencia"
            }
        
        precio_min = min(precios_competencia)
        precio_max = max(precios_competencia)
        precio_promedio = sum(precios_competencia) / len(precios_competencia)
        
        system_prompt = """Eres un experto en estrategia de precios y análisis competitivo."""
        
        prompt = f"""
Producto: {producto}
Precio actual: ${precio_actual}
Precio mínimo competencia: ${precio_min}
Precio máximo competencia: ${precio_max}
Precio promedio competencia: ${precio_promedio}

Analiza la posición competitiva y da recomendaciones.

Responde en formato JSON:
{{
    "posicion_mercado": "competitivo/premium/economico",
    "diferencia_porcentual": 15.5,
    "recomendacion": "...",
    "estrategia_sugerida": "..."
}}
"""
        
        response = self._call_claude(prompt, system_prompt)
        
        try:
            cleaned_response = response.strip()
            if cleaned_response.startswith("```json"):
                cleaned_response = cleaned_response[7:]
            if cleaned_response.endswith("```"):
                cleaned_response = cleaned_response[:-3]
            
            result = json.loads(cleaned_response.strip())
            return result
        except json.JSONDecodeError:
            return {
                "posicion_mercado": "promedio",
                "diferencia_porcentual": 0,
                "recomendacion": "Mantener precio actual",
                "estrategia_sugerida": "Monitorear competencia"
            }


# Ejemplo de uso
if __name__ == "__main__":
    # Requiere tener ANTHROPIC_API_KEY en .env
    try:
        enricher = AIEnricher()
        
        # Ejemplo de enriquecimiento de producto
        result = enricher.enrich_product_description(
            nombre="Calefón Eléctrico Heizen 8.8 kW",
            descripcion_original="Calefón eléctrico a inducción",
            especificaciones={
                "Potencia": "8.8 kW",
                "Tecnología": "Inducción electromagnética",
                "Garantía": "24 meses"
            }
        )
        
        print("Resultado de enriquecimiento:")
        print(json.dumps(result, indent=2, ensure_ascii=False))
        
    except ValueError as e:
        print(f"Error: {e}")
        print("Asegúrate de configurar ANTHROPIC_API_KEY en tu archivo .env")
