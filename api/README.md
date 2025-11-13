# API - Azure Functions

This directory contains the Azure Functions backend for the EPAR Data Portal.

## Functions

- **ingest_blob** - Blob trigger that processes uploaded documents
- **search** - HTTP GET endpoint for searching documents
- **download** - HTTP POST endpoint for secure file downloads

## Setup

1. Install Azure Functions Core Tools
2. Copy `.env.dev` values to `local.settings.json`
3. Run `pip install -r requirements.txt`
4. Run `func host start`

