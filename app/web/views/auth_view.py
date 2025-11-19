from django.shortcuts import redirect
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.shortcuts import render

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