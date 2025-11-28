from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import timedelta

from app.db.session import get_db
from app.models.conductor import Conductor
from app.schemas.conductor import ConductorLogin, Token
from app.core.security import verify_password, create_access_token

router = APIRouter()

@router.post("/login", response_model=Token)
def login(conductor_data: ConductorLogin, db: Session = Depends(get_db)):
    conductor = db.query(Conductor).filter(Conductor.email == conductor_data.email).first()
    if not conductor or not verify_password(conductor_data.password, conductor.password):
        raise HTTPException(status_code=401, detail="Credenciales inválidas")
    
    access_token = create_access_token(
        data={"sub": str(conductor.id)}, expires_delta=timedelta(minutes=30)
    )
    return {"access_token": access_token, "token_type": "bearer"}