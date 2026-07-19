import polars as pl

RUTA = "Analisis_de_Datos_Proyecto/data/processed/consolidacion.parquet"

pl.Config.set_tbl_rows(20)
pl.Config.set_tbl_cols(20)

df = pl.read_parquet(RUTA)

df = df.with_columns([
    pl.col("fecha").dt.year().alias("anio"),
    pl.col("fecha").dt.strftime("%Y-%m").alias("anio_mes"),
])

# Primera preg.
print("1. VENTAS POR FAMILIA DE PRODUCTO")
print("=" * 70)

ventas_categoria = (
    df.group_by("categoria")
    .agg(pl.col("ventas").sum().alias("ventas_totales"))
    .sort("ventas_totales", descending=True)
    .with_columns((pl.col("ventas_totales") / pl.col("ventas_totales").sum() * 100).round(2).alias("pct"))
)
print(ventas_categoria)

top3 = ventas_categoria.head(3)
pct_top3 = top3["pct"].sum()
print(f"\n-> Las 3 familias con mayor volumen son: {top3['categoria'].to_list()}, "
      f"que concentran en conjunto el {pct_top3:.1f}% de las ventas totales.")

# Segunda preg.
print("2. VENTAS TOTALES POR TIENDA - RANKING TOP 10")
print("=" * 70)

ventas_tienda = (
    df.group_by("num_tienda")
    .agg(pl.col("ventas").sum().alias("ventas_totales"))
    .sort("ventas_totales", descending=True)
)
print("Top 10 MAYOR venta:")
print(ventas_tienda.head(10))
print("\nTop 10 MENOR venta:")
print(ventas_tienda.tail(10).sort("ventas_totales"))

mejor = ventas_tienda.head(1)
peor = ventas_tienda.tail(1)
print(f"\n-> La tienda #{mejor['num_tienda'][0]} es la de mayor venta total ({mejor['ventas_totales'][0]:,.0f}); "
      f"la tienda #{peor['num_tienda'][0]} es la de menor venta ({peor['ventas_totales'][0]:,.0f}).")


# Pregunta 12
# ¿Qué ciudades mostraron mayor sensibilidad a la caída del petróleo?
print("\n" + "=" * 70)
print("12. CIUDADES MÁS SENSIBLES A LA CAÍDA DEL PETRÓLEO")
print("=" * 70)
print("(Comparando venta promedio jun-nov 2014 vs jun-dic 2015; ajustar rango si el grupo definió otro)")

antes = df.filter((pl.col("anio_mes") >= "2014-06") & (pl.col("anio_mes") <= "2014-11"))
despues = df.filter((pl.col("anio_mes") >= "2015-06") & (pl.col("anio_mes") <= "2015-12"))

ventas_ciudad_antes = antes.group_by("ciudad").agg(pl.col("ventas").mean().alias("venta_antes"))
ventas_ciudad_despues = despues.group_by("ciudad").agg(pl.col("ventas").mean().alias("venta_despues"))

comparacion_ciudad = ventas_ciudad_antes.join(ventas_ciudad_despues, on="ciudad", how="inner")
comparacion_ciudad = comparacion_ciudad.with_columns(
    ((pl.col("venta_despues") - pl.col("venta_antes")) / pl.col("venta_antes") * 100).round(2).alias("cambio_pct")
).sort("cambio_pct")

print(comparacion_ciudad)

top_afectadas = comparacion_ciudad.head(5)
print(f"\n-> Las ciudades con mayor caída de ventas asociada a la caída del petróleo son: "
      f"{top_afectadas['ciudad'].to_list()} (cambios de {top_afectadas['cambio_pct'].to_list()}%).")


# Pregunta 13
# Relación entre número de transacciones y volumen de ventas por tienda.
print("\n" + "=" * 70)
print("13. TRANSACCIONES VS VENTAS POR TIENDA")
print("=" * 70)

resumen_tienda = (
    df.group_by("num_tienda")
    .agg([
        pl.col("ventas").sum().alias("ventas_totales"),
        pl.col("transacciones").sum().alias("transacciones_totales"),
    ])
)
r_trans = resumen_tienda.select(pl.corr("transacciones_totales", "ventas_totales")).item()
conclusion_trans = "relación fuerte" if r_trans > 0.6 else "relación moderada" if r_trans > 0.3 else "relación débil"
print(f"-> Correlación transacciones vs ventas por tienda (polars): r={r_trans:.3f} -> {conclusion_trans}.")


# Pregunta 14
# Identificación de tiendas con ticket promedio alto 
# (pocas transacciones, altas ventas) vs ticket bajo 
# (muchas transacciones, bajas ventas).
print("\n" + "=" * 70)
print("14. TICKET PROMEDIO POR TIENDA (ventas / transacciones)")
print("=" * 70)

resumen_tienda = resumen_tienda.with_columns(
    (pl.col("ventas_totales") / pl.col("transacciones_totales")).round(2).alias("ticket_promedio")
).sort("ticket_promedio", descending=True)

print("Tiendas con TICKET PROMEDIO más alto (pocas transacciones, ventas altas por transacción):")
print(resumen_tienda.head(10))
print("\nTiendas con TICKET PROMEDIO más bajo (muchas transacciones, ventas bajas por transacción):")
print(resumen_tienda.tail(10).sort("ticket_promedio"))

alto = resumen_tienda.head(3)
bajo = resumen_tienda.tail(3).sort("ticket_promedio")
print(f"\n-> Ticket promedio más alto: tiendas {alto['num_tienda'].to_list()} "
      f"({alto['ticket_promedio'].to_list()}).")
print(f"-> Ticket promedio más bajo: tiendas {bajo['num_tienda'].to_list()} "
      f"({bajo['ticket_promedio'].to_list()}).")

print("\n" + "=" * 70)
print("EDA PROFUNDO COMPLETO")
print("=" * 70)
