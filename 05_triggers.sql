-- Restaurante Mr. Miga - Base de Datos I
-- Triggers para reforzar reglas de negocio que involucran mas de una
-- tabla y que no se pueden validar solo con PK/FK/CHECK
-- Ejecutar despues de 01_creacion_tablas.sql

-- Trigger 1: un empleado no puede estar en Repartidor y Planilla a la vez
CREATE OR REPLACE FUNCTION fn_valida_exclusividad_empleado()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_TABLE_NAME = 'repartidor' THEN
        IF EXISTS (SELECT 1 FROM Planilla WHERE dni = NEW.dni) THEN
            RAISE EXCEPTION 'El empleado % ya está registrado en Planilla y no puede ser Repartidor', NEW.dni;
        END IF;
    ELSIF TG_TABLE_NAME = 'planilla' THEN
        IF EXISTS (SELECT 1 FROM Repartidor WHERE dni = NEW.dni) THEN
            RAISE EXCEPTION 'El empleado % ya está registrado como Repartidor y no puede estar en Planilla', NEW.dni;
        END IF;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_repartidor_exclusividad
BEFORE INSERT OR UPDATE ON Repartidor
FOR EACH ROW EXECUTE FUNCTION fn_valida_exclusividad_empleado();

CREATE TRIGGER trg_planilla_exclusividad
BEFORE INSERT OR UPDATE ON Planilla
FOR EACH ROW EXECUTE FUNCTION fn_valida_exclusividad_empleado();


-- Trigger 2: un pago no puede tener Boleta y Factura a la vez
CREATE OR REPLACE FUNCTION fn_valida_exclusividad_pago()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_TABLE_NAME = 'boleta' THEN
        IF EXISTS (SELECT 1 FROM Factura WHERE id_pago = NEW.id_pago) THEN
            RAISE EXCEPTION 'El pago % ya tiene una Factura registrada y no puede tener Boleta', NEW.id_pago;
        END IF;
    ELSIF TG_TABLE_NAME = 'factura' THEN
        IF EXISTS (SELECT 1 FROM Boleta WHERE id_pago = NEW.id_pago) THEN
            RAISE EXCEPTION 'El pago % ya tiene una Boleta registrada y no puede tener Factura', NEW.id_pago;
        END IF;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_boleta_exclusividad
BEFORE INSERT OR UPDATE ON Boleta
FOR EACH ROW EXECUTE FUNCTION fn_valida_exclusividad_pago();

CREATE TRIGGER trg_factura_exclusividad
BEFORE INSERT OR UPDATE ON Factura
FOR EACH ROW EXECUTE FUNCTION fn_valida_exclusividad_pago();


-- Trigger 3: un pedido no puede ser presencial, delivery y de plataforma a la vez
CREATE OR REPLACE FUNCTION fn_valida_exclusividad_pedido()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_TABLE_NAME = 'pedido_presencial' THEN
        IF EXISTS (SELECT 1 FROM Pedido_delivery WHERE id_pedido = NEW.id_pedido)
           OR EXISTS (SELECT 1 FROM Pedido_plataforma WHERE id_pedido = NEW.id_pedido) THEN
            RAISE EXCEPTION 'El pedido % ya está registrado en otra modalidad (delivery o plataforma)', NEW.id_pedido;
        END IF;
    ELSIF TG_TABLE_NAME = 'pedido_delivery' THEN
        IF EXISTS (SELECT 1 FROM Pedido_presencial WHERE id_pedido = NEW.id_pedido)
           OR EXISTS (SELECT 1 FROM Pedido_plataforma WHERE id_pedido = NEW.id_pedido) THEN
            RAISE EXCEPTION 'El pedido % ya está registrado en otra modalidad (presencial o plataforma)', NEW.id_pedido;
        END IF;
    ELSIF TG_TABLE_NAME = 'pedido_plataforma' THEN
        IF EXISTS (SELECT 1 FROM Pedido_presencial WHERE id_pedido = NEW.id_pedido)
           OR EXISTS (SELECT 1 FROM Pedido_delivery WHERE id_pedido = NEW.id_pedido) THEN
            RAISE EXCEPTION 'El pedido % ya está registrado en otra modalidad (presencial o delivery)', NEW.id_pedido;
        END IF;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_pedido_presencial_exclusividad
BEFORE INSERT OR UPDATE ON Pedido_presencial
FOR EACH ROW EXECUTE FUNCTION fn_valida_exclusividad_pedido();

CREATE TRIGGER trg_pedido_delivery_exclusividad
BEFORE INSERT OR UPDATE ON Pedido_delivery
FOR EACH ROW EXECUTE FUNCTION fn_valida_exclusividad_pedido();

CREATE TRIGGER trg_pedido_plataforma_exclusividad
BEFORE INSERT OR UPDATE ON Pedido_plataforma
FOR EACH ROW EXECUTE FUNCTION fn_valida_exclusividad_pedido();


-- Trigger 4: acumulacion automatica de puntos por pago (1 punto por sol gastado)
CREATE OR REPLACE FUNCTION fn_acumular_puntos()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.id_puntos IS NOT NULL THEN
        UPDATE CuentaPuntos
        SET puntos = COALESCE(puntos, 0) + FLOOR(NEW.monto)::INT
        WHERE id_puntos = NEW.id_puntos;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_pago_acumula_puntos
AFTER INSERT ON Pago
FOR EACH ROW EXECUTE FUNCTION fn_acumular_puntos();


-- Trigger 5: descuento automatico de stock de ingredientes al vender un producto
CREATE OR REPLACE FUNCTION fn_descontar_stock_ingrediente()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE Ingrediente i
    SET cantidad_stock = i.cantidad_stock - NEW.cantidad
    FROM Usa u
    WHERE u.nombre_ingrediente = i.nombre
      AND u.id_producto = NEW.id_producto;

    IF EXISTS (
        SELECT 1 FROM Ingrediente WHERE cantidad_stock < 0
    ) THEN
        RAISE EXCEPTION 'Stock insuficiente de ingrediente para el producto %', NEW.id_producto;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_detalle_pedido_descuenta_stock
AFTER INSERT ON Detalle_pedido
FOR EACH ROW EXECUTE FUNCTION fn_descontar_stock_ingrediente();
