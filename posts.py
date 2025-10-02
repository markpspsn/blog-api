from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, validator
from models import storage

router = APIRouter(prefix="/api/posts", tags=["posts"])

class CreatePostRequest(BaseModel):
    authorId: int
    title: str
    content: str

    @validator('title')
    def validate_title(cls, title):
        if len(title) < 3:
            raise ValueError('Заголовок должен быть не менее 3 символов')
        if len(title) > 100:
            raise ValueError('Заголовок должен быть не более 100 символов')
        return title

    @validator('content')
    def validate_content(cls, content):
        if len(content) < 10:
            raise ValueError('Текст поста должен быть не менее 10 символов')
        return content

class UpdatePostRequest(BaseModel):
    title: str
    content: str

@router.post("/")
async def create_new_post(post_data: CreatePostRequest):
    try:
        author = storage.get_user_by_id(post_data.authorId)
        if author is None:
            raise HTTPException(status_code=404, detail="Автор не найден")
        
        post = storage.create_post(
            authorId=post_data.authorId,
            title=post_data.title,
            content=post_data.content
        )
        
        return {
            "id": post.id,
            "authorId": post.authorId,
            "title": post.title,
            "content": post.content,
            "createdAt": post.createdAt.isoformat(),
            "updatedAt": post.updatedAt.isoformat()
        }
    except Exception as error:
        raise HTTPException(status_code=400, detail=str(error))

@router.get("/")
async def get_all_posts():
    posts = storage.get_all_posts()
    
    posts_list = []
    for post in posts:
        posts_list.append({
            "id": post.id,
            "authorId": post.authorId,
            "title": post.title,
            "content": post.content,
            "createdAt": post.createdAt.isoformat(),
            "updatedAt": post.updatedAt.isoformat()
        })
    
    return posts_list

@router.get("/{post_id}")
async def get_post_by_id(post_id: int):
    post = storage.get_post_by_id(post_id)
    
    if post is None:
        raise HTTPException(status_code=404, detail="Пост не найден")
    
    return {
        "id": post.id,
        "authorId": post.authorId,
        "title": post.title,
        "content": post.content,
        "createdAt": post.createdAt.isoformat(),
        "updatedAt": post.updatedAt.isoformat()
    }

@router.get("/author/{author_id}")
async def get_posts_by_author(author_id: int):
    author = storage.get_user_by_id(author_id)
    if author is None:
        raise HTTPException(status_code=404, detail="Автор не найден")
    
    posts = storage.get_posts_by_author(author_id)
    
    posts_list = []
    for post in posts:
        posts_list.append({
            "id": post.id,
            "authorId": post.authorId,
            "title": post.title,
            "content": post.content,
            "createdAt": post.createdAt.isoformat(),
            "updatedAt": post.updatedAt.isoformat()
        })
    
    return posts_list

@router.put("/{post_id}")
async def update_post_data(post_id: int, post_data: UpdatePostRequest):
    post = storage.update_post(
        post_id=post_id,
        title=post_data.title,
        content=post_data.content
    )
    
    if post is None:
        raise HTTPException(status_code=404, detail="Пост не найден")
    
    return {
        "id": post.id,
        "authorId": post.authorId,
        "title": post.title,
        "content": post.content,
        "createdAt": post.createdAt.isoformat(),
        "updatedAt": post.updatedAt.isoformat()
    }

@router.delete("/{post_id}")
async def delete_post_by_id(post_id: int):
    success = storage.delete_post(post_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Пост не найден")
    
    return {"message": "Пост успешно удален"}