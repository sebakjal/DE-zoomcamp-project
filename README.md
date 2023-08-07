# DE-zoomcamp-project
Final project for the Data Engineering Zoomcamp 2023

For this project I built a pipeline that extracts earthquake data from the USGS earthquakes catalog and presents it in a dashboard.

![Dashboard](https://github.com/sebakjal/DE-zoomcamp-project/assets/48660452/7e51e2e1-a766-486d-896d-7d42d9ac3712)

The main goal of the project was to gain hands-on experience with some of the most common data engineering tools. To achieve that, I utilized the following technologies:

* Google Cloud Platform services (GCE, GCP, BigQuery, Looker Studio)
* Terraform for infrastructure provisioning
* Spark for data processing
* Airflow for workflow orchestration

![flow](https://github.com/sebakjal/DE-zoomcamp-project/assets/48660452/1173dd1b-d087-45ca-ae1c-000d9d06c341)

Here's a brief overview of the project's workflow:
1. I set up a Virtual Machine (VM) in Google Compute Engine (GCE) to serve as my primary workspace.
2. Using Terraform, I created a data lake and data warehouse on GCP. The historical earthquake data was pulled from USGS servers and loaded into the data lake.
3. I used PySpark to transform and load the cleaned data into BigQuery, which serves as the data warehouse.
4. The clean and structured data is then used as the primary data source for the interactive dashboard.
5. Airflow was integrated into the pipeline to ensure that the data warehouse receives daily updates with new data.

Dashboard link: https://shorturl.at/xyIV3
