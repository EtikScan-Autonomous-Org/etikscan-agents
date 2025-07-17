terraform {
  required_version = ">= 1.5.0"

  required_providers {
    cloudflare = {
      source  = "cloudflare/cloudflare" # <-- C'est la ligne qui corrige l'erreur
      version = "~> 4.0"
    }
    tembo = {
      source  = "tembo-io/tembo"
      version = ">= 0.1.0"
    }
  }
}

# Configuration pour le fournisseur Cloudflare.
provider "cloudflare" {}

# Configuration pour le fournisseur Tembo.
provider "tembo" {}