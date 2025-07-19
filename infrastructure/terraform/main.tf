# main.tf

resource "tembo_instance" "etikscan_db" {
  instance_name = "etikscan-main-db"
  org_id        = var.tembo_org_id
  stack_name    = "Standard"
  cpu           = "0.25"
  memory        = "1Gi"
  storage       = "10Gi"
  replicas      = 1
}