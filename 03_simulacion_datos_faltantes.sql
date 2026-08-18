-- Restaurante Mr. Miga - Base de Datos I
-- Simula valores nulos en algunos campos (referencia de delivery, alias
-- de cliente en plataforma, celular) para reflejar datos incompletos
-- que llegan de distintas fuentes y plataformas
-- Ejecutar despues de 02_insercion_datos_experimentales.sql

UPDATE Pedido_delivery
SET referencia = NULL
WHERE id_pedido IN (
    SELECT id_pedido
    FROM Pedido_delivery
    ORDER BY random()
    LIMIT 1
);

UPDATE Pedido_plataforma
SET nombre_alias = NULL
WHERE id_pedido IN (
    SELECT id_pedido
    FROM Pedido_plataforma
    ORDER BY random()
    LIMIT 1
);

UPDATE Persona
SET celular = NULL
WHERE dni IN (
    SELECT dni
    FROM Persona
    ORDER BY random()
    LIMIT 1
);
