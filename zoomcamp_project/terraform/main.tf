terraform {
  required_version = ">= 1.0"
  backend "local" {}  
  required_providers {
    google = {
      source  = "hashicorp/google"
    }
  }
}

provider "google" {
  project = var.project
  region = var.region
}

# GCS bucket for new daily data
resource "google_storage_bucket" "data-lake-daily" {
  name          = "daily_earthquakes_${var.project}" # Concatenating DL bucket & Project name for unique naming
  location      = var.region

  storage_class = var.storage_class
  uniform_bucket_level_access = true

  versioning {
    enabled     = true
  }

}

# GCS bucket for historical data
resource "google_storage_bucket" "data-lake-historical" {
  name          = "historical_earthquakes_${var.project}" # Concatenating DL bucket & Project name for unique naming
  location      = var.region

  storage_class = var.storage_class
  uniform_bucket_level_access = true

  versioning {
    enabled     = true
  }

}

# Dataset and Table creation in BQ
resource "google_bigquery_dataset" "default" {
  dataset_id = var.bq_dataset
  project    = var.project
  location   = var.region

}

resource "google_bigquery_table" "default" {
  dataset_id = google_bigquery_dataset.default.dataset_id
  table_id   = var.table_name

  time_partitioning {
    type = "YEAR"
    field = "time"
  }

  # Schema for the table
  schema = file("schema.json")

  deletion_protection=false
}