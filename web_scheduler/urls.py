"""web_scheduler URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
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
from django.urls import path, include
from rest_framework.routers import SimpleRouter

from schedulers import views
from schedulers.auto_api import JobLogViewSet
router = SimpleRouter()
router.register('api/job_log', JobLogViewSet, basename='job_log')

urlpatterns = [
    # 管理页面，管理任务创建，触发器创建等
    path('admin/', admin.site.urls),
    # 消息提示
    path('email/test', views.email_test),
    # 用户 登录
    path('', views.index),
    path('login/', views.login_web),
    path('logout/', views.logout_view),
    # 任务管理
    path('jobs/', views.get_job),
    path('jobs/query', views.query_job),
    path('jobs/modify', views.modify_jobs),
    path('', include(router.urls)),
]

