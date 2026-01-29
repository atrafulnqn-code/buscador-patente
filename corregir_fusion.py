"""
Post-procesamiento para corregir números fusionados en Desc. Tipo
Separa números de 7+ dígitos y los asigna a las columnas de años correctas
"""

import pandas as pd
import re

INPUT_CSV = "datos_patentes.csv"
OUTPUT_CSV = "datos_patentes_corregido.csv"

# Columnas de años en orden
COLUMNAS_ANIOS = [
    "0Km", "2025", "2024", "2023", "2022", "2021",
    "2020", "2019", "2018", "2017", "2016", "2015",
    "2014", "2013", "2012", "2011", "2010", "2009",
    "2008", "2007", "2006", "2005", "2004", "2003", "2002"
]

def separar_numeros_pegados(numero_str):
    """Separa números que están pegados (ej: 121368900106298850 -> [121368900, 106298850])"""
    if len(numero_str) <= 10:
        return [numero_str]

    # Los precios típicos tienen 7-9 dígitos
    # Intentar separar en chunks de 8-9 dígitos
    numeros = []
    pos = 0

    while pos < len(numero_str):
        # Tomar 8-9 dígitos (priorizar 9 si hay suficiente)
        if len(numero_str) - pos >= 9:
            # Intentar encontrar el mejor corte (buscar inicio probable de precio)
            # Los precios suelen empezar con 1-9, no con 0
            mejor_corte = 9
            for i in range(8, 10):
                if pos + i < len(numero_str) and numero_str[pos + i] != '0':
                    mejor_corte = i
                    break

            chunk = numero_str[pos:pos + mejor_corte]
            numeros.append(chunk)
            pos += mejor_corte
        else:
            # Tomar lo que queda
            chunk = numero_str[pos:]
            if len(chunk) >= 7:  # Solo si es un precio válido
                numeros.append(chunk)
            pos = len(numero_str)

    return numeros

def extraer_numeros(texto):
    """Extrae números de 7+ dígitos de un texto y los separa si están pegados"""
    if pd.isna(texto):
        return [], texto

    # Buscar números de 7 o más dígitos
    numeros_brutos = re.findall(r'\d{7,}', str(texto))

    # Separar números pegados
    numeros = []
    for num in numeros_brutos:
        numeros.extend(separar_numeros_pegados(num))

    # Limpiar el texto removiendo los números
    texto_limpio = re.sub(r'\d{7,}', '', str(texto))
    texto_limpio = re.sub(r'\s+', ' ', texto_limpio).strip()

    return numeros, texto_limpio

def corregir_fila(row):
    """Corrige una fila que tiene números fusionados"""
    desc_tipo = row['Desc. Tipo']

    # Extraer números
    numeros, texto_limpio = extraer_numeros(desc_tipo)

    if not numeros:
        return row

    # Actualizar Desc. Tipo sin números
    row['Desc. Tipo'] = texto_limpio

    # Asignar números a columnas de años
    # Empezar desde la primera columna vacía
    col_idx = 0
    for num in numeros:
        # Buscar siguiente columna vacía
        while col_idx < len(COLUMNAS_ANIOS):
            col = COLUMNAS_ANIOS[col_idx]
            if pd.isna(row[col]) or str(row[col]).strip() in ['', '-']:
                row[col] = num
                col_idx += 1
                break
            col_idx += 1

    return row

def main():
    print("=" * 60)
    print("POST-PROCESAMIENTO: Corregir números fusionados")
    print("=" * 60)

    # 1. Cargar CSV
    print(f"\n[1/4] Cargando {INPUT_CSV}...")
    df = pd.read_csv(INPUT_CSV, dtype=str)
    print(f"   Total registros: {len(df)}")

    # 2. Detectar filas problemáticas
    print(f"\n[2/4] Detectando filas con números fusionados...")
    mascara = df['Desc. Tipo'].str.contains(r'\d{7,}', na=False, regex=True)
    filas_problematicas = df[mascara].copy()

    print(f"   Filas a corregir: {len(filas_problematicas)}")

    if len(filas_problematicas) == 0:
        print("\n   No hay filas problemáticas. CSV ya está correcto.")
        return

    # Mostrar ejemplos
    print(f"\n   Ejemplos antes de corregir:")
    for i, (idx, row) in enumerate(filas_problematicas.head(3).iterrows()):
        print(f"   {i+1}. {row['MTM/FMM']}: {row['Desc. Tipo'][:60]}...")

    # 3. Corregir filas
    print(f"\n[3/4] Corrigiendo filas...")

    filas_corregidas = 0
    for idx in filas_problematicas.index:
        row_original = df.loc[idx].copy()
        row_corregida = corregir_fila(df.loc[idx].copy())

        # Verificar si se corrigió algo
        numeros_antes, _ = extraer_numeros(row_original['Desc. Tipo'])
        numeros_despues, _ = extraer_numeros(row_corregida['Desc. Tipo'])

        if len(numeros_despues) < len(numeros_antes):
            df.loc[idx] = row_corregida
            filas_corregidas += 1

    print(f"   Filas corregidas exitosamente: {filas_corregidas}")

    # Verificar que se corrigieron
    print(f"\n   Verificando corrección...")
    mascara_post = df['Desc. Tipo'].str.contains(r'\d{7,}', na=False, regex=True)
    filas_restantes = df[mascara_post]

    if len(filas_restantes) > 0:
        print(f"   [!] Quedan {len(filas_restantes)} filas con números fusionados")
        print(f"       (Pueden ser casos especiales o números parte del texto)")
    else:
        print(f"   [OK] Todas las filas corregidas exitosamente")

    # Mostrar ejemplos corregidos
    print(f"\n   Ejemplos después de corregir:")
    for i, (idx, row) in enumerate(filas_problematicas.head(3).iterrows()):
        row_nueva = df.loc[idx]
        print(f"   {i+1}. {row_nueva['MTM/FMM']}: {row_nueva['Desc. Tipo']}")

        # Mostrar valores en años
        valores = []
        for col in COLUMNAS_ANIOS[:5]:
            val = row_nueva[col]
            if pd.notna(val) and str(val).strip() and val != '-':
                valores.append(f"{col}={val}")
        if valores:
            print(f"       Valores: {', '.join(valores)}")

    # 4. Guardar CSV corregido
    print(f"\n[4/4] Guardando CSV corregido...")
    df.to_csv(OUTPUT_CSV, index=False, encoding='utf-8-sig')
    print(f"   Guardado en: {OUTPUT_CSV}")

    # Resumen final
    print("\n" + "=" * 60)
    print("CORRECCIÓN COMPLETADA")
    print("=" * 60)
    print(f"Total registros: {len(df)}")
    print(f"Filas corregidas: {filas_corregidas}")
    print(f"Filas con números restantes: {len(filas_restantes)}")
    print(f"\nPrecisión: {((len(df) - len(filas_restantes)) / len(df) * 100):.2f}%")
    print(f"\nCSV corregido guardado en: {OUTPUT_CSV}")
    print("\nSiguientes pasos:")
    print("1. Verifica algunos registros en el CSV nuevo")
    print("2. Si todo está bien, reemplaza datos_patentes.csv")
    print("3. Sube a GitHub y Streamlit se actualizará")

if __name__ == "__main__":
    main()
