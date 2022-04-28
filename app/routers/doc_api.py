from typing import Optional
from fastapi import APIRouter, HTTPException

from fastapi.responses import JSONResponse

from decouple import config

from deta import Deta

router = APIRouter(
    prefix="/doc-api",
    tags=["doc-api"],
    responses={404: {"description": "Not found"}},
)

DETA_PROJECT_KEY = config("DETA_PROJECT_KEY")

@router.post("/query/")
async def query_data(
    base_name: str, 
    filter: Optional[dict or list] = None,
    ):

    if not DETA_PROJECT_KEY:
        raise HTTPException(status_code=400, detail="No deta project key found!")

    deta = Deta(DETA_PROJECT_KEY)
    
    db = deta.Base(base_name)

    try:
        res = db.fetch(query=filter)

        all_items = res.items

        # fetch until last is 'None'
        while res.last:
            res = db.fetch(last=res.last)
            all_items += res.items

        return JSONResponse({
            "status": "OK",
            "message": all_items
        })

    except Exception as err:
        raise HTTPException(status_code=400, detail="Failed to fetch files")

@router.post("/add/")
async def upload_data(
    base_name: str, 
    payload: dict,
    key: Optional[str] = None, 
    ):

    if not DETA_PROJECT_KEY:
        raise HTTPException(status_code=400, detail="No deta project key found!")

    deta = Deta(DETA_PROJECT_KEY)
    
    db = deta.Base(base_name)

    try:
        res = db.put(payload, key=key)

        return JSONResponse({
            "status": "OK",
            "message": res
        })

    except Exception as err:
        raise HTTPException(status_code=400, detail="Failed to upload data")