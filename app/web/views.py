import json
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.shortcuts import render, get_object_or_404
from .models import Restaurant, Menu, Review
from django.db.models import Avg, Count
from .forms import RestaurantForm

# (중요) 이전에 만든 UserLocation 모델 임포트
from .models import UserLocation


# (필요) 식당, 리뷰, 게시글 모델도 임포트해야 합니다 (이름은 예시)
# from .models import Restaurant, Review, Post

# ==================================================================
# 1. 메인 페이지 뷰 (HTML 렌더링)
# ==================================================================

def index(request):
    # (기존) GET / : 메인 페이지 (지도 화면)
    return render(request, 'web/index.html')

def test_page(request):
    return render(request, 'web/test.html')

def search_page(request):
    # (신규) GET /search : 검색 화면
    # ... 검색 로직 ...
    context = {}
    return render(request, 'web/search_panel.html')  # 'search.html' 템플릿 예시


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


# ==================================================================
# 2. 게시판 뷰 (HTML 렌더링)
# ==================================================================
def board(request):
    return render(request, 'web/board.html')



def board_list(request, category):
    # (신규) GET, POST /board/{category}

    if request.method == 'POST':
        # (신규) POST : 작성된 게시글을 저장 (로그인 필요)
        pass  # ⬅️ 여기에 게시글 "저장" 로직 구현

    # GET: 게시판 목록 화면
    # posts = Post.objects.filter(category=category)
    # context = {'category': category, 'posts': posts}
    # return render(request, 'web/board_list.html', context)
    pass  # ⬅️ 여기에 게시글 "목록" 로직 구현


def post_detail(request, category, postid):
    # (신규) GET /board/{category}/{postid} : 게시글 상세 화면
    # post = get_object_or_404(Post, pk=postid, category=category)
    # context = {'post': post}
    # return render(request, 'web/post_detail.html', context)
    pass  # ⬅️ 여기에 게시글 "상세" 로직 구현


@login_required  # 명세서: "로그인 필요"
def post_write_form(request, category):
    # (신규) GET /board/{category}/write : 게시글 작성 폼
    # context = {'category': category}
    # return render(request, 'web/post_write_form.html', context)
    pass  # ⬅️ 여기에 게시글 "작성 폼" 로직 구현


# ==================================================================
# 3. 인증 뷰 (HTML 렌더링)
# ==================================================================

def register(request):
    # (기존) GET, POST /register (회원가입 폼 및 처리)
    # (참고: urls.py에서 'register'라는 name으로 이 뷰를 사용 중)
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'환영합니다, {user.username}님!')
            return redirect('/')
    else:
        form = UserCreationForm()
    return render(request, 'web/register.html', {'form': form})


# (참고: /login, /logout은 project/urls.py에서 Django 내장 뷰(auth_views)를
#  사용하고 있으므로 여기서는 만들 필요가 없습니다.)

# ==================================================================
# 4. API 뷰 (JSON 응답)
# ==================================================================

def user_locations_api(request):
    # (기존) GET /api/locations
    locations = UserLocation.objects.filter(lat__isnull=False, lng__isnull=False)
    data = list(locations.values('lat', 'lng', 'user__username'))
    return JsonResponse(data, safe=False)


@login_required
@require_POST  # POST 요청만 받도록 설정
def update_user_location_api(request):
    # (기존) POST /api/update_location
    try:
        data = json.loads(request.body)
        lat = data.get('lat')
        lng = data.get('lng')
        if lat is None or lng is None:
            return JsonResponse({'status': 'fail', 'message': 'Lat/Lng missing'}, status=400)

        UserLocation.objects.update_or_create(
            user=request.user,
            defaults={'lat': lat, 'lng': lng}
        )
        return JsonResponse({'status': 'success'})
    except json.JSONDecodeError:
        return JsonResponse({'status': 'fail', 'message': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'status': 'fail', 'message': str(e)}, status=500)


def restaurant_list_api(request):
    # (신규) GET /api/restaurants : 식당 목록 조회
    # (Serializer를 사용하는 것을 권장합니다)
    # restaurants = Restaurant.objects.all()
    # serializer = RestaurantSerializer(restaurants, many=True)
    # return JsonResponse(serializer.data, safe=False)
    pass  # ⬅️ 여기에 식당 목록 API 로직 구현


def restaurant_detail_api(request, id):
    # (신규) GET /api/restaurants/{id} : 식당 상세 조회
    # (Serializer를 사용하는 것을 권장합니다)
    # restaurant = get_object_or_404(Restaurant, pk=id)
    # serializer = RestaurantSerializer(restaurant)
    # return JsonResponse(serializer.data)
    pass  # ⬅️ 여기에 식당 상세 API 로직 구현