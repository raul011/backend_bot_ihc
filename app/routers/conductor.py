from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from datetime import datetime
from app.models.conductor import Conductor, ConductorEstado
from app.schemas.conductor import EstadoUpdate, UbicacionUpdate
router = APIRouter(prefix="/conductor", tags=["Conductor"])

# 1. Actualizar estado (conectado / desconectado)
@router.put("/{conductor_id}/estado")
def actualizar_estado(conductor_id: int, payload: EstadoUpdate, db: Session = Depends(get_db)):
    conductor = db.query(Conductor).filter(Conductor.id == conductor_id).first()
    if not conductor:
        raise HTTPException(status_code=404, detail="Conductor no encontrado")

    conductor.estado = payload.estado
    db.commit()
    db.refresh(conductor)
    return {"message": f"Estado actualizado a {payload.estado}", "conductor_id": conductor.id}


# 2. Actualizar ubicación (lat/lng)
@router.put("/{conductor_id}/ubicacion")
def actualizar_ubicacion(conductor_id: int, payload: UbicacionUpdate, db: Session = Depends(get_db)):
    conductor = db.query(Conductor).filter(Conductor.id == conductor_id).first()
    if not conductor:
        raise HTTPException(status_code=404, detail="Conductor no encontrado")

    conductor.latitude = payload.lat
    conductor.longitude = payload.lng
    conductor.last_update = datetime.utcnow() 
    db.commit()
    db.refresh(conductor)
    return {
        "message": "Ubicación actualizada",
        "conductor_id": conductor.id,
        "lat": conductor.latitude,
        "lng": conductor.longitude
    }