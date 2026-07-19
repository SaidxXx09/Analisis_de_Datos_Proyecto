import polars as pl

def consolidar_dataset():
    train = pl.read_parquet("/home/azureuser/proyecto_favorita/Analisis_de_Datos_Proyecto/data/processed/train_limpio.parquet")
    holidays = pl.read_parquet("/home/azureuser/proyecto_favorita/Analisis_de_Datos_Proyecto/data/processed/holidays_events_limpio.parquet")
    oil = pl.read_parquet("/home/azureuser/proyecto_favorita/Analisis_de_Datos_Proyecto/data/processed/oil_limpio.parquet")
    stores = pl.read_parquet("/home/azureuser/proyecto_favorita/Analisis_de_Datos_Proyecto/data/processed/stores_limpio.parquet")
    transactions = pl.read_parquet("/home/azureuser/proyecto_favorita/Analisis_de_Datos_Proyecto/data/processed/transactions_limpio.parquet")

    holidays_unicos = holidays.group_by('fecha').first()
    oil_unicos = oil.unique(subset=['fecha'])

    df_consolidado = (
        train
        .join(stores, on = "num_tienda", how = "left")
        .join(transactions, on = ["fecha", "num_tienda"], how="left")
        .join(oil_unicos, on="fecha", how="left")
        .join(holidays_unicos, on="fecha", how="left")
        .with_columns([
            pl.col("transacciones").fill_null(0),
            pl.col("precio_diario_petroleo").fill_null(strategy="forward")
        ])
    )

    print("Datasets concatenados", df_consolidado.shape)

    df_consolidado = df_consolidado.sort("fecha")

    # Tratamiento para datos sobrantes 
    # Strings
    df_consolidado = df_consolidado.with_columns([
        pl.col("tipo_feriado").fill_null("Día no feriado"),
        pl.col("alcance").fill_null("No aplica"),
        pl.col("nombre_lugar").fill_null("No aplica"),
        pl.col("descripcion").fill_null("Sin evento registrado"),
    ])

    # Numéricas
    df_consolidado = df_consolidado.with_columns([
        pl.col("transacciones").fill_null(0),
        pl.col("precio_diario_petroleo").fill_null(strategy="forward"),  
    ])

    # Booleanos
    df_consolidado = df_consolidado.with_columns([
        pl.col("transferido").fill_null(False)
    ])

    print("Dataset tratado correctamente", df_consolidado.shape)

    # Verificación 
    nulos_finales = df_consolidado.null_count().to_dicts()[0]
    filas = df_consolidado.shape[0]
    for col, cantidad in nulos_finales.items():
        porcentaje = (cantidad / filas) * 100
        print(f"{col} - Porcentaje de nulos: {porcentaje}%")

    df_consolidado.write_parquet("/home/azureuser/proyecto_favorita/Analisis_de_Datos_Proyecto/data/processed/consolidacion.parquet")
