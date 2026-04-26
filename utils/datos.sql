----- Departamentos ----------

INSERT INTO departamentos (nombre) VALUES
('Ahuachapán'),
('Santa Ana'),
('Sonsonate'),
('La Libertad'),
('Chalatenango'),
('San Salvador'),
('Cuscatlán'),
('La Paz'),
('Cabañas'),
('San Vicente'),
('Usulután'),
('San Miguel'),
('Morazán'),
('La Unión');


----------- Municipios ----------------
-- Ahuachapán
INSERT INTO municipios (nombre, id_departamento) VALUES
('Ahuachapán Centro', 1),
('Ahuachapán Norte', 1),
('Ahuachapán Sur', 1),

-- Santa Ana
('Santa Ana Centro', 2),
('Santa Ana Norte', 2),
('Santa Ana Oeste', 2),

-- Sonsonate
('Sonsonate Centro', 3),
('Sonsonate Este', 3),
('Sonsonate Oeste', 3),

-- La Libertad
('La Libertad Centro', 4),
('La Libertad Costa', 4),
('La Libertad Norte', 4),

-- Chalatenango
('Chalatenango Centro', 5),
('Chalatenango Norte', 5),

-- San Salvador
('San Salvador Centro', 6),
('San Salvador Este', 6),
('San Salvador Norte', 6),
('San Salvador Oeste', 6),

-- Cuscatlán
('Cuscatlán Norte', 7),
('Cuscatlán Sur', 7),

-- La Paz
('La Paz Centro', 8),
('La Paz Este', 8),
('La Paz Oeste', 8),

-- Cabañas
('Cabañas Este', 9),
('Cabañas Oeste', 9),

-- San Vicente
('San Vicente Norte', 10),
('San Vicente Sur', 10),

-- Usulután
('Usulután Norte', 11),
('Usulután Este', 11),
('Usulután Oeste', 11),

-- San Miguel
('San Miguel Centro', 12),
('San Miguel Norte', 12),
('San Miguel Oeste', 12),

-- Morazán
('Morazán Norte', 13),
('Morazán Sur', 13),

-- La Unión
('La Unión Norte', 14),
('La Unión Sur', 14);


--------- Tiendas ---------------
INSERT INTO tiendas (nombre, id_municipio)
SELECT nombre, id_municipio FROM municipios;
