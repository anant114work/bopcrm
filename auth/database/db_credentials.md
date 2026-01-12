# Database Credentials

## SQLite (Development)
- **File**: `db.sqlite3`
- **Location**: Project root
- **Backup**: Daily automated backup

## PostgreSQL (Production)
- **Host**: `[DB_HOST]`
- **Port**: `5432`
- **Database**: `[DB_NAME]`
- **Username**: `[DB_USER]`
- **Password**: `[DB_PASSWORD]`

## Redis (Caching)
- **Host**: `[REDIS_HOST]`
- **Port**: `6379`
- **Password**: `[REDIS_PASSWORD]`

## Notes
- Use connection pooling in production
- Enable SSL for remote connections
- Regular database backups required