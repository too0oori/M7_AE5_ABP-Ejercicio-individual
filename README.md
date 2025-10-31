# M7_AE5_ABP - Ejercicio Individual Django ORM

## 1. Recuperando Registros con Django ORM

**Modelo creado:**
```python
class Producto(models.Model):
    nombre = models.CharField(max_length=100)
    precio = models.DecimalField(max_digits=5, decimal_places=2)
    disponible = models.BooleanField(default=True)
```

**Comandos ejecutados:**
```bash
python manage.py makemigrations
python manage.py migrate
```

**Consulta:**
```python
from productos.models import Producto
productos = Producto.objects.all()
for p in productos:
    print(f"{p.nombre}: ${p.precio}")
```

**Explicación:** `objects.all()` recupera todos los registros de la tabla usando el ORM de Django.

---

## 2. Aplicando Filtros en Recuperación de Registros

**Productos con precio mayor a 50,000:**
```python
productos = Producto.objects.filter(precio__gt=50000)
```

**Productos cuyo nombre empiece con "A":**
```python
productos = Producto.objects.filter(nombre__startswith="A")
```

**Productos disponibles:**
```python
productos = Producto.objects.filter(disponible=True)
```

**Explicación:** Django ORM usa lookups (`__gt`, `__startswith`) para aplicar filtros sin escribir SQL directamente.

---

## 3. Ejecutando Queries SQL desde Django

**Consulta con raw():**
```python
productos = Producto.objects.raw('SELECT * FROM productos_producto WHERE precio < 100000')
for p in productos:
    print(p.nombre, p.precio, p.disponible)
```

**Explicación:** `raw()` permite ejecutar SQL personalizado mientras mapea los resultados a instancias del modelo Django.

---

## 4. Mapeando Campos de Consultas al Modelo

**Query con campo calculado:**
```python
productos = Producto.objects.raw('SELECT *, precio * 0.8 AS precio_con_descuento FROM productos_producto')
for p in productos:
    print(p.nombre, p.precio, p.precio_con_descuento, p.disponible)
```

**Explicación:** Django mapea automáticamente los campos del SELECT (incluyendo calculados como `precio_con_descuento`) a atributos del objeto. El campo calculado NO se guarda en la BD, solo existe en memoria.

---

## 5. Realizando Búsquedas de Índice

**Verificación del índice:**
```python
from django.db import connection

with connection.cursor() as cursor:
    cursor.execute("EXPLAIN SELECT * FROM productos_producto WHERE nombre = 'Laptop'")
    print(cursor.fetchall())
```

**Resultado:**
```
('ref', 'productos_producto_nombre_3e7bf33e', 1, 100.0)
```

**Explicación:** 
- `type: 'ref'` = MySQL usa el índice (eficiente)
- `rows: 1` = Solo examina 1 registro en lugar de toda la tabla
- `filtered: 100.0` = Eficiencia del 100%

Los índices mejoran el rendimiento de búsquedas creando una estructura optimizada que permite acceso directo a registros sin escanear toda la tabla, es util sobretodo para bases de datos con miles de registros.

---

## 6. Exclusión de Campos del Modelo

**Usando values():**
```python
productos = Producto.objects.values('nombre', 'precio')
for p in productos:
    print(p['nombre'], p['precio'])
```

**Explicación:** `values()` retorna diccionarios con solo los campos especificados, excluyendo `disponible`.

---

## 7. Añadiendo Anotaciones en Consultas

**Calcular precio con impuesto (16%):**
```python
from django.db.models import F

productos = Producto.objects.annotate(precio_con_impuesto=F('precio') * 1.16)
for p in productos:
    print(f"{p.nombre} - Precio: ${p.precio} - Con impuesto: ${p.precio_con_impuesto}")
```

**Explicación:** `annotate()` agrega campos calculados dinámicamente a cada objeto. `F('precio')` referencia el valor del campo en la BD para realizar operaciones.

---

## 8. Pasando Parámetros a raw()

**Query con parámetros:**
```python
precio_limite = 80000
disponibilidad = True

productos = Producto.objects.raw(
    'SELECT * FROM productos_producto WHERE precio < %s AND disponible = %s', 
    [precio_limite, disponibilidad]
)

for p in productos:
    print(f"{p.nombre}: ${p.precio} - Disponible: {p.disponible}")
```

**Resultado:**
```
Teclado: $45000 - Disponible: True
```

**Explicación:** Usar `%s` como placeholder y pasar valores en lista previene **SQL injection** y permite reutilización. 

---

## 9. SQL Personalizado Directamente

**INSERT con cursor:**
```python
from django.db import connection

with connection.cursor() as cursor:
    cursor.execute(
        "INSERT INTO productos_producto (nombre, precio, disponible) VALUES (%s, %s, %s)",
        ['Mouse Inalámbrico', 35000, True]
    )
```

**Resultado:**
```
Laptop 1200000 True
Mouse 25000 False
Teclado 45000 True
Monitor 350000 True
Audífonos 80000 False
Mouse Inalámbrico 35000 True  ← Nuevo producto
```

**Explicación:** `connection.cursor()` permite ejecutar SQL directo (INSERT, UPDATE, DELETE) sin pasar por el ORM. Útil para operaciones masivas o queries muy complejas, pero se pierden las ventajas del ORM (signals, validaciones).

---

## 10. Conexiones y Cursores

**Ventajas del cursor:**
- Control total sobre el SQL ejecutado
- Mayor rendimiento en operaciones masivas
- Acceso a funcionalidades específicas de la BD

**Desventajas:**
- Pérdida de portabilidad entre bases de datos
- No se ejecutan signals ni validaciones de Django
- Código menos mantenible que el ORM

**Cuándo usar:** Operaciones masivas (millones de registros), queries muy complejas, o funcionalidades específicas de MySQL/PostgreSQL.

---

## 11. Invocación a Procedimientos Almacenados

**Crear procedimiento:**
```python
from django.db import connection

with connection.cursor() as cursor:
    cursor.execute("DROP PROCEDURE IF EXISTS productos_disponibles")
    cursor.execute("""
        CREATE PROCEDURE productos_disponibles()
        BEGIN
            SELECT nombre, precio 
            FROM productos_producto 
            WHERE disponible = TRUE;
        END
    """)
```

**Invocar procedimiento:**
```python
with connection.cursor() as cursor:
    cursor.callproc('productos_disponibles')
    resultados = cursor.fetchall()
    
    for fila in resultados:
        print(f"{fila[0]}: ${fila[1]}")
```

**Explicación:** Los procedimientos almacenados son funciones SQL guardadas en la BD. `callproc()` los ejecuta desde Django. Son útiles para lógica compleja reutilizable, pero reducen la portabilidad y son más difíciles de mantener que código Python.

---

## Resumen de Técnicas

| Técnica | Uso | Ventaja |
|---------|-----|---------|
| `objects.all()` | Recuperar registros | Simple, usa ORM |
| `filter()` | Filtrar datos | Seguro |
| `raw()` | SQL personalizado | Mapea a modelos |
| `annotate()` | Campos calculados | Operaciones en BD |
| `values()` | Excluir campos | Optimiza memoria |
| `cursor.execute()` | SQL directo | Máximo control |
| `cursor.callproc()` | Procedimientos | Lógica reutilizable |

Lo ideal es usar ORM de Django siempre que sea posible. SQL directo solo para casos especiales.