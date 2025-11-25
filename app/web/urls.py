# campuslog/web/urls.py

from django.urls import path
from . import views

urlpatterns = [
    # 1. 메인 페이지 및 검색
    path('', views.index, name='index'),  # GET /
    path('search', views.search_page, name='search_panel'),  # GET /search

    path('test', views.test_page, name='test'),
    path('start', views.start_page, name='start'),
    path('board',views.board,name='board'),
    path('register', views.register, name='register'),
    # 2. 식당 및 리뷰 (명세서 기반)
    # {id} -> <int:id>
    path('restaurant', views.restaurant_list, name='restaurant_list'),

    path('restaurant/<int:id>/', views.restaurant_detail, name='restaurant_detail'),  # GET

    path('restaurant/new/', views.restaurant_create, name='restaurant_create'),

    # GET (후기 목록), POST (후기 저장)
    path('restaurant/<int:id>/reviews', views.restaurant_reviews, name='restaurant_reviews'),

    path('restaurant/<int:id>/reviews/write', views.review_write_form, name='review_write_form'),  # GET

    # 3. 통합 게시판 (카테고리 없음)
    # /board -> 게시판 목록 (GET), 게시글 작성 (POST)
    path('board/list', views.board_list, name='board_list'),

    # /board/write -> 게시글 작성 폼
    path('board/write', views.post_write_form, name='post_write_form'),

    # /board/{postid} -> 게시글 상세
    path('board/<int:postid>', views.post_detail, name='post_detail'),

    # 게시판 패널용 경로 추가
    path('board_panel', views.board_list, name='board_panel'),

    # (이전에 우리가 대화로 만든 위치 API)
    path('api/locations', views.user_locations_api, name='api_locations'),
    path('api/update_location', views.update_user_location_api, name='api_update_location'),
    path('api/restaurants', views.restaurant_list_api, name='api_restaurant_list'),
]