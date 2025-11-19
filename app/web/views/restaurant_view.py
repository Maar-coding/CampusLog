import json
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.shortcuts import render, get_object_or_404
from web.models import Restaurant, Menu, Review
from django.db.models import Avg, Count
from web.forms import RestaurantForm

# (중요) 이전에 만든 UserLocation 모델 임포트
from web.models import UserLocation


def restaurant_detail(request, id):
    """
    GET /restaurant/{id} : 식당 상세 정보
    """

    # 1. 식당 정보 (기본)
    #    효율성을 위해 annotate를 사용하여 평균 별점(avg_rating)과
    #    리뷰 개수(review_count)를 한 번의 쿼리로 가져옵니다.
    restaurant = get_object_or_404(
        Restaurant.objects.annotate(
            avg_rating=Avg('reviews__rating'),
            review_count=Count('reviews')
        ),
        pk=id
    )

    # 2. 메뉴 목록
    menus = restaurant.menus.all()  # related_name='menus' 사용

    # 3. 후기 목록 (최신 5개만)
    #    전체 후기는 'restaurant_reviews' 뷰에서 처리
    reviews = restaurant.reviews.all().order_by('-created_at')[:5]

    # 4. 별점 통계 (rating_stats)
    #    템플릿에서 5, 4, 3, 2, 1점 순서로 막대 그래프를 그립니다.

    # 먼저 전체 리뷰 수를 가져옵니다. (위에서 계산한 restaurant.review_count 사용)
    total_review_count = restaurant.review_count

    # 별점(1~5)별 개수를 가져옵니다.
    rating_counts = restaurant.reviews.values('rating').annotate(
        count=Count('rating')
    ).order_by('-rating')  # {'rating': 5, 'count': N}, {'rating': 4, 'count': M} ...

    # 템플릿에 맞게 {star, count, percent} 리스트로 가공
    rating_counts_dict = {item['rating']: item['count'] for item in rating_counts}
    rating_stats = []

    for star in range(5, 0, -1):  # 5, 4, 3, 2, 1 순서
        count = rating_counts_dict.get(star, 0)
        percent = (count / total_review_count) * 100 if total_review_count > 0 else 0

        rating_stats.append({
            'star': star,
            'count': count,
            'percent': round(percent)  # 템플릿 style(width)에 사용
        })

    # 5. Context 데이터 조합
    context = {
        'restaurant': restaurant,
        'menus': menus,
        'reviews': reviews,
        'rating_stats': rating_stats,
    }

    return render(request, 'web/restaurant.html', context)


# @login_required 로그인 필요시 삽입
def restaurant_create(request):
    """
    POST /restaurant/new/ : 식당 생성
    GET  /restaurant/new/ : 식당 등록 폼
    """
    if request.method == 'POST':
        # ⬇️ 'RestaurantForm' (폼 설계도)을 사용합니다.
        form = RestaurantForm(request.POST)
        if form.is_valid():
            restaurant = form.save()
            return redirect('restaurant_detail', id=restaurant.id)
    else:
        # ⬇️ 'RestaurantForm' (폼 설계도)을 사용합니다.
        form = RestaurantForm() # ⬅️ GET 요청 시 빈 폼

    context = {'form': form}

    # ⬇️ 'restaurant_form.html' 파일을 화면에 보여줍니다.
    return render(request, 'web/restaurant_form.html', context)


def restaurant_reviews(request, id):
    # (신규) GET, POST /restaurant/{id}/reviews
    # restaurant = get_object_or_404(Restaurant, pk=id)

    if request.method == 'POST':
        # (신규) POST : 리뷰 내용 저장 (로그인 필요)
        # @login_required 데코레이터를 이 함수에 붙이거나,
        # if not request.user.is_authenticated: ... 등으로 체크
        pass  # ⬅️ 여기에 리뷰 "저장" 로직 구현

    # GET: 후기 목록 화면
    # reviews = Review.objects.filter(restaurant=restaurant)
    # context = {'restaurant': restaurant, 'reviews': reviews}
    # return render(request, 'web/restaurant_reviews.html', context)
    pass  # ⬅️ 여기에 리뷰 "목록" 로직 구현


@login_required  # 명세서: "로그인 필요"
def review_write_form(request, id):
    # (신규) GET /restaurant/{id}/reviews/write : 리뷰 작성 폼
    # restaurant = get_object_or_404(Restaurant, pk=id)
    # context = {'restaurant': restaurant}
    # return render(request, 'web/review_write_form.html', context)
    pass  # ⬅️ 여기에 리뷰 "작성 폼" 로직 구현