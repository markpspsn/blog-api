from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, validator
from models import storage

router = APIRouter(prefix="/api/users", tags=["users"])

class CreateUserRequest(BaseModel):
    email: str
    login: str
    password: str

    @validator('email')
    def validate_email(cls, email):
        if '@' not in email:
            raise ValueError('Email должен содержать @')
        return email

    @validator('password')
    def validate_password(cls, password):
        if len(password) < 6:
            raise ValueError('Пароль должен быть не менее 6 символов')
        return password

    @validator('login')
    def validate_login(cls, login):
        if len(login) < 3:
            raise ValueError('Логин должен быть не менее 3 символов')
        return login

class UpdateUserRequest(BaseModel):
    email: str
    login: str
    password: str

@router.post("/")
async def create_new_user(user_data: CreateUserRequest):
    try:
        user = storage.create_user(
            email=user_data.email,
            login=user_data.login,
            password=user_data.password
        )
        
        return {
            "id": user.id,
            "email": user.email,
            "login": user.login,
            "createdAt": user.createdAt.isoformat(),
            "updatedAt": user.updatedAt.isoformat()
        }
    except Exception as error:
        raise HTTPException(status_code=400, detail=str(error))

@router.get("/")
async def get_all_users():
    users = storage.get_all_users()
    
    users_list = []
    for user in users:
        users_list.append({
            "id": user.id,
            "email": user.email,
            "login": user.login,
            "createdAt": user.createdAt.isoformat(),
            "updatedAt": user.updatedAt.isoformat()
        })
    
    return users_list

@router.get("/{user_id}")
async def get_user_by_id(user_id: int):
    user = storage.get_user_by_id(user_id)
    
    if user is None:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    
    return {
        "id": user.id,
        "email": user.email,
        "login": user.login,
        "createdAt": user.createdAt.isoformat(),
        "updatedAt": user.updatedAt.isoformat()
    }

@router.put("/{user_id}")
async def update_user_data(user_id: int, user_data: UpdateUserRequest):
    user = storage.update_user(
        user_id=user_id,
        email=user_data.email,
        login=user_data.login,
        password=user_data.password
    )
    
    if user is None:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    
    return {
        "id": user.id,
        "email": user.email,
        "login": user.login,
        "createdAt": user.createdAt.isoformat(),
        "updatedAt": user.updatedAt.isoformat()
    }

@router.delete("/{user_id}")
async def delete_user_by_id(user_id: int):
    success = storage.delete_user(user_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    
    return {"message": "Пользователь успешно удален"}