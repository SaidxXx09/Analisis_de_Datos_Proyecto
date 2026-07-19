import polars as pl
import json
import os 

RUTA_REPORTE = "/home/azureuser/proyecto_favorita/Analisis_de_Datos_Proyecto/data/reports/reporte_limpio.json"

def limpiar_stores():
    df = pl.read_parquet("/home/azureuser/proyecto_favorita/Analisis_de_Datos_Proyecto/data/processed/stores.parquet")

    print("Renombrando columnas...")
    df = df.rename({
        "city": "ciudad",
        "store_nbr": "num_tienda",
        "state": "estado",
        "type": "tipo",
        "cluster": "grupo",
    })
    print("Columnas renombradas correctamente.")

    print("Conversion de tipos de datos...")

    print("\nColumnas y tipos")
    for columna, tipo in df.schema.items():
        print(f"- {columna}: {tipo}")

    info_stores_limpio = {
        "filas": df.shape[0],
        "columnas": df.shape[1],
        "tipos_de_dato": {col: str(tipo) for col, tipo in df.schema.items()},
        "nulos_por_columna": df.null_count().to_dicts()[0],
        "duplicados": int(df.is_duplicated().sum()),
        }
    
    if os.path.exists(RUTA_REPORTE):
        with open(RUTA_REPORTE, "r", encoding="utf-8") as archivo:
            reporte = json.load(archivo)
    else:
        reporte = {}

    reporte["INFORMACION_STORES"] = info_stores_limpio

    with open(RUTA_REPORTE,"w", encoding="utf-8") as e:
        json.dump(reporte,e,indent=4,ensure_ascii=False)

    df = df.write_parquet("/home/azureuser/proyecto_favorita/Analisis_de_Datos_Proyecto/data/processed/stores_limpio.parquet")

