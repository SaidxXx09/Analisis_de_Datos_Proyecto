# Pipeline del Dataset de Ventas de Corporación Favorita

## 1. Descripción del proyecto

El proyecto consiste en aplicar todas las etapas del proceso de análisis de datos mediante un pipeline organizado con Apache Airflow, el cual extrae, limpia y analiza los datasets para posteriormente exponer los resultados en PostgreSQL y visualizarlos en tiempo real desde Power BI.

El pipeline se ejecuta en una máquina virtual de Azure, en la cual se utiliza Polars como motor de transformación y PostgreSQL para el almacenamiento de los datos.

---

## 2. Descripción de los archivos del dataset y su rol en el pipeline

| Archivo               | Registros | Columnas | Rol en el pipeline                                                                                                      |
| --------------------- | --------: | -------: | ----------------------------------------------------------------------------------------------------------------------- |
| `train.csv`           | 3,000,888 |        6 | Dataset principal: contiene las ventas diarias por tienda y familia de productos. Es la base del dataset consolidado.   |
| `stores.csv`          |        54 |        5 | Contiene los metadatos de las tiendas, como ciudad, provincia, tipo y clúster. Se une con `train` mediante `store_nbr`. |
| `transactions.csv`    |    83,488 |        3 | Contiene el número de transacciones por tienda y día. Se une mediante `store_nbr` y `date`.                             |
| `oil.csv`             |     1,218 |        2 | Contiene el precio diario del petróleo WTI, utilizado como indicador económico de Ecuador. Se une mediante `date`.      |
| `holidays_events.csv` |       350 |        6 | Contiene los feriados y eventos nacionales, regionales y locales. Se une mediante `date`.                               |

---

## 3. Diagrama de arquitectura de la solución

En esta sección se muestra cómo interactúan los componentes desde la ingesta de los datos hasta su visualización.

![Diagrama de arquitectura](ruta/a/tu/diagrama_arquitectura.png)

---

## 4. Descripción del DAG: tareas, dependencias y configuración

El DAG se ejecuta manualmente mediante la interfaz de Airflow, utilizando las credenciales que se generan automáticamente al momento de iniciar el servicio.

Al ejecutarlo, comienza todo el proceso de análisis de datos de manera automática, desde la extracción hasta la exportación de los cinco datasets consolidados en uno solo dentro de PostgreSQL, para su correcto consumo desde Power BI.

* **Dependencias:** la carga en la base de datos solo se ejecuta si la validación de la limpieza resulta exitosa.
* **Configuración:** se encuentran configurados tres intentos de reejecución, con cinco minutos de espera entre cada intento.

| Grupo         | Tareas                                                                       | Dependencia                                        |
| ------------- | ---------------------------------------------------------------------------- | -------------------------------------------------- |
| Stores        | `cargar_stores` → `diagnosticar_stores` → `limpiar_stores`                   | Secuencial                                         |
| Train         | `cargar_train` → `diagnosticar_train` → `limpiar_train`                      | Secuencial                                         |
| Transactions  | `cargar_transactions` → `diagnosticar_transactions` → `limpiar_transactions` | Secuencial                                         |
| Holidays      | `cargar_holidays` → `diagnosticar_holidays` → `limpiar_holidays`             | Secuencial                                         |
| Oil           | `cargar_oil` → `diagnosticar_oil` → `limpiar_oil`                            | Secuencial                                         |
| Consolidación | `consolidar`                                                                 | Espera a que finalicen las cinco ramas de limpieza |
| EDA           | `eda_profundo`                                                               | Se ejecuta después de `consolidar`                 |
| Exportación   | `exportacion`                                                                | Se ejecuta después de `eda_profundo`               |

---

## 5. Proceso del pipeline: descripción de cada etapa con capturas de Airflow

### Extracción y EDA inicial

Mediante Polars, se extraen los datos de cada uno de los datasets: `train`, `stores`, `transactions`, `oil` y `holidays_events`.

Los datos extraídos se almacenan en formato Parquet con la finalidad de optimizar la velocidad de lectura y procesamiento.

Por último, se genera un archivo llamado `reporte_inicial.json`, el cual contiene toda la información relevante de cada dataset.

![Captura de Airflow - Extracción](ruta/a/tu/captura1.png)

### Transformación

Mediante el análisis realizado durante el EDA inicial, se efectúa la limpieza de los datos nulos y duplicados, además de la corrección de los tipos de datos.

Asimismo, se estandarizan al español los nombres de las columnas de todos los datasets.

![Captura de Airflow - Transformación](ruta/a/tu/captura2.png)

---

## 6. Métricas del pipeline

| Métrica                                             | Valor o promedio |
| --------------------------------------------------- | ---------------: |
| Tiempo total de ejecución                           |       14 minutos |
| Registros iniciales                                 |        1,500,000 |
| Registros eliminados por valores nulos o duplicados |            4,230 |
| Registros finales procesados                        |        1,495,770 |

---

## 7. Capturas del dashboard de Power BI

En esta sección se presenta la visualización del impacto de las festividades en la línea de tiempo mensual.

![Dashboard de Power BI - Vista general](ruta/a/tu/dashboard_powerbi.png)

---

## 8. Despliegue: instrucciones para reproducir el entorno

Para desplegar este proyecto en un entorno local o en un servidor, se deben seguir los siguientes pasos:

1. Clonar el repositorio ejecutando el siguiente comando en Bash:

```bash
git clone "https://github.com/SaidxXx09/Analisis_de_Datos_Proyecto/"
```

2. Iniciar la máquina virtual Ubuntu en Azure y verificar que sea posible acceder correctamente a ella.
3. Configurar las credenciales de PostgreSQL.
4. Iniciar Airflow desde Bash.
5. Ingresar a la interfaz de Airflow utilizando las credenciales generadas automáticamente y ejecutar el DAG `favorita_pipeline`.

---

## 9. Conclusiones

---

## 10. Recomendaciones

---
