 CREATE DATABASE bd_iotiblab;
  \c bd_iotiblab;

 CREATE SCHEMA fis_disp;
 CREATE SCHEMA audit;
 CREATE SCHEMA bsd;

CREATE TABLE fis_disp.Fabricant(
    id_fabricant SERIAL PRIMARY KEY,
    fabricant VARCHAR(128)
);

CREATE TABLE fis_disp.Model(
    id_model SERIAL PRIMARY KEY, 
    model VARCHAR(64), 
    ruta_doc VARCHAR(512), 
    ruta_decod VARCHAR(512), 
    descripcio TEXT,
    id_fabricant INTEGER, 

    CONSTRAINT fk_fabricant FOREIGN KEY (id_fabricant) REFERENCES fis_disp.Fabricant (id_fabricant) 
);

CREATE TABLE fis_disp.Dispositiu(
    id_disp SERIAL PRIMARY KEY,
    nom varchar(64) NOT NULL, 
    num_serie varchar(128) UNIQUE,
    id_model INTEGER,
    usr varchar(64) NOT NULL, 
    passw varchar(64) NOT NULL, 
    url text NOT NULL, 

    CONSTRAINT fk_model FOREIGN KEY (id_model) REFERENCES fis_disp.Model (id_model) 
);

CREATE TABLE fis_disp.AppKey(
    id_appKey SERIAL PRIMARY KEY,
    appKey VARCHAR(128), 
    tstmp TIMESTAMP with time zone DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE fis_disp.Tipus_direccio_disp(
    tipus VARCHAR(16) PRIMARY KEY
);


CREATE TABLE fis_disp.Direccio_disp(
    id_direccio_disp SERIAL PRIMARY KEY,
    direccio VARCHAR(128),
    id_disp INTEGER,
    tipus VARCHAR (16), 
    MQTT BOOLEAN NOT NULL DEFAULT FALSE, 
    CONSTRAINT fk_disp FOREIGN KEY (id_disp) REFERENCES fis_disp.Dispositiu (id_disp),
    CONSTRAINT fk_tipus_direccio_disp FOREIGN KEY (tipus) REFERENCES fis_disp.Tipus_direccio_disp (tipus) 
);

CREATE TABLE fis_disp.Dada(
    id_dada BIGSERIAL PRIMARY KEY, 
    dada TEXT, 
    tstmp TIMESTAMP with time zone DEFAULT CURRENT_TIMESTAMP,
    id_disp INTEGER, 

    CONSTRAINT fk_disp FOREIGN KEY (id_disp) REFERENCES fis_disp.Dispositiu (id_disp)
);

CREATE TABLE fis_disp.Tipus(
    id_tipus REGTYPE PRIMARY KEY
);

CREATE TABLE fis_disp.Unitat(
    id_unitat SERIAL PRIMARY KEY, 
    nom VARCHAR (32), 
    id_tipus REGTYPE, 

    CONSTRAINT fk_tipus FOREIGN KEY (id_tipus) REFERENCES fis_disp.Tipus (id_tipus)
);

CREATE TABLE fis_disp.Mesura( 
    id_mesura SERIAL PRIMARY KEY,
    nom VARCHAR(32),
    id_unitat INTEGER,

    CONSTRAINT fk_unitat FOREIGN KEY (id_unitat) REFERENCES fis_disp.Unitat (id_unitat)
);

CREATE TABLE fis_disp.Sensor(
    id_sensor SERIAL PRIMARY KEY,
    nom VARCHAR(32),
    descripcio TEXT,
    id_mesura INTEGER,

    CONSTRAINT fk_mesura FOREIGN KEY (id_mesura) REFERENCES fis_disp.Mesura (id_mesura) 
);

CREATE TABLE fis_disp.Accio(
    accio VARCHAR (32) PRIMARY KEY,
    descripcio TEXT
);

CREATE TABLE fis_disp.Zona(
    nom VARCHAR (128) PRIMARY KEY 
);

CREATE TABLE fis_disp.Estacio(
    id_estacio SERIAL PRIMARY KEY,
    nom VARCHAR (64),
    latitud DOUBLE PRECISION,
    longitud DOUBLE PRECISION,
    nom_zona VARCHAR(128),

    CONSTRAINT fk_nom_zona FOREIGN KEY (nom) REFERENCES fis_disp.Zona (nom)
);

CREATE TABLE fis_disp.Projecte(
    id_proj SERIAL PRIMARY KEY,
    nom VARCHAR (256),
    descripcio TEXT
);


CREATE TABLE fis_disp.Usuari(
   id_usuari SERIAL PRIMARY KEY,
    nom VARCHAR (64),   
    password VARCHAR (256),
    caducitat TIMESTAMP with time zone NOT NULL
);

CREATE TABLE fis_disp.Rol(
    rol VARCHAR (64) PRIMARY KEY,
    tstmp TIMESTAMP with time zone DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE fis_disp.Organitzacio(
    organitzacio VARCHAR (64) PRIMARY KEY
);


CREATE TABLE fis_disp.R_Projecte_Sensor(
    id_proj INTEGER,
    id_sensor INTEGER,

    PRIMARY KEY (id_proj, id_sensor),
    CONSTRAINT fk_proj FOREIGN KEY (id_proj) REFERENCES fis_disp.Projecte (id_proj),
    CONSTRAINT fk_sensor FOREIGN KEY (id_sensor) REFERENCES fis_disp.Sensor (id_sensor) 
);

CREATE TABLE fis_disp.R_Projecte_Estacio(
    id_proj INTEGER, 
    id_estacio INTEGER,

    PRIMARY KEY (id_proj, id_estacio),
    CONSTRAINT fk_proj FOREIGN KEY (id_proj) REFERENCES fis_disp.Projecte (id_proj),
    CONSTRAINT fk_estacio FOREIGN KEY (id_estacio) REFERENCES fis_disp.Estacio (id_estacio)
);

CREATE TABLE fis_disp.R_Projecte_Dispositiu(
    id_proj INTEGER, 
    id_disp INTEGER, 

    PRIMARY KEY (id_proj, id_disp),
    CONSTRAINT fk_proj FOREIGN KEY (id_proj) REFERENCES fis_disp.Projecte (id_proj),
    CONSTRAINT fk_disp FOREIGN KEY (id_disp) REFERENCES fis_disp.Dispositiu (id_disp)
);

CREATE TABLE fis_disp.R_Dispositiu_AppKey(
    id_AppKey INTEGER, 
    id_disp INTEGER, 

    PRIMARY KEY (id_disp, id_AppKey),
    CONSTRAINT fk_disp FOREIGN KEY (id_disp) REFERENCES fis_disp.Dispositiu (id_disp),
    CONSTRAINT fk_appKey FOREIGN KEY (id_AppKey) REFERENCES fis_disp.AppKey (id_AppKey)
);

CREATE TABLE fis_disp.R_Dispositiu_Usuari(
    id_r_disp_usuari SERIAL PRIMARY KEY, 
    id_disp INTEGER, 
    id_usuari INTEGER, 
    id_accio VARCHAR (32),
    tstmp TIMESTAMP with time zone NOT NULL DEFAULT CURRENT_TIMESTAMP, 

    CONSTRAINT fk_disp FOREIGN KEY (id_disp) REFERENCES fis_disp.Dispositiu (id_disp),
    CONSTRAINT fk_usuari FOREIGN KEY (id_usuari) REFERENCES fis_disp.Usuari (id_usuari),
    CONSTRAINT fk_accio FOREIGN KEY (id_accio) REFERENCES fis_disp.Accio (accio)
);

CREATE TABLE fis_disp.R_Direccio_disp_Tipus_direccio_disp(
    tipus VARCHAR (16), 
    id_direccio_disp INTEGER, 

    PRIMARY KEY (tipus, id_direccio_disp),
    CONSTRAINT fk_tipus FOREIGN KEY (tipus) REFERENCES fis_disp.Tipus_direccio_disp (tipus),
    CONSTRAINT fk_direccio FOREIGN KEY (id_direccio_disp) REFERENCES fis_disp.Direccio_disp (id_direccio_disp)
);

CREATE TABLE fis_disp.R_Dispositiu_Estacio(
    id_disp INTEGER, 
    id_estacio INTEGER,
    tstmp TIMESTAMP with time zone NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_disp FOREIGN KEY (id_disp) REFERENCES fis_disp.Dispositiu (id_disp) ,
    CONSTRAINT fk_estacio FOREIGN KEY (id_estacio) REFERENCES fis_disp.Estacio (id_estacio)
);

CREATE TABLE fis_disp.R_Dispositiu_Sensor(
    id_disp INTEGER,
    id_sensor INTEGER,

    CONSTRAINT fk_disp FOREIGN KEY (id_disp) REFERENCES fis_disp.Dispositiu (id_disp),
    CONSTRAINT fk_sensor FOREIGN KEY (id_sensor) REFERENCES fis_disp.Sensor (id_sensor)
);

CREATE TABLE fis_disp.R_Projecte_Usuari(
    id_proj INTEGER, 
    id_usuari INTEGER, 

    CONSTRAINT fk_proj FOREIGN KEY (id_proj) REFERENCES fis_disp.Projecte (id_proj),
    CONSTRAINT fk_usuari FOREIGN KEY (id_usuari) REFERENCES fis_disp.Usuari (id_usuari) 
);

CREATE TABLE fis_disp.R_Acces_ProjecteUsuari(
    id_acces_projecteusuari SERIAL PRIMARY KEY,
    id_proj INTEGER,
    id_usuari INTEGER,
    tstmp TIMESTAMP with time zone NOT NULL DEFAULT CURRENT_TIMESTAMP, 

    CONSTRAINT fk_proj FOREIGN KEY (id_proj) REFERENCES fis_disp.Projecte (id_proj),
    CONSTRAINT fk_usuari FOREIGN KEY (id_usuari) REFERENCES fis_disp.Usuari (id_usuari) 
);
    
CREATE TABLE fis_disp.R_Usuari_Organitzacio(
    id_usuari INTEGER, 
    id_organitzacio VARCHAR (64), 

    PRIMARY KEY (id_usuari, id_organitzacio),
    CONSTRAINT fk_usuari FOREIGN KEY (id_usuari) REFERENCES fis_disp.Usuari (id_usuari) , 
    CONSTRAINT fk_organitzacion FOREIGN KEY (id_organitzacio) REFERENCES fis_disp.Organitzacio (organitzacio)
);

CREATE TABLE fis_disp.R_Rol_UsuariOrganitzacio(
    id_rol_usuariorganitzacio SERIAL PRIMARY KEY,
    id_usuari INTEGER,
    id_organitzacio VARCHAR(64),
    rol VARCHAR(64),

    CONSTRAINT fk_usuari FOREIGN KEY (id_usuari) REFERENCES fis_disp.Usuari (id_usuari) , 
    CONSTRAINT fk_organitzacion FOREIGN KEY (id_organitzacio) REFERENCES fis_disp.Organitzacio (organitzacio),
    CONSTRAINT fk_rol FOREIGN KEY (rol) REFERENCES fis_disp.Rol (rol)
);

CREATE TABLE bsd.Tipus_disp(
    id_tipus_disp SERIAL PRIMARY KEY,
    icona TEXT,
    id_mesura INTEGER,
    id_sensor INTEGER,
    CONSTRAINT fk_sensor FOREIGN KEY (id_sensor) REFERENCES fis_disp.Sensor (id_sensor)
);

CREATE TABLE bsd.Localitzacio(
    id_localitzacio SERIAL PRIMARY KEY, 
    latitud_camara_visor DOUBLE PRECISION,
    longitud_camara_visor DOUBLE PRECISION, 
    altura_camara_visor DOUBLE PRECISION,
    heading_camara_visor DOUBLE PRECISION,
    pitch_camara_visor DOUBLE PRECISION,
    nom_zona VARCHAR (128),

    CONSTRAINT fk_zona FOREIGN KEY (nom_zona) REFERENCES fis_disp.Zona (nom)
);

CREATE TABLE audit.Historic_audit(
    id_audit BIGSERIAL PRIMARY KEY,
    nom_schema VARCHAR (64),
    nom_taula VARCHAR (64),
    nom_usuari VARCHAR (64),
    accio_timestamp TIMESTAMP with time zone not null DEFAULT CURRENT_TIMESTAMP, 
    accio CHAR NOT NULL check (audit.Historic_audit.accio in ('I','D','U')),
    dada_original JSONB,
    nova_dada JSONB,
    consulta text
);

