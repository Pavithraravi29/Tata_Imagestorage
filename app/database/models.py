from pony.orm import Database, Required, Set, PrimaryKey, Optional
from datetime import datetime


db = Database()

class User(db.Entity):
    _table_ = 'users'
    id = PrimaryKey(int, auto=True)
    username = Required(str, unique=True)
    email = Required(str, unique=True)
    hashed_password = Required(str)
    role = Required(str)
    created_at = Required(datetime, default=datetime.utcnow)
    updated_at = Optional(datetime)
    logs = Set('UserLog')

class UserLog(db.Entity):
    _table_ = 'user_logs'
    id = PrimaryKey(int, auto=True)
    user = Required(User)
    username = Required(str)
    email = Required(str)
    login_time = Required(datetime, default=datetime.utcnow)

class PartNumber(db.Entity):
    _table_ = 'part_numbers'
    id = PrimaryKey(int, auto=True)
    part_number = Required(str, unique=True)
    images = Set('ImageData', reverse='pid')  # Update the reverse reference


class ImageData(db.Entity):
    _table_ = 'image_data'
    id = Required(int, auto=True)
    timestamp = Required(datetime)
    file_path = Required(str)
    production_line = Required(str)
    pid = Required(PartNumber)
    PrimaryKey(id, timestamp)

