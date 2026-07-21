
import polars as pl
import adbc_driver_postgresql.dbapi


RUTA_PARQUET = (
    "/home/azureuser/proyecto_favorita/"
    "Analisis_de_Datos_Proyecto/data/processed/consolidacion.parquet"
)

CONEXION_POSTGRES = (
    "postgresql://favorita_user:"
    "183132"
    "@localhost:5432/favorita_db"
)


def exportar_consolidado():
    print("Leyendo archivo consolidado...")

    df = pl.read_parquet(RUTA_PARQUET)

    conexion = adbc_driver_postgresql.dbapi.connect(
        CONEXION_POSTGRES
    )

    try:
        # El TRUNCATE y la inserción forman parte
        # de la misma transacción.
        with conexion.cursor() as cursor:
            cursor.execute(
                "TRUNCATE TABLE public.datos_consolidados"
            )

        filas_reportadas = df.write_database(
            table_name="public.datos_consolidados",
            connection=conexion,
            if_table_exists="append",
            engine="adbc",
        )

        conexion.commit()

        with conexion.cursor() as cursor:
            cursor.execute(
                "SELECT COUNT(*) "
                "FROM public.datos_consolidados"
            )
            total_postgres = cursor.fetchone()[0]

        if total_postgres != df.height:
            raise RuntimeError(
                "La cantidad cargada no coincide. "
                f"Parquet: {df.height:,}; "
                f"PostgreSQL: {total_postgres:,}"
            )

        print(f"Filas reportadas por ADBC: {filas_reportadas}")
        print(
            "Datos cargados correctamente: "
            f"{total_postgres:,} registros."
        )

    except Exception:
        conexion.rollback()
        print("La exportación falló. Se revirtieron los cambios.")
        raise

    finally:
        conexion.close()


if __name__ == "__main__":
    exportar_consolidado()

