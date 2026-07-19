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