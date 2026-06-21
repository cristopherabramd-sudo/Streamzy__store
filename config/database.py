import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Forzamos la carga del archivo .env que está en la raíz
load_dotenv()

# Usamos valores por defecto en caso de que os.getenv devuelva None
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")  # Lo dejamos como string temporalmente
DB_NAME = os.getenv("DB_NAME", "marketplace_db")

# Construimos la URL de conexión de forma segura
DATABASE_URL = f"postgresql+pg8000://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Intento de creación de la base de datos si no existe de forma automática
try:
    import pg8000.dbapi
    # Nos conectamos a la base de datos por defecto 'postgres' para crear la base de datos de la app
    conn = pg8000.dbapi.connect(
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=int(DB_PORT),
        database="postgres"
    )
    conn.autocommit = True
    cursor = conn.cursor()
    # Comprobamos si la base de datos ya existe
    cursor.execute(f"SELECT 1 FROM pg_database WHERE datname = '{DB_NAME}'")
    exists = cursor.fetchone()
    if not exists:
        cursor.execute(f"CREATE DATABASE {DB_NAME}")
        print(f"Base de datos '{DB_NAME}' creada con éxito.")
    cursor.close()
    conn.close()
except Exception as e:
    # Si falla, imprimimos advertencia pero dejamos que SQLAlchemy intente conectar por si acaso
    print(f"Advertencia al verificar/crear la base de datos '{DB_NAME}': {e}")

# Creamos el motor de SQLAlchemy
engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()