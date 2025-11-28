from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model, logout
from django.contrib import messages

def logout_view(request):
    """
    GET/POST 모두 허용하는 로그아웃 뷰
    """
    logout(request)
    return redirect('/')  # 메인 페이지로 리다이렉트

def register(request):
    if request.method == 'POST':
        # 1. HTML form의 name 속성으로 데이터 가져오기
        login_id = request.POST.get('loginId')  # 프론트: loginId -> 백엔드 변수
        password = request.POST.get('password')
        password_confirm = request.POST.get('passwordConfirm')
        nickname = request.POST.get('nickname')
        job = request.POST.get('job')
        join_path_input = request.POST.get('joinPath')  # 프론트: joinPath

        # 2. 유효성 검사 (예시)
        if password != password_confirm:
            # 에러 메시지를 담아서 다시 폼으로 보냄
            return render(request, 'register.html', {'error_message': '비밀번호가 일치하지 않습니다.'})

        User = get_user_model()  # CustomUser 모델 가져오기

        # 아이디 중복 검사
        if User.objects.filter(username=login_id).exists():
            return render(request, 'register.html', {'error_message': '이미 존재하는 아이디입니다.'})

        # 3. 회원 생성 (Mapping 발생 구간)
        try:
            user = User.objects.create_user(
                username=login_id,  # ★ 중요: loginId를 username 필드에 저장
                password=password,
                nickname=nickname,
                job=job,
                join_path=join_path_input  # ★ 중요: joinPath를 join_path 필드에 저장
            )
            # 회원가입 후 로그인 페이지로 이동
            return redirect('login')

        except Exception as e:
            # 기타 에러 처리
            return render(request, 'web/register.html', {'error_message': f'가입 중 오류가 발생했습니다: {e}'})

    # GET 요청일 경우 회원가입 페이지 보여주기
    return render(request, 'web/register.html')