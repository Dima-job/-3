from pydantic import BaseModel
from typing import List

class Post(BaseModel):
    id: int
    author: str
    title: str
    content: str
    tags: List[str] = []
    is_private: bool = False
    allowed_users: List[str] = []