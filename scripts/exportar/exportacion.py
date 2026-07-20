import polars as pl

conn_str = "postgresql://favorita_user:183132@localhost:5432/favorita_db"
df = pl.read_parquet("/home/azureuser/proyecto_favorita/Analisis_de_Datos_Proyecto/data/processed/consolidacion.parquet")

df.write_database(
    table_name='datos_consolidados',
    connection=conn_str,
    if_table_exists='replace',
    engine='adbc'
)

print("Datos cargados correctamente")