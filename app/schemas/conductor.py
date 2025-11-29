from pydantic import BaseModel

class ConductorLogin(BaseModel):
    email: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class EstadoUpdate(BaseModel):
    estado: ConductorEstado

class UbicacionUpdate(BaseModel):
    lat: float
    lng: float
