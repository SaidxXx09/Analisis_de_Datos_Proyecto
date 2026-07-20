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
# 3. Ventas promedio por ciudad y provincia
    ventas_ciudad = (
        df.group_by("ciudad").agg(pl.col("ventas").mean().round(2).alias("venta_promedio"))
        .sort("venta_promedio", descending=True)
    )
    ventas_provincia = (
        df.group_by("estado").agg(pl.col("ventas").mean().round(2).alias("venta_promedio"))
        .sort("venta_promedio", descending=True)
    )
    r["3_ventas_ciudad_provincia"] = {
        "ciudad_mayor": {"ciudad": ventas_ciudad["ciudad"][0], "venta_promedio": ventas_ciudad["venta_promedio"][0]},
        "provincia_mayor": {"estado": ventas_provincia["estado"][0], "venta_promedio": ventas_provincia["venta_promedio"][0]},
    }
 
    # 4. Evolución temporal 2013-2017
    ventas_anuales = df.group_by("anio").agg(pl.col("ventas").sum().alias("ventas_totales")).sort("anio")
    crecimiento = ((ventas_anuales["ventas_totales"][-1] - ventas_anuales["ventas_totales"][0])
                   / ventas_anuales["ventas_totales"][0] * 100)
    r["4_evolucion_temporal"] = {
        "ventas_por_anio": ventas_anuales.to_dicts(),
        "crecimiento_acumulado_pct": round(crecimiento, 2),
    }
 
    # 5. Impacto de feriados nacionales en ventas
    df = df.with_columns(
        ((pl.col("alcance") == "National") & (~pl.col("transferido"))
         & (pl.col("tipo_feriado") != "Work Day")).alias("es_feriado_nacional")
    )
    ventas_diarias = (
        df.group_by(["fecha", "es_feriado_nacional"]).agg(pl.col("ventas").sum().alias("ventas_del_dia"))
    )
    resumen_feriado = (
        ventas_diarias.group_by("es_feriado_nacional")
        .agg(pl.col("ventas_del_dia").mean().round(2).alias("venta_diaria_promedio"))
    )
    media_feriado = resumen_feriado.filter(pl.col("es_feriado_nacional"))["venta_diaria_promedio"][0]
    media_normal = resumen_feriado.filter(~pl.col("es_feriado_nacional"))["venta_diaria_promedio"][0]
    diferencia_pct = round((media_feriado - media_normal) / media_normal * 100, 2)
    r["5_impacto_feriados"] = {
        "venta_diaria_promedio_feriado": media_feriado,
        "venta_diaria_promedio_normal": media_normal,
        "diferencia_pct": diferencia_pct,
    }
 
    # 6. Ventas ventana -3/+3 dias por familia (categoria)
    fechas_feriado_nacional = df.filter(pl.col("es_feriado_nacional")).select("fecha").unique()
    ventas_por_familia_dia = (
        df.group_by(["fecha", "categoria"]).agg(pl.col("ventas").sum().alias("ventas_dia"))
    )
    fechas_ventana = fechas_feriado_nacional.select(
        pl.concat_list([(pl.col("fecha") + pl.duration(days=d)) for d in range(-3, 4)]).alias("fecha")
    ).explode("fecha").unique()
    ventana_familia = (
        ventas_por_familia_dia.filter(pl.col("fecha").is_in(fechas_ventana["fecha"]))
        .group_by("categoria").agg(pl.col("ventas_dia").mean().round(2).alias("venta_promedio_ventana"))
        .sort("venta_promedio_ventana", descending=True)
    )
    r["6_ventana_feriados_por_familia"] = {
        "familias_top3_ventana": ventana_familia.head(3).to_dicts(),
        "familias_bottom3_ventana": ventana_familia.tail(3).to_dicts(),
    }


    #10. Correlación entre precio del petróleo y ventas totales mensuales.
    ventas_mensuales = df.group_by("anio_mes").agg(pl.col("ventas").sum().alias("ventas_totales")).sort("anio_mes")
    petroleo_mensual = (
        df.group_by("anio_mes").agg(pl.col("precio_diario_petroleo").mean().round(2).alias("precio_promedio_petroleo"))
        .sort("anio_mes")
    )
    serie = ventas_mensuales.join(petroleo_mensual, on="anio_mes", how="inner").sort("anio_mes")
    corr = round(serie.select(pl.corr("ventas_totales", "precio_promedio_petroleo")).item(), 3)

    r["10_correlacion_petroleo_ventas"] = {"r_pearson": corr}
 


    #11. Identificación del lag temporal entre caída del petróleo y caída en ventas (período 2015-2016).
    serie_periodo = serie.filter((pl.col("anio_mes") >= "2015-01") & (pl.col("anio_mes") <= "2016-12"))
    correlaciones_lag = {}
    for lag in range(-6, 7):
        rr = serie_periodo.select(pl.corr(pl.col("ventas_totales"), pl.col("precio_promedio_petroleo").shift(lag))).item()
        if rr is not None:
            correlaciones_lag[lag] = round(rr, 3)
    mejor_lag = max(correlaciones_lag, key=lambda k: abs(correlaciones_lag[k]))

    r["11_lag_petroleo_ventas"] = {"mejor_lag_meses": mejor_lag, "r_pearson": correlaciones_lag[mejor_lag]}



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