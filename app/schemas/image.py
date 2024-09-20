from pydantic import BaseModel
from datetime import datetime

class PartNumberSchema(BaseModel):
    id: int
    part_number: str

class ImageDataSchema(BaseModel):
    id: int
    timestamp: datetime
    file_path: str
    production_line: str
    part_number_id: int

class ImageResponse(BaseModel):
    part_number: str
    file_path: str
    production_line: str
    timestamp: datetime

