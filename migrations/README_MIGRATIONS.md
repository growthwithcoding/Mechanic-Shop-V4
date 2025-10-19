# Database Migrations for Mechanic Shop V4

This folder contains Alembic/Flask-Migrate database migrations for version control of the database schema.

## Current Migration

**001_initial_schema.py** - Complete initial schema with all 11 models and junction tables

This migration creates all tables from scratch for Mechanic Shop V4:

### Tables Created:
1. **customers** - Customer accounts with authentication
2. **vehicles** - Customer vehicles
3. **mechanics** - Staff members
4. **services** - Service catalog
5. **service_tickets** - Work orders
6. **parts** - Inventory/parts catalog
7. **specializations** - Mechanic certifications
8. **service_packages** - Bundled services

### Junction Tables:
9. **ticket_mechanics** - Mechanic assignments to tickets
10. **ticket_line_items** - Services on tickets
11. **ticket_parts** - Parts used on tickets (with quantity, warranty, etc.)
12. **mechanic_specializations** - Mechanic certifications
13. **service_prerequisites** - Service dependencies
14. **service_package_items** - Services in packages

## How to Use Migrations

### Initial Setup (Fresh Database)

```bash
# 1. Create database using SQL script
# Run: SQL/recreate_database.sql in MySQL

# 2. Set Flask app environment variable
set FLASK_APP=app.py  # Windows
# export FLASK_APP=app.py  # Mac/Linux

# 3. Run migrations to create all tables
flask db upgrade
```

### After Model Changes

If you modify any models in `application/models.py`:

```bash
# 1. Generate new migration
flask db migrate -m "Description of changes"

# 2. Review generated migration in versions/
# Check the new file in migrations/versions/

# 3. Apply migration
flask db upgrade
```

### Rollback Changes

```bash
# Rollback last migration
flask db downgrade

# Rollback to specific version
flask db downgrade <revision_id>
```

### View Migration History

```bash
# Show all migrations
flask db history

# Show current version
flask db current
```

## Migration Workflow

1. **Make changes** to models in `application/models.py`
2. **Generate migration**: `flask db migrate -m "descriptive message"`
3. **Review migration** file in `versions/`
4. **Test migration** on development database
5. **Apply migration**: `flask db upgrade`
6. **Commit migration** to version control

## Troubleshooting

### "Target database is not up to date"
Run `flask db upgrade` first to apply all pending migrations

### "Database doesn't exist"
Create database using `SQL/recreate_database.sql`

### "Migration conflicts"
Check `alembic_version` table in database and resolve version conflicts

### "Duplicate column/table"
Database may have old schema. Use `SQL/recreate_database.sql` to start fresh

## Important Notes

- Always review auto-generated migrations before applying
- Test migrations on development environment first
- Keep migrations in version control
- Never edit applied migrations
- For fresh setup, use SQL scripts + `flask db upgrade`
- Migrations are incremental - they build on previous ones

## Clean Database Setup

For a completely fresh start:

```bash
# 1. Drop and recreate database
# Run SQL/recreate_database.sql

# 2. Apply migrations
flask db upgrade

# 3. Seed sample data
# Run SQL/seed_sample_data.sql
```

This ensures a clean schema matching the current models exactly.
