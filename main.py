from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Dict, Optional

app = FastAPI()

# --- ЭМУЛЯЦИЯ БАЗЫ ДАННЫХ ---
users_db = {
    "Admin": {"username": "Admin", "password": "123", "following": ["Егор", "Кристина"]},
    "Сергей": {"username": "Сергей", "password": "123", "following": ["Admin"]},
    "Антон": {"username": "Антон", "password": "123", "following": ["Сергей"]},
    "Егор": {"username": "Егор", "password": "123", "following": ["Admin"]},
    "Кристина": {"username": "Кристина", "password": "123", "following": ["Admin", "Егор"]},
}

posts_db = [
    {"id": 1, "author": "Admin", "title": "Добро пожаловать!", "content": "Это официальный запуск TechBlog.", "private": False, "allowed": [], "likes": ["Кристина"], "tags": ["новости", "блог"], "comments": []},
    {"id": 2, "author": "Сергей", "title": "Обзор Resident Evil", "content": "Прошел новую часть. Атмосфера пушка!", "private": False, "allowed": [], "likes": ["Admin", "Егор"], "tags": ["игры", "resident evil"], "comments": []},
    {"id": 3, "author": "Антон", "title": "Устал работать", "content": "Еще один день на веб-разработке и отдых.", "private": False, "allowed": [], "likes": ["Сергей"], "tags": ["работа", "web"], "comments": []},
    {"id": 4, "author": "Егор", "title": "Мой новый ПК", "content": "Собрал на RTX 4090.", "private": False, "allowed": [], "likes": ["Антон"], "tags": ["железо", "пк", "minecraft"], "comments": []},
    {"id": 5, "author": "Кристина", "title": "Мои исходники", "content": "Тут спрятан код моего сайта", "private": True, "allowed": ["Admin"], "likes": [], "tags": ["js", "код"], "comments": []},
    {"id": 6, "author": "Егор", "title": "Секреты", "content": "в книги я прячу деньги", "private": True, "allowed": [], "likes": [], "tags": ["железо", "оверклокинг"], "comments": []}
]

pending_requests: Dict[int, List[str]] = {}

class PostUpdate(BaseModel):
    title: str
    content: str
    private: bool
    author: str
    tags: str

class PostCreate(BaseModel):
    author: str
    title: str
    content: str
    private: bool
    tags: str

class CommentCreate(BaseModel):
    post_id: int
    username: str
    text: str

# --- API ЭНДПОИНТЫ ---

@app.post("/login")
def login(user: dict):
    u = user["username"].strip()
    if u in users_db and users_db[u]["password"] == user["password"]:
        return {"status": "success"}
    raise HTTPException(status_code=401)

# --- ДОБАВЛЕННЫЙ ЭНДПОИНТ РЕГИСТРАЦИИ ---
@app.post("/register")
def register(user: dict):
    u = user["username"].strip()
    p = user["password"]
    
    if not u or not p:
        raise HTTPException(status_code=400, detail="Логин и пароль не могут быть пустыми")
    
    if u in users_db:
        raise HTTPException(status_code=400, detail="Пользователь уже существует")
    
    # Добавляем нового пользователя в твою структуру users_db
    users_db[u] = {
        "username": u,
        "password": p,
        "following": []
    }
    print(f"Новый пользователь: {u}")
    return {"status": "success"}

@app.post("/api/create_post")
def create_post(post: PostCreate):
    new_id = max([p["id"] for p in posts_db]) + 1 if posts_db else 1
    tags_list = [t.strip().lower() for t in post.tags.split(',') if t.strip()]
    posts_db.append({
        "id": new_id, "author": post.author.strip(), "title": post.title,
        "content": post.content, "private": post.private, "allowed": [], "likes": [], "tags": tags_list, "comments": []
    })
    return {"status": "success"}

@app.put("/api/update_post/{post_id}")
def update_post(post_id: int, data: PostUpdate):
    post = next((p for p in posts_db if p["id"] == post_id), None)
    if post and post["author"] == data.author.strip():
        tags_list = [t.strip().lower() for t in data.tags.split(',') if t.strip()]
        post["title"] = data.title
        post["content"] = data.content
        post["private"] = data.private
        post["tags"] = tags_list
        return {"status": "updated"}
    raise HTTPException(status_code=403)

@app.delete("/api/delete_post/{post_id}")
def delete_post(post_id: int, author: str):
    global posts_db
    post = next((p for p in posts_db if p["id"] == post_id), None)
    if post and post["author"] == author.strip():
        posts_db = [p for p in posts_db if p["id"] != post_id]
        return {"status": "deleted"}
    raise HTTPException(status_code=403)

@app.post("/api/like")
def toggle_like(post_id: int, username: str):
    u = username.strip()
    post = next((p for p in posts_db if p["id"] == post_id), None)
    if not post: raise HTTPException(status_code=404)
    if "likes" not in post: post["likes"] = []
    if u in post["likes"]:
        post["likes"].remove(u)
        return {"liked": False}
    else:
        post["likes"].append(u)
        return {"liked": True}

@app.post("/api/comment")
def add_comment(comm: CommentCreate):
    post = next((p for p in posts_db if p["id"] == comm.post_id), None)
    if not post: raise HTTPException(status_code=404)
    if "comments" not in post: post["comments"] = []
    post["comments"].append({"user": comm.username.strip(), "text": comm.text.strip()})
    return {"status": "success"}

@app.get("/posts/public")
def get_public(viewer: str = None, filter_following: bool = False, tag: str = None, q: str = None):
    res = []
    v = viewer.strip() if viewer else None
    following_list = users_db[v]["following"] if v and v in users_db else []
    
    for p in posts_db:
        if filter_following and p["author"] not in following_list:
            continue
        if tag and tag.lower() not in p.get("tags", []):
            continue
        if q:
            q_lower = q.lower()
            t_match = q_lower in p["title"].lower()
            c_match = q_lower in p["content"].lower()
            tag_match = any(q_lower in t.lower() for t in p.get("tags", []))
            if not (t_match or c_match or tag_match):
                continue
            
        if not p.get("private") or (v and (v == p["author"] or v in p.get("allowed", []))):
            res.append({**p, "is_locked": False})
        else:
            res.append({
                "id": p["id"], "author": p["author"], 
                "title": f"🔒 [ПО ЗАПРОСУ] {p['title']}", 
                "content": "Контент скрыт.", "is_locked": True, "private": True, "likes": [], "tags": [], "comments": []
            })
    return res

@app.get("/api/profile/{username}")
def get_profile(username: str, viewer: str = None):
    u = username.strip()
    v = viewer.strip() if viewer else None
    if u not in users_db: raise HTTPException(status_code=404)
    
    user_posts = [p for p in posts_db if p["author"] == u]
    processed_posts = []
    
    for p in user_posts:
        if p.get("private") and (not v or (v != p["author"] and v not in p.get("allowed", []))):
            processed_posts.append({
                "id": p["id"], "author": p["author"], 
                "title": f"🔒 [ПО ЗАПРОСУ] {p['title']}", 
                "content": "Контент скрыт.", "is_locked": True, "private": True, "tags": [], "likes": [], "comments": []
            })
        else:
            processed_posts.append({**p, "is_locked": False})
            
    return {
        "username": u,
        "posts": processed_posts,
        "following": users_db[u].get("following", []),
        "followers": [n for n, d in users_db.items() if u in d.get("following", [])]
    }

@app.post("/api/request_access")
def request_access(post_id: int, username: str):
    u = username.strip()
    if post_id not in pending_requests: pending_requests[post_id] = []
    if u not in pending_requests[post_id]: pending_requests[post_id].append(u)
    return {"status": "success"}

@app.get("/api/my_requests")
def get_my_requests(author: str):
    author = author.strip()
    my_ids = [p["id"] for p in posts_db if p["author"] == author]
    res = []
    for pid, users in pending_requests.items():
        if pid in my_ids:
            post = next((p for p in posts_db if p["id"] == pid), None)
            if post:
                for u in users: res.append({"post_id": pid, "post_title": post["title"], "user": u})
    return res

@app.post("/api/approve_access")
def approve_access(post_id: int, target_user: str, author: str):
    post = next((p for p in posts_db if p["id"] == post_id), None)
    if post and post["author"] == author.strip():
        if target_user.strip() not in post["allowed"]: post["allowed"].append(target_user.strip())
        if post_id in pending_requests:
            if target_user.strip() in pending_requests[post_id]:
                pending_requests[post_id].remove(target_user.strip())
        return {"status": "ok"}
    raise HTTPException(status_code=403)

@app.post("/api/follow")
def toggle_follow(target: str, follower: str):
    t, f = target.strip(), follower.strip()
    if t not in users_db or f not in users_db: raise HTTPException(status_code=404)
    if t in users_db[f]["following"]:
        users_db[f]["following"].remove(t)
        return {"is_following": False}
    users_db[f]["following"].append(t)
    return {"is_following": True}

app.mount("/static", StaticFiles(directory="static"), name="static")
@app.get("/")
async def read_index(): return FileResponse('static/index.html')