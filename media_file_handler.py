# main media file uploader
from csv import DictReader
from os import path, remove

from deta import Deta

from decouple import config

from fastapi import UploadFile

STATIC_DIR = "static"

DETA_PROJECT_KEY = config("DETA_PROJECT_KEY")

async def delete_uploaded_file(filename: str) -> bool:
    '''
        delete resource at given path
    '''
    res = path.join(STATIC_DIR, filename)
    
    if path.isfile(res):
        try:
            remove(res)
            return True
        
        except:
            return False

    return False

async def save_upload_file(upload_file: UploadFile):
    '''
        save the uploaded course file name to resource_path dir
    '''
    file_location = path.join(STATIC_DIR , upload_file.filename)

    with open(file_location, "wb") as file_object:
        file_object.write(upload_file.file.read())

    print('File location: ', file_location)

    return file_location

async def multiple_add_course(base_name, fname):
    deta = Deta(DETA_PROJECT_KEY)
    db = deta.Base(base_name)

    try:
        payload = []

        success = []

        failed = []

        with open(fname) as res:
            _reader = DictReader(res)

            line_count = 0

            for row in _reader:
                if line_count == 0:
                    print(f'Column names are {", ".join(row)}\n')

                    line_count += 1

                if not row.get('dpt'):
                    raise Exception('failed to parse course template')

                row['part'] = f'part {row["part"]}'.strip()
                row['key'] = row['code'].upper().strip()
                row['code'] = row['code'].upper().strip()
                row['dpt'] = row['dpt'].upper().strip()
                row['name'] = row['name'].title().strip()

                payload.append(row)

                line_count += 1

            print(f'processed {line_count} lines.\n')

        # https://softhints.com/python-split-list-into-evenly-sized-lists/#:~:text=Another%20alternative%20t%20o%20split%20lists%20into%20equal,5%20%5Bmy_list%5Bi%3Ai%2Bn%5D%20for%20i%20in%20range%280%2C%20len%28my_list%29%2C%20n%29%5D

        # ? only 25 items at a time
        n = 25

        chunked_payload = [payload[i:i+n] for i in range(0, len(payload), n)]

        try:
            for chunk in chunked_payload:
                res = db.put_many(chunk)

                success.append(chunk)

        except Exception as err:
            print('[DETA-UPLOAD-ERR] Error course uploading many: ', err)
            failed.append(payload)

        return {
            "success": success,
            "failed": failed
        }

    except Exception as err:
        return f"failed to add data: {err}"

async def multiple_add_fd(base_name, fname):
    deta = Deta(DETA_PROJECT_KEY)
    db = deta.Base(base_name)

    try:
        payload = []

        success = []

        failed = []

        with open(fname) as res:
            _reader = DictReader(res)

            line_count = 0

            for row in _reader:
                if line_count == 0:
                    print(f'Column names are {", ".join(row)}\n')

                    line_count += 1

                if not row.get('faculty'):
                    raise Exception('failed to parse faculty-department template')

                row['key'] = row['dptCode'].upper().strip()
                row['dptCode'] = row['dptCode'].upper().strip()
                row['dptName'] = row['dptName'].title().strip()
                row['faculty'] = row['faculty'].title().strip()

                payload.append(row)

                line_count += 1

            print(f'processed {line_count} lines.\n')

        # ? only 25 items at a time
        n = 25

        chunked_payload = [payload[i:i+n] for i in range(0, len(payload), n)]

        try:
            for chunk in chunked_payload:
                res = db.put_many(chunk)

                success.append(chunk)

        except Exception as err:
            print('[DETA-UPLOAD-ERR] Error fd uploading many: ', err)
            failed.append(payload)

        return {
            "success": success,
            "failed": failed
        }

    except Exception as err:
        return f"failed to add data: {err}"