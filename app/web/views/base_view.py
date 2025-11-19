import json
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.shortcuts import render, get_object_or_404
from web.models import UserLocation


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