from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List

from app.services.structure import GetStructure
from app.services.comparation import CompareStructures

router = APIRouter()

class CompareRequest(BaseModel):
    Codes: List[str]

@router.post("/compare")
async def Compare(data: CompareRequest):
    codes = data.Codes
    if not codes or len(codes) < 2:
        raise HTTPException(status_code=400, detail="At least two codes are required to compare")

    structures = []
    errors = []

    for code in codes:
        structure, error = GetStructure(code.strip().upper())
        if error:
            errors.append({"code": code, "error": error})
            structures.append({"code": code, "structure": []})
        else:
            structures.append({"code": code, "structure": structure})

    report = CompareStructures(structures)

    return {
        "structures": structures,
        "errors": errors,
        "report": report
    }
