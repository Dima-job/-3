from pydantic import BaseModel
from typing import List, Optional

class User(BaseModel):
    username: str
    password: str

class PostCreate(BaseModel):
    title: str
    content: str
    tags: List[str] = []
    is_private: bool = False

class PostResponse(BaseModel):
    id: int
    author: str
    title: str
    content: str
    tags: List[str]

class CommentCreate(BaseModel):
    text: str
    author: str

class CommentResponse(BaseModel):
    id: int
    post_id: int
    author: str
    text: str