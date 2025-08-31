terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = ">= 5.0.0"
    }
  }
  required_version = ">= 1.5.0"
}

provider "google" {
  project = var.project_id
  region  = var.region
}

# Cloud Run service
resource "google_cloud_run_v2_service" "escape_room_tastet" {
  name     = var.service_name
  location = var.region

  template {
    containers {
      image = var.image
      env {
        name  = "SECRET_KEY"
        value = var.secret_key
      }
    }
  }
}

# Permetre accés públic (unauthenticated)
resource "google_cloud_run_v2_service_iam_member" "noauth" {
  location = var.region
  project  = var.project_id
  name     = google_cloud_run_v2_service.escape_room_tastet.name
  role     = "roles/run.invoker"
  member   = "allUsers"
}
