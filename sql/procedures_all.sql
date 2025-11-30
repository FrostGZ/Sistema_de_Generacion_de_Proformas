USE `sistemaproforma`;
DELIMITER //

DROP PROCEDURE IF EXISTS sp_Agregar_Proveedor //
CREATE PROCEDURE sp_Agregar_Proveedor(
    IN p_RUC VARCHAR(11),
    IN p_Raz_Soc VARCHAR(50),
    IN p_Direccion VARCHAR(50),
    IN p_Telefono VARCHAR(15),
    IN p_Email VARCHAR(50)
)
BEGIN
    INSERT INTO Proveedor (RUC, Raz_Soc, Direccion)
    VALUES (p_RUC, p_Raz_Soc, p_Direccion);

    INSERT INTO Telefono_Proveedor (RUC_Proveedor, Telefono)
    VALUES (p_RUC, p_Telefono);

    INSERT INTO Email_Proveedor (RUC_Proveedor, Email)
    VALUES (p_RUC, p_Email);
END //

DROP PROCEDURE IF EXISTS sp_Agregar_Empleado //
CREATE PROCEDURE sp_Agregar_Empleado(
    IN p_Codigo CHAR(5),
    IN p_Nombre VARCHAR(50),
    IN p_Telefono VARCHAR(15)
)
BEGIN
    INSERT INTO Empleado (Codigo, Nombre)
    VALUES (p_Codigo, p_Nombre);

    INSERT INTO Contacto_Empleado (Codigo_Empleado, Telefono)
    VALUES (p_Codigo, p_Telefono);
END //

DROP PROCEDURE IF EXISTS sp_Agregar_Repuesto //
CREATE PROCEDURE sp_Agregar_Repuesto(
    IN p_Nro_Parte VARCHAR(10),
    IN p_Descripcion VARCHAR(100),
    IN p_Marca VARCHAR(50),
    IN p_Status VARCHAR(10),
    IN p_Precio DECIMAL(10,2),
    IN p_Cantidad INT
)
BEGIN
    INSERT INTO Repuesto (Nro_Parte, Descripcion, Marca, Status, Precio_Unitario, Cantidad)
    VALUES (p_Nro_Parte, p_Descripcion, p_Marca, p_Status, p_Precio, p_Cantidad);
END //

DROP PROCEDURE IF EXISTS sp_Actualizar_Stock //
CREATE PROCEDURE sp_Actualizar_Stock(
    IN p_Nro_Parte VARCHAR(10),
    IN p_Cantidad INT,
    IN p_Operacion VARCHAR(10)
)
BEGIN
    IF UPPER(p_Operacion) = 'SUMA' THEN
        UPDATE Repuesto SET Cantidad = Cantidad + p_Cantidad WHERE Nro_Parte = p_Nro_Parte;
    ELSEIF UPPER(p_Operacion) = 'RESTA' THEN
        UPDATE Repuesto SET Cantidad = Cantidad - p_Cantidad WHERE Nro_Parte = p_Nro_Parte;
    END IF;
END //

DROP PROCEDURE IF EXISTS sp_Registrar_OrdenCompra //
CREATE PROCEDURE sp_Registrar_OrdenCompra(
    IN p_Nro_Orden VARCHAR(10),
    IN p_Per_UM VARCHAR(25),
    IN p_Fecha_Entrega DATE,
    IN p_Precio_Neto DECIMAL(10,2),
    IN p_Item INT,
    IN p_Cantidad INT,
    IN p_UM VARCHAR(20),
    IN p_FormaPago VARCHAR(50),
    IN p_Incoterms VARCHAR(100),
    IN p_Desc_Orden VARCHAR(100),
    IN p_Codigo_Empleado VARCHAR(5),
    IN p_RUC_Proveedor VARCHAR(11),
    IN p_RUC_Empresa VARCHAR(11),
    IN p_Nro_Parte VARCHAR(10)
)
BEGIN
    INSERT INTO Orden_Compra (Nro_Orden, Per_UM, Fecha_Entrega, Precio_Neto, Item, Cantidad, UM, Forma_pago,
                              Incoterms_2000, Desc_Orden, Codigo_Empleado, RUC_Proveedor, RUC_Empresa)
    VALUES (p_Nro_Orden, p_Per_UM, p_Fecha_Entrega, p_Precio_Neto, p_Item, p_Cantidad, p_UM, p_FormaPago,
            p_Incoterms, p_Desc_Orden, p_Codigo_Empleado, p_RUC_Proveedor, p_RUC_Empresa);

    CALL sp_Actualizar_Stock(p_Nro_Parte, p_Cantidad, 'SUMA');
END //

DROP PROCEDURE IF EXISTS sp_Actualizar_OrdenCompra //
CREATE PROCEDURE sp_Actualizar_OrdenCompra(
    IN p_Nro_Orden VARCHAR(10),
    IN p_Per_UM VARCHAR(25),
    IN p_Fecha_Entrega DATE,
    IN p_Precio_Neto DECIMAL(10,2),
    IN p_Item INT,
    IN p_NuevaCantidad INT,
    IN p_UM VARCHAR(20),
    IN p_FormaPago VARCHAR(50),
    IN p_Incoterms VARCHAR(100),
    IN p_Desc_Orden VARCHAR(100),
    IN p_Codigo_Empleado VARCHAR(5),
    IN p_RUC_Proveedor VARCHAR(11),
    IN p_RUC_Empresa VARCHAR(11),
    IN p_Nro_Parte VARCHAR(10)
)
BEGIN
    DECLARE v_CantidadActual INT;

    START TRANSACTION;

    SELECT Cantidad INTO v_CantidadActual
      FROM Orden_Compra
     WHERE Nro_Orden = p_Nro_Orden
     FOR UPDATE;

    IF v_CantidadActual IS NULL THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'La orden no existe';
    END IF;

    UPDATE Orden_Compra
       SET Per_UM = p_Per_UM,
           Fecha_Entrega = p_Fecha_Entrega,
           Precio_Neto = p_Precio_Neto,
           Item = p_Item,
           Cantidad = p_NuevaCantidad,
           UM = p_UM,
           Forma_pago = p_FormaPago,
           Incoterms_2000 = p_Incoterms,
           Desc_Orden = p_Desc_Orden,
           Codigo_Empleado = p_Codigo_Empleado,
           RUC_Proveedor = p_RUC_Proveedor,
           RUC_Empresa = p_RUC_Empresa
     WHERE Nro_Orden = p_Nro_Orden;

    IF p_NuevaCantidad > v_CantidadActual THEN
        CALL sp_Actualizar_Stock(p_Nro_Parte, p_NuevaCantidad - v_CantidadActual, 'SUMA');
    ELSEIF p_NuevaCantidad < v_CantidadActual THEN
        CALL sp_Actualizar_Stock(p_Nro_Parte, v_CantidadActual - p_NuevaCantidad, 'RESTA');
    END IF;

    COMMIT;
END //

DROP PROCEDURE IF EXISTS sp_Eliminar_OrdenCompra //
CREATE PROCEDURE sp_Eliminar_OrdenCompra(
    IN p_Nro_Orden VARCHAR(10),
    IN p_Nro_Parte VARCHAR(10)
)
BEGIN
    DECLARE v_Q INT;

    START TRANSACTION;

    SELECT Cantidad INTO v_Q
      FROM Orden_Compra
     WHERE Nro_Orden = p_Nro_Orden
     FOR UPDATE;

    IF v_Q IS NULL THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'La orden no existe';
    END IF;

    CALL sp_Actualizar_Stock(p_Nro_Parte, v_Q, 'RESTA');

    DELETE FROM Orden_Compra WHERE Nro_Orden = p_Nro_Orden;

    COMMIT;
END //

DROP PROCEDURE IF EXISTS sp_Actualizar_Empleado //
CREATE PROCEDURE sp_Actualizar_Empleado(
    IN p_Codigo CHAR(5),
    IN p_Nombre VARCHAR(50),
    IN p_Telefono VARCHAR(15)
)
BEGIN
    UPDATE Empleado SET Nombre = p_Nombre WHERE Codigo = p_Codigo;
    UPDATE Contacto_Empleado SET Telefono = p_Telefono WHERE Codigo_Empleado = p_Codigo;
END //

DROP PROCEDURE IF EXISTS sp_Eliminar_Empleado //
CREATE PROCEDURE sp_Eliminar_Empleado(
    IN p_Codigo CHAR(5)
)
BEGIN
    DELETE FROM Contacto_Empleado WHERE Codigo_Empleado = p_Codigo;
    DELETE FROM Empleado WHERE Codigo = p_Codigo;
END //

DROP PROCEDURE IF EXISTS sp_Actualizar_Repuesto //
CREATE PROCEDURE sp_Actualizar_Repuesto(
    IN p_Nro_Parte VARCHAR(10),
    IN p_Descripcion VARCHAR(100),
    IN p_Marca VARCHAR(50),
    IN p_Status VARCHAR(10),
    IN p_Precio DECIMAL(10,2),
    IN p_Cantidad INT
)
BEGIN
    UPDATE Repuesto
    SET Descripcion = p_Descripcion,
        Marca = p_Marca,
        Status = p_Status,
        Precio_Unitario = p_Precio,
        Cantidad = p_Cantidad
    WHERE Nro_Parte = p_Nro_Parte;
END //

DROP PROCEDURE IF EXISTS sp_Eliminar_Repuesto //
CREATE PROCEDURE sp_Eliminar_Repuesto(
    IN p_Nro_Parte VARCHAR(10)
)
BEGIN
    DELETE FROM Repuesto WHERE Nro_Parte = p_Nro_Parte;
END //

DROP PROCEDURE IF EXISTS sp_Actualizar_Proveedor //
CREATE PROCEDURE sp_Actualizar_Proveedor(
    IN p_RUC VARCHAR(11),
    IN p_Raz_Soc VARCHAR(50),
    IN p_Direccion VARCHAR(50),
    IN p_Telefono VARCHAR(15),
    IN p_Email VARCHAR(50)
)
BEGIN
    UPDATE Proveedor
    SET Raz_Soc = p_Raz_Soc,
        Direccion = p_Direccion
    WHERE RUC = p_RUC;

    UPDATE Telefono_Proveedor
    SET Telefono = p_Telefono
    WHERE RUC_Proveedor = p_RUC;

    UPDATE Email_Proveedor
    SET Email = p_Email
    WHERE RUC_Proveedor = p_RUC;
END //

DROP PROCEDURE IF EXISTS sp_Eliminar_Proveedor //
CREATE PROCEDURE sp_Eliminar_Proveedor(
    IN p_RUC VARCHAR(11)
)
BEGIN
    IF EXISTS(SELECT 1 FROM Orden_Compra WHERE RUC_Proveedor = p_RUC) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'No se puede eliminar: proveedor con órdenes de compra asociadas';
    END IF;

    DELETE FROM Email_Proveedor WHERE RUC_Proveedor = p_RUC;
    DELETE FROM Telefono_Proveedor WHERE RUC_Proveedor = p_RUC;
    DELETE FROM Proveedor WHERE RUC = p_RUC;
END //

DROP PROCEDURE IF EXISTS sp_Agregar_Empresa //
CREATE PROCEDURE sp_Agregar_Empresa(
    IN p_RUC VARCHAR(11),
    IN p_Raz_Soc VARCHAR(50),
    IN p_FAX VARCHAR(15),
    IN p_Ciudad VARCHAR(25),
    IN p_Calle VARCHAR(25),
    IN p_Distrito VARCHAR(25),
    IN p_Telefono VARCHAR(15),
    IN p_Correo VARCHAR(50)
)
BEGIN
    START TRANSACTION;

    IF EXISTS(SELECT 1 FROM Empresa WHERE RUC = p_RUC) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'La empresa ya existe';
    END IF;

    INSERT INTO Empresa (RUC, Raz_Soc, FAX)
    VALUES (p_RUC, p_Raz_Soc, p_FAX);

    INSERT INTO Direccion_Empresa (RUC_Empresa, Ciudad, Calle, Distrito)
    VALUES (p_RUC, p_Ciudad, p_Calle, p_Distrito);

    INSERT INTO Telefono_Empresa (RUC_Empresa, Telefono)
    VALUES (p_RUC, p_Telefono);

    INSERT INTO Correo_Empresa (RUC_Empresa, Correo)
    VALUES (p_RUC, p_Correo);

    COMMIT;
END //

DROP PROCEDURE IF EXISTS sp_Actualizar_Empresa //
CREATE PROCEDURE sp_Actualizar_Empresa(
    IN p_RUC VARCHAR(11),
    IN p_Raz_Soc VARCHAR(50),
    IN p_FAX VARCHAR(15),
    IN p_Ciudad VARCHAR(25),
    IN p_Calle VARCHAR(25),
    IN p_Distrito VARCHAR(25),
    IN p_Telefono VARCHAR(15),
    IN p_Correo VARCHAR(50)
)
BEGIN
    START TRANSACTION;

    IF NOT EXISTS(SELECT 1 FROM Empresa WHERE RUC = p_RUC) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'La empresa no existe';
    END IF;

    UPDATE Empresa
      SET Raz_Soc = p_Raz_Soc,
          FAX     = p_FAX
    WHERE RUC = p_RUC;

    IF EXISTS(SELECT 1 FROM Direccion_Empresa WHERE RUC_Empresa = p_RUC) THEN
        UPDATE Direccion_Empresa
           SET Ciudad = p_Ciudad, Calle = p_Calle, Distrito = p_Distrito
         WHERE RUC_Empresa = p_RUC;
    ELSE
        INSERT INTO Direccion_Empresa (RUC_Empresa, Ciudad, Calle, Distrito)
        VALUES (p_RUC, p_Ciudad, p_Calle, p_Distrito);
    END IF;

    IF EXISTS(SELECT 1 FROM Telefono_Empresa WHERE RUC_Empresa = p_RUC) THEN
        UPDATE Telefono_Empresa SET Telefono = p_Telefono WHERE RUC_Empresa = p_RUC;
    ELSE
        INSERT INTO Telefono_Empresa (RUC_Empresa, Telefono) VALUES (p_RUC, p_Telefono);
    END IF;

    IF EXISTS(SELECT 1 FROM Correo_Empresa WHERE RUC_Empresa = p_RUC) THEN
        UPDATE Correo_Empresa SET Correo = p_Correo WHERE RUC_Empresa = p_RUC;
    ELSE
        INSERT INTO Correo_Empresa (RUC_Empresa, Correo) VALUES (p_RUC, p_Correo);
    END IF;

    COMMIT;
END //

DROP PROCEDURE IF EXISTS sp_Eliminar_Empresa //
CREATE PROCEDURE sp_Eliminar_Empresa(
    IN p_RUC VARCHAR(11)
)
BEGIN
    START TRANSACTION;

    IF EXISTS(SELECT 1 FROM Orden_Compra WHERE RUC_Empresa = p_RUC) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'No se puede eliminar: la empresa tiene órdenes de compra asociadas';
    END IF;

    DELETE FROM Correo_Empresa  WHERE RUC_Empresa = p_RUC;
    DELETE FROM Telefono_Empresa WHERE RUC_Empresa = p_RUC;
    DELETE FROM Direccion_Empresa WHERE RUC_Empresa = p_RUC;
    DELETE FROM Empresa WHERE RUC = p_RUC;

    COMMIT;
END //

DROP PROCEDURE IF EXISTS sp_Agregar_Proforma //
CREATE PROCEDURE sp_Agregar_Proforma(
    IN p_Nro_Proforma VARCHAR(10),
    IN p_Item INT,
    IN p_Cantidad INT,
    IN p_Fecha DATE,
    IN p_Peso DECIMAL(8,3),
    IN p_Nro_Parte VARCHAR(10),
    IN p_Codigo_Empleado CHAR(5)
)
BEGIN
    START TRANSACTION;

    IF EXISTS(SELECT 1 FROM Proforma WHERE Nro_Proforma = p_Nro_Proforma) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'La proforma ya existe';
    END IF;

    IF NOT EXISTS(SELECT 1 FROM Empleado WHERE Codigo = p_Codigo_Empleado) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Empleado no válido';
    END IF;

    IF NOT EXISTS(SELECT 1 FROM Repuesto WHERE Nro_Parte = p_Nro_Parte) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Repuesto no válido';
    END IF;

    INSERT INTO Proforma (Nro_Proforma, Item, Cantidad, Fecha, Peso, Nro_Parte, Codigo_Empleado)
    VALUES (p_Nro_Proforma, p_Item, p_Cantidad, p_Fecha, p_Peso, p_Nro_Parte, p_Codigo_Empleado);

    COMMIT;
END //

DROP PROCEDURE IF EXISTS sp_Actualizar_Proforma //
CREATE PROCEDURE sp_Actualizar_Proforma(
    IN p_Nro_Proforma VARCHAR(10),
    IN p_Item INT,
    IN p_Cantidad INT,
    IN p_Fecha DATE,
    IN p_Peso DECIMAL(8,3),
    IN p_Nro_Parte VARCHAR(10),
    IN p_Codigo_Empleado CHAR(5)
)
BEGIN
    START TRANSACTION;

    IF NOT EXISTS(SELECT 1 FROM Proforma WHERE Nro_Proforma = p_Nro_Proforma) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'La proforma no existe';
    END IF;

    IF NOT EXISTS(SELECT 1 FROM Empleado WHERE Codigo = p_Codigo_Empleado) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Empleado no válido';
    END IF;

    IF NOT EXISTS(SELECT 1 FROM Repuesto WHERE Nro_Parte = p_Nro_Parte) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Repuesto no válido';
    END IF;

    UPDATE Proforma
       SET Item = p_Item,
           Cantidad = p_Cantidad,
           Fecha = p_Fecha,
           Peso = p_Peso,
           Nro_Parte = p_Nro_Parte,
           Codigo_Empleado = p_Codigo_Empleado
     WHERE Nro_Proforma = p_Nro_Proforma;

    COMMIT;
END //

DROP PROCEDURE IF EXISTS sp_Eliminar_Proforma //
CREATE PROCEDURE sp_Eliminar_Proforma(
    IN p_Nro_Proforma VARCHAR(10)
)
BEGIN
    START TRANSACTION;

    IF NOT EXISTS(SELECT 1 FROM Proforma WHERE Nro_Proforma = p_Nro_Proforma) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'La proforma no existe';
    END IF;

    DELETE FROM Proforma WHERE Nro_Proforma = p_Nro_Proforma;

    COMMIT;
END //

DELIMITER ;