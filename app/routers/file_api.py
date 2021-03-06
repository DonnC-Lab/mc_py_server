import io
import mimetypes
from enum import Enum
from typing import Optional
from csv import DictReader

from fastapi import APIRouter, HTTPException, Response, UploadFile
from fastapi.responses import JSONResponse
from app.constants.constants import FETCH_LIMIT

from decouple import config

from deta import Deta

from media_file_handler import multiple_add_course, multiple_add_fd, save_upload_file, delete_uploaded_file

router = APIRouter(
    prefix="/file-api",
    tags=["file-api"],
    responses={404: {"description": "Not found"}},
)

DETA_PROJECT_KEY = config("DETA_PROJECT_KEY")

STATIC_DIR = "static"

class TemplateEnum(str, Enum):
    Other = 'other'
    Course = 'course'
    FacultyDepartment = 'faculty_department'

@router.post("/upload/")
async def create_upload_file(
    file: UploadFile, 
    drive_name: str, 
    filename: Optional[str] = None, 
    directory:Optional[str] = None
    ):

    if not DETA_PROJECT_KEY:
        raise HTTPException(status_code=400, detail="No deta project key found!")

    deta = Deta(DETA_PROJECT_KEY)
    
    drive = deta.Drive(drive_name)

    try:
        if filename:
            file_name = filename.strip()

        else:
            file_name = file.filename 

        if directory:
            file_name = directory.strip() + '/' + file_name

        cloud_filename = drive.put(file_name, io.BytesIO(file.file.read()))
        
        return JSONResponse({
            "status": "OK",
            "message": cloud_filename
        })

    except Exception as err:
        print('[UPLOAD-ERROR] ', err)
        raise HTTPException(status_code=400, detail="Failed to upload file")

@router.post("/template/upload/")
async def tpl_upload_file(
    file: UploadFile, 
    base_name: str, 
    template: TemplateEnum,
    ):
    '''
        faculty: faculty_dptDB
        course: learn_courseDB
    '''

    if not DETA_PROJECT_KEY:
        raise HTTPException(status_code=400, detail="No deta project key found!")

    if template.value == 'other':
        raise HTTPException(status_code=400, detail="No valid template selected!")

    try:
        cached_csv = await save_upload_file(file)

        result = 'err'

        if template.value == 'course':
            result = await multiple_add_course(base_name, cached_csv)

        if template.value == 'faculty_department':
            result = await multiple_add_fd(base_name, cached_csv)

         # delete once done
        await delete_uploaded_file(file.filename)

        return JSONResponse({
            "status": "OK",
            "message": result
        })

    except Exception as err:
        print('[UPLOAD-ERROR] ', err)
        raise HTTPException(status_code=400, detail="Failed to upload template file")

@router.get("/download/")
async def download_file(
    drive_name: str, 
    filename: str
    ):

    if not DETA_PROJECT_KEY:
        raise HTTPException(status_code=400, detail="No deta project key found!")

    deta = Deta(DETA_PROJECT_KEY)
    
    drive = deta.Drive(drive_name)

    try:
        file_obj = drive.get(filename)

        contents = file_obj.read()

        file_obj.close()

        print('[MIMETYPE-GUESSED] ', mimetypes.guess_type(filename))

        return Response(contents, media_type=mimetypes.guess_type(filename)[0])

    except Exception as err:
        raise HTTPException(status_code=400, detail="Failed to download file")


@router.delete("/delete/")
async def delete_file(
    drive_name: str, 
    filename: str
    ):

    if not DETA_PROJECT_KEY:
        raise HTTPException(status_code=400, detail="No deta project key found!")

    deta = Deta(DETA_PROJECT_KEY)
    
    drive = deta.Drive(drive_name)

    try:
        deleted_file = drive.delete(filename) 

        return JSONResponse({
            "status": "OK",
            "message": deleted_file
        })

    except Exception as err:
        raise HTTPException(status_code=400, detail="Failed to delete file")

@router.get("/files/")
async def get_all_files(
    drive_name: str, 
    limit: Optional[int] = FETCH_LIMIT, 
    prefix: Optional[str] = '', 
    last: Optional[str] = None, 
    ):

    if not DETA_PROJECT_KEY:
        raise HTTPException(status_code=400, detail="No deta project key found!")

    deta = Deta(DETA_PROJECT_KEY)
    
    drive = deta.Drive(drive_name)

    try:
        result = drive.list(
            limit=limit,
            prefix=prefix
        )

        all_files = result.get("names")

        paging = result.get("paging")

        _last = paging.get("last") if paging else None

        while (_last):
            # provide last from previous call
            result = drive.list(last=_last, prefix=prefix)

            all_files += result.get("names")

            # update last
            paging = result.get("paging")
            
            _last = paging.get("last") if paging else None

        return JSONResponse({
            "status": "OK",
            "message": all_files
        })

    except Exception as err:
        raise HTTPException(status_code=400, detail="Failed to get files")