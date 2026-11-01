from sqlalchemy.orm import Session
from bbdd.models import Usuari, Dada, Dispositiu, Projecte, R_Projecte_Usuari, R_Projecte_Dispositiu
from datetime import datetime
from datetime import timezone

#Obtenir un usuari
def get_user_by_name(db: Session, name: str):
    return db.query(Usuari).filter(Usuari.nom == name).first()

#Crear una nova dada
def create_dada(db: Session, *, dada: str, id_disp: int):
    try:
        registre = Dada(
            dada=dada,
            id_disp=id_disp,
            tstmp=datetime.now(timezone.utc)
        )
        db.add(registre)
        db.commit()
        db.refresh(registre)
        return registre
    except Exception as e:
        db.rollback()
        raise e


#Obtenir una dada per ID
def get_dada(db: Session, id_dada: int):
    return db.query(Dada).filter(Dada.id_dada == id_dada).first()

#Obtenir dada per rang de dates i dispositiu
def get_dades(db: Session, id_disp: int, data_inici=None, data_final=None):
    query = db.query(Dada).filter(
        Dada.id_disp == id_disp,
    )

    if data_inici is not None:
        query = query.filter(Dada.tstmp >= data_inici)
    
    if data_final is not None:
        query = query.filter(Dada.tstmp <= data_final)

    return query.all()

#Llistar dades d'un dispositiu
def get_dades_by_dispositiu(db: Session, id_disp: int, limit: int = 40):
    return (
        db.query(Dada)
        .filter(Dada.id_disp == id_disp)
        .order_by(Dada.tstmp.asc())
        .limit(limit)
        .all()
    )


#Cercar dispositiu per nom
def get_dispositiu_by_nom(db: Session, nom: str):
    return db.query(Dispositiu)\
             .filter(Dispositiu.nom == nom)\
             .first()


#Obtenir projectes associats a un usuari
def get_projectes_by_usuari(db: Session, id_usuari: int):
    return (
        db.query(Projecte)
        .join(R_Projecte_Usuari, R_Projecte_Usuari.c.id_proj == Projecte.id_proj)
        .filter(R_Projecte_Usuari.c.id_usuari == id_usuari)
        .all()
    )

#Obtenir dispositius associats a un usuari per projecte
def get_dispositius_by_usuari_projecte(db: Session, id_usuari: int, id_projecte: int):
    return (
        db.query(Dispositiu)
        .join(R_Projecte_Dispositiu, R_Projecte_Dispositiu.c.id_disp == Dispositiu.id_disp)  
        .join(Projecte, Projecte.id_proj == R_Projecte_Dispositiu.c.id_proj) 
        .join(R_Projecte_Usuari, R_Projecte_Usuari.c.id_proj == Projecte.id_proj) 
        .filter(R_Projecte_Usuari.c.id_usuari == id_usuari)  
        .filter(Projecte.id_proj == id_projecte)  
        .all()
    )

