from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List

from app.services.articulos.oldstructure import get_structure
from app.services.articulos.oldcomparation import compare_structures
from app.validation import auth_required

router = APIRouter()


class CompareRequest(BaseModel):
    Codes: List[str]


@router.post("/compare", dependencies=[Depends(auth_required)])
async def compare(data: CompareRequest):
    """
    Compara la estructura de múltiples artículos y devuelve un reporte.
    """
    codes = data.Codes
    if not codes or len(codes) < 2:
        raise HTTPException(
            status_code=400,
            detail="At least two codes are required to compare"
        )

    structures = []
    errors = []

    for code in codes:
        structure, error = get_structure(code.strip().upper())
        if error:
            errors.append({"code": code, "error": error})
            structures.append({"code": code, "structure": []})
        else:
            structures.append({"code": code, "structure": structure})

    report = compare_structures(structures)

    return {
        "structures": structures,
        "errors": errors,
        "report": report
    }
