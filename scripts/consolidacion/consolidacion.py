import polars as pl

def consolidar_dataset():
    train = pl.read_parquet("/home/azureuser/proyecto_favorita/Analisis_de_Datos_Proyecto/data/processed/train_limpio.parquet")
    holidays = pl.read_parquet("/home/azureuser/proyecto_favorita/Analisis_de_Datos_Proyecto/data/processed/holidays_events_limpio.parquet")
    oil = pl.read_parquet("/home/azureuser/proyecto_favorita/Analisis_de_Datos_Proyecto/data/processed/oil_limpio.parquet")
    stores = pl.read_parquet("/home/azureuser/proyecto_favorita/Analisis_de_Datos_Proyecto/data/processed/stores_limpio.parquet")
    transactions = pl.read_parquet("/home/azureuser/proyecto_favorita/Analisis_de_Datos_Proyecto/data/processed/transactions_limpio.parquet")

    df = train.join(stores, on="num_tienda", how="left")
    df = df.join(transactions, on=["num_tienda", "fecha"], how="left")
    df = df.join(oil, on="fecha", how="left")
    df = df.join(holidays, on="fecha", how="left")

    print("Datasets concatenados")

    df = df.sort("fecha")

    # Tratamiento para datos sobrantes 

    # Strings
    df = df.with_columns([
        pl.col("tipo_feriado").fill_null("Día no feriado"),
        pl.col("alcance").fill_null("No aplica"),
        pl.col("nombre_lugar").fill_null("No aplica"),
        pl.col("descripcion").fill_null("Sin evento registrado"),
    ])

    # Numéricas
    df = df.with_columns([
        pl.col("transacciones").fill_null(0),
        pl.col("precio_diario_petroleo").fill_null(strategy="forward"),  
    ])

    # Booleanos
    df = df.with_columns([
        pl.col("transferido").fill_null(False)
    ])

    print("Dataset tratado correctamente")

    # Verificación 
    nulos_finales = df.null_count().to_dicts()[0]
    filas = df.shape[0]
    for col, cantidad in nulos_finales.items():
        porcentaje = (cantidad / filas) * 100
        print(f"{col} - Porcentaje de nulos: {porcentaje}%")

    df.write_parquet("/home/azureuser/proyecto_favorita/Analisis_de_Datos_Proyecto/data/processed/concatenado.parquet")


consolidar_dataset()