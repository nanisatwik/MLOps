# Import necessary libraries and modules
from airflow import DAG
from airflow.providers.standard.operators.python import PythonOperator
from datetime import datetime, timedelta
from src.lab import validate_data, load_data, data_preprocessing, build_save_model, load_model_elbow


# Define default arguments for your DAG
default_args = {
    'owner': 'Satwik',
    'start_date': datetime(2026, 1, 15),
    'retries': 2,  # Retry a failed task up to 2 more times before giving up
    'retry_delay': timedelta(minutes=1),  # Wait 1 minute between retries
}

# Create a DAG instance named 'Airflow_Lab1' with the defined default arguments
with DAG(
    'Airflow_Lab1',
    default_args=default_args,
    description='K-Means customer clustering pipeline with data validation',
    catchup=False,
) as dag:

    # Task to validate the input data before anything else runs
    validate_data_task = PythonOperator(
        task_id='validate_data_task',
        python_callable=validate_data,
    )

    # Task to load data, calls the 'load_data' Python function
    load_data_task = PythonOperator(
        task_id='load_data_task',
        python_callable=load_data,
    )

    # Task to perform data preprocessing, depends on 'load_data_task'
    data_preprocessing_task = PythonOperator(
        task_id='data_preprocessing_task',
        python_callable=data_preprocessing,
        op_args=[load_data_task.output],
    )

    # Task to build and save a model, depends on 'data_preprocessing_task'
    build_save_model_task = PythonOperator(
        task_id='build_save_model_task',
        python_callable=build_save_model,
        op_args=[data_preprocessing_task.output, "model.sav"],
    )

    # Task to load a model using the 'load_model_elbow' function, depends on 'build_save_model_task'
    load_model_task = PythonOperator(
        task_id='load_model_task',
        python_callable=load_model_elbow,
        op_args=["model.sav", build_save_model_task.output],
    )

    # Set task dependencies
    validate_data_task >> load_data_task >> data_preprocessing_task >> build_save_model_task >> load_model_task

# If this script is run directly, allow command-line interaction with the DAG
if __name__ == "__main__":
    dag.test()