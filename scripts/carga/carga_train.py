import polars as pl
import json 
import os

RUTA_REPORTE = "data/reports/reporte_informativo.json"

def cargar_train():
    df = pl.read_csv("data/datasets/train.csv")
    df.write_parquet("data/processed/train.parquet")
    print("train cargado...")

def diagnosticar_train():
    df = pl.read_parquet("data/processed/train.parquet")

    print(f"Forma del dataset: \n{df.shape}")
    print(f"Tipo de datos: \n{df.dtypes}")
    print(f"Descripcion de datos: \n{df.describe()}")
    print(f"Nombre de columnas: \n{df.columns}")
    print(f"Total de nulos por columna: \n{df.null_count()}")
    print(f"Total de filas duplicadas: \n{df.is_duplicated().sum()}")
    print(f"Rango de fechas: {df['date'].min()} a {df['date'].max()}")

    info_train = {
        "filas" : df.shape[0],
        "columnas" : df.shape[1],
        "tipos_de_dato" : {col: str(tipo) for col, tipo in df.schema.items()},
        "nulos_por_columna" : df.null_count().to_dicts()[0],
        "duplicados" : int(df.is_duplicated().sum()),
        "fecha_rango" : {
            "min": df['date'].min(),
            "max": df['date'].max()}
    }
    
    if os.path.exists(RUTA_REPORTE):
        with open(RUTA_REPORTE, "r",encoding="utf-8") as f:
            reporte = json.load(f)
    else:
        reporte = {}

    reporte["INFORMACION_TRAIN"] = info_train

    with open(RUTA_REPORTE, "w",encoding="utf-8") as f:
        json.dump(reporte, f, indent= 4, ensure_ascii= False)

cargar_train()
diagnosticar_train()