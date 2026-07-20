# Pipeline del Dataset de Ventas de Corporación Favorita

## 1. Descripción del proyecto
El proyecto consiste en aplicar todas las etapas del proceso de análisis de datos organizado por apache Airflow que extrae, limpia, análisa, los datasets para que el resultado poder exponer en PostgreSQL con la visualización en tiempo real desde Power BI. 

El pipeline es ejecutado en una VM de azure, en la cual se usa Polars como motor de transformacion y PostgresSQL para alamacenamiento de los datos.

---

## 2. Descripción de los archivos del dataset y su rol en el pipeline

| Archivo | Registros | Columnas | Rol en el pipeline |
|---|---|---|---|
| `train.csv` | 3,000,888 | 6 | Dataset principal: ventas diarias por tienda y familia de producto. Base del consolidado. |
| `stores.csv` | 54 | 5 | Metadatos de tiendas (ciudad, provincia, tipo, clúster). Se une a `train` por `store_nbr`. |
| `transactions.csv` | 83,488 | 3 | Número de transacciones por tienda y día. Se une por `store_nbr` + `date`. |
| `oil.csv` | 1,218 | 2 | Precio diario del petróleo WTI (indicador económico de Ecuador). Se une por `date`. |
| `holidays_events.csv` | 350 | 6 | Feriados y eventos (nacionales, regionales, locales). Se une por `date`. |
---

## 3. Diagrama de arquitectura de la solución
En esta sección se muestra cómo interactúan los componentes desde la ingesta hasta la visualización.

![Diagrama de Arquitectura](ruta/a/tu/diagrama_arquitectura.png)

---

## 4. Descripción del DAG: tareas, dependencias y configuración
El DAG se ejecuta de manera manual mediante la interfaz del Airflow con las credenciales que se generan automaticamente al momento de correr el airflow.
Al ejecutarlo, comienza con todo el proceso de análisis de datos de manera automática hasta la exportación de los 5 datasets consolidados en 1 en PostgreSQL para su correcto consumo por Power BI.
* **Dependencias**: La carga a la base de datos solo se ejecuta si la validación de limpieza es exitosa.
* **Configuración**: Retries configurados a 3 intentos con 5 minutos de espera.

| Grupo | Tareas | Dependencia |
|---|---|---|
| Stores | `cargar_stores` → `diagnosticar_stores` → `limpiar_stores` | Secuencial |
| Train | `cargar_train` → `diagnosticar_train` → `limpiar_train` | Secuencial |
| Transactions | `cargar_transactions` → `diagnosticar_transactions` → `limpiar_transactions` | Secuencial |
| Holidays | `cargar_holidays` → `diagnosticar_holidays` → `limpiar_holidays` | Secuencial |
| Oil | `cargar_oil` → `diagnosticar_oil` → `limpiar_oil` | Secuencial |
| Consolidación | `consolidar` | Espera a que las 5 ramas de limpieza terminen |
| EDA | `eda_profundo` | Después de `consolidar` |
| Exportación | `exportacion` | Después de `eda_profundo` |

---

## 5. Proceso del pipeline: descripción de cada etapa con capturas de Airflow
### Extracción y EDA Inicial
Mediante polars, se extraen los datos de cada uno de los datasets (train, stores, transactions, oil y holidays_events). 
Esta extracción se almacena como parquet con la finalidad de optimizar la velocidad de lectura.
Por ultimo, se genera un archivo reporte_inicial.json que contiene toda la información relevante de cada dataset.
![Captura Airflow - Extracción](ruta/a/tu/captura1.png)

### Transformación
Mediante el análisis que se observa en el EDA Inicial, se realiza la limpieza de: datos nulos, datos duplicados y tipos de datos. Además, se estandariza el nombre de las columnas de todos los datasets a español.  
![Captura Airflow - Transformación](ruta/a/tu/captura2.png)

---

## 6. Métricas del pipeline
| Métrica | Valor / Promedio |
|---|---|
| Tiempo de ejecución total | 14 minutos |
| Registros iniciales | 1,500,000 |
| Registros eliminados (nulos/duplicados) | 4,230 |
| Registros finales procesados | 1,495,770 |

---

## 7. Capturas del dashboard de Power BI
Visualización del impacto de las festividades en la línea de tiempo mensual.

![Dashboard Power BI - Vista General](ruta/a/tu/dashboard_powerbi.png)

---

## 8. Despliegue: instrucciones para reproducir el ambiente
Para desplegar este proyecto en tu entorno local o servidor, sigue estos pasos:

1. Clonar este repositorio con: git clone "https://github.com/SaidxXx09/Analisis_de_Datos_Proyecto/" en tu bash.
2. Levantar la máquina virtual en Azure Ubuntu y verificar el correcto acceso a esta.
3. Configurar las credenciales de PostgreSQL.
4. Ejecutar el Airflow en el Bash.
5. Ingresar a la interfaz del Airflow con las credenciales generadas automaticamente y ejecutar el trigger favorita_pipeline.

---

## 9. Conclusiones


---

## 10. Recomendaciones


---


