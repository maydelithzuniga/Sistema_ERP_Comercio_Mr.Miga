-- Restaurante Mr. Miga - Base de Datos I
-- Creacion de tablas del modelo relacional
-- Motor: PostgreSQL
-- Se respeta el orden de dependencias por llaves foraneas

-- Tablas principales

CREATE TABLE Persona (
    dni VARCHAR(8) PRIMARY KEY,
    genero VARCHAR(1),
    nombre VARCHAR(30),
    apellidos VARCHAR(30),
    fecha_nacimiento DATE,
    celular VARCHAR(9)
);

CREATE TABLE Cliente (
    dni VARCHAR(8) PRIMARY KEY,
    FOREIGN KEY (dni) REFERENCES Persona(dni)
);

CREATE TABLE Empleado (
    dni VARCHAR(8) PRIMARY KEY,
    horario VARCHAR(1),
    dias_descanso VARCHAR(2),
    sueldo NUMERIC(8,2),
    FOREIGN KEY (dni) REFERENCES Persona(dni)
);

CREATE TABLE Local (
    id_local VARCHAR(8) PRIMARY KEY,
    nombre_local VARCHAR(40),
    direccion VARCHAR(40),
    distrito VARCHAR(40),
    aforo INT,
    telefono VARCHAR(7)
);

CREATE TABLE Repartidor (
    dni VARCHAR(8) PRIMARY KEY,
    repartos_completados INT,
    placa_vehiculo VARCHAR(6),
    FOREIGN KEY (dni) REFERENCES Empleado(dni)
);

CREATE TABLE Planilla (
    dni VARCHAR(8) PRIMARY KEY,
    id_local VARCHAR(8),
    area_trabajo VARCHAR(20),
    desde DATE,
    hasta DATE,
    FOREIGN KEY (dni) REFERENCES Empleado(dni),
    FOREIGN KEY (id_local) REFERENCES Local(id_local)
);

-- Fidelizacion, pagos y comprobantes

CREATE TABLE CuentaPuntos (
    id_puntos VARCHAR(8) PRIMARY KEY,
    puntos INT,
    fecha DATE,
    dni_cliente VARCHAR(8),
    FOREIGN KEY (dni_cliente) REFERENCES Cliente(dni)
);

CREATE TABLE Pago (
    id_pago INT PRIMARY KEY,
    id_puntos VARCHAR(8),
    fecha_emision DATE,
    metodo_pago VARCHAR(20),
    monto NUMERIC(10,2),
    FOREIGN KEY (id_puntos) REFERENCES CuentaPuntos(id_puntos)
);

CREATE TABLE Movimiento_puntos (
    id_movimiento VARCHAR(8) PRIMARY KEY,
    id_puntos VARCHAR(8),
    puntos_gastados INT,
    fecha DATE,
    descripcion VARCHAR(50),
    id_pago INT,
    FOREIGN KEY (id_puntos) REFERENCES CuentaPuntos(id_puntos),
    FOREIGN KEY (id_pago) REFERENCES Pago(id_pago)
);

CREATE TABLE Boleta (
    id_pago INT PRIMARY KEY,
    FOREIGN KEY (id_pago) REFERENCES Pago(id_pago)
);

CREATE TABLE Factura (
    id_pago INT PRIMARY KEY,
    ruc VARCHAR(11),
    razon_social VARCHAR(20),
    FOREIGN KEY (id_pago) REFERENCES Pago(id_pago)
);

-- Pedidos y sus modalidades

CREATE TABLE Pedido (
    id_pedido VARCHAR(8) PRIMARY KEY,
    id_local VARCHAR(8),
    estado_pedido VARCHAR(20),
    hora TIME,
    fecha DATE,
    total_pago NUMERIC(10,2),
    id_pago INT,
    FOREIGN KEY (id_local) REFERENCES Local(id_local),
    FOREIGN KEY (id_pago) REFERENCES Pago(id_pago)
);

CREATE TABLE Pedido_plataforma (
    id_pedido VARCHAR(8) PRIMARY KEY,
    nombre_plataforma VARCHAR(20),
    comision_plataforma INT,
    estado_externo VARCHAR(20),
    id_plataforma_pedido VARCHAR(20),
    nombre_alias VARCHAR(20),
    direccion VARCHAR(20),
    FOREIGN KEY (id_pedido) REFERENCES Pedido(id_pedido)
);

CREATE TABLE Pedido_delivery (
    id_pedido VARCHAR(8) PRIMARY KEY,
    dni_cliente VARCHAR(8),
    dni_repartidor VARCHAR(8),
    direccion VARCHAR(20),
    distrito VARCHAR(20),
    hora_entrega TIME,
    referencia VARCHAR(20),
    hora_salida TIME,
    costo_delivery NUMERIC(8,2),
    estado_delivery VARCHAR(20),
    FOREIGN KEY (id_pedido) REFERENCES Pedido(id_pedido),
    FOREIGN KEY (dni_cliente) REFERENCES Cliente(dni),
    FOREIGN KEY (dni_repartidor) REFERENCES Repartidor(dni)
);

CREATE TABLE Pedido_presencial (
    id_pedido VARCHAR(8) PRIMARY KEY,
    dni_cliente VARCHAR(8),
    numero_turno INT,
    FOREIGN KEY (id_pedido) REFERENCES Pedido(id_pedido),
    FOREIGN KEY (dni_cliente) REFERENCES Cliente(dni)
);

-- Productos, promociones, toppings e ingredientes

CREATE TABLE Producto (
    id_producto VARCHAR(8) PRIMARY KEY,
    nombre VARCHAR(20),
    fecha_p DATE,
    hora_p TIME,
    descripcion VARCHAR(20),
    categoria VARCHAR(20),
    precio_venta NUMERIC(8,2),
    estado VARCHAR(20)
);

CREATE TABLE Promocion (
    id_promocion VARCHAR(8) PRIMARY KEY,
    nombre_promocion VARCHAR(20),
    tipo_promocion VARCHAR(20),
    valor NUMERIC(5,2),
    fecha_inicio DATE,
    fecha_fin DATE
);

CREATE TABLE Incluye (
    id_producto VARCHAR(8),
    id_promocion VARCHAR(8),
    PRIMARY KEY (id_producto, id_promocion),
    FOREIGN KEY (id_producto) REFERENCES Producto(id_producto),
    FOREIGN KEY (id_promocion) REFERENCES Promocion(id_promocion)
);

CREATE TABLE Detalle_pedido (
    id_detalle_pedido VARCHAR(8) PRIMARY KEY,
    id_pedido VARCHAR(8),
    id_producto VARCHAR(8),
    id_promocion VARCHAR(8),
    cantidad INT,
    precio_unitario NUMERIC(8,2),
    FOREIGN KEY (id_pedido) REFERENCES Pedido(id_pedido),
    FOREIGN KEY (id_producto) REFERENCES Producto(id_producto),
    FOREIGN KEY (id_promocion) REFERENCES Promocion(id_promocion)
);

CREATE TABLE Topping (
    id_topping VARCHAR(8) PRIMARY KEY,
    nombre VARCHAR(20),
    precio NUMERIC(8,2)
);

CREATE TABLE Detalle_topping (
    id_detalle_topping VARCHAR(8) PRIMARY KEY,
    id_detalle_pedido VARCHAR(8),
    id_pedido VARCHAR(8),
    id_topping VARCHAR(8),
    cantidad NUMERIC(8,2),
    precio_unitario_topping NUMERIC(8,2),
    FOREIGN KEY (id_detalle_pedido) REFERENCES Detalle_pedido(id_detalle_pedido),
    FOREIGN KEY (id_pedido) REFERENCES Pedido(id_pedido),
    FOREIGN KEY (id_topping) REFERENCES Topping(id_topping)
);

CREATE TABLE Ingrediente (
    nombre VARCHAR(20) PRIMARY KEY,
    precio_compra NUMERIC(8,2),
    cantidad_stock INT
);

CREATE TABLE Usa (
    nombre_ingrediente VARCHAR(20),
    id_producto VARCHAR(8),
    PRIMARY KEY (nombre_ingrediente, id_producto),
    FOREIGN KEY (nombre_ingrediente) REFERENCES Ingrediente(nombre),
    FOREIGN KEY (id_producto) REFERENCES Producto(id_producto)
);
