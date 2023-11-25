class BaseConfig:
  DB_USER = 'postgres'
  DB_PASS = 'AlanF20'
  DB_HOST = 'localhost'
  DB_NAME = 'pmultipara'
  SQLALCHEMY_DATABASE_URI=f'postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}/{DB_NAME}'
  SECRET_KEY = 'seguridadExtrema'
  SQLALCHEMY_TRACK_MODIFICATIONS=False
  DEBUG=False
  BCRYPT_LOG_ROUNDS=13