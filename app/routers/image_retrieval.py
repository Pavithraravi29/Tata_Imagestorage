import os
from asyncio.log import logger
from datetime import datetime

from starlette.responses import FileResponse

from app.database.models import PartNumber, ImageData
from fastapi import APIRouter, HTTPException
from pony.orm import db_session, select, desc
from app.schemas.image import ImageResponse
from typing import List


router = APIRouter()


@db_session
def process_alias_folder(alias_path: str, alias: str):
    print(f"Processing folder: {alias_path} with alias: {alias}")
    for file in os.listdir(alias_path):
        if file.lower().endswith(('.jpg', '.jpeg')):
            file_path = os.path.join(alias_path, file)
            part_number_str = os.path.splitext(file)[0]
            timestamp = datetime.fromtimestamp(os.path.getmtime(file_path))

            part_number = PartNumber.get(part_number=part_number_str)
            if not part_number:
                part_number = PartNumber(part_number=part_number_str)
                print(f"Inserted new part number: {part_number_str}")

            existing_image = select(img for img in ImageData if img.pid == part_number).first()
            if existing_image:
                if existing_image.timestamp < timestamp:
                    existing_image.file_path = file_path
                    existing_image.timestamp = timestamp
                    existing_image.production_line = alias
                    print(f"Updated: {part_number_str}")
            else:
                ImageData(id=part_number.id, timestamp=timestamp, file_path=file_path, production_line=alias,
                          pid=part_number)
                print(f"Inserted: {part_number_str}")



@db_session
def update_database(directory: str):
    print(f"Updating database with directory: {directory}")
    for year in os.listdir(directory):
        year_path = os.path.join(directory, year)
        if not os.path.isdir(year_path):
            continue
        for month in os.listdir(year_path):
            month_path = os.path.join(year_path, month)
            if not os.path.isdir(month_path):
                continue
            for day in os.listdir(month_path):
                day_path = os.path.join(month_path, day)
                if not os.path.isdir(day_path):
                    continue
                for alias in os.listdir(day_path):
                    alias_path = os.path.join(day_path, alias)
                    if not os.path.isdir(alias_path):
                        continue
                    process_alias_folder(alias_path, alias)
    print("Database update completed.")


# @router.get("/image/{part_number}", response_model=ImageResponse)
# @db_session
# def get_image(part_number: str):
#     print(f"Searching for part number: {part_number}")
#     part = PartNumber.get(part_number=part_number)
#
#     if not part:
#         print(f"Part number not found: {part_number}")
#         raise HTTPException(status_code=404, detail="Part number not found")
#
#     print(f"Found part number: {part_number}")
#
#     # Retrieve the latest image associated with this part number
#     image = select(img for img in ImageData if img.pid == part).order_by(desc(ImageData.timestamp)).first()
#
#     if image:
#         print(f"Found image for part number: {part_number}")
#         return ImageResponse(part_number=part.part_number, file_path=image.file_path,
#                              production_line=image.production_line, timestamp=image.timestamp)
#
#     print(f"Image not found for part number: {part_number}")
#     raise HTTPException(status_code=404, detail="Image not found")


@router.post("/update_database")
def update_db():
    centralized_folder = 'C:\\Users\\SDC-03\\Downloads\\Data_received\\archive'
    update_database(centralized_folder)
    return {"message": "Database updated successfully"}

@router.get("/images_by_production_line/{production_line}", response_model=List[ImageResponse])
@db_session
def get_images_by_production_line(production_line: str):
    images = select((img.pid.part_number, img.file_path, img.production_line, img.timestamp)
                    for img in ImageData if img.production_line == production_line)[:]
    if images:
        return [ImageResponse(part_number=pn, file_path=fp, production_line=a, timestamp=ts) for pn, fp, a, ts in images]
    raise HTTPException(status_code=404, detail="No images found for this production_line")

@router.get("/partnumbers")
@db_session
def get_all_partnumbers():
    part_numbers = select(p for p in PartNumber)[:]
    return [{"id": p.id, "part_number": p.part_number} for p in part_numbers]


@router.get("/elnewimage/{part_number}")
@db_session
def get_image(part_number: str):
    print(f"Searching for part number: {part_number}")
    part = PartNumber.get(part_number=part_number)

    if not part:
        print(f"Part number not found: {part_number}")
        raise HTTPException(status_code=404, detail="Part number not found")

    print(f"Found part number: {part_number}")

    # Retrieve the latest image associated with this part number
    image = select(img for img in ImageData if img.pid == part).order_by(desc(ImageData.timestamp)).first()

    if image:
        print(f"Found image for part number: {part_number}")
        if os.path.exists(image.file_path):
            return FileResponse(image.file_path)
        else:
            raise HTTPException(status_code=404, detail="Image file not found")

    print(f"Image not found for part number: {part_number}")
    raise HTTPException(status_code=404, detail="Image not found")

@router.get("/elnewimage_info/{part_number}", response_model=ImageResponse)
@db_session
def get_image_info(part_number: str):
    print(f"Searching for part number info: {part_number}")
    part = PartNumber.get(part_number=part_number)

    if not part:
        print(f"Part number not found: {part_number}")
        raise HTTPException(status_code=404, detail="Part number not found")

    image = select(img for img in ImageData if img.pid == part).order_by(desc(ImageData.timestamp)).first()

    if image:
        return ImageResponse(part_number=part.part_number, file_path=image.file_path,
                             production_line=image.production_line, timestamp=image.timestamp)

    raise HTTPException(status_code=404, detail="Image not found")
