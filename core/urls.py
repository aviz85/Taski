"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include, re_path
from rest_framework.routers import DefaultRouter
from rest_framework_nested import routers
from tasks.views import TaskViewSet, TaskCommentViewSet, ChecklistItemViewSet
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from authentication.views import register, get_user
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView

# Main router for top-level endpoints
router = DefaultRouter()
router.register(r'tasks', TaskViewSet, basename='task')

# Nested router for task comments
task_router = routers.NestedSimpleRouter(router, r'tasks', lookup='task')
task_router.register(r'comments', TaskCommentViewSet, basename='task-comment')

# Nested router for task checklist items
task_router.register(r'checklist', ChecklistItemViewSet, basename='task-checklist')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api/', include(task_router.urls)),
    path('api/auth/register/', register, name='register'),
    path('api/auth/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/auth/user/', get_user, name='get_user'),
    
    # Serve the frontend HTML at the root URL
    re_path(r'^.*', TemplateView.as_view(template_name='index.html')),
]

# הוספת תמיכה בקבצים סטטיים במצב פיתוח
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
