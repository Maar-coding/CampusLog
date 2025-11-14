from django.urls import path
from . import views

urlpatterns = [
    # http://localhost:8000/ 에 접속하면 views.index 함수를 실행
    path('', views.index, name='index'),
    path('signup/', views.signup, name='signup'),
]