import polars as pl
import json
import os

def limpiar_train():
    df = pl.read_parquet("Analisis_de_Datos_Proyecto/data/processed/train.parquet")
    print("Cambiando nombre de columnas...")
    print("Ingles -> Español")
    df = df.rename({"date":"fecha",
                    "store_nbr":"num_tienda",
                    "family":"categoria",
                    "sales":"ventas",
                    "onpromotion":"promocion"})
    print("Columnas cambiadas con exito")
    print("Nombres nuevos: ", df.columns)

limpiar_train()