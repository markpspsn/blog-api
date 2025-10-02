from datetime import datetime
from typing import Dict, Optional, List
import json
import os

# Класс пользователя
class User:
    def __init__(self, id: int, email: str, login: str, password: str):
        self.id = id
        self.email = email
        self.login = login
        self.password = password
        self.createdAt = datetime.now()
        self.updatedAt = datetime.now()

# Класс поста
class Post:
    def __init__(self, id: int, authorId: int, title: str, content: str):
        self.id = id
        self.authorId = authorId
        self.title = title
        self.content = content
        self.createdAt = datetime.now()
        self.updatedAt = datetime.now()
        self.likes = 0
        self.dislikes = 0

# Главное хранилище данных
class Storage:
    def __init__(self):
        self.users: Dict[int, User] = {}
        self.posts: Dict[int, Post] = {}
        self.next_user_id = 1
        self.next_post_id = 1
    
    # создание пользователя
    def create_user(self, email: str, login: str, password: str) -> User:
        user = User(self.next_user_id, email, login, password)
        self.users[self.next_user_id] = user
        self.next_user_id += 1
        self._save_users_to_file()
        return user
    
    # все пользователи
    def get_all_users(self) -> List[User]:
        return list(self.users.values())
    
    def get_user_by_id(self, user_id: int) -> Optional[User]:
        return self.users.get(user_id)

    def update_user(self, user_id: int, email: str, login: str, password: str) -> Optional[User]:
        if user_id not in self.users:
            return None
        user = self.users[user_id]
        user.email = email
        user.login = login
        user.password = password
        user.updatedAt = datetime.now()
        self._save_users_to_file()
        return user
    
    # удаление пользователя
    def delete_user(self, user_id: int) -> bool:
        if user_id in self.users:
            del self.users[user_id]
            self._save_users_to_file()
            return True
        return False
    
    # создание поста
    def create_post(self, authorId: int, title: str, content: str) -> Post:
        post = Post(self.next_post_id, authorId, title, content)
        self.posts[self.next_post_id] = post
        self.next_post_id += 1
        self._save_posts_to_file()
        return post
    
    def get_all_posts(self) -> List[Post]:
        return list(self.posts.values())
    
    def get_post_by_id(self, post_id: int) -> Optional[Post]:
        return self.posts.get(post_id)
    
    def get_posts_by_author(self, authorId: int) -> List[Post]:
        return [post for post in self.posts.values() if post.authorId == authorId]
    
    # обновление поста
    def update_post(self, post_id: int, title: str, content: str) -> Optional[Post]:
        if post_id not in self.posts:
            return None
        post = self.posts[post_id]
        post.title = title
        post.content = content
        post.updatedAt = datetime.now()
        self._save_posts_to_file()
        return post
    
    # удаление поста
    def delete_post(self, post_id: int) -> bool:
        if post_id in self.posts:
            del self.posts[post_id]
            self._save_posts_to_file()
            return True
        return False
    
    # лайк поста
    def like_post(self, post_id: int) -> bool:
        if post_id in self.posts:
            self.posts[post_id].likes += 1
            self._save_posts_to_file()
            return True
        return False
    
    # дизлайк поста
    def dislike_post(self, post_id: int) -> bool:
        if post_id in self.posts:
            self.posts[post_id].dislikes += 1
            self._save_posts_to_file()
            return True
        return False
    
    def _save_users_to_file(self):
        data = {
            'users': {
                str(uid): {
                    'id': user.id,
                    'email': user.email,
                    'login': user.login,
                    'password': user.password,
                    'createdAt': user.createdAt.isoformat(),
                    'updatedAt': user.updatedAt.isoformat()
                } for uid, user in self.users.items()
            },
            'next_user_id': self.next_user_id
        }
        with open('users_data.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def _save_posts_to_file(self):
        data = {
            'posts': {
                str(pid): {
                    'id': post.id,
                    'authorId': post.authorId,
                    'title': post.title,
                    'content': post.content,
                    'createdAt': post.createdAt.isoformat(),
                    'updatedAt': post.updatedAt.isoformat(),
                    'likes': post.likes,
                    'dislikes': post.dislikes
                } for pid, post in self.posts.items()
            },
            'next_post_id': self.next_post_id
        }
        with open('posts_data.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def load_users_from_file(self):
        if os.path.exists('users_data.json'):
            with open('users_data.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.next_user_id = data['next_user_id']
                for uid, user_data in data['users'].items():
                    user = User(
                        user_data['id'],
                        user_data['email'],
                        user_data['login'],
                        user_data['password']
                    )
                    user.createdAt = datetime.fromisoformat(user_data['createdAt'])
                    user.updatedAt = datetime.fromisoformat(user_data['updatedAt'])
                    self.users[user_data['id']] = user
    
    def load_posts_from_file(self):
        if os.path.exists('posts_data.json'):
            with open('posts_data.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.next_post_id = data['next_post_id']
                for pid, post_data in data['posts'].items():
                    post = Post(
                        post_data['id'],
                        post_data['authorId'],
                        post_data['title'],
                        post_data['content']
                    )
                    post.createdAt = datetime.fromisoformat(post_data['createdAt'])
                    post.updatedAt = datetime.fromisoformat(post_data['updatedAt'])
                    post.likes = post_data.get('likes', 0)
                    post.dislikes = post_data.get('dislikes', 0)
                    self.posts[post_data['id']] = post

storage = Storage()