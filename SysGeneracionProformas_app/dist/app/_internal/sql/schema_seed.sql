CREATE SCHEMA IF NOT EXISTS `sistemaproforma` DEFAULT CHARACTER SET utf8 ;
USE `sistemaproforma` ;

CREATE TABLE IF NOT EXISTS `sistemaproforma`.`Empresa` (
  `RUC` VARCHAR(11) NOT NULL,
  `Raz_Soc` TEXT(50) NOT NULL,
  `FAX` VARCHAR(15) NULL,
  PRIMARY KEY (`RUC`))
ENGINE = InnoDB;

CREATE TABLE IF NOT EXISTS `sistemaproforma`.`Direccion_Empresa` (
  `RUC_Empresa` VARCHAR(11) NOT NULL,
  `Ciudad` TEXT(25) NOT NULL,
  `Calle` TEXT(25) NOT NULL,
  `Distrito` TEXT(25) NOT NULL,
  PRIMARY KEY (`RUC_Empresa`),
  INDEX `fk_Direccion_Empresa_Empresa_idx` (`RUC_Empresa` ASC) VISIBLE,
  CONSTRAINT `fk_Direccion_Empresa_Empresa`
    FOREIGN KEY (`RUC_Empresa`)
    REFERENCES `sistemaproforma`.`Empresa` (`RUC`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;

CREATE TABLE IF NOT EXISTS `sistemaproforma`.`Telefono_Empresa` (
  `RUC_Empresa` VARCHAR(11) NOT NULL,
  `Telefono` VARCHAR(15) NOT NULL,
  PRIMARY KEY (`RUC_Empresa`),
  INDEX `fk_Telefono_Empresa_Empresa1_idx` (`RUC_Empresa` ASC) VISIBLE,
  CONSTRAINT `fk_Telefono_Empresa_Empresa1`
    FOREIGN KEY (`RUC_Empresa`)
    REFERENCES `sistemaproforma`.`Empresa` (`RUC`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;

CREATE TABLE IF NOT EXISTS `sistemaproforma`.`Correo_Empresa` (
  `RUC_Empresa` VARCHAR(11) NOT NULL,
  `Correo` VARCHAR(50) NOT NULL,
  PRIMARY KEY (`RUC_Empresa`),
  INDEX `fk_Correo_Empresa_Empresa1_idx` (`RUC_Empresa` ASC) VISIBLE,
  CONSTRAINT `fk_Correo_Empresa_Empresa1`
    FOREIGN KEY (`RUC_Empresa`)
    REFERENCES `sistemaproforma`.`Empresa` (`RUC`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;

CREATE TABLE IF NOT EXISTS `sistemaproforma`.`Empleado` (
  `Codigo` CHAR(5) NOT NULL,
  `Nombre` TEXT(50) NOT NULL,
  PRIMARY KEY (`Codigo`))
ENGINE = InnoDB;

CREATE TABLE IF NOT EXISTS `sistemaproforma`.`Proveedor` (
  `RUC` VARCHAR(11) NOT NULL,
  `Direccion` TEXT(50) NULL,
  `Raz_Soc` TEXT(50) NOT NULL,
  PRIMARY KEY (`RUC`))
ENGINE = InnoDB;

CREATE TABLE IF NOT EXISTS `sistemaproforma`.`Orden_Compra` (
  `Nro_Orden` VARCHAR(10) NOT NULL,
  `Per_UM` TEXT(25) NOT NULL,
  `Fecha_Entrega` DATE NOT NULL,
  `Precio_Neto` DECIMAL(10,2) NOT NULL,
  `Item` INT NOT NULL,
  `Cantidad` INT NOT NULL,
  `UM` TEXT(20) NOT NULL,
  `Forma_pago` TEXT(50) NOT NULL,
  `Incoterms_2000` TEXT(100) NULL,
  `Desc_Orden` TEXT(100) NOT NULL,
  `Codigo_Empleado` VARCHAR(5) NOT NULL,
  `RUC_Proveedor` VARCHAR(11) NOT NULL,
  `RUC_Empresa` VARCHAR(11) NOT NULL,
  PRIMARY KEY (`Nro_Orden`),
  INDEX `fk_Orden_Compra_Empresa1_idx` (`RUC_Empresa` ASC) VISIBLE,
  INDEX `fk_Orden_Compra_Empleado1_idx` (`Codigo_Empleado` ASC) VISIBLE,
  INDEX `fk_Orden_Compra_Proveedor1_idx` (`RUC_Proveedor` ASC) VISIBLE,
  CONSTRAINT `fk_Orden_Compra_Empresa1`
    FOREIGN KEY (`RUC_Empresa`)
    REFERENCES `sistemaproforma`.`Empresa` (`RUC`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_Orden_Compra_Empleado1`
    FOREIGN KEY (`Codigo_Empleado`)
    REFERENCES `sistemaproforma`.`Empleado` (`Codigo`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_Orden_Compra_Proveedor1`
    FOREIGN KEY (`RUC_Proveedor`)
    REFERENCES `sistemaproforma`.`Proveedor` (`RUC`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;

CREATE TABLE IF NOT EXISTS `sistemaproforma`.`Contacto_Empleado` (
  `Codigo_Empleado` VARCHAR(5) NOT NULL,
  `Telefono` VARCHAR(15) NOT NULL,
  PRIMARY KEY (`Codigo_Empleado`),
  INDEX `fk_Contacto_Empleado_Empleado1_idx` (`Codigo_Empleado` ASC) VISIBLE,
  CONSTRAINT `fk_Contacto_Empleado_Empleado1`
    FOREIGN KEY (`Codigo_Empleado`)
    REFERENCES `sistemaproforma`.`Empleado` (`Codigo`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;

CREATE TABLE IF NOT EXISTS `sistemaproforma`.`Email_Proveedor` (
  `RUC_Proveedor` VARCHAR(11) NOT NULL,
  `Email` VARCHAR(50) NULL,
  PRIMARY KEY (`RUC_Proveedor`),
  INDEX `fk_Email_Proveedor_Proveedor1_idx` (`RUC_Proveedor` ASC) VISIBLE,
  CONSTRAINT `fk_Email_Proveedor_Proveedor1`
    FOREIGN KEY (`RUC_Proveedor`)
    REFERENCES `sistemaproforma`.`Proveedor` (`RUC`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;

CREATE TABLE IF NOT EXISTS `sistemaproforma`.`Telefono_Proveedor` (
  `RUC_Proveedor` VARCHAR(11) NOT NULL,
  `Telefono` VARCHAR(15) NULL,
  PRIMARY KEY (`RUC_Proveedor`),
  INDEX `fk_Telefono_Proveedor_Proveedor1_idx` (`RUC_Proveedor` ASC) VISIBLE,
  CONSTRAINT `fk_Telefono_Proveedor_Proveedor1`
    FOREIGN KEY (`RUC_Proveedor`)
    REFERENCES `sistemaproforma`.`Proveedor` (`RUC`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;

CREATE TABLE IF NOT EXISTS `sistemaproforma`.`Repuesto` (
  `Nro_Parte` VARCHAR(10) NOT NULL,
  `Cantidad` INT NOT NULL,
  `Descripcion` TEXT(100) NOT NULL,
  `Marca` TEXT(50) NOT NULL,
  `Status` TEXT(10) NOT NULL,
  `Precio_Unitario` DECIMAL(10,2) NOT NULL,
  PRIMARY KEY (`Nro_Parte`))
ENGINE = InnoDB;

CREATE TABLE IF NOT EXISTS `sistemaproforma`.`Proforma` (
  `Nro_Proforma` VARCHAR(10) NOT NULL,
  `Item` INT NOT NULL,
  `Cantidad` INT NOT NULL,
  `Fecha` DATE NOT NULL,
  `Peso` DECIMAL(8,3) NOT NULL,
  `Nro_Parte` VARCHAR(10) NOT NULL,
  `Codigo_Empleado` CHAR(5) NOT NULL,
  PRIMARY KEY (`Nro_Proforma`),
  INDEX `fk_Proforma_Repuesto1_idx` (`Nro_Parte` ASC) VISIBLE,
  INDEX `fk_Proforma_Empleado1_idx` (`Codigo_Empleado` ASC) VISIBLE,
  CONSTRAINT `fk_Proforma_Repuesto1`
    FOREIGN KEY (`Nro_Parte`)
    REFERENCES `sistemaproforma`.`Repuesto` (`Nro_Parte`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_Proforma_Empleado1`
    FOREIGN KEY (`Codigo_Empleado`)
    REFERENCES `sistemaproforma`.`Empleado` (`Codigo`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;

INSERT IGNORE INTO empleado (codigo, nombre)
VALUES 
('E0001', 'Jean Yauri'),
('E0002', 'Juan Perez'),
('E0003', 'Luis Garcia'),
('E0004', 'Maria Rivas'),
('E0005', 'Joseph Aguilar'),
('E0006', 'Luis Meza'),
('E0007', 'María González'),
('E0008', 'Carlos Mendoza'),
('E0009', 'Ana Torres'),
('E0010', 'Luis Fernández'),
('E0011', 'Elena Rojas'),
('E0012', 'Miguel Huamán'),
('E0013', 'Sofía Castillo'),
('E0014', 'Jorge Vargas'),
('E0015', 'Lucía Ramos'),
('E0016', 'David Quispe'),
('E0017', 'Carmen Flores'),
('E0018', 'Pedro Sánchez'),
('E0019', 'Julia Romero'),
('E0020', 'Joaquin Velarde');

INSERT IGNORE INTO contacto_empleado (Codigo_Empleado, Telefono)
VALUES 
('E0001', '51945733680'),
('E0002', '51999999999'),
('E0003', '51953910281'),
('E0004', '51842019612'),
('E0005', '51555948167'),
('E0006', '51481950123'),
('E0007', '51987456123'),
('E0008', '51982345678'),
('E0009', '51956789012'),
('E0010', '51943210987'),
('E0011', '51932165498'),
('E0012', '51965432109'),
('E0013', '51978901234'),
('E0014', '51923456789'),
('E0015', '51912345670'),
('E0016', '51987654321'),
('E0017', '51945612378'),
('E0018', '51932198765'),
('E0019', '51965478912'),
('E0020', '51998765432');

INSERT IGNORE INTO proveedor (RUC, Direccion, Raz_Soc)
VALUES 
('20123456789', 'Av. Industrias 320 - Ate','Importadora Andina S.A.C.'),
('20456789012', 'Jr. Maquinarias 145 - Cercado','Soluciones Mecánicas E.I.R.L.'),
('20500000011', 'Av. Nicolás Arriola 2042 - San Luis','Gamatractor S.A.C.'),
('20500000029', 'Jr. Bélgica 1684 - La Victoria','Tractopartes S.A.C.'),
('20500000037', 'Mz. M Lt. 15, Urb. El Pinar - Comas','Katzer Perú S.A.C.'),
('20500000045', 'Panamericana Sur Km 29.5 - Lurín','Masa Equipos Industriales S.A.C.'),
('20500000052', 'Av. Próceres de la Independencia 1050 - San Juan de Lurigancho','Distribuidora de Repuestos y Filtros E.I.R.L.'),
('20500000060', 'Av. Alfredo Mendiola 5500 - Los Olivos','Headmark Maquinarias S.A.C.'),
('20500000079', 'Av. Separadora Industrial 125 - Ate','MR Maquinarias S.A.C.'),
('20500000087', 'Av. Argentina 3450 - Callao','Servimaq M&C del Perú S.A.C.'),
('20500000095', 'Av. República de Panamá 3550 - Surquillo','CKR Perú S.A.C.'),
('20500000109', 'Av. Evitamiento 740 - El Agustino','CF Parts and Machinery S.A.C.'),
('20500000117', 'Av. Universitaria 1500 - San Miguel','Maquinarias y Repuestos S.A.C.'),
('20500000125', 'Av. Colonial 4200 - Bellavista','Autoamerican Repuestos E.I.R.L.'),
('20500000133', 'Av. Túpac Amaru 2100 - Independencia','Solumec Soluciones Mecánicas S.A.C.'),
('20500000141', 'Av. Faucett 3100 - Callao','Brimec Soluciones Mecánicas E.I.R.L.'),
('20500000150', 'Av. La Molina 500 - La Molina','Diproagro Repuestos S.A.C.'),
('20500000168', 'Av. Guardia Civil 850 - Chorrillos','Maquinarias y Servicios Industriales S.A.C.'),
('20500000176', 'Av. Javier Prado Este 4200 - La Molina','Repmac Maquinaria Pesada S.A.C.'),
('20500000184', 'Av. Tomás Valle 1200 - San Martín de Porres','Tecno Repuestos Industriales E.I.R.L.');

INSERT IGNORE INTO email_proveedor (RUC_Proveedor, Email)
VALUES 
('20123456789', 'contacto@intandina.com.pe'),
('20456789012', 'contacto@solumec.com.pe'),
('20500000011', 'ventas@gamatractor.com'),
('20500000029', 'ventas@tractopartes.com.pe'),
('20500000037', 'info@katzerperu.com'),
('20500000045', 'contacto@masaequipos.com.pe'),
('20500000052', 'ventas@distrepuestosyfiltros.com.pe'),
('20500000060', 'info@headmarkmaquinarias.com.pe'),
('20500000079', 'contacto@mrmaquinarias.com.pe'),
('20500000087', 'ventas@servimaqmc.com.pe'),
('20500000095', 'contacto@ckrperu.com'),
('20500000109', 'ventas@cfparts.com.pe'),
('20500000117', 'info@maquinariasyrepuestos.com.pe'),
('20500000125', 'contacto@autoamericanrepuestos.com.pe'),
('20500000133', 'ventas@solumec.com.pe'),
('20500000141', 'info@brimecsoluciones.com.pe'),
('20500000150', 'ventas@diproagrorepuestos.com.pe'),
('20500000168', 'contacto@msindustriales.com.pe'),
('20500000176', 'ventas@repmac.com.pe'),
('20500000184', 'contacto@tecnorepuestos.com.pe');

INSERT IGNORE INTO telefono_proveedor (RUC_Proveedor, Telefono)
VALUES 
('20123456789', '(01)3820541'),
('20456789012', '(01)4429185'),
('20500000011', '(01)3456789'),
('20500000029', '(01)3367890'),
('20500000037', '(01)3478901'),
('20500000045', '(01)3589012'),
('20500000052', '(01)3690123'),
('20500000060', '(01)3791234'),
('20500000079', '(01)3892345'),
('20500000087', '(01)3993456'),
('20500000095', '(01)3104567'),
('20500000109', '(01)3205678'),
('20500000117', '(01)3306789'),
('20500000125', '(01)3407890'),
('20500000133', '(01)3508901'),
('20500000141', '(01)3609012'),
('20500000150', '(01)3700123'),
('20500000168', '(01)3801234'),
('20500000176', '(01)3902345'),
('20500000184', '(01)3003456');

INSERT IGNORE INTO repuesto (Nro_Parte, Cantidad, Descripcion, Marca, Status, Precio_Unitario)
VALUES 
('4857395', 2, 'BAR-SQUARE 4857395', 'CAT', 'Entrega', 1507.3),
('4910250', 2, 'ANCHOR AS 4910250', 'CAT', 'Almacen', 2898.75),
('4832039', 4, 'BAR-STOP 4832039', 'CAT', 'Almacen', 168.1),
('4795962', 4, 'STOP-BAR 4795962', 'CAT', 'Almacen', 200.49),
('4832040', 2, 'BAR-STOP 4832040', 'CAT', 'En camino', 74.65),
('5305628', 2, 'BAR 5305628', 'CAT', 'En camino', 93.56),
('4804881', 2, 'PLATE 4804881', 'CAT', 'En camino', 492.15),
('4667352', 2, 'CYL GP-HYD 4667352', 'CAT', 'Entrega', 1489.21),
('5312086', 8, 'BOLT-PC 5312086', 'CAT 2', 'Entrega', 1.11),
('3B4611', 4, 'Cotter Pin 3B4611', 'CAT', 'Almacen', 0.80),
('5303939', 2, 'STOP-ARM 5303939', 'CAT', 'En camino', 561.46),
('5306855', 2, 'BAR-ROUND 5306855', 'CAT', 'En camino', 503.65),
('4703870', 2, 'PLATE AS 4703870', 'CAT', 'En camino', 1503.24),
('8T8919', 2, 'BOLT 8T8919', 'NOT ORIGINAL', 'Almacen', 1.40),
('1D5117', 2, 'NUT 1D5117', 'NOT ORIGINAL', 'Almacen', 0.39),
('4703873', 2, 'SHAFT 4703873', 'CAT', 'En camino', 316.26),
('1D5119', 2, 'NUT 1D5119', 'NOT ORIGINAL', 'Almacen', 1.02),
('4703874', 2, 'SPRING 4703874', 'CAT', 'En camino', 149.23),
('4703875', 2, 'BUSHING-HEXA 4703875', 'CAT', 'En camino', 69.63),
('4703876', 2, 'SPACER 4703876', 'CAT', 'En camino', 39.43);

INSERT IGNORE INTO empresa (RUC, Raz_Soc, FAX)
VALUES 
('20302241598', 'KOMATSU-MITSUI', '(51-1)615-8410'),
('20170072465', 'Cerro Verde', '(51-1)215-6910'),
('20100147514', 'Southern Peru Copper Corporation', '(51-1)217-1348'),
('20330262428', 'Anta mina', '(51-1)217-3695'),
('20100028698', 'Ferreyros S.A.', '(51-1)626-4001'),
('20102078781', 'San Martin Contratistas Generales S.A.', '(51-1)450-1991'),
('20100082391', 'COSAPI S.A.', '(51-1)211-3501'),
('20137291313', 'Minera Yanacocha S.R.L.', '(51-1)512-1101'),
('20538428524', 'Minera Las Bambas S.A.', '(51-1)418-2701'),
('20114915026', 'Compañía Minera Antapaccay S.A.', '(51-84)582-301'),
('20100136741', 'Minsur S.A.', '(51-1)215-8331'),
('20511165181', 'Hudbay Peru S.A.C.', '(51-1)612-2901'),
('20383045267', 'Volcan Compañía Minera S.A.A.', '(51-1)416-7001'),
('20100142989', 'Shougang Hierro Peru S.A.A.', '(51-1)714-5201'),
('20100017572', 'Sociedad Minera El Brocal S.A.A.', '(51-1)215-9201'),
('20508972734', 'Marcobre S.A.C.', '(51-1)215-9601'),
('20100137390', 'Unión Andina de Cementos S.A.A. - UNACEM S.A.A.', '(51-1)411-0001'),
('20312372895', 'Yura S.A.', '(51-54)495-061'),
('20100079501', 'Compañía de Minas Buenaventura S.A.A.', '(51-1)419-2501'),
('20332600592', 'Aenza S.A.A.', '(51-1)213-6565');

INSERT IGNORE INTO direccion_empresa (RUC_Empresa, Ciudad, Calle, Distrito)
VALUES 
('20302241598', 'Arequipa', 'Vía de Evitamiento Km. 1', 'Arequipa'),
('20170072465', 'Arequipa', 'Jacinto Ibáñez Nro. 315', 'Uchumayo'),
('20100147514', 'Lima', 'Av.Caminos del Inca N° 171', 'Santiago de Surco '),
('20330262428', 'Lima', 'Av.El Derby N°055, Torre 1', 'Santiago de Surco'),
('20100028698', 'Lima', 'Jr. Cristóbal de Peralta Norte 820', 'Santiago de Surco'),
('20102078781', 'Lima', 'Jr. Morro Solar 1010, Urb. Juan Pablo de Monterrico', 'Santiago de Surco'),
('20100082391', 'Lima', 'Av. República de Colombia 791, Urb. Chacarilla de Santa Cruz', 'San Isidro'),
('20137291313', 'Lima', 'Av. La Paz 1049, Int. 401', 'Miraflores'),
('20538428524', 'Lima', 'Av. El Derby 055, Torre 3, Piso 9', 'Santiago de Surco'),
('20114915026', 'Cusco', 'Campamento Minero Tintaya s/n', 'Espinar'),
('20100136741', 'Lima', 'Jr. Giovanni Battista Lorenzo 149, Int. 501A', 'San Borja'),
('20511165181', 'Lima', 'Av. Jorge Chávez 235, Dpto. 701', 'Miraflores'),
('20383045267', 'Lima', 'Av. Manuel Olguín 375, Piso 7, Urb. Los Granados', 'Santiago de Surco'),
('20100142989', 'Lima', 'Av. República de Chile 262', 'Jesús María'),
('20100017572', 'Lima', 'Calle Las Begonias 415, Piso 19', 'San Isidro'),
('20508972734', 'Lima', 'Jr. Giovanni Battista Lorenzo 149, Int. 301', 'San Borja'),
('20100137390', 'Lima', 'Av. Carlos Villarán 508', 'La Victoria'),
('20312372895', 'Arequipa', 'Carretera a Yura Km 26', 'Yura'),
('20100079501', 'Lima', 'Calle Las Begonias 415, Piso 19', 'San Isidro'),
('20332600592', 'Lima', 'Av. Paseo de la República 4675', 'Surquillo');

INSERT IGNORE INTO telefono_empresa (RUC_Empresa, Telefono)
VALUES 
('20302241598', '(01)615 8400'),
('20170072465', '(054)381 515'),
('20100147514', '(01)512 0440'),
('20330262428', '(01)217 3000'),
('20100028698', '(01)626 4000'),
('20102078781', '(01)450 1990'),
('20100082391', '(01)211 3500'),
('20137291313', '(01)512 1100'),
('20538428524', '(01)418 2700'),
('20114915026', '(084)582 300'),
('20100136741', '(01)215 8330'),
('20511165181', '(01)612 2900'),
('20383045267', '(01)416 7000'),
('20100142989', '(01)714 5200'),
('20100017572', '(01)215 9200'),
('20508972734', '(01)215 9600'),
('20100137390', '(01)411 0000'),
('20312372895', '(054)495 060'),
('20100079501', '(01)419 2500'),
('20332600592', '(01)213 6565');

INSERT IGNORE INTO correo_empresa (RUC_Empresa, Correo)
VALUES 
('20302241598', 'contacto.komatsu@kmmp.com.pe'),
('20170072465', 'smcv@fmi.com'),
('20100147514', 'spcc@southernperu.com.pe'),
('20330262428', 'comunicaciones@antamina.com'),
('20100028698', 'contacto@ferreyros.com.pe'),
('20102078781', 'contacto@sanmartin.com'),
('20100082391', 'informes@cosapi.com.pe'),
('20137291313', 'contacto@yanacocha.com'),
('20538428524', 'proveedores@lasbambas.com'),
('20114915026', 'contacto@antapaccay.com'),
('20100136741', 'aacc@minsur.com'),
('20511165181', 'info.peru@hudbay.com'),
('20383045267', 'lcotrina@volcan.com.pe'),
('20100142989', 'Wanglingen@shp.pe'),
('20100017572', 'contacto@elbrocal.com.pe'),
('20508972734', 'informes@marcobre.com.pe'),
('20100137390', 'informes@unacem.com.pe'),
('20312372895', 'contactos_yura@yura.com'),
('20100079501', 'sebastian.valencia@buenaventura.pe'),
('20332600592', 'contacto@aenza.com.pe');

INSERT IGNORE INTO proforma (Nro_Proforma, Item, Cantidad, Fecha, Peso, Nro_Parte, Codigo_Empleado)
VALUES
('OC-0242', 01, 1, '2021-06-22', 700, '4795962', 'E0001'),
('OC-0243', 02, 1, '2021-06-22', 1224, '4910250', 'E0002'),
('OC-0244',03,2,'2021-06-23',800,'4910250','E0001'),
('OC-0245',04,1,'2021-06-23',950,'4857395','E0003'),
('OC-0246',05,3,'2021-06-24',1500,'4857395','E0003'),
('OC-0247',06,2,'2021-06-24',900,'4832039','E0004'),
('OC-0248',07,1,'2021-06-25',1100,'4832039','E0004'),
('OC-0249',08,1,'2021-06-25',950,'5305628','E0005'),
('OC-0250',09,4,'2021-06-26',1200,'4804881','E0006'),
('OC-0251',10,2,'2021-06-26',1400,'4667352','E0007'),
('OC-0252',11,3,'2021-06-27',1450,'4667352','E0007'),
('OC-0253',12,10,'2021-06-27',60,'5312086','E0008'),
('OC-0254',13,20,'2021-06-28',40,'3B4611','E0008'),
('OC-0255',14,2,'2021-06-28',1150,'5303939','E0009'),
('OC-0256',15,2,'2021-06-29',1050,'5306855','E0010'),
('OC-0257',16,1,'2021-06-29',1300,'4703870','E0010'),
('OC-0258',17,30,'2021-06-30',45,'8T8919','E0011'),
('OC-0259',18,40,'2021-06-30',35,'1D5117','E0011'),
('OC-0260',19,2,'2021-07-01',900,'4703873','E0012'),
('OC-0261',20,3,'2021-07-01',950,'4703873','E0001');

INSERT IGNORE INTO orden_compra (Nro_Orden, Per_UM, Fecha_Entrega, Precio_Neto, Item, Cantidad, UM, Forma_pago, Incoterms_2000, Desc_Orden, Codigo_Empleado, RUC_Proveedor, RUC_Empresa)
VALUES 
('4519381029','Per 1','2024-05-10', 74.65, 01, 1, 'lb', '30 días después', '','STOP-BAR 4795962','E0001','20123456789','20302241598'),
('4519381030','Per 1','2024-10-15', 2898.75, 02, 1, 'lb', 'Pago contra entrega', 'EXW','ANCHOR AS 4910250','E0002','20123456789','20302241598'),
('4519381031','Per 1','2024-03-20',1507.3,03,2,'lb','Pago inmediato','FOB','BAR-SQUARE 4857395','E0001','20123456789','20302241598'),
('4519381032','Per 1','2024-03-28',1.11,04,8,'lb','30 días después','','BOLT-PC 5312086','E0003','20123456789','20302241598'),
('4519381033','Per 1','2024-04-10',200.49,05,4,'lb','Pago contra entrega','EXW','STOP-BAR 4795962','E0002','20500000011','20170072465'),
('4519381034','Per 1','2024-04-25',1489.21,06,1,'lb','30 días después','CIF','CYL GP-HYD 4667352','E0004','20500000029','20538428524'),
('4519381035','Per 1','2024-05-05',2898.75,07,1,'lb','Pago inmediato','','ANCHOR AS 4910250','E0005','20500000029','20100147514'),
('4519381036','Per 1','2024-05-18',1.40,08,10,'lb','Pago contra entrega','FOB','BOLT 8T8919','E0003','20500000037','20383045267'),
('4519381037','Per 1','2024-06-02',492.15,09,2,'lb','30 días después','','PLATE 4804881','E0006','20500000045','20312372895'),
('4519381038','Per 1','2024-06-15',503.65,10,2,'lb','Pago inmediato','EXW','BAR-ROUND 5306855','E0001','20500000011','20100147514'),
('4519381039','Per 1','2024-07-01',149.23,11,3,'lb','Pago contra entrega','CIF','SPRING 4703874','E0007','20500000052','20100079501'),
('4519381040','Per 1','2024-07-20',316.26,12,2,'lb','30 días después','','SHAFT 4703873','E0002','20500000060','20508972734'),
('4519381041','Per 1','2024-08-05',0.80,13,20,'lb','Pago inmediato','FOB','Cotter Pin 3B4611','E0005','20500000079','20170072465'),
('4519381042','Per 1','2024-08-18',1503.24,14,1,'lb','Pago contra entrega','EXW','PLATE AS 4703870','E0008','20500000087','20114915026'),
('4519381043','Per 1','2024-09-01',69.63,15,4,'lb','30 días después','','BUSHING-HEXA 4703875','E0003','20500000095','20538428524'),
('4519381044','Per 1','2024-09-14',0.39,16,50,'lb','Pago inmediato','CIF','NUT 1D5117','E0004','20500000109','20100137390'),
('4519381045','Per 1','2024-09-28',168.1,17,3,'lb','Pago contra entrega','','BAR-STOP 4832039','E0006','20500000117','20312372895'),
('4519381046','Per 1','2024-10-10',39.43,18,10,'lb','30 días después','FOB','SPACER 4703876','E0002','20500000125','20511165181'),
('4519381047','Per 1','2024-10-25',2898.75,19,1,'lb','Pago inmediato','EXW','ANCHOR AS 4910250','E0001','20500000133','20137291313'),
('4519381048','Per 1','2024-11-05',93.56,20,5,'lb','Pago contra entrega','CIF','BAR 5305628','E0003','20500000141','20302241598');