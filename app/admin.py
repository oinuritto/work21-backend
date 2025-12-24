"""
Админ-панель WORK21
Доступна по адресу: /admin
"""
from sqladmin import Admin, ModelView
from sqladmin.authentication import AuthenticationBackend
from starlette.requests import Request

from app.core.database import engine
from app.core.security import verify_password
from app.models.user import User, UserRole
from app.models.project import Project, Task, Application
from app.models.rating import Rating
from app.models.contract import Contract


# ============= Аутентификация админ-панели =============

class AdminAuth(AuthenticationBackend):
    """
    Простая аутентификация для админ-панели.
    Логин: admin, Пароль: admin123
    """
    
    async def login(self, request: Request) -> bool:
        form = await request.form()
        username = form.get("username")
        password = form.get("password")
        
        print(f"[ADMIN] Login attempt: username={username}")
        
        if username == "admin" and password == "admin123":
            request.session.update({"token": "admin-authenticated"})
            print("[ADMIN] Login successful!")
            return True
        
        print("[ADMIN] Login failed!")
        return False
    
    async def logout(self, request: Request) -> bool:
        request.session.clear()
        return True
    
    async def authenticate(self, request: Request) -> bool:
        token = request.session.get("token")
        return token == "admin-authenticated"


# ============= Представления моделей =============

class UserAdmin(ModelView, model=User):
    """Админка пользователей"""
    
    name = "User"
    name_plural = "Users"
    icon = "fa-solid fa-user"
    
    # Колонки в списке
    column_list = [
        User.id, 
        User.email, 
        User.first_name, 
        User.last_name,
        User.role, 
        User.rating_score,
        User.completed_projects,
        User.is_active,
        User.created_at
    ]
    
    # Колонки для поиска
    column_searchable_list = [User.email, User.first_name, User.last_name]
    
    # Сортировка по умолчанию
    column_default_sort = [(User.created_at, True)]
    
    # Поля формы (пароль исключён)
    form_columns = [
        User.email,
        User.first_name,
        User.last_name,
        User.role,
        User.bio,
        User.skills,
        User.rating_score,
        User.completed_projects,
        User.is_active,
        User.is_verified,
    ]
    
    # Экспорт
    can_export = True
    export_types = ["csv", "json"]


class ProjectAdmin(ModelView, model=Project):
    """Админка проектов"""
    
    name = "Project"
    name_plural = "Projects"
    icon = "fa-solid fa-folder"
    
    column_list = [
        Project.id,
        Project.title,
        Project.status,
        Project.budget,
        Project.customer_id,
        Project.created_at
    ]
    
    column_searchable_list = [Project.title, Project.description]
    # column_filters = [Project.status]  # enum не поддерживается
    column_default_sort = [(Project.created_at, True)]
    
    form_columns = [
        Project.title,
        Project.description,
        Project.requirements,
        Project.budget,
        Project.deadline,
        Project.tech_stack,
        Project.status,
        Project.customer_id,
        Project.generated_spec,
    ]
    
    can_export = True


class TaskAdmin(ModelView, model=Task):
    """Админка задач"""
    
    name = "Task"
    name_plural = "Tasks"
    icon = "fa-solid fa-list-check"
    
    column_list = [
        Task.id,
        Task.title,
        Task.status,
        Task.complexity,
        Task.project_id,
        Task.assignee_id
    ]
    
    column_searchable_list = [Task.title]
    # column_filters = [Task.status, Task.complexity]  # enum не поддерживается


class ApplicationAdmin(ModelView, model=Application):
    """Админка заявок"""
    
    name = "Application"
    name_plural = "Applications"
    icon = "fa-solid fa-file-lines"
    
    column_list = [
        Application.id,
        Application.project_id,
        Application.student_id,
        Application.status,
        Application.proposed_rate,
        Application.created_at
    ]
    
    # column_filters = [Application.status]  # enum не поддерживается
    column_default_sort = [(Application.created_at, True)]


class RatingAdmin(ModelView, model=Rating):
    """Админка рейтингов"""
    
    name = "Rating"
    name_plural = "Ratings"
    icon = "fa-solid fa-star"
    
    column_list = [
        Rating.id,
        Rating.project_id,
        Rating.reviewer_id,
        Rating.reviewee_id,
        Rating.score,
        Rating.created_at
    ]
    
    # column_filters = [Rating.score]  # временно отключено


class ContractAdmin(ModelView, model=Contract):
    """Админка договоров"""
    
    name = "Contract"
    name_plural = "Contracts"
    icon = "fa-solid fa-file-contract"
    
    column_list = [
        Contract.id,
        Contract.project_id,
        Contract.customer_id,
        Contract.student_id,
        Contract.total_amount,
        Contract.status,
        Contract.created_at
    ]
    
    # column_filters = [Contract.status]  # enum не поддерживается


# ============= Функция создания админки =============

def create_admin(app):
    """
    Создаёт и настраивает админ-панель
    """
    # Временно отключена авторизация для отладки
    # authentication_backend = AdminAuth(secret_key="admin-secret-key-change-me")
    
    admin = Admin(
        app,
        engine,
        title="WORK21 Admin",
        # authentication_backend=authentication_backend,  # Раскомментируйте для включения авторизации
    )
    
    # Регистрируем модели
    admin.add_view(UserAdmin)
    admin.add_view(ProjectAdmin)
    admin.add_view(TaskAdmin)
    admin.add_view(ApplicationAdmin)
    admin.add_view(RatingAdmin)
    admin.add_view(ContractAdmin)
    
    return admin

