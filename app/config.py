SECRET_KEY = 'generateSecretKey'
SQLALCHEMY_DATABASE_URI = 'mysql://test:1234@localhost/aucase?unix_socket=/run/mysqld/mysqld.sock'
SQLALCHEMY_TRACK_MODIFICATIONS = False
SQLALCHEMY_ENGINE_OPTIONS = { 'pool_pre_ping': True }
JSON_AS_ASCII = False
TESTING = False
DEBUG = False
