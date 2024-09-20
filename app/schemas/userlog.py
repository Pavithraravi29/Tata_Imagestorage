# from pydantic import BaseModel
# from datetime import datetime
#
# class UserLogBase(BaseModel):
#     user_id: int
#     username: str
#     email: str
#
# class UserLogCreate(UserLogBase):
#     pass
#
# class UserLog(UserLogBase):
#     id: int
#     login_time: datetime
#
#     class Config:
#         orm_mode = True