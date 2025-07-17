# backend.tf

# Configuration pour utiliser le backend sécurisé de Terraform Cloud.
terraform {
  cloud {
    organization = "EtikScan-Autonomous-Org" # Remplacez par le nom de votre organisation

    workspaces {
      name = "etikscan-agents-infra"
    }
  }
}