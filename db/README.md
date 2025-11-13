# Database

This directory contains the SQLite database file for the EPAR Data Portal.

## Files

- `docs.sqlite` - Main database with FTS5 search index (not committed to git)

## Schema

- **docs** - Document metadata table
- **docs_fts** - FTS5 full-text search index

## Notes

- Database files are excluded from git via `.gitignore`
- WAL mode enabled for better concurrency
- Deterministic IDs based on blob path SHA-256

