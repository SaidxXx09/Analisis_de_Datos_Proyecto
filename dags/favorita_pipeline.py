from airflow import DAG
from airflow.providers.standard.operators.python import PythonOperator
from datetime import datetime, timedelta
import sys
import logging

sys.path.append("/home/azureuser/proyecto_favorita")

# --- Carga y EDA inicial ---
from Analisis_de_Datos_Proyecto.scripts.carga.carga_train import cargar_train, diagnosticar_train
from Analisis_de_Datos_Proyecto.scripts.carga.carga_stores import cargar_stores, diagnosticar_stores
from Analisis_de_Datos_Proyecto.scripts.carga.carga_transactions import cargar_transactions, diagnosticar_transactions
from Analisis_de_Datos_Proyecto.scripts.carga.carga_holidays import cargar_holidays, diagnosticar_holidays
from Analisis_de_Datos_Proyecto.scripts.carga.carga_oil import cargar_oil, diagnosticar_oil

# --- Limpieza ---
from Analisis_de_Datos_Proyecto.scripts.limpieza.limpieza_train import limpiar_train
from Analisis_de_Datos_Proyecto.scripts.limpieza.limpieza_stores import limpiar_stores
from Analisis_de_Datos_Proyecto.scripts.limpieza.limpieza_transaccions import limpiar_transactions
from Analisis_de_Datos_Proyecto.scripts.limpieza.limpieza_holidays import limpiar_holidays
from Analisis_de_Datos_Proyecto.scripts.limpieza.limpieza_oil import limpiar_oil

# --- Concatenacion ---
from Analisis_de_Datos_Proyecto.scripts.consolidacion.consolidacion import consolidar_dataset

#--- EDA Profundo ---
from Analisis_de_Datos_Proyecto.scripts.eda.eda_profundo import eda_profundo


def registrar_error(context):
    logging.error(
        f"Fallo en tarea: {context['task_instance'].task_id} - DAG: {context['dag'].dag_id}"
    )


default_args = {
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
    "on_failure_callback": registrar_error,
}


with DAG(
    dag_id="favorita_pipeline",
    start_date=datetime(2026, 7, 1),
    schedule=None,
    catchup=False,
    default_args=default_args,
) as dag:

    # --- Stores ---
    t_cargar_stores = PythonOperator(
        task_id="cargar_stores",
        python_callable=cargar_stores,
    )
    t_diagnosticar_stores = PythonOperator(
        task_id="diagnosticar_stores",
        python_callable=diagnosticar_stores,
    )
    t_limpiar_stores = PythonOperator(
        task_id="limpiar_stores",
        python_callable=limpiar_stores,
    )


    # --- Train ---
    t_cargar_train = PythonOperator(
        task_id="cargar_train",
        python_callable=cargar_train,
    )
    t_diagnosticar_train = PythonOperator(
        task_id="diagnosticar_train",
        python_callable=diagnosticar_train,
    )
    t_limpiar_train = PythonOperator(
        task_id="limpiar_train",
        python_callable=limpiar_train)

    # --- Transactions ---
    t_cargar_transactions = PythonOperator(
        task_id="cargar_transactions",
        python_callable=cargar_transactions,
    )
    t_diagnosticar_transactions = PythonOperator(
        task_id="diagnosticar_transactions",
        python_callable=diagnosticar_transactions,
    )
    t_limpiar_transactions = PythonOperator(
        task_id="limpiar_transactions",
        python_callable=limpiar_transactions,
    )

    # --- Holidays ---
    t_cargar_holidays = PythonOperator(
        task_id="cargar_holidays",
        python_callable=cargar_holidays,
    )
    t_diagnosticar_holidays = PythonOperator(
        task_id="diagnosticar_holidays",
        python_callable=diagnosticar_holidays,
    )
    t_limpiar_holidays = PythonOperator(
        task_id = 'limpiar_holidays',
        python_callable = limpiar_holidays
    )

    # --- Oil ---
    t_cargar_oil = PythonOperator(
        task_id="cargar_oil",
        python_callable=cargar_oil,
    )
    t_diagnosticar_oil = PythonOperator(
        task_id="diagnosticar_oil",
        python_callable=diagnosticar_oil,
    )
    t_limpiar_oil = PythonOperator(
        task_id = 'limpiar_oil',
        python_callable = limpiar_oil
    )

    # --- Consolidacion ---
    t_consolidacion = PythonOperator(
        task_id = "consolidar",
        python_callable = consolidar_dataset
    )

    # --- EDA Profundo ---
    t_eda_profundo = PythonOperator(
    task_id="eda_profundo",
    python_callable=eda_profundo
    )

    t_cargar_stores >> t_diagnosticar_stores >> t_limpiar_stores
    t_cargar_train >> t_diagnosticar_train >> t_limpiar_train
    t_cargar_transactions >> t_diagnosticar_transactions >> t_limpiar_transactions
    t_cargar_holidays >> t_diagnosticar_holidays >> t_limpiar_holidays
    t_cargar_oil >> t_diagnosticar_oil >> t_limpiar_oil
    [t_limpiar_holidays,t_limpiar_transactions,t_limpiar_oil,t_limpiar_stores,t_limpiar_train] >> t_consolidacion >> t_eda_profundo