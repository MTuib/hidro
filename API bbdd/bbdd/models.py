from sqlalchemy import (Column, Integer, String, TIMESTAMP, BigInteger, Text, ForeignKey, Table, text)
from sqlalchemy.orm import relationship
from bbdd.database import Base


class Fabricant(Base):
    __tablename__ = "fabricant"
    __table_args__ = {"schema": "fis_disp"}

    id_fabricant = Column(Integer, primary_key=True)
    fabricant = Column(String(128))


class Model(Base):
    __tablename__ = "model"
    __table_args__ = {"schema": "fis_disp"}

    id_model = Column(Integer, primary_key=True)
    model = Column(String(64))
    ruta_doc = Column(String(512))
    ruta_decod = Column(String(512))
    descripcio = Column(Text)
    id_fabricant = Column(Integer, ForeignKey("fis_disp.fabricant.id_fabricant"))


#Model de dades per a l'usuari

class Usuari(Base):
    __tablename__ = "usuari"
    __table_args__ = {"schema": "fis_disp"}

    id_usuari = Column(Integer, primary_key=True)
    nom = Column(String(64), nullable=True)
    password = Column(String(256), nullable=True)
    caducitat = Column(TIMESTAMP(timezone=True), nullable=False)

    projectes = relationship(
        "Projecte",
        secondary="fis_disp.r_projecte_usuari",
        back_populates="usuaris"
    )

    def __repr__(self):
        return f"<Usuari(id={self.id_usuari}, nom='{self.nom}')>"


class Dada(Base):
    __tablename__ = "dada"
    __table_args__ = {"schema": "fis_disp"}

    id_dada = Column(BigInteger, primary_key=True)
    dada = Column(Text, nullable=True)
    tstmp = Column(TIMESTAMP(timezone=True), nullable=True,
                   server_default=text("CURRENT_TIMESTAMP"))
    id_disp = Column(
        Integer,
        ForeignKey("fis_disp.dispositiu.id_disp"),
        nullable=True
    )

    def __repr__(self):
        return f"<Dada(id={self.id_dada}, disp={self.id_disp})>"


class Dispositiu(Base):
    __tablename__ = "dispositiu"
    __table_args__ = {"schema": "fis_disp"}

    id_disp = Column(Integer, primary_key=True)
    nom = Column(String(64), nullable=False)
    num_serie = Column(String(128), unique=True)
    id_model = Column(Integer, ForeignKey("fis_disp.model.id_model"))
    usr = Column(String(64), nullable=False)
    passw = Column(String(64), nullable=False)
    url = Column(Text, nullable=False)

    projectes = relationship(
        "Projecte",
        secondary="fis_disp.r_projecte_dispositiu",
        back_populates="dispositiu"
    )

    def __repr__(self):
        return f"<Dispositiu(id={self.id_disp}, nom='{self.nom}')>"


class Projecte(Base):
    __tablename__ = "projecte"
    __table_args__ = {"schema": "fis_disp"}

    id_proj = Column(Integer, primary_key=True)
    nom = Column(String(256))
    descripcio = Column(Text)

    usuaris = relationship(
        "Usuari",
        secondary="fis_disp.r_projecte_usuari",
        back_populates="projectes"
    )

    dispositiu = relationship(
        "Dispositiu",
        secondary="fis_disp.r_projecte_dispositiu",
        back_populates="projectes"
    )

    def __repr__(self):
        return f"<Projecte(id={self.id_proj}, nom='{self.nom}')>"


R_Projecte_Usuari = Table(
    "r_projecte_usuari",
    Base.metadata,
    Column(
        "id_proj",
        Integer,
        ForeignKey("fis_disp.projecte.id_proj"),
        nullable=True
    ),
    Column(
        "id_usuari",
        Integer,
        ForeignKey("fis_disp.usuari.id_usuari"),
        nullable=True
    ),
    schema="fis_disp"
)

R_Projecte_Dispositiu = Table(
    "r_projecte_dispositiu",
    Base.metadata,
    Column(
        "id_proj",
        Integer,
        ForeignKey("fis_disp.projecte.id_proj"),
        primary_key=True
    ),
    Column(
        "id_disp",
        Integer,
        ForeignKey("fis_disp.dispositiu.id_disp"),
        primary_key=True
    ),
    schema="fis_disp"
)
