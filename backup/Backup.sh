# Backup
pg_dump -U postgres -h localhost -p 5440 fintrack > backup_fintrack.sql

# Restore
psql -U postgres -h localhost -p 5440 -d fintrack < backup_fintrack.sql