import polars as pl
import json
import os

RUTA = "Analisis_de_Datos_Proyecto/data/processed/consolidacion.parquet"
RUTA_RESULTADOS = "/home/azureuser/proyecto_favorita/Analisis_de_Datos_Proyecto/data/reports/reporte_eda_profundo.json"

def eda_profundo():
    r = {}
    df = pl.read_parquet(RUTA).with_columns([
        pl.col("fecha").dt.year().alias("anio"),
        pl.col("fecha").dt.strftime("%Y-%m").alias("anio_mes"),
    ])


 
    #1. Distribución de ventas por familia de producto: ¿qué categorías concentran el mayor volumen?
    ventas_categoria = (
        df.group_by("categoria").agg(pl.col("ventas").sum().alias("ventas_totales")).sort("ventas_totales", descending=True)
        .with_columns((pl.col("ventas_totales") / pl.col("ventas_totales").sum() * 100).round(2).alias("pct"))
    )

    top3 = ventas_categoria.head(3)
    r["1_familias_mayor_volumen"] = {
        "familias_top3": top3["categoria"].to_list(),
        "pct_acumulado_top3": round(top3["pct"].sum(), 2),
    }
 


    #2. Ventas totales por tienda y ranking de las 10 tiendas con mayor y menor venta.
    ventas_tienda = (
        df.group_by("num_tienda").agg(pl.col("ventas").sum().alias("ventas_totales")).sort("ventas_totales", descending=True)
    )
    
    r["2_ranking_tiendas"] = {
        "top10_mayor_venta": ventas_tienda.head(10).to_dicts(),
        "top10_menor_venta": ventas_tienda.tail(10).sort("ventas_totales").to_dicts(),
    }



    #12. ¿Qué ciudades mostraron mayor sensibilidad a la caída del petróleo?
    antes = df.filter((pl.col("anio_mes") >= "2014-06") & (pl.col("anio_mes") <= "2014-11"))
    despues = df.filter((pl.col("anio_mes") >= "2015-06") & (pl.col("anio_mes") <= "2015-12"))
    comparacion_ciudad = (
        antes.group_by("ciudad").agg(pl.col("ventas").mean().alias("venta_antes"))
        .join(despues.group_by("ciudad").agg(pl.col("ventas").mean().alias("venta_despues")), on="ciudad", how="inner")
        .with_columns(((pl.col("venta_despues") - pl.col("venta_antes")) / pl.col("venta_antes") * 100).round(2).alias("cambio_pct"))
        .sort("cambio_pct")
    )

    r["12_ciudades_sensibles_petroleo"] = {
        "ciudades_mas_afectadas": comparacion_ciudad.head(5).select(["ciudad", "cambio_pct"]).to_dicts(),
    }



    #13. Relación entre número de transacciones y volumen de ventas por tienda.
    resumen_tienda = (
        df.group_by("num_tienda").agg([pl.col("ventas").sum().alias("ventas_totales"), pl.col("transacciones").sum().alias("transacciones_totales")])
    )

    r_trans = round(resumen_tienda.select(pl.corr("transacciones_totales", "ventas_totales")).item(), 3)
    r["13_transacciones_vs_ventas"] = {"r_pearson": r_trans}



    #14. Identificación de tiendas con ticket promedio alto (pocas transacciones, altas ventas) 
    # vs ticket bajo (muchas transacciones, bajas ventas).
    resumen_tienda = resumen_tienda.with_columns(
        (pl.col("ventas_totales") / pl.col("transacciones_totales")).round(2).alias("ticket_promedio")
    ).sort("ticket_promedio", descending=True)

    r["14_ticket_promedio_tienda"] = {
        "ticket_mas_alto": resumen_tienda.head(3).select(["num_tienda", "ticket_promedio"]).to_dicts(),
        "ticket_mas_bajo": resumen_tienda.tail(3).sort("ticket_promedio").select(["num_tienda", "ticket_promedio"]).to_dicts(),
    }