import streamlit as st
import pandas as pd

# Configuración de la página
st.set_page_config(page_title="Buscador de Patentes", layout="wide")

st.title("🚗 Buscador de Patentes (MTM/FMM)")

# Cargar datos (con caché para que sea rápido)
@st.cache_data
def load_data():
    try:
        # Leemos el CSV (versión limpia)
        df = pd.read_csv("datos_patentes_limpio.csv", dtype=str)
        
        # --- LIMPIEZA DE DATOS ---
        df.fillna('-', inplace=True)
        
        # Unir columnas fragmentadas si existen
        cols = df.columns
        if 'Desc. Tipo' in cols and 'Col_8' in cols and 'Col_9' in cols:
            df['Desc. Tipo'] = df.apply(
                lambda row: (str(row['Desc. Tipo']) + str(row['Col_8']) + str(row['Col_9']))
                .replace('-', '')
                .replace('nan', ''), 
                axis=1
            )
            df.drop(columns=['Col_8', 'Col_9'], inplace=True, errors='ignore')
            
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
        st.dataframe(resultados, use_container_width=True)
    else:
        st.info("👆 Escribe un código arriba para empezar a buscar.")
        # Mostrar una vista previa pequeña
        st.write("Vista previa de la base de datos:")
        st.dataframe(df.head(10))

else:
    st.error("⚠️ No se encontró el archivo 'datos_patentes.csv'. Asegúrate de subirlo junto con el código.")
