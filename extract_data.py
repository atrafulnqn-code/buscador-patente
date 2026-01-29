import pdfplumber
import pandas as pd

def extract_all_data(pdf_path, output_csv):
    """
    Extrae datos del PDF mapeando palabras a columnas basándose en su posición X.
    Este enfoque es más robusto para tablas sin bordes.
    """

    # Definir los límites X de cada columna (basado en el análisis real del PDF)
    # Cada columna se define como (nombre, x_inicio, x_fin)
    column_defs = [
        ("I/N", 19, 26),
        ("MTM/FMM", 26, 48),
        ("T", 48, 56),
        ("Fab", 56, 77),
        ("Marca", 77, 85),
        ("Tipo", 85, 96),
        ("Desc. marca", 96, 130),
        ("Desc. Modelo", 130, 147),
        ("Desc. Tipo", 147, 231),
        ("0Km", 231, 253),
        ("2025", 253, 275),
        ("2024", 275, 297),
        ("2023", 297, 319),
        ("2022", 319, 341),
        ("2021", 341, 363),
        ("2020", 363, 385),
        ("2019", 385, 407),
        ("2018", 407, 429),
        ("2017", 429, 451),
        ("2016", 451, 473),
        ("2015", 473, 495),
        ("2014", 495, 517),
        ("2013", 517, 539),
        ("2012", 539, 561),
        ("2011", 561, 583),
        ("2010", 583, 605),
        ("2009", 605, 627),
        ("2008", 627, 649),
        ("2007", 649, 671),
        ("2006", 671, 693),
        ("2005", 693, 715),
        ("2004", 715, 737),
        ("2003", 737, 759),
        ("2002", 759, 785)
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
