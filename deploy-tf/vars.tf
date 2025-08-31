variable "project_id" {}
variable "region" {
  default = "europe-southwest1"
}
variable "service_name" {
  default = "tastet-escape-room"
}
variable "secret_key" {
  default = "revetllaalataleia"
}
variable "image" {
  description = "Docker image URI (Artifact Registry)"
}