# Tembo UI

This repository contains the UI components for Tembo's web application, focusing on infrastructure management features including Organization ID display and API Token creation for Terraform integration.

## Features

- Organization Settings page displaying the Organization ID needed for Terraform
- API Token management interface for creating and managing tokens used with Terraform
- Clear instructions for users on how to use these credentials with the Tembo Terraform provider

## Getting Started

1. Clone this repository
2. Install dependencies: `npm install`
3. Start the development server: `npm start`

## Using with Terraform

The UI provides a dedicated Settings page where users can:

1. Find their Organization ID
2. Create and manage API Tokens for infrastructure provisioning
3. View example Terraform configuration snippets

Example Terraform configuration:

```hcl
provider "tembo" {
  org_id    = "your-organization-id"  # From Organization Settings
  api_token = "your-api-token"        # Created in API Tokens section
}

resource "tembo_postgres" "example" {
  name     = "example-db"
  postgres_version = "15"
  # Additional configuration...
}
```

## API Reference

The UI interacts with Tembo's API to:
- Retrieve organization information
- Manage API tokens for infrastructure access