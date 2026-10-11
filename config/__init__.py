# Ensure PyMySQL is registered as MySQLdb for MySQL / TiDB database engine support
try:
    import pymysql
    pymysql.install_as_MySQLdb()

    # Allow MySQL 8.0+ and TiDB Cloud Serverless (which reports 8.0.11-TiDB)
    from django.db.backends.base.base import BaseDatabaseWrapper
    BaseDatabaseWrapper.check_database_version_supported = lambda self: None
except ImportError:
    pass
