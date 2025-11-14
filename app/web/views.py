from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages # (선택) 알림 메시지용

def index(request):
    # 'front/index.html' 템플릿을 렌더링
    return render(request, 'web/index.html')


def signup(request):
    if request.method == 'POST':
        # 1. 사용자가 데이터를 POST 방식으로 보냈을 때 (회원가입 버튼 클릭)
        form = UserCreationForm(request.POST)

        if form.is_valid():
            # 2. 폼이 유효하면
            user = form.save()  # 사용자를 DB에 저장
            login(request, user)  # 해당 사용자로 즉시 로그인

            # (선택) 환영 메시지
            messages.success(request, f'환영합니다, {user.username}님!')

            # 3. 로그인 성공 시 이동할 메인 페이지로 리다이렉트
            return redirect('/')  # LOGIN_REDIRECT_URL과 동일

    else:
        # 4. GET 방식으로 페이지에 처음 접속했을 때 (빈 폼)
        form = UserCreationForm()

    # 5. POST에서 폼이 유효하지 않거나, GET 요청일 경우
    # 'form' 변수에 담긴 (오류 메시지가 포함된 폼 또는 빈 폼)을 템플릿으로 전달
    return render(request, 'web/signup.html', {'form': form})