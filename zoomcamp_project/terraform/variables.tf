
variable "project" {
  description = "Your GCP Project ID"
}

variable "region" {
  description = "Region for GCP resources"
  default = "us-west1"
  type = string
}

variable "storage_class" {
  description = "Storage class type"
  default = "STANDARD"
}

variable "bq_dataset" {
  description = "BigQuery Dataset that raw data (from GCS) will be written to"
  type = string
  default = "earthquakes_dataset"
}

variable "table_name" {
  description = "Name of the BigQuery table."
  type        = string
  default     = "earthquakes"
}
