Create database ScanLogix;
Use ScanLogix;


CREATE TABLE departamentos (
    id_departamento INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL UNIQUE
);

CREATE TABLE municipios (
    id_municipio INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    id_departamento INT NOT NULL,
    FOREIGN KEY (id_departamento) REFERENCES departamentos(id_departamento)
);

CREATE TABLE tiendas (
    id_tienda INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(150) NOT NULL,
    id_municipio INT NOT NULL,
    FOREIGN KEY (id_municipio) REFERENCES municipios(id_municipio)
);

CREATE TABLE paquetes (
    id_paquete INT AUTO_INCREMENT PRIMARY KEY,
    nombre_cliente VARCHAR(100) NOT NULL,
    nombre_vendedor VARCHAR(100),
    telefono VARCHAR(20),
    email VARCHAR(150),

    id_departamento INT NOT NULL,
    id_municipio INT NOT NULL,
    id_tienda INT NOT NULL,

    precio DECIMAL(10,2) NOT NULL,
    codigo_barras VARCHAR(100) UNIQUE,
    envio VARCHAR(20),
    comision VARCHAR(200),
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (id_departamento) REFERENCES departamentos(id_departamento),
    FOREIGN KEY (id_municipio) REFERENCES municipios(id_municipio),
    FOREIGN KEY (id_tienda) REFERENCES tiendas(id_tienda)
);

