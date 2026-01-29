import pdfplumber
import pandas as pd

def extract_all_data(pdf_path, output_csv):
    """
    Extrae datos del PDF mapeando palabras a columnas basándose en su posición X.
    Este enfoque es más robusto para tablas sin bordes.
    """

    # Definir los límites X de cada columna (basado en el análisis real del PDF)
    # Cada columna se define como (nombre, x_inicio, x_fin)
    # Para los años, usamos el punto medio entre columnas como límite
    column_defs = [
        ("I/N", 19, 26),
        ("MTM/FMM", 26, 48),
        ("T", 48, 56),
        ("Fab", 56, 77),
        ("Marca", 77, 85),
        ("Tipo", 85, 96),
        ("Desc. marca", 96, 130),
        ("Desc. Modelo", 130, 147),
        ("Desc. Tipo", 147, 220),  # Ajustado para no capturar valores de 0Km
        ("0Km", 220, 242.5),       # Ampliado para capturar valores desde ~227
        ("2025", 242.5, 264),     # Desde punto medio con 0Km hasta punto medio con 2024
        ("2024", 264, 285.9),     # Desde punto medio con 2025 hasta punto medio con 2023
        ("2023", 285.9, 307.8),
        ("2022", 307.8, 329.8),
        ("2021", 329.8, 351.7),
        ("2020", 351.7, 373.7),
        ("2019", 373.7, 395.6),
        ("2018", 395.6, 421.6),   # Punto medio entre 2018(414.7) y 2017(428.6) = 421.65
        ("2017", 421.6, 443.6),   # Punto medio entre 2017(436.7) y 2016(450.6) = 443.65
        ("2016", 443.6, 465.6),   # Punto medio entre 2016(458.7) y 2015(472.5) = 465.6
        ("2015", 465.6, 483.5),
        ("2014", 483.5, 505.5),
        ("2013", 505.5, 527.5),
        ("2012", 527.5, 549.4),
        ("2011", 549.4, 571.4),
        ("2010", 571.4, 593.3),
        ("2009", 593.3, 615.3),
        ("2008", 615.3, 637.3),
        ("2007", 637.3, 659.2),
        ("2006", 659.2, 681.2),
        ("2005", 681.2, 703.1),
        ("2004", 703.1, 725.1),
        ("2003", 725.1, 747.1),
        ("2002", 747.1, 785)
    ]

    headers = [col[0] for col in column_defs]
    all_rows = []

    print(f"Abriendo {pdf_path}...")

    try:
        with pdfplumber.open(pdf_path) as pdf:
            total_pages = len(pdf.pages)
            print(f"Total de páginas a procesar: {total_pages}")
            print(f"Columnas definidas: {len(headers)}")

            for page_num, page in enumerate(pdf.pages):
                if (page_num + 1) % 10 == 0 or page_num == 0:
                    print(f"Procesando página {page_num + 1}/{total_pages}...", end='\r')

                # Extraer palabras con sus posiciones
                words = page.extract_words()

                # Agrupar palabras por línea (Y similar)
                lines = {}
                for word in words:
                    y = round(word['top'] / 2) * 2  # Redondear a múltiplos de 2 para agrupar líneas cercanas
                    if y not in lines:
                        lines[y] = []
                    lines[y].append(word)

                # Procesar cada línea
                for y in sorted(lines.keys()):
                    line_words = lines[y]

                    # Saltar líneas de header (contienen "I/N" o "MTM/FMM" o "Vigencia")
                    line_text = ' '.join([w['text'] for w in line_words])
                    if any(skip_word in line_text for skip_word in ['I/N', 'MTM/FMM', 'Vigencia', 'Fab Marca']):
                        continue

                    # Mapear palabras a columnas basándose en posición X
                    row = [''] * len(column_defs)

                    for word in line_words:
                        x = word['x0']
                        text = word['text']

                        # Encontrar a qué columna pertenece esta palabra
                        for col_idx, (col_name, x_min, x_max) in enumerate(column_defs):
                            if x_min <= x < x_max:
                                # Agregar texto a la columna (concatenar si ya hay algo)
                                if row[col_idx]:
                                    row[col_idx] += ' ' + text
                                else:
                                    row[col_idx] = text
                                break

                    # Solo agregar la fila si tiene al menos algunos datos
                    if any(cell.strip() for cell in row):
                        all_rows.append(row)

            print(f"\nExtracción completada. Total de filas extraídas: {len(all_rows)}")

            # Crear DataFrame
            if all_rows:
                df = pd.DataFrame(all_rows, columns=headers)

                # Guardar a CSV
                print(f"Guardando datos en {output_csv}...")
                df.to_csv(output_csv, index=False, encoding='utf-8-sig')
                print("¡Listo!")
                return True
            else:
                print("Error: No se pudieron extraer datos.")
                return False

    except Exception as e:
        print(f"\nOcurrió un error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    extract_all_data("tabla_patente.pdf", "datos_patentes.csv")
