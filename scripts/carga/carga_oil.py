import polars as pl
import json
import os

def cargar_oil():
    df = pl.read_csv("Analisis_de_Datos_Proyecto/data/datasets/oil.csv")
    df.write_parquet("Analisis_de_Datos_Proyecto/data/processed/oil.parquet")
    print(f"stores cargado: {df.shape}")


def diagnosticar_oil():
    df = pl.read_parquet("Analisis_de_Datos_Proyecto/data/processed/oil.parquet")

    print(f"Forma del dataset: \n{df.shape}")
    print(f"Tipo de datos: \n{df.dtypes}")
    print(f"Descripcion de datos: \n{df.describe()}")
    print(f"Nombre de columnas: \n{df.columns}")
    print(f"Total de nulos por columna: \n{df.null_count()}")
    print(f"Total de filas duplicadas: \n{df.is_duplicated().sum()}")

    info_oil = {
        "filas" : df.shape[0],
        "columnas" : df.shape[1],
        "tipos_de_dato" : {col: str(tipo) for col, tipo in df.schema.items()},
        "nulos_por_columna" : df.null_count().to_dicts()[0],
        "duplicados" : int(df.is_duplicated().sum()),
    }



    RUTA_REPORTE = "Analisis_de_Datos_Proyecto/data/reports/reporte_informativo.json"


    if os.path.exists(RUTA_REPORTE):
        with open(RUTA_REPORTE, "r", encoding= "utf-8") as archivo:
            reporte = json.load(archivo)
    else:
        reporte = {}

    reporte["INFORMACION_OIL"] = info_oil

    with open (RUTA_REPORTE, "w", encoding="utf-8") as archivo:
        json.dump(reporte, archivo, indent=4, ensure_ascii=False)


cargar_oil()
diagnosticar_oil()