import streamlit as st
import pandas as pd

# Configuración de la página
st.set_page_config(page_title="Buscador de Patentes", layout="wide")

st.title("🚗 Buscador de Patentes (MTM/FMM)")

# Cargar datos (caché deshabilitado temporalmente para forzar actualización)
# @st.cache_data  # Deshabilitado para forzar recarga del CSV corregido
def load_data():
    try:
        # Leemos el CSV con datos corregidos (extraídos por posición X)
        # Versión: 2025-01-29 - Corregido desfase de años
        df = pd.read_csv("datos_patentes.csv", dtype=str)

        # Reemplazar valores vacíos con guiones
        df.fillna('-', inplace=True)

        return df
    except FileNotFoundError:
        return None

df = load_data()

if df is not None:
    # Identificar columna de búsqueda (la segunda, índice 1)
    columna_busqueda = df.columns[1] if len(df.columns) > 1 else df.columns[0]
    
    # Campo de búsqueda
    busqueda = st.text_input(f"🔍 Ingrese código ({columna_busqueda}):", "")

    if busqueda:
        # Filtrar
        resultados = df[df[columna_busqueda].astype(str).str.contains(busqueda, case=False, na=False)]
        
        st.write(f"Resultados encontrados: **{len(resultados)}**")
        
        # Mostrar tabla interactiva
        st.dataframe(resultados, width='stretch')
    else:
        st.info("👆 Escribe un código arriba para empezar a buscar.")
        # Mostrar una vista previa pequeña
        st.write("Vista previa de la base de datos:")
        st.dataframe(df.head(10))

else:
    st.error("⚠️ No se encontró el archivo 'datos_patentes.csv'. Asegúrate de subirlo junto con el código.")
