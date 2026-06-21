import os

# Ejecuta el comando SQL de forma directa e independiente a través de psql
os.system('psql -U postgres -d marketplace_db -c "UPDATE proveedores SET status = \'aprobado\' WHERE nombre_tienda = \'STREAMZY STORE\';"')