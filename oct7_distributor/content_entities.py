from typing import Optional, TypeAlias
from pydantic import BaseModel

class Post(BaseModel):
    url: str
    text: str
    author: str

class Comment(BaseModel):
    url: Optional[str] = None
    text: str
    author: str

ContentEntity: TypeAlias = Post | Comment