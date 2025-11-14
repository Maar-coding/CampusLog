# app/campuslog_project/urls.py

from django.contrib import admin
from django.urls import path, include
# 1. Django의 내장 인증 뷰 임포트
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('web.urls')), # 'front' 앱의 URL들

    # 2. 로그인 URL 추가
    path(
        'login/',
        auth_views.LoginView.as_view(
            # Django가 이 템플릿을 사용하도록 알려줌
            template_name='web/login.html'
        ),
        name='login'
    ),

    # 3. 로그아웃 URL 추가
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
]