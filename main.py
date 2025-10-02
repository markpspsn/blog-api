from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from models import storage
from routers import users, posts
import uvicorn

# Главное приложение
app = FastAPI(
    title="Blog API",
    description="REST API для блога",
    version="1.0.0"
)

# работа с HTML шаблонами
templates = Jinja2Templates(directory="templates")

# Подключаем API для пользователей и постов
app.include_router(users.router)
app.include_router(posts.router)

def create_test_user():
    # Создает тестового пользователя при первом запуске
    users = storage.get_all_users()
    if not users:
        user = storage.create_user("test@mail.ru", "testuser", "123456")
        print(f"✅ Создан тестовый пользователь: ID {user.id}")
        return user.id
    else:
        print(f"✅ Пользователи уже есть. ID первого: {users[0].id}")
        return users[0].id

# Запускается при старте приложения
@app.on_event("startup")
async def startup_event():
    # Загружаем данные из файлов
    storage.load_users_from_file()
    storage.load_posts_from_file()
    user_id = create_test_user()
    print("✅ Данные загружены из файлов")
    print(f"🎯 Тестовый пользователь ID: {user_id}")
    print("✅ Сервер запущен: http://localhost:8000")
    print("✅ Документация API: http://localhost:8000/docs")

# Главная страница со списком постов
@app.get("/", response_class=HTMLResponse)
async def home_page(request: Request):
    all_posts = storage.get_all_posts()
    return templates.TemplateResponse("index.html", {
        "request": request, 
        "posts": all_posts
    })

# Страница создания пользователя
@app.get("/users/create", response_class=HTMLResponse)
async def create_user_page(request: Request):
    return templates.TemplateResponse("create_user.html", {"request": request})

# создание пользователя
@app.post("/users/create", response_class=HTMLResponse)
async def create_user_handler(
    request: Request,
    email: str = Form(...),
    login: str = Form(...),
    password: str = Form(...)
):
    try:
        print(f"🔧 Создаем пользователя: {email}, {login}")
        user = storage.create_user(email, login, password)
        print(f"✅ Пользователь создан: ID {user.id}")
        
        all_posts = storage.get_all_posts()
        return templates.TemplateResponse("index.html", {
            "request": request, 
            "posts": all_posts,
            "message": f"Пользователь '{login}' успешно создан! ID: {user.id}"
        })
    except Exception as error:
        error_msg = f"Ошибка при создании пользователя: {str(error)}"
        print(f"❌ {error_msg}")
        return templates.TemplateResponse("create_user.html", {
            "request": request,
            "error": error_msg
        })

# Страница создания поста
@app.get("/posts/create", response_class=HTMLResponse)
async def create_post_page(request: Request):
    # список пользователей для выбора автора
    users = storage.get_all_users()
    return templates.TemplateResponse("create_post.html", {
        "request": request,
        "users": users
    })

# создание поста
@app.post("/posts/create", response_class=HTMLResponse)
async def create_post_handler(
    request: Request,
    authorId: int = Form(...),
    title: str = Form(...),
    content: str = Form(...)
):
    try:
        print(f"🔧 Получены данные: authorId={authorId}, title='{title}'")

        author = storage.get_user_by_id(authorId)
        if not author:
            error_msg = f"Автор с ID {authorId} не найден"
            print(f"❌ {error_msg}")
            users = storage.get_all_users()
            return templates.TemplateResponse("create_post.html", {
                "request": request,
                "users": users,
                "error": error_msg
            })
        
        # Создаем пост
        post = storage.create_post(authorId, title, content)
        print(f"✅ Пост создан: ID {post.id}")
        
        all_posts = storage.get_all_posts()
        return templates.TemplateResponse("index.html", {
            "request": request, 
            "posts": all_posts,
            "message": f"Пост '{title}' успешно создан!"
        })
    except Exception as error:
        error_msg = f"Ошибка при создании поста: {str(error)}"
        print(f"❌ {error_msg}")
        users = storage.get_all_users()
        return templates.TemplateResponse("create_post.html", {
            "request": request,
            "users": users,
            "error": error_msg
        })

# Страница просмотра поста
@app.get("/posts/{post_id}", response_class=HTMLResponse)
async def view_post_page(request: Request, post_id: int):
    post = storage.get_post_by_id(post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Пост не найден")
    
    return templates.TemplateResponse("post.html", {
        "request": request, 
        "post": post
    })

# Страница редактирования поста
@app.get("/posts/{post_id}/edit", response_class=HTMLResponse)
async def edit_post_page(request: Request, post_id: int):
    post = storage.get_post_by_id(post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Пост не найден")
    
    return templates.TemplateResponse("edit_post.html", {
        "request": request, 
        "post": post
    })

#редактирование поста
@app.post("/posts/{post_id}/edit", response_class=HTMLResponse)
async def edit_post_handler(
    request: Request,
    post_id: int,
    title: str = Form(...),
    content: str = Form(...)
):
    post = storage.update_post(post_id, title, content)
    if not post:
        raise HTTPException(status_code=404, detail="Пост не найден")
    
    all_posts = storage.get_all_posts()
    return templates.TemplateResponse("index.html", {
        "request": request, 
        "posts": all_posts,
        "message": "Пост успешно обновлен!"
    })

# Удаление поста
@app.post("/posts/{post_id}/delete")
async def delete_post_handler(post_id: int):
    success = storage.delete_post(post_id)
    if not success:
        raise HTTPException(status_code=404, detail="Пост не найден")
    
    # Возвращаем на главную страницу
    return RedirectResponse(url="/", status_code=303)

# Лайк поста
@app.post("/posts/{post_id}/like")
async def like_post_handler(post_id: int):
    success = storage.like_post(post_id)
    if not success:
        raise HTTPException(status_code=404, detail="Пост не найден")

    return RedirectResponse(url=f"/posts/{post_id}", status_code=303)

# Дизлайк поста
@app.post("/posts/{post_id}/dislike")
async def dislike_post_handler(post_id: int):
    success = storage.dislike_post(post_id)
    if not success:
        raise HTTPException(status_code=404, detail="Пост не найден")

    return RedirectResponse(url=f"/posts/{post_id}", status_code=303)

# Запуск сервера
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)