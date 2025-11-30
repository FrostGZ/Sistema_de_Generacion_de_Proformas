USE `sistemaproforma`;
DELIMITER //

DROP TRIGGER IF EXISTS trg_AutoCorreoProveedor //
CREATE TRIGGER trg_AutoCorreoProveedor
AFTER INSERT ON Proveedor
FOR EACH ROW
BEGIN
    INSERT INTO Email_Proveedor (RUC_Proveedor, Email)
    VALUES (NEW.RUC, NULL);
END //

DROP TRIGGER IF EXISTS trg_AutoTelefonoProveedor //
CREATE TRIGGER trg_AutoTelefonoProveedor
AFTER INSERT ON Proveedor
FOR EACH ROW
BEGIN
    INSERT INTO Telefono_Proveedor (RUC_Proveedor, Telefono)
    VALUES (NEW.RUC, NULL);
END //

DELIMITER ;