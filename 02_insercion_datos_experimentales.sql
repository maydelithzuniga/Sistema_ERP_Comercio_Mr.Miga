-- Restaurante Mr. Miga - Base de Datos I
-- Carga inicial de datos de prueba (locales, productos, personas, pedidos, pagos)
-- Ejecutar despues de 01_creacion_tablas.sql

-- Locales, productos, toppings e ingredientes

INSERT INTO Local (id_local, nombre_local, direccion, distrito, aforo, telefono)
VALUES
('LOC00001', 'Mr. Miga Barranco', 'Delucchi 364', 'Barranco', 40, '1234567'),
('LOC00002', 'Mr. Miga Jockey Plaza', 'Av. Javier Prado Este 4200', 'Surco', 60, '7654321');

INSERT INTO Producto (id_producto, nombre, fecha_p, hora_p, descripcion, categoria, precio_venta, estado)
VALUES
('PROD0001', 'Hamburguesa', CURRENT_DATE, CURRENT_TIME, 'Clasica', 'Comida', 14.90, 'Disponible'),
('PROD0002', 'Salchipapa', CURRENT_DATE, CURRENT_TIME, 'Clasica', 'Comida', 12.90, 'Disponible'),
('PROD0003', 'Pollo broaster', CURRENT_DATE, CURRENT_TIME, 'Personal', 'Comida', 16.90, 'Disponible'),
('PROD0004', 'Gaseosa', CURRENT_DATE, CURRENT_TIME, 'Bebida', 'Bebida', 4.50, 'Disponible');

INSERT INTO Topping (id_topping, nombre, precio)
VALUES
('TOP00001', 'Queso', 2.00),
('TOP00002', 'Tocino', 3.00),
('TOP00003', 'Huevo', 2.50),
('TOP00004', 'Salsa extra', 1.00);

INSERT INTO Ingrediente (nombre, precio_compra, cantidad_stock)
VALUES
('Pan', 0.80, 500),
('Carne', 4.50, 300),
('Papa', 1.20, 400),
('Pollo', 5.00, 250),
('Queso', 2.00, 150);

-- Personas, clientes y empleados

INSERT INTO Persona (dni, genero, nombre, apellidos, fecha_nacimiento, celular)
VALUES
('70000001', 'M', 'Luis', 'Perez Ramos', '2002-05-10', '987654321'),
('70000002', 'F', 'Maria', 'Lopez Diaz', '2001-08-21', '987654322'),
('70000003', 'M', 'Jose', 'Torres Vega', '1998-03-15', '987654323'),
('70000004', 'F', 'Ana', 'Garcia Ruiz', '1999-11-02', '987654324');

INSERT INTO Cliente (dni)
VALUES
('70000001'),
('70000002');

INSERT INTO Empleado (dni, horario, dias_descanso, sueldo)
VALUES
('70000003', 'M', 'LU', 1500.00),
('70000004', 'T', 'MA', 1600.00);

INSERT INTO Repartidor (dni, repartos_completados, placa_vehiculo)
VALUES
('70000003', 120, 'ABC123');

INSERT INTO Planilla (dni, id_local, area_trabajo, desde, hasta)
VALUES
('70000004', 'LOC00001', 'Caja', '2024-01-01', NULL);

-- Pagos, pedidos y detalles de pedido

INSERT INTO Pago (id_pago, fecha_emision, metodo_pago, monto)
VALUES
(1, CURRENT_DATE, 'Yape', 29.80),
(2, CURRENT_DATE, 'Efectivo', 16.90);

INSERT INTO Pedido (id_pedido, id_local, estado_pedido, hora, fecha, total_pago, id_pago)
VALUES
('PED00001', 'LOC00001', 'Completado', CURRENT_TIME, CURRENT_DATE, 29.80, 1),
('PED00002', 'LOC00002', 'Completado', CURRENT_TIME, CURRENT_DATE, 16.90, 2);

INSERT INTO Pedido_presencial (id_pedido, dni_cliente, numero_turno)
VALUES
('PED00001', '70000001', 1);

INSERT INTO Pedido_delivery (
    id_pedido, dni_cliente, dni_repartidor, direccion, distrito,
    hora_entrega, referencia, hora_salida, costo_delivery, estado_delivery
)
VALUES
('PED00002', '70000002', '70000003', 'Av. Lima 123', 'Surco',
 CURRENT_TIME, 'Casa blanca', CURRENT_TIME, 5.00, 'Entregado');

INSERT INTO Detalle_pedido (
    id_detalle_pedido, id_pedido, id_producto, id_promocion, cantidad, precio_unitario
)
VALUES
('DET00001', 'PED00001', 'PROD0001', NULL, 2, 14.90),
('DET00002', 'PED00002', 'PROD0003', NULL, 1, 16.90);
