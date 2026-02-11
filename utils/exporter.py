"""
Módulo para exportar datos a Excel con análisis y visualizaciones
"""
import pandas as pd
from typing import List, Dict
from datetime import datetime
from pathlib import Path
import json
from loguru import logger
from config.settings import EXPORTS_DIR, EXPORT_CONFIG


class DataExporter:
    """Clase para exportar datos a diferentes formatos"""
    
    def __init__(self, output_dir: Path = EXPORTS_DIR):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
    
    def export_to_excel(
        self,
        productos: List[Dict],
        empresas: List[Dict],
        resenas: List[Dict],
        leads: List[Dict],
        posts_sociales: List[Dict] = None,
        filename: str = None
    ) -> str:
        """
        Exportar todos los datos a un archivo Excel con múltiples hojas
        
        Args:
            productos: Lista de productos
            empresas: Lista de empresas
            resenas: Lista de reseñas
            leads: Lista de leads
            posts_sociales: Lista de posts de redes sociales
            filename: Nombre del archivo (opcional)
            
        Returns:
            Ruta del archivo generado
        """
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"ramsa_heizen_data_{timestamp}.xlsx"
        
        filepath = self.output_dir / filename
        
        logger.info(f"📊 Exportando datos a Excel: {filepath}")
        
        # Crear writer de Excel
        with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
            
            # 1. Hoja de Productos
            if productos:
                df_productos = self._prepare_productos_df(productos)
                df_productos.to_excel(writer, sheet_name='Productos', index=False)
                logger.info(f"✅ Exportados {len(df_productos)} productos")
            
            # 2. Hoja de Empresas
            if empresas:
                df_empresas = self._prepare_empresas_df(empresas)
                df_empresas.to_excel(writer, sheet_name='Empresas', index=False)
                logger.info(f"✅ Exportadas {len(df_empresas)} empresas")
            
            # 3. Hoja de Reseñas
            if resenas:
                df_resenas = self._prepare_resenas_df(resenas)
                df_resenas.to_excel(writer, sheet_name='Reseñas', index=False)
                logger.info(f"✅ Exportadas {len(df_resenas)} reseñas")
            
            # 4. Hoja de Leads
            if leads:
                df_leads = self._prepare_leads_df(leads)
                df_leads.to_excel(writer, sheet_name='Leads', index=False)
                logger.info(f"✅ Exportados {len(df_leads)} leads")
            
            # 5. Hoja de Posts Sociales
            if posts_sociales:
                df_posts = self._prepare_posts_df(posts_sociales)
                df_posts.to_excel(writer, sheet_name='Redes Sociales', index=False)
                logger.info(f"✅ Exportados {len(df_posts)} posts")
            
            # 6. Hoja de Análisis de Productos
            if productos:
                df_analisis = self._create_product_analysis(productos)
                df_analisis.to_excel(writer, sheet_name='Análisis Productos', index=False)
            
            # 7. Hoja de Análisis de Precios
            if productos:
                df_precios = self._create_price_analysis(productos)
                df_precios.to_excel(writer, sheet_name='Análisis Precios', index=False)
            
            # 8. Hoja de Análisis de Leads
            if leads:
                df_lead_analysis = self._create_lead_analysis(leads)
                df_lead_analysis.to_excel(writer, sheet_name='Análisis Leads', index=False)
        
        logger.info(f"✅ Excel generado exitosamente: {filepath}")
        return str(filepath)
    
    def _prepare_productos_df(self, productos: List[Dict]) -> pd.DataFrame:
        """Preparar DataFrame de productos"""
        df = pd.DataFrame(productos)
        
        # Columnas principales
        columnas_orden = [
            'nombre', 'categoria', 'subcategoria', 'marca', 'modelo',
            'precio', 'descuento_porcentaje', 'precio_oferta',
            'descripcion', 'descripcion_enriquecida',
            'fuente', 'url_producto', 'imagen_url',
            'stock_disponible', 'popularidad_score',
            'fecha_creacion'
        ]
        
        # Mantener solo columnas que existan
        columnas_existentes = [col for col in columnas_orden if col in df.columns]
        
        # Agregar columnas JSON como texto
        for col in df.columns:
            if df[col].dtype == 'object':
                df[col] = df[col].apply(lambda x: json.dumps(x, ensure_ascii=False) if isinstance(x, (dict, list)) else x)
        
        return df[columnas_existentes] if columnas_existentes else df
    
    def _prepare_empresas_df(self, empresas: List[Dict]) -> pd.DataFrame:
        """Preparar DataFrame de empresas"""
        df = pd.DataFrame(empresas)
        
        columnas_orden = [
            'nombre', 'tipo', 'categoria',
            'telefono', 'whatsapp', 'email', 'website',
            'direccion', 'ciudad', 'provincia',
            'calificacion', 'numero_resenas',
            'facebook_url', 'instagram_url'
        ]
        
        columnas_existentes = [col for col in columnas_orden if col in df.columns]
        return df[columnas_existentes] if columnas_existentes else df
    
    def _prepare_resenas_df(self, resenas: List[Dict]) -> pd.DataFrame:
        """Preparar DataFrame de reseñas"""
        df = pd.DataFrame(resenas)
        
        columnas_orden = [
            'calificacion', 'titulo', 'texto',
            'autor_nombre', 'sentimiento', 'sentimiento_score',
            'fuente', 'fecha_publicacion'
        ]
        
        columnas_existentes = [col for col in columnas_orden if col in df.columns]
        
        # Convertir JSON a texto
        for col in ['temas_principales', 'palabras_clave']:
            if col in df.columns:
                df[col] = df[col].apply(lambda x: ', '.join(x) if isinstance(x, list) else x)
        
        return df[columnas_existentes] if columnas_existentes else df
    
    def _prepare_leads_df(self, leads: List[Dict]) -> pd.DataFrame:
        """Preparar DataFrame de leads"""
        df = pd.DataFrame(leads)
        
        columnas_orden = [
            'nombre_empresa', 'tipo_negocio', 'industria',
            'telefono', 'email', 'website',
            'direccion', 'ciudad', 'provincia',
            'score_calidad', 'nivel_prioridad',
            'similitud_ramsa_heizen', 'razon_lead',
            'fuente_lead', 'estado'
        ]
        
        columnas_existentes = [col for col in columnas_orden if col in df.columns]
        
        # Convertir JSON a texto
        if 'productos_potenciales' in df.columns:
            df['productos_potenciales'] = df['productos_potenciales'].apply(
                lambda x: ', '.join(x) if isinstance(x, list) else x
            )
        
        return df[columnas_existentes] if columnas_existentes else df
    
    def _prepare_posts_df(self, posts: List[Dict]) -> pd.DataFrame:
        """Preparar DataFrame de posts sociales"""
        df = pd.DataFrame(posts)
        
        columnas_orden = [
            'plataforma', 'tipo_post', 'contenido',
            'likes', 'comentarios', 'compartidos', 'engagement_rate',
            'sentimiento_audiencia', 'fecha_publicacion', 'url_post'
        ]
        
        columnas_existentes = [col for col in columnas_orden if col in df.columns]
        
        # Convertir listas a texto
        for col in ['temas', 'productos_mencionados']:
            if col in df.columns:
                df[col] = df[col].apply(lambda x: ', '.join(x) if isinstance(x, list) else x)
        
        return df[columnas_existentes] if columnas_existentes else df
    
    def _create_product_analysis(self, productos: List[Dict]) -> pd.DataFrame:
        """Crear análisis de productos por categoría"""
        df = pd.DataFrame(productos)
        
        if 'categoria' not in df.columns:
            return pd.DataFrame()
        
        # Análisis por categoría
        analisis = df.groupby('categoria').agg({
            'nombre': 'count',
            'precio': ['mean', 'min', 'max', 'median'],
            'popularidad_score': 'mean' if 'popularidad_score' in df.columns else 'count'
        }).round(2)
        
        analisis.columns = [
            'Cantidad Productos',
            'Precio Promedio',
            'Precio Mínimo',
            'Precio Máximo',
            'Precio Mediana',
            'Popularidad Promedio'
        ]
        
        analisis = analisis.reset_index()
        analisis.columns = ['Categoría'] + list(analisis.columns[1:])
        
        return analisis
    
    def _create_price_analysis(self, productos: List[Dict]) -> pd.DataFrame:
        """Crear análisis de precios"""
        df = pd.DataFrame(productos)
        
        if 'precio' not in df.columns or 'nombre' not in df.columns:
            return pd.DataFrame()
        
        # Filtrar productos con precio
        df_precios = df[df['precio'].notna()].copy()
        
        if df_precios.empty:
            return pd.DataFrame()
        
        # Top 10 productos más caros
        top_caros = df_precios.nlargest(10, 'precio')[['nombre', 'precio', 'categoria', 'fuente']]
        
        # Top 10 productos más baratos
        top_baratos = df_precios.nsmallest(10, 'precio')[['nombre', 'precio', 'categoria', 'fuente']]
        
        # Combinar
        analisis = pd.DataFrame({
            'Ranking': list(range(1, 11)) * 2,
            'Tipo': ['Más Caros'] * 10 + ['Más Baratos'] * 10,
            'Producto': list(top_caros['nombre']) + list(top_baratos['nombre']),
            'Precio': list(top_caros['precio']) + list(top_baratos['precio']),
            'Categoría': list(top_caros['categoria']) + list(top_baratos['categoria'])
        })
        
        return analisis
    
    def _create_lead_analysis(self, leads: List[Dict]) -> pd.DataFrame:
        """Crear análisis de leads"""
        df = pd.DataFrame(leads)
        
        if df.empty:
            return pd.DataFrame()
        
        # Agrupar por fuente
        analisis_fuente = df.groupby('fuente_lead').size().reset_index()
        analisis_fuente.columns = ['Fuente', 'Cantidad de Leads']
        
        # Agrupar por prioridad si existe
        if 'nivel_prioridad' in df.columns:
            analisis_prioridad = df.groupby('nivel_prioridad').size().reset_index()
            analisis_prioridad.columns = ['Prioridad', 'Cantidad']
            
            # Combinar análisis
            analisis = pd.concat([
                analisis_fuente,
                pd.DataFrame([['', '']] * (len(analisis_prioridad) - len(analisis_fuente))),
                analisis_prioridad
            ], axis=1) if len(analisis_fuente) > 0 else analisis_prioridad
        else:
            analisis = analisis_fuente
        
        return analisis
    
    def export_to_csv(self, data: List[Dict], filename: str) -> str:
        """
        Exportar datos a CSV
        
        Args:
            data: Lista de diccionarios
            filename: Nombre del archivo
            
        Returns:
            Ruta del archivo generado
        """
        filepath = self.output_dir / filename
        
        df = pd.DataFrame(data)
        df.to_csv(filepath, index=False, encoding='utf-8-sig')
        
        logger.info(f"✅ CSV generado: {filepath}")
        return str(filepath)
    
    def export_summary_report(
        self,
        productos: List[Dict],
        empresas: List[Dict],
        resenas: List[Dict],
        leads: List[Dict]
    ) -> str:
        """
        Generar reporte resumen en texto
        
        Returns:
            Ruta del archivo de reporte
        """
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        filename = f"reporte_resumen_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        filepath = self.output_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write("=" * 80 + "\n")
            f.write("REPORTE DE SCRAPING Y ENRIQUECIMIENTO - RAMSA & HEIZEN\n")
            f.write("=" * 80 + "\n")
            f.write(f"Fecha de generación: {timestamp}\n\n")
            
            f.write("RESUMEN DE DATOS RECOPILADOS:\n")
            f.write("-" * 80 + "\n")
            f.write(f"Total de Productos: {len(productos)}\n")
            f.write(f"Total de Empresas: {len(empresas)}\n")
            f.write(f"Total de Reseñas: {len(resenas)}\n")
            f.write(f"Total de Leads: {len(leads)}\n\n")
            
            if productos:
                f.write("ANÁLISIS DE PRODUCTOS:\n")
                f.write("-" * 80 + "\n")
                df_prod = pd.DataFrame(productos)
                
                if 'categoria' in df_prod.columns:
                    categorias = df_prod['categoria'].value_counts()
                    f.write("Productos por categoría:\n")
                    for cat, count in categorias.items():
                        f.write(f"  - {cat}: {count}\n")
                
                if 'precio' in df_prod.columns:
                    precios = df_prod['precio'].dropna()
                    if len(precios) > 0:
                        f.write(f"\nRango de precios:\n")
                        f.write(f"  - Mínimo: ${precios.min():.2f}\n")
                        f.write(f"  - Máximo: ${precios.max():.2f}\n")
                        f.write(f"  - Promedio: ${precios.mean():.2f}\n")
                f.write("\n")
            
            if leads:
                f.write("ANÁLISIS DE LEADS:\n")
                f.write("-" * 80 + "\n")
                df_leads = pd.DataFrame(leads)
                
                if 'fuente_lead' in df_leads.columns:
                    fuentes = df_leads['fuente_lead'].value_counts()
                    f.write("Leads por fuente:\n")
                    for fuente, count in fuentes.items():
                        f.write(f"  - {fuente}: {count}\n")
                
                if 'nivel_prioridad' in df_leads.columns:
                    prioridades = df_leads['nivel_prioridad'].value_counts()
                    f.write("\nLeads por prioridad:\n")
                    for prior, count in prioridades.items():
                        f.write(f"  - {prior}: {count}\n")
                f.write("\n")
            
            f.write("=" * 80 + "\n")
            f.write("Fin del reporte\n")
        
        logger.info(f"✅ Reporte resumen generado: {filepath}")
        return str(filepath)


# Ejemplo de uso
if __name__ == "__main__":
    exporter = DataExporter()
    
    # Datos de ejemplo
    productos_ejemplo = [
        {
            'nombre': 'Calefón Heizen 8.8kW',
            'categoria': 'Calefones Eléctricos',
            'precio': 450.0,
            'fuente': 'website_ramsa'
        },
        {
            'nombre': 'Casita Infantil',
            'categoria': 'Juguetes Infantiles',
            'precio': 125.0,
            'fuente': 'website_ramsa'
        }
    ]
    
    # Exportar a Excel
    filepath = exporter.export_to_excel(
        productos=productos_ejemplo,
        empresas=[],
        resenas=[],
        leads=[]
    )
    
    print(f"Archivo generado: {filepath}")
