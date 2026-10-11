# Ensure PyMySQL is registered as MySQLdb for MySQL database engine support
try:
    import pymysql
    pymysql.install_as_MySQLdb()
except ImportError:
    pass
