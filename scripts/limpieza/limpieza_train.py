import polars as pl

def limpiar_train():
    df = pl.read_parquet("/home/azureuser/proyecto_favorita/Analisis_de_Datos_Proyecto/data/processed/train.parquet")

    print("Renombrando columnas...")
    df = df.rename({
        "date": "fecha",
        "store_nbr": "num_tienda",
        "family": "categoria",
        "sales": "ventas",
        "onpromotion": "promocion",
    })
    print("Columnas renombradas correctamente.")

    print("Conversion de tipos de datos...")

    # Transformar a tipo fecha
    df = df.with_columns(
        pl.col("fecha").str.to_datetime(format="%Y-%m-%d")
    )

    # Quitar los milisegundos
    df = df.with_columns(
        pl.col("fecha").dt.date()
    )
    print("Conversión completada.")

    print("\nColumnas y tipos")
    for columna, tipo in df.schema.items():
        print(f"- {columna}: {tipo}")


limpiar_train()