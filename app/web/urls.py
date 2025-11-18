# campuslog/web/urls.py

from django.urls import path
from . import views

urlpatterns = [
    # 1. 메인 페이지 및 검색
    path('', views.index, name='index'),  # GET /
    path('search_panel', views.search_page, name='search_panel'),  # GET /search

    path('board',views.board,name='board'),
    # 2. 식당 및 리뷰 (명세서 기반)
    # {id} -> <int:id>
    path('restaurant/<int:id>', views.restaurant_detail, name='restaurant_detail'),  # GET

    path('restaurant/new/', views.restaurant_create, name='restaurant_create'),

    # GET (후기 목록), POST (후기 저장)
    path('restaurant/<int:id>/reviews', views.restaurant_reviews, name='restaurant_reviews'),

    path('restaurant/<int:id>/reviews/write', views.review_write_form, name='review_write_form'),  # GET

    # 3. 게시판 (명세서 기반)
    # {category} -> <str:category>
    # GET (게시글 목록), POST (게시글 저장)
    path('board/<str:category>', views.board_list, name='board_list'),

    path('board/<str:category>/write', views.post_write_form, name='post_write_form'),  # GET

    # {postid} -> <int:postid>
    path('board/<str:category>/<int:postid>', views.post_detail, name='post_detail'),  # GET

    # 4. API (명세서 + 이전에 만든 API)
    # (명세서에 있던 API)
    path('api/restaurants', views.restaurant_list_api, name='api_restaurant_list'),
    path('api/restaurants/<int:id>', views.restaurant_detail_api, name='api_restaurant_detail'),

    # (이전에 우리가 대화로 만든 위치 API)
    path('api/locations', views.user_locations_api, name='api_locations'),
    path('api/update_location', views.update_user_location_api, name='api_update_location'),
]