import polars as pl
import psycopg2


def exportar_consolidado():
    conn_str = "postgresql://favorita_user:183132@localhost:5432/favorita_db"
    df = pl.read_parquet("/home/azureuser/proyecto_favorita/Analisis_de_Datos_Proyecto/data/processed/consolidacion.parquet")

    # Truncate a la tabla para no eliminar las vistas que consume mi PowerBI
    conn = psycopg2.connect(conn_str)
    conn.autocommit = True
    with conn.cursor() as cur:
        cur.execute("TRUNCATE TABLE datos_consolidados")
    conn.close()

    df.write_database(
        table_name='datos_consolidados',
        connection=conn_str,
        if_table_exists='append',
        engine='adbc'
    )
    print("Datos cargados correctamente!")

exportar_consolidado()