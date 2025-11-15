from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from web import views as web_views  # web 앱의 signup 뷰를 가져오기 위해

urlpatterns = [
    # 1. 관리자 페이지
    path('admin/', admin.site.urls),

    # 2. 인증 (명세서 기반)
    # GET, POST /login (이전에 만든 로그인 폼 템플릿 지정)
    path('login', auth_views.LoginView.as_view(template_name='web/login.html'), name='login'),

    # GET, POST /register (이전에 만든 web.views.signup 함수 사용)
    path('register', web_views.register, name='register'),  # 명세서의 /register와 일치

    # POST /logout
    path('logout', auth_views.LogoutView.as_view(), name='logout'),

    # 3. 나머지 모든 웹 기능
    # '/' (메인), '/search', '/restaurant/', '/board/', '/api/' 등...
    # 이 모든 요청을 web/urls.py 파일로 넘깁니다.
    path('', include('web.urls')),
]