from datetime import datetime

from pydantic import BaseModel, ConfigDict


class DispositiuBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_disp: int
    nom: str
    num_serie: str | None = None
    id_model: int | None = None
    usr: str
    passw: str
    url: str


class DispositiuOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_disp: int
    nom: str
    num_serie: str | None
    url: str



class DadaIngesta(BaseModel):
    id_disp: int
    payload: str


class DadaPayload(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_dada: int
    dada: str
    tstmp: datetime
    id_disp: int


class ProjecteBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_proj: int
    nom: str
    descripcio: str | None = None
