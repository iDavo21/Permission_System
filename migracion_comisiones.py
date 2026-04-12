from core.database import get_connection

conn = get_connection('comisiones.db')

# Agregar columnas si no existen
try:
    conn.execute('ALTER TABLE comisiones ADD COLUMN fecha_salida TEXT')
    print('Columna fecha_salida agregada')
except Exception as e:
    print(f'fecha_salida: {e}')

try:
    conn.execute('ALTER TABLE comisiones ADD COLUMN finalizada INTEGER DEFAULT 0')
    print('Columna finalizada agregada')
except Exception as e:
    print(f'finalizada: {e}')

# Migrar datos
try:
    conn.execute("UPDATE comisiones SET fecha_salida = fecha_desde WHERE fecha_salida IS NULL")
    print('Datos migrados de fecha_desde a fecha_salida')
except Exception as e:
    print(f'Migracion: {e}')

conn.commit()
conn.close()
print('DB comisiones actualizada')