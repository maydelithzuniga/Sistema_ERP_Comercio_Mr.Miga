# Simulacion.py - Mr. Miga
# Replica la logica de los scripts 03_generar_data_<escala>.sql para
# poder generar los mismos datasets (1000, 10000, 100000, 1000000)
# directamente desde Python.
#
# Uso: python Simulacion.py --scale 1000 | 10000 | 100000 | 1000000
# Requiere: pip install psycopg2-binary

import argparse
import random
import time as time_module
import psycopg2
from psycopg2.extras import execute_batch
from datetime import date, time, timedelta

# Datos de conexion, cambiar segun el entorno
DB_CONFIG = {
    "host":     "localhost",
    "port":     5433,
    "dbname":   "PARTE 2",
    "user":     "postgres",
    "password": "Ut3c0760*",
}

# Tamaño de cada lote de INSERT. Ajustar segun RAM disponible
# (1K-10K -> 500, 100K -> 2000, 1M -> 5000)
BATCH = 2000

# Funciones auxiliares
EPOCH     = date(1970, 1, 1)
BASE_DATE = date(2025, 1, 1)
MAX_DATE  = date(2025, 12, 31)
DELTA_MAX = (MAX_DATE - BASE_DATE).days   # 364

def rand_date() -> date:
    return BASE_DATE + timedelta(days=random.randint(0, DELTA_MAX))

def det_date(i: int) -> date:
    """Versión determinista (para escala 1M, evita random() por fila)."""
    return BASE_DATE + timedelta(days=i % 365)

def rand_time_of_day() -> time:
    base_minutes = 10 * 60   # 10:00
    offset = random.randint(0, 720)
    total  = base_minutes + offset
    return time(total // 60, total % 60)

def det_time(i: int) -> time:
    total = 600 + (i % 720)      # 10:00 + offset cíclico
    return time(total // 60, total % 60)

def lpad(n: int, width: int = 8) -> str:
    return str(n).zfill(width)

def celular_rand() -> str:
    return "9" + str(random.randint(0, 99_999_999)).zfill(8)

def celular_det(i: int) -> str:
    return "9" + str(i % 99_999_999).zfill(8)

# Listas de valores posibles, igual que en los SQL
GENEROS    = ["M", "F"]
HORARIOS   = ["M", "T", "N"]
DIAS       = ["LU","MA","MI","JU","VI","SA","DO"]
METODOS    = ["Efectivo","Yape","Plin","Tarjeta"]
ESTADOS_PED= ["Pendiente","Preparando","Entregado","Cancelado"]
PLATAFORMAS= ["Rappi","PedidosYa","UberEats"]
ESTADOS_DEL= ["Asignado","En camino","Entregado","Cancelado"]
ESTADOS_EXT= ["Recibido","Preparando","Entregado","Cancelado"]
AREAS      = ["Cocina","Caja","Atencion","Limpieza"]
LOCALES    = ["LOC00001","LOC00002"]
DISTRITOS  = ["Barranco","Santiago de Surco"]

# Precios fijos por producto (igual que en los SQL)
PRECIOS = {
    "PROD0001": 15.90,
    "PROD0002": 12.50,
    "PROD0003":  7.50,
    "PROD0004":  8.90,
}

# Tablas base, iguales en todos los scripts

def step_persona(cur, n: int, fast: bool = False):
    """
    Escala 1K-100K → random()   (igual que SQL 1K/10K/100K)
    Escala 1M      → determinista, sin random() por fila (igual que SQL 1M)
    """
    t0 = time_module.time()
    print(f"  Persona ({n:,})...", end=" ", flush=True)

    # En 1M el SQL solo genera n*0.85 + 1000 personas
    total = n if not fast else int(n * 0.85) + 1000

    rows = []
    for i in range(1, total + 1):
        if fast:
            gen = "M" if i % 2 == 0 else "F"
            cel = celular_det(i)
            nac = EPOCH + timedelta(days=i % 15000)
        else:
            gen = random.choice(GENEROS)
            cel = celular_rand()
            nac = EPOCH + timedelta(days=random.randint(0, 15000))
        rows.append((lpad(i), gen, f"Nombre_{i}", f"Apellido_{i}", nac, cel))
        if len(rows) == BATCH:
            execute_batch(cur,
                "INSERT INTO Persona(dni,genero,nombre,apellidos,fecha_nacimiento,celular)"
                " VALUES(%s,%s,%s,%s,%s,%s) ON CONFLICT DO NOTHING", rows)
            rows = []
    if rows:
        execute_batch(cur,
            "INSERT INTO Persona(dni,genero,nombre,apellidos,fecha_nacimiento,celular)"
            " VALUES(%s,%s,%s,%s,%s,%s) ON CONFLICT DO NOTHING", rows)
    print(f"listo ({time_module.time()-t0:.1f}s)")


def step_clientes(cur, n: int):
    """85% de las personas son clientes."""
    t0 = time_module.time()
    lim = int(n * 0.85)
    print(f"  Cliente ({lim:,})...", end=" ", flush=True)
    rows = [(lpad(i),) for i in range(1, lim + 1)]
    execute_batch(cur,
        "INSERT INTO Cliente(dni) VALUES(%s) ON CONFLICT DO NOTHING",
        rows, page_size=BATCH)
    print(f"listo ({time_module.time()-t0:.1f}s)")
    return lim   # cantidad de clientes


def step_empleados(cur, n: int, fast: bool = False):
    """Del 85% al 100% de las personas son empleados."""
    t0 = time_module.time()
    inicio = int(n * 0.85) + 1
    fin    = n if not fast else int(n * 0.85) + 1000
    print(f"  Empleado ({fin-inicio+1:,})...", end=" ", flush=True)
    rows = []
    for i in range(inicio, fin + 1):
        if fast:
            hor = HORARIOS[i % 3]
            dia = DIAS[i % 7]
            sue = 1500 + (i % 1000)
        else:
            hor = random.choice(HORARIOS)
            dia = random.choice(DIAS)
            sue = round(1200 + random.random() * 1800, 2)
        rows.append((lpad(i), hor, dia, sue))
        if len(rows) == BATCH:
            execute_batch(cur,
                "INSERT INTO Empleado(dni,horario,dias_descanso,sueldo)"
                " VALUES(%s,%s,%s,%s) ON CONFLICT DO NOTHING", rows)
            rows = []
    if rows:
        execute_batch(cur,
            "INSERT INTO Empleado(dni,horario,dias_descanso,sueldo)"
            " VALUES(%s,%s,%s,%s) ON CONFLICT DO NOTHING", rows)
    print(f"listo ({time_module.time()-t0:.1f}s)")
    return inicio, fin   # rango empleados


def step_repartidores(cur, n: int, emp_inicio: int, fast: bool = False):
    """Del 85% al 88% son repartidores (o primeros 1000 empleados en 1M)."""
    t0 = time_module.time()
    if fast:
        inicio = int(n * 0.85) + 1
        fin    = int(n * 0.85) + 1000
    else:
        inicio = int(n * 0.85) + 1
        fin    = int(n * 0.88)
    print(f"  Repartidor ({fin-inicio+1:,})...", end=" ", flush=True)
    rows = []
    seq  = 1
    for i in range(inicio, fin + 1):
        repartos = i % 500 if fast else random.randint(0, 500)
        placa    = "A" + str(seq).zfill(5)
        rows.append((lpad(i), repartos, placa))
        seq += 1
        if len(rows) == BATCH:
            execute_batch(cur,
                "INSERT INTO Repartidor(dni,repartos_completados,placa_vehiculo)"
                " VALUES(%s,%s,%s) ON CONFLICT DO NOTHING", rows)
            rows = []
    if rows:
        execute_batch(cur,
            "INSERT INTO Repartidor(dni,repartos_completados,placa_vehiculo)"
            " VALUES(%s,%s,%s) ON CONFLICT DO NOTHING", rows)
    print(f"listo ({time_module.time()-t0:.1f}s)")
    return inicio, fin   # rango repartidores


def step_planilla(cur, n: int, emp_inicio: int, emp_fin: int,
                  rep_inicio: int, rep_fin: int):
    """Empleados que NO son repartidores → Planilla."""
    t0 = time_module.time()
    rep_set = set(range(rep_inicio, rep_fin + 1))
    rows    = []
    count   = 0
    for i in range(emp_inicio, emp_fin + 1):
        if i in rep_set:
            continue
        inicio_lab = date(2024, 1, 1) + timedelta(days=random.randint(0, 365))
        rows.append((
            lpad(i),
            random.choice(LOCALES),
            random.choice(AREAS),
            inicio_lab,
            None,
        ))
        count += 1
        if len(rows) == BATCH:
            execute_batch(cur,
                "INSERT INTO Planilla(dni,id_local,area_trabajo,desde,hasta)"
                " VALUES(%s,%s,%s,%s,%s) ON CONFLICT DO NOTHING", rows)
            rows = []
    if rows:
        execute_batch(cur,
            "INSERT INTO Planilla(dni,id_local,area_trabajo,desde,hasta)"
            " VALUES(%s,%s,%s,%s,%s) ON CONFLICT DO NOTHING", rows)
    print(f"  Planilla ({count:,})... listo ({time_module.time()-t0:.1f}s)")


def step_cuenta_puntos(cur, n: int):
    """
    59.5% de los clientes tienen cuenta de puntos.
    IDs: PUN000000001 .. PUN000595000 (para n=1M)
    """
    t0  = time_module.time()
    lim = int(n * 0.595)
    print(f"  CuentaPuntos ({lim:,})...", end=" ", flush=True)
    rows = []
    for i in range(1, lim + 1):
        rows.append((
            "PUN" + str(i).zfill(9),
            random.randint(0, 1000),
            rand_date(),
            lpad(i),          # dni_cliente = mismo índice
        ))
        if len(rows) == BATCH:
            execute_batch(cur,
                "INSERT INTO CuentaPuntos(id_puntos,puntos,fecha,dni_cliente)"
                " VALUES(%s,%s,%s,%s) ON CONFLICT DO NOTHING", rows)
            rows = []
    if rows:
        execute_batch(cur,
            "INSERT INTO CuentaPuntos(id_puntos,puntos,fecha,dni_cliente)"
            " VALUES(%s,%s,%s,%s) ON CONFLICT DO NOTHING", rows)
    print(f"listo ({time_module.time()-t0:.1f}s)")
    return lim   # total_puntos


def step_tablas_fijas(cur):
    """Local, Producto, Topping, Promocion, siempre los mismos."""
    print("  Tablas fijas (Local/Producto/Topping/Promocion)...", end=" ", flush=True)
    cur.execute("""
        INSERT INTO Local(id_local,nombre_local,direccion,distrito,aforo,telefono)
        VALUES
          ('LOC00001','Mr. Miga Barranco','Delucchi 364','Barranco',60,'2541001'),
          ('LOC00002','Mr. Miga Jockey Plaza','Av Javier Prado Este 4200','Santiago de Surco',80,'6100002')
        ON CONFLICT DO NOTHING
    """)
    cur.execute("""
        INSERT INTO Producto(id_producto,nombre,descripcion,categoria,precio_venta,estado)
        VALUES
          ('PROD0001','Hamburguesa Clasica',   'Clasica con queso','Hamburguesas',15.90,'Activo'),
          ('PROD0002','Hamburguesa Hambrienta','Doble carne','Hamburguesas',12.50,'Activo'),
          ('PROD0003','Salchipapas Clasica',   'Con sal','Salchipapas',7.50,'Activo'),
          ('PROD0004','Pollo Broaster 1/4',    'Con papas','Pollos',8.90,'Activo'),
          ('PROD0005','Combo Estudiante',      'Burger + papas + gaseosa','Combos',22.00,'Activo'),
          ('PROD0006','Gaseosa Personal',      'Inca Kola 500ml','Bebidas',5.00,'Activo')
        ON CONFLICT DO NOTHING
    """)
    cur.execute("""
        INSERT INTO Topping(id_topping,nombre,precio)
        VALUES
          ('TOP00001','Queso Extra',2.50),
          ('TOP00002','Tocino',3.00),
          ('TOP00003','Salsa BBQ',1.50),
          ('TOP00004','Salsa Andina',1.50),
          ('TOP00005','Jalapenos',1.00),
          ('TOP00006','Cebolla Caramelizada',2.00),
          ('TOP00007','Huevo Frito',2.50),
          ('TOP00008','Aguacate',3.50)
        ON CONFLICT DO NOTHING
    """)
    cur.execute("""
        INSERT INTO Promocion(id_promocion,nombre_promocion,tipo_promocion,valor,fecha_inicio,fecha_fin)
        VALUES
          ('PROM0001','2x1 Hamburguesa','2x1',100.00,'2024-01-01','2025-12-31'),
          ('PROM0002','Desc 20pct Combo','Descuento',20.00,'2024-03-01','2024-06-30'),
          ('PROM0003','Happy Hour 15pct','Descuento',15.00,'2024-01-01','2025-12-31'),
          ('PROM0004','Promo Rappi 10pct','Descuento',10.00,'2024-01-01','2025-12-31')
        ON CONFLICT DO NOTHING
    """)
    cur.execute("""
        INSERT INTO Ingrediente(nombre,precio_compra,cantidad_stock)
        VALUES
          ('Pan de hamburguesa',0.80,500),
          ('Carne de res 150g',3.50,300),
          ('Lechuga',0.30,200),
          ('Tomate',0.40,200),
          ('Queso amarillo',1.20,250),
          ('Papa fresca 200g',0.60,400),
          ('Pollo entero',8.00,100),
          ('Aceite de girasol',0.50,50)
        ON CONFLICT DO NOTHING
    """)
    print("listo")


# Cadena principal: Pago -> Pedido -> subtipos -> Detalle -> Topping -> Movimientos
def step_cadena_pedidos(cur, n: int, n_clientes: int,
                        rep_inicio: int, rep_fin: int,
                        total_puntos: int, fast: bool = False):
    """
    Genera toda la cadena con las mismas proporciones que los SQL:
      40% presencial | 30% delivery | 30% plataforma
      3 detalles por pedido (1 en modo 1M)
      Topping: primeros n*1.2 detalles (1 topping cada uno)
      Movimiento_puntos: 50% de los pedidos
    """
    n_reps   = rep_fin - rep_inicio + 1
    det_mult = 1 if fast else 3

    # toppings disponibles
    cur.execute("SELECT id_topping FROM Topping")
    topping_ids = [r[0] for r in cur.fetchall()]
    n_tops      = len(topping_ids)

    # Contadores de filas por tabla
    pagos_r = []; boletas_r = []; facturas_r = []
    pedidos_r = []
    presencial_r = []; delivery_r = []; plataforma_r = []
    detalle_r = []
    det_top_r = []
    movimiento_r = []

    det_seq = 1
    dto_seq = 1
    mov_seq = 1
    MAX_DTO = int(n * 1.2)   # límite de toppings (igual que SQL)

    def flush(table, sql, rows):
        if rows:
            execute_batch(cur, sql, rows, page_size=BATCH)
            rows.clear()

    FLUSH_EVERY = BATCH * 4  # acumular más antes de flush para reducir round-trips

    t0 = time_module.time()
    print(f"  Pagos + Pedidos + Detalles ({n:,})...")

    for i in range(1, n + 1):

        # Pago
        if fast:
            fecha_p = det_date(i)
            metodo  = METODOS[i % 4]
            monto   = round(10 + (i % 90), 2)
            id_pts  = None                     # SQL 1M no usa CuentaPuntos en Pago
        else:
            fecha_p = rand_date()
            metodo  = random.choice(METODOS)
            monto   = round(10 + random.random() * 90, 2)
            # 75% de chance de usar puntos si existen
            if total_puntos > 0 and random.random() >= 0.25:
                idx_pts = ((i - 1) % total_puntos) + 1
                id_pts  = "PUN" + str(idx_pts).zfill(9)
            else:
                id_pts = None

        pagos_r.append((i, id_pts, fecha_p, metodo, monto))

        # Boleta (80%) vs Factura (20%)
        if random.random() < 0.80:
            boletas_r.append((i,))
        else:
            ruc   = str(random.randint(10_000_000_000, 99_999_999_999))
            razon = f"Empresa_{i}"[:80]
            facturas_r.append((i, ruc, razon))

        # Pedido base
        id_ped   = "PED" + str(i).zfill(9)
        local    = LOCALES[i % 2] if fast else random.choice(LOCALES)
        estado_p = ESTADOS_PED[i % 4] if fast else random.choice(ESTADOS_PED)
        hora_p   = det_time(i) if fast else rand_time_of_day()
        fecha_ped= det_date(i) if fast else rand_date()
        pedidos_r.append((id_ped, local, estado_p, hora_p, fecha_ped, monto, i))

        # Subtipo: 40% presencial / 30% delivery / 30% plataforma
        if i <= int(n * 0.40):
            # Presencial
            cli_idx = ((i % n_clientes) + 1) if fast else (random.randint(1, n_clientes))
            presencial_r.append((id_ped, lpad(cli_idx), (i % 200) + 1 if fast else random.randint(1, 200)))

        elif i <= int(n * 0.70):
            # Delivery
            cli_idx = ((i % n_clientes) + 1) if fast else random.randint(1, n_clientes)
            rep_idx = rep_inicio + (i % n_reps) if fast else rep_inicio + random.randint(0, n_reps - 1)
            hora_s  = det_time(i)     if fast else rand_time_of_day()
            hora_e  = det_time(i + 30) if fast else rand_time_of_day()
            dist    = DISTRITOS[i % 2] if fast else random.choice(DISTRITOS)
            estado_d= ESTADOS_DEL[i % 4] if fast else random.choice(ESTADOS_DEL)
            delivery_r.append((
                id_ped,
                lpad(cli_idx),
                lpad(rep_idx),
                f"Direccion_{i}",
                dist,
                hora_e,
                f"Referencia_{i}",
                hora_s,
                round(3 + (i % 7), 2) if fast else round(3 + random.random() * 7, 2),
                estado_d,
            ))

        else:
            # Plataforma
            plat    = PLATAFORMAS[i % 3] if fast else random.choice(PLATAFORMAS)
            comision= round(10 + (i % 20), 2) if fast else round(random.random() * 30, 2)
            est_ext = ESTADOS_EXT[i % 4] if fast else random.choice(ESTADOS_EXT)
            plataforma_r.append((
                id_ped, plat, comision, est_ext,
                f"EXT{i}", f"Alias_{i}", f"Direccion_{i}",
            ))

        # Detalle pedido
        n_det = det_mult   # 1 (fast) o 3 (normal)
        for d in range(n_det):
            prod_num = ((det_seq - 1) % 4) + 1
            prod_id  = f"PROD{str(prod_num).zfill(4)}"
            precio   = PRECIOS.get(prod_id, 10.00)
            promo    = None
            if not fast:
                if prod_id == "PROD0001" and random.random() < 0.30:
                    promo = "PROM0001"
                elif prod_id == "PROD0002" and random.random() < 0.30:
                    promo = "PROM0002"
            qty = (det_seq % 3) + 1 if fast else random.randint(1, 3)

            # En modo normal: el pedido de destino es aleatorio (igual que SQL)
            ped_dest = id_ped if fast else "PED" + str(random.randint(1, i)).zfill(9)

            id_det = "DET" + str(det_seq).zfill(9)
            detalle_r.append((id_det, ped_dest, prod_id, promo, qty, precio))

            # topping (solo los primeros MAX_DTO detalles)
            if det_seq <= MAX_DTO and n_tops > 0:
                top_id = topping_ids[dto_seq % n_tops]
                id_dto = "DTO" + str(dto_seq).zfill(9)
                det_top_r.append((
                    id_dto, id_det, ped_dest, top_id,
                    (dto_seq % 2) + 1 if fast else random.randint(1, 2),
                    round(1 + random.random() * 4, 2),
                ))
                dto_seq += 1

            det_seq += 1

        # Movimiento de puntos (50% de los pedidos)
        if total_puntos > 0 and i <= int(n * 0.5):
            idx_mov = ((i - 1) % total_puntos) + 1
            movimiento_r.append((
                "MOV" + str(mov_seq).zfill(9),
                "PUN" + str(idx_mov).zfill(9),
                random.randint(0, 200),
                rand_date(),
                "Movimiento de puntos",
                i,
            ))
            mov_seq += 1

        # flush por lotes
        if i % FLUSH_EVERY == 0:
            pct = i / n * 100
            print(f"    {pct:5.1f}% ({i:,}/{n:,}) flush...", end=" ", flush=True)
            t1 = time_module.time()

            execute_batch(cur,
                "INSERT INTO Pago(id_pago,id_puntos,fecha_emision,metodo_pago,monto)"
                " VALUES(%s,%s,%s,%s,%s)", pagos_r, page_size=BATCH)
            execute_batch(cur,
                "INSERT INTO Boleta(id_pago) VALUES(%s)", boletas_r, page_size=BATCH)
            execute_batch(cur,
                "INSERT INTO Factura(id_pago,ruc,razon_social) VALUES(%s,%s,%s)",
                facturas_r, page_size=BATCH)
            execute_batch(cur,
                "INSERT INTO Pedido(id_pedido,id_local,estado_pedido,hora,fecha,total_pago,id_pago_fk)"
                " VALUES(%s,%s,%s,%s,%s,%s,%s)", pedidos_r, page_size=BATCH)
            execute_batch(cur,
                "INSERT INTO Pedido_presencial(id_pedido,dni_cliente,numero_turno)"
                " VALUES(%s,%s,%s)", presencial_r, page_size=BATCH)
            execute_batch(cur,
                "INSERT INTO Pedido_delivery(id_pedido,dni_cliente,dni_repartidor,"
                "direccion,distrito,hora_entrega,referencia,hora_salida,costo_delivery,estado_delivery)"
                " VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)", delivery_r, page_size=BATCH)
            execute_batch(cur,
                "INSERT INTO Pedido_plataforma(id_pedido,nombre_plataforma,comision_plataforma,"
                "estado_externo,id_plataforma_pedido,nombre_alias,direccion)"
                " VALUES(%s,%s,%s,%s,%s,%s,%s)", plataforma_r, page_size=BATCH)
            execute_batch(cur,
                "INSERT INTO Detalle_pedido(id_detalle_pedido,id_pedido,id_producto,"
                "id_promocion,cantidad,precio_unitario)"
                " VALUES(%s,%s,%s,%s,%s,%s)", detalle_r, page_size=BATCH)
            execute_batch(cur,
                "INSERT INTO Detalle_topping(id_detalle_topping,id_detalle_pedido,id_pedido,"
                "id_topping,cantidad,precio_unitario_topping)"
                " VALUES(%s,%s,%s,%s,%s,%s)", det_top_r, page_size=BATCH)
            execute_batch(cur,
                "INSERT INTO Movimiento_puntos(id_movimiento,id_puntos,puntos_gastados,"
                "fecha,descripcion,id_pago_fk)"
                " VALUES(%s,%s,%s,%s,%s,%s)", movimiento_r, page_size=BATCH)

            pagos_r.clear(); boletas_r.clear(); facturas_r.clear()
            pedidos_r.clear()
            presencial_r.clear(); delivery_r.clear(); plataforma_r.clear()
            detalle_r.clear(); det_top_r.clear(); movimiento_r.clear()
            print(f"listo ({time_module.time()-t1:.1f}s)")

    # flush final
    print("    Flush final...", end=" ", flush=True)
    tf = time_module.time()
    for rows, sql in [
        (pagos_r,
         "INSERT INTO Pago(id_pago,id_puntos,fecha_emision,metodo_pago,monto) VALUES(%s,%s,%s,%s,%s)"),
        (boletas_r,
         "INSERT INTO Boleta(id_pago) VALUES(%s)"),
        (facturas_r,
         "INSERT INTO Factura(id_pago,ruc,razon_social) VALUES(%s,%s,%s)"),
        (pedidos_r,
         "INSERT INTO Pedido(id_pedido,id_local,estado_pedido,hora,fecha,total_pago,id_pago_fk) VALUES(%s,%s,%s,%s,%s,%s,%s)"),
        (presencial_r,
         "INSERT INTO Pedido_presencial(id_pedido,dni_cliente,numero_turno) VALUES(%s,%s,%s)"),
        (delivery_r,
         "INSERT INTO Pedido_delivery(id_pedido,dni_cliente,dni_repartidor,direccion,distrito,hora_entrega,referencia,hora_salida,costo_delivery,estado_delivery) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"),
        (plataforma_r,
         "INSERT INTO Pedido_plataforma(id_pedido,nombre_plataforma,comision_plataforma,estado_externo,id_plataforma_pedido,nombre_alias,direccion) VALUES(%s,%s,%s,%s,%s,%s,%s)"),
        (detalle_r,
         "INSERT INTO Detalle_pedido(id_detalle_pedido,id_pedido,id_producto,id_promocion,cantidad,precio_unitario) VALUES(%s,%s,%s,%s,%s,%s)"),
        (det_top_r,
         "INSERT INTO Detalle_topping(id_detalle_topping,id_detalle_pedido,id_pedido,id_topping,cantidad,precio_unitario_topping) VALUES(%s,%s,%s,%s,%s,%s)"),
        (movimiento_r,
         "INSERT INTO Movimiento_puntos(id_movimiento,id_puntos,puntos_gastados,fecha,descripcion,id_pago_fk) VALUES(%s,%s,%s,%s,%s,%s)"),
    ]:
        if rows:
            execute_batch(cur, sql, rows, page_size=BATCH)
    print(f"listo ({time_module.time()-tf:.1f}s)")
    print(f"  Cadena completa, listo ({time_module.time()-t0:.1f}s total)")


def main():
    parser = argparse.ArgumentParser(description="Mr. Miga - simulador de datos")
    parser.add_argument("--scale", type=int, default=1000,
                        choices=[1000, 10000, 100000, 1000000],
                        help="Escala de pedidos: 1000 | 10000 | 100000 | 1000000")
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    random.seed(args.seed)
    n    = args.scale
    fast = (n == 1_000_000)   # modo determinista = igual que SQL 1M

    global BATCH
    if   n == 1_000:   BATCH = 500
    elif n == 10_000:  BATCH = 1000
    elif n == 100_000: BATCH = 2000
    else:              BATCH = 5000

    print(f"\nMr. Miga - escala {n:,} pedidos (seed={args.seed})")
    print(f"Modo: {'determinista (rapido)' if fast else 'aleatorio'}, batch size: {BATCH}\n")

    t_total = time_module.time()
    conn = psycopg2.connect(**DB_CONFIG)

    # Acelerar: desactivar autocommit y usar una transacción grande
    conn.autocommit = False
    cur = conn.cursor()

    # Mismo hint que los SQL originales
    cur.execute("SET LOCAL synchronous_commit = OFF")
    cur.execute("SET LOCAL work_mem = '256MB'" if n < 1_000_000 else "SET LOCAL work_mem = '1GB'")

    try:
        print("[1/5] Tablas fijas...")
        step_tablas_fijas(cur)
        conn.commit()

        print(f"\n[2/5] Personas, clientes, empleados...")
        step_persona(cur, n, fast)
        n_clientes = step_clientes(cur, n)
        emp_ini, emp_fin = step_empleados(cur, n, fast)
        conn.commit()

        print(f"\n[3/5] Repartidores y Planilla...")
        rep_ini, rep_fin = step_repartidores(cur, n, emp_ini, fast)
        if not fast:   # en 1M solo hay repartidores, no planilla adicional
            step_planilla(cur, n, emp_ini, emp_fin, rep_ini, rep_fin)
        conn.commit()

        print(f"\n[4/5] CuentaPuntos...")
        total_puntos = step_cuenta_puntos(cur, n)
        conn.commit()

        print(f"\n[5/5] Cadena de pedidos (Pago/Pedido/Detalle/Topping/Movimientos)...")
        step_cadena_pedidos(cur, n, n_clientes, rep_ini, rep_fin, total_puntos, fast)
        conn.commit()

        print(f"\n[Post] ANALYZE...")
        cur.execute("ANALYZE")
        conn.commit()

        elapsed = time_module.time() - t_total
        print(f"\nCompletado en {elapsed:.1f}s ({elapsed/60:.1f} min)")
        print(f"Pedidos insertados: {n:,}")
        print(f"Detalles (~{n * (1 if fast else 3):,}) + Toppings (~{int(n*1.2):,})\n")

    except Exception as e:
        conn.rollback()
        print(f"\n[ERROR] {e}")
        raise
    finally:
        cur.close()
        conn.close()


if __name__ == "__main__":
    main()