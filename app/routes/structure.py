from fastapi import APIRouter, Query, HTTPException, Depends
from app.services.articulos.structure import GetStructure
from app.validation import AuthRequired

router = APIRouter()

@router.get("/estructura", dependencies=[Depends(AuthRequired)])
def obtener_estructura(codigo: str = Query(..., description="Código del artículo")):
    estructura, error = GetStructure(codigo.strip().upper())
    if error:
        if "inexistente" in error.lower():
            raise HTTPException(status_code=404, detail=error)
        raise HTTPException(status_code=500, detail=error)
    return estructura
