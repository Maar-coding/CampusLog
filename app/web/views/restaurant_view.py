from web.forms import RestaurantForm
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from web.models import Restaurant, Review
from web.forms import ReviewForm, MenuForm  # forms.py를 만들어야 합니다 (아래 설명)
from django.db.models import Avg, Count
from django.core.paginator import Paginator
from django.http import JsonResponse


# 1. 식당 선택 뷰 (리스트 보여주기)
def restaurant_select(request):
    # 모든 식당을 가져옵니다. (최신순 정렬)
    restaurants = Restaurant.objects.all().order_by('-created_at')
    return render(request, 'web/restaurant_select.html', {'restaurants': restaurants})


# 2. 메뉴 등록 뷰 (선택한 식당에 메뉴 추가)
def menu_create(request, restaurant_id):
    restaurant = get_object_or_404(Restaurant, pk=restaurant_id)

    if request.method == 'POST':
        form = MenuForm(request.POST)
        if form.is_valid():
            menu = form.save(commit=False)
            menu.restaurant = restaurant  # URL에서 받은 식당 ID 연결
            menu.save()

            # ⭐ 핵심 로직: 어떤 버튼을 눌렀느냐에 따라 갈림길
            if 'add_another' in request.POST:
                # [저장하고 계속 추가] -> 같은 페이지로 리다이렉트 (새로고침 효과)
                return redirect('menu_create', restaurant_id=restaurant.id)
            else:
                # [저장하고 종료] -> 식당 선택 리스트로 이동
                return redirect('restaurant_select')
    else:
        form = MenuForm()

    context = {
        'form': form,
        'restaurant': restaurant,
        # 이미 등록된 메뉴들도 보여주면 편하겠죠?
        'existing_menus': restaurant.menus.all()
    }
    return render(request, 'web/menu_create.html', context)

def restaurant_list_api(request):
    restaurants = Restaurant.objects.all()

    data = []
    for r in restaurants:
        # 2. 카테고리에 따라 이미지 자동 선택 (프론트엔드 로직을 백엔드로 이동)
        img_src = "../../static/img/restaurant.png"
        if r.category == 'cafe':
            img_src = "../../static/img/cafe.png"
        elif r.category == 'play':
            img_src = "../../static/img/play.png"

        # 3. 프론트엔드 'storeData' 구조와 똑같이 만듭니다.
        data.append({
            'id': r.id,
            'name': r.name,
            'lat': r.lat,
            'lng': r.lng,
            'image': img_src,
            'tags': [r.category]  # 프론트엔드는 배열 형태의 tags를 원함
        })

    # 4. JSON으로 변환하여 반환
    return JsonResponse(data, safe=False)




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

    return render(request, 'web/restaurant_panel.html', context)


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
            return redirect('restaurant_select')
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

    return render(request, 'web/reviews_panel.html', context)





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