# Pipeline del Dataset de Ventas de Corporación Favorita

## 1. Descripción del proyecto
El desarrollo del proyecto consiste en la automatización de: extracción, transformación y carga de datos de diferentes fuentes. 

## 2. Descripción de los archivos del dataset y su rol en el pipeline
* **train.csv**: Contiene los registros transaccionales base que ingresan al sistema.
* **stores.csv**: Dataset dimensional utilizado para el análisis de impacto comparativo de ventas durante días festivos.
* **transactions.csv**: Catálogo para normalizar las categorías durante la fase de transformación.
* **oil.csv**: Catálogo para normalizar las categorías durante la fase de transformación.
* **holidays_events.csv**: Catálogo para normalizar las categorías durante la fase de transformación.

## 3. Diagrama de arquitectura de la solución
En esta sección se muestra cómo interactúan los componentes desde la ingesta hasta la visualización.

![Diagrama de Arquitectura](ruta/a/tu/diagrama_arquitectura.png)

## 4. Descripción del DAG: tareas, dependencias y configuración
El DAG se ejecuta de manera manual mediante la interfaz del Airflow con las credenciales que se generan automaticamente al momento de correr el airflow. 
* **Tareas**: `extraer_datos` -> `limpiar_nulos` -> `cargar_postgres`
* **Dependencias**: La carga a la base de datos solo se ejecuta si la validación de limpieza es exitosa.
* **Configuración**: Retries configurados a 3 intentos con 5 minutos de espera.

## 5. Proceso del pipeline: descripción de cada etapa con capturas de Airflow
### Extracción y EDA Inicial
Mediante polars, se extraen los datos de cada uno de los datasets (train, stores, transactions, oil y holidays_events). 
Esta extracción se almacena como parquet con la finalidad de optimizar la velocidad de lectura.
Por ultimo, se genera un archivo reporte_inicial.json que contiene toda la información relevante de cada dataset.
![Captura Airflow - Extracción](ruta/a/tu/captura1.png)

### Transformación
Mediante el análisis que se observa en el EDA Inicial, se realiza la limpieza de: datos nulos, datos duplicados y tipos de datos. Además, se estandariza el nombre de las columnas de todos los datasets a español.  
![Captura Airflow - Transformación](ruta/a/tu/captura2.png)

## 6. Métricas del pipeline
| Métrica | Valor / Promedio |
|---|---|
| Tiempo de ejecución total | 14 minutos |
| Registros iniciales | 1,500,000 |
| Registros eliminados (nulos/duplicados) | 4,230 |
| Registros finales procesados | 1,495,770 |

## 7. Capturas del dashboard de Power BI
Visualización del impacto de las festividades en la línea de tiempo mensual.

![Dashboard Power BI - Vista General](ruta/a/tu/dashboard_powerbi.png)

## 8. Despliegue: instrucciones para reproducir el ambiente
Para desplegar este proyecto en tu entorno local o servidor, sigue estos pasos:

1. Clonar este repositorio con: git clone "https://github.com/SaidxXx09/Analisis_de_Datos_Proyecto/" en tu bash.
2. Levantar la máquina virtual en Azure Ubuntu y verificar el correcto acceso a esta.
3. Configurar las credenciales de PostgreSQL.
4. Ejecutar el script de inicialización de contenedores:
   ```bash
   docker-compose up -d

## 9. Conclusiones


## 10. Recomendaciones



