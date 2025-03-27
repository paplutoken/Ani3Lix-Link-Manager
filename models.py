from pydantic import BaseModel

class Admin(BaseModel):
    username: str
    password: str

class Link(BaseModel):
    name: str
    url: str
