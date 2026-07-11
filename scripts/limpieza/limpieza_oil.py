import polars as pl
import json
import os


RUTA_REPORTE = '/home/azureuser/proyecto_favorita/Analisis_de_Datos_Proyecto/data/reports/reporte_limpio.json'


def limpiar_oil():
    df = pl.read_parquet('/home/azureuser/proyecto_favorita/Analisis_de_Datos_Proyecto/data/processed/oil.parquet')
    

    print('Renombrando columnas...')
    df = df.rename({
        'date':'fecha',
        'dcoilwtico': 'precio_diario_petroleo' 
    })
    print('Columnas renombradas con éxito.')


    print('Corrigiendo tipos de datos...')
    df = df.with_columns(
        pl.col('fecha').str.to_datetime(format="%Y-%m-%d")
    )
    print('Corrección realizada con éxito.')


    print('Corrigiendo registros nulos:')
    mediana_pdp = pl.col('precio_diario_petroleo').median()
    df = df.with_columns(
        pl.col('precio_diario_petroleo').fill_null(mediana_pdp)
    )
    print("Corrección realizada con éxito.")


    print('Columnas y sus tipos:')
    for columna, tipo in df.schema.items():
        print(f"-{columna}: {tipo}")


    info_oil_limpio = {
        'filas': df.shape[0],
        'columnas': df.shape[1],
        'tipos_de_dato': {col: str(tipo) for col, tipo in df.schema.items()},
        'nulos_por_columna': df.null_count().to_dicts()[0],
        'duplicados': int(df.is_duplicated().sum()),
        'fecha_rango': {
            'min': str(df['fecha'].min()),
            'max': str(df['fecha'].max())}
    }


    if os.path.exists(RUTA_REPORTE):
        with open(RUTA_REPORTE, 'r', encoding='utf-8') as f:
            reporte_limpieza_oil = json.load(f)
    else:
        reporte_limpieza_oil = {}


    reporte_limpieza_oil['INFORMACION_OIL'] = info_oil_limpio


    with open(RUTA_REPORTE, 'w', encoding='utf-8') as f:
        json.dump(reporte_limpieza_oil, f, indent=4, ensure_ascii=False)


limpiar_oil()