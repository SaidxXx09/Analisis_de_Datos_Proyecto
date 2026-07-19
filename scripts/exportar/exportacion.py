import polars as pl

conn_str = "postgresql://admin:admin123@localhost:5432/proyecto_favorita"
df = pl.read_parquet("/home/azureuser/proyecto_favorita/Analisis_de_Datos_Proyecto/data/processed/consolidacion.parquet")

df.write_database(
    table_name='datos_consolidados',
    connection=conn_str,
    if_table_exists='replace',
    engine='adbc'
)

print("Datos cargados correctamente")