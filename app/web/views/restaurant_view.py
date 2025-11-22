from web.forms import RestaurantForm
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from web.models import Restaurant, Review
from web.forms import ReviewForm  # forms.py를 만들어야 합니다 (아래 설명)
from django.db.models import Q, Avg, Count
from django.core.paginator import Paginator


def restaurant_list(request):
    """
    GET /restaurant : 식당 검색 페이지
    - 키워드 검색 (이름, 주소)
    - 카테고리 필터링 (식당/디저트/놀거리)
    - 정렬 옵션 (가나다순/별점순/거리순/리뷰수순)
    """
    # 1. 기본 쿼리셋 (평점 평균, 리뷰 개수 포함)
    restaurants = Restaurant.objects.annotate(
        avg_rating=Avg('reviews__rating'),
        review_count=Count('reviews')
    )

    # 2. 키워드 검색
    query = request.GET.get('q', '')
    if query:
        restaurants = restaurants.filter(
            Q(name__icontains=query) | Q(address__icontains=query)
        )

    # 3. 카테고리 필터
    category = request.GET.get('category', '')
    if category:
        restaurants = restaurants.filter(category=category)

    # 4. 정렬 옵션
    sort = request.GET.get('sort', 'name')  # 기본값: 가나다순

    if sort == 'name':
        # 가나다순
        restaurants = restaurants.order_by('name')
    elif sort == 'rating':
        # 별점순 (높은 순)
        restaurants = restaurants.order_by('-avg_rating', '-review_count')
    elif sort == 'review_count':
        # 리뷰 개수순 (많은 순)
        restaurants = restaurants.order_by('-review_count', '-avg_rating')
    elif sort == 'distance':
        # 거리순 - 사용자 위치 필요
        user_lat = request.GET.get('lat')
        user_lng = request.GET.get('lng')

        if user_lat and user_lng:
            try:
                user_lat = float(user_lat)
                user_lng = float(user_lng)

                # 거리 계산을 위해 리스트로 변환 후 정렬
                restaurants_list = list(restaurants)

                def calculate_distance(restaurant):
                    """두 지점 간 거리 계산 (Haversine formula)"""
                    if not restaurant.lat or not restaurant.lng:
                        return float('inf')

                    lat1, lng1 = math.radians(user_lat), math.radians(user_lng)
                    lat2, lng2 = math.radians(restaurant.lat), math.radians(restaurant.lng)

                    dlat = lat2 - lat1
                    dlng = lng2 - lng1

                    a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlng / 2) ** 2
                    c = 2 * math.asin(math.sqrt(a))

                    # 지구 반지름 (km)
                    radius = 6371
                    return radius * c

                restaurants_list.sort(key=calculate_distance)
                restaurants = restaurants_list
            except (ValueError, TypeError):
                # 위치 정보가 잘못된 경우 기본 정렬
                restaurants = restaurants.order_by('name')
        else:
            # 위치 정보가 없으면 기본 정렬
            restaurants = restaurants.order_by('name')
    else:
        # 기본 정렬
        restaurants = restaurants.order_by('name')

    # 5. 페이지네이션
    paginator = Paginator(restaurants, 12)
    page = request.GET.get('page', 1)
    page_obj = paginator.get_page(page)

    # 6. 카테고리 목록
    categories = Restaurant.CATEGORY_CHOICES

    context = {
        'restaurants': page_obj,
        'query': query,
        'selected_category': category,
        'categories': categories,
        'sort': sort,
    }

    return render(request, 'web/restaurant_list.html', context)


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
    """
    GET /restaurant/{id}/reviews : 식당 전체 리뷰 목록 (페이징 + 정렬)
    """

    # 1. 식당 정보 가져오기
    #    리뷰 페이지 상단에도 "OOO 식당의 리뷰 (4.5점)" 처럼 보여주기 위해
    #    평점/개수 정보를 함께 가져옵니다.
    restaurant = get_object_or_404(
        Restaurant.objects.annotate(
            avg_rating=Avg('reviews__rating'),
            review_count=Count('reviews')
        ),
        pk=id
    )

    # 2. 정렬 기준 처리 (Query String 받기)
    #    URL 예시: ?sort=recent (최신순), ?sort=high (높은순), ?sort=low (낮은순)
    sort = request.GET.get('sort', 'recent')  # 기본값은 최신순

    if sort == 'high':
        order_by_field = '-rating'  # 별점 높은 순
    elif sort == 'low':
        order_by_field = 'rating'  # 별점 낮은 순
    else:
        order_by_field = '-created_at'  # 최신 순 (기본)

    # 3. 리뷰 쿼리셋 가져오기
    #    select_related('author'): 작성자 정보(닉네임 등)를 가져올 때
    #    N+1 쿼리 문제를 방지하기 위해 미리 조인합니다.
    reviews_list = restaurant.reviews.select_related('author').order_by(order_by_field)

    # 4. 페이지네이션 (Paginator)
    #    한 페이지당 10개씩 보여주기
    page = request.GET.get('page', '1')
    paginator = Paginator(reviews_list, 10)

    reviews = paginator.get_page(page)

    context = {
        'restaurant': restaurant,
        'reviews': reviews,
        'sort': sort,  # 현재 정렬 기준을 템플릿에 전달 (버튼 활성화용)
    }

    return render(request, 'web/reviews.html', context)





@login_required
def review_write_form(request, id):
    """
    GET/POST /restaurant/{id}/review/write : 리뷰 작성
    - 로그인한 사용자만 접근 가능
    """
    # 1. 어떤 식당에 대한 리뷰인지 확인
    restaurant = get_object_or_404(Restaurant, pk=id)

    # [선택 사항] 중복 리뷰 방지 (한 식당에 한 명당 1개만 가능하게 하려면)
    if Review.objects.filter(restaurant=restaurant, author=request.user).exists():
        messages.error(request, "이미 이 식당에 대한 리뷰를 작성하셨습니다.")
        return redirect('restaurant_detail', id=id)

    if request.method == 'POST':
        # 3. 데이터 저장 요청 (POST)
        form = ReviewForm(request.POST)

        if form.is_valid():
            # commit=False: DB에 바로 저장하지 않고 메모리에만 객체 생성
            review = form.save(commit=False)

            # 누락된 정보 채우기 (작성자, 식당)
            review.author = request.user
            review.restaurant = restaurant

            # 최종 저장
            review.save()

            # 작성 후 상세 페이지로 이동
            return redirect('restaurant_detail', id=id)

    else:
        # 2. 폼 보여주기 요청 (GET)
        form = ReviewForm()

    context = {
        'form': form,
        'restaurant': restaurant
    }
    return render(request, 'web/review_write.html', context)