import polars as pl
import json
import os 

RUTA_REPORTE = "/home/azureuser/proyecto_favorita/Analisis_de_Datos_Proyecto/data/reports/reporte_limpio.json"

def limpiar_transactions():
    df = pl.read_parquet("/home/azureuser/proyecto_favorita/Analisis_de_Datos_Proyecto/data/processed/transactions.parquet")

    print("Renombrando columnas...")
    df = df.rename({
        "transactions": "transacciones",
        "store_nbr": "num_tienda",
        "date": "fecha",
    })
    print("Columnas renombradas correctamente.")

    print("Conversion de tipos de datos...")

    df = df.with_columns(
        pl.col("fecha").str.to_datetime(format="%Y-%m-%d")
    )

    df = df.with_columns(
        pl.col("fecha").dt.date()
    )


    print("\nColumnas y tipos")
    for columna, tipo in df.schema.items():
        print(f"- {columna}: {tipo}")

    info_limpieza_transactions = {
        "filas": df.shape[0],
        "columnas": df.shape[1],
        "tipos_de_dato": {col: str(tipo) for col, tipo in df.schema.items()},
        "nulos_por_columna": df.null_count().to_dicts()[0],
        "duplicados": int(df.is_duplicated().sum()),
        "fecha_rango": {
            "min": str(df["fecha"].min()),
            "max": str(df["fecha"].max())}
        }
    
    if os.path.exists(RUTA_REPORTE):
        with open(RUTA_REPORTE, "r", encoding="utf-8") as archivo:
            reporte = json.load(archivo)
    else:
        reporte = {}

    reporte["INFORMACION_TRANSACTIONS"] = info_limpieza_transactions

    with open(RUTA_REPORTE,"w", encoding="utf-8") as e:
        json.dump(reporte,e,indent=4,ensure_ascii=False)

    df = df.write_parquet("/home/azureuser/proyecto_favorita/Analisis_de_Datos_Proyecto/data/processed/transactions_limpio.parquet")

