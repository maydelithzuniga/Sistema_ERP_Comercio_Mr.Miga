-- Restaurante Mr. Miga - Base de Datos I
-- Consultas para la seccion de optimizacion del informe

-- Consulta 1: producto mas vendido (cantidad e ingreso), sin pedidos cancelados
SELECT
    pr.id_producto,
    pr.nombre AS producto,
    SUM(dp.cantidad) AS total_vendido,
    SUM(dp.cantidad * dp.precio_unitario) AS ingreso_generado
FROM Detalle_pedido dp
JOIN Producto pr
    ON dp.id_producto = pr.id_producto
JOIN Pedido pe
    ON dp.id_pedido = pe.id_pedido
WHERE pe.estado_pedido <> 'Cancelado'
GROUP BY pr.id_producto, pr.nombre
ORDER BY total_vendido DESC, ingreso_generado DESC
LIMIT 1;


-- Consulta 2: pedidos presenciales vs virtuales (delivery propio + plataformas)
SELECT
    canal,
    COUNT(*) AS cantidad_pedidos
FROM (
    SELECT 'Presencial' AS canal
    FROM Pedido_presencial

    UNION ALL

    SELECT 'Virtual' AS canal
    FROM Pedido_delivery

    UNION ALL

    SELECT 'Virtual' AS canal
    FROM Pedido_plataforma
) AS canales
GROUP BY canal
ORDER BY cantidad_pedidos DESC;


-- Consulta 3: edad promedio de clientes que piden entre 12pm y 3pm, lunes a viernes
WITH clientes_horario AS (
    SELECT
        pp.dni_cliente,
        pe.fecha,
        pe.hora
    FROM Pedido pe
    JOIN Pedido_presencial pp
        ON pp.id_pedido = pe.id_pedido
    WHERE pe.hora BETWEEN TIME '12:00:00' AND TIME '15:00:00'
      AND EXTRACT(ISODOW FROM pe.fecha) BETWEEN 1 AND 5

    UNION ALL

    SELECT
        pd.dni_cliente,
        pe.fecha,
        pe.hora
    FROM Pedido pe
    JOIN Pedido_delivery pd
        ON pd.id_pedido = pe.id_pedido
    WHERE pe.hora BETWEEN TIME '12:00:00' AND TIME '15:00:00'
      AND EXTRACT(ISODOW FROM pe.fecha) BETWEEN 1 AND 5
)
SELECT
    ROUND(
        AVG(EXTRACT(YEAR FROM AGE(CURRENT_DATE, p.fecha_nacimiento))),
        2
    ) AS edad_promedio
FROM clientes_horario ch
JOIN Persona p
    ON p.dni = ch.dni_cliente;


-- Consulta 4: canal con mayor ingreso total (plataforma descuenta comision)
SELECT
    canal,
    SUM(ingreso) AS ingreso_total
FROM (
    SELECT
        'Presencial' AS canal,
        pe.total_pago AS ingreso
    FROM Pedido pe
    JOIN Pedido_presencial pp
        ON pp.id_pedido = pe.id_pedido

    UNION ALL

    SELECT
        'Delivery propio' AS canal,
        pe.total_pago AS ingreso
    FROM Pedido pe
    JOIN Pedido_delivery pd
        ON pd.id_pedido = pe.id_pedido

    UNION ALL

    SELECT
        'Plataforma' AS canal,
        pe.total_pago - pp.comision_plataforma AS ingreso
    FROM Pedido pe
    JOIN Pedido_plataforma pp
        ON pp.id_pedido = pe.id_pedido
) AS ingresos
GROUP BY canal
ORDER BY ingreso_total DESC
LIMIT 1;
