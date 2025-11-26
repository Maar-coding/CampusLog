from web.models import Restaurant, Menu
from django import forms
from web.models import Review
from web.models import Post


# (기존 RestaurantForm이 있다면 그대로 두세요)

class MenuForm(forms.ModelForm):
    class Meta:
        model = Menu
        # restaurant 필드는 URL에서 식당 ID를 받아 처리하므로 폼에서는 제외합니다.
        fields = ['name', 'price', 'image_url']

        labels = {
            'name': '메뉴 이름',
            'price': '가격 (원)',
            'image_url': '메뉴 이미지 URL',
        }

        # 🎨 CSS 클래스('form_input')를 여기서 미리 적용합니다.
        # 템플릿에서 {{ form.name }}만 써도 스타일이 적용됩니다.
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form_input',
                'placeholder': '예: 김치찌개'
            }),
            'price': forms.NumberInput(attrs={
                'class': 'form_input',
                'placeholder': '숫자만 입력해 주세요'
            }),
            'image_url': forms.URLInput(attrs={
                'class': 'form_input',
                'placeholder': 'https://...'
            }),
        }

class RestaurantForm(forms.ModelForm):
    """
    식당 등록을 위한 모델 폼 (관리자용)
    """

    class Meta:
        model = Restaurant
        # 사용자가 입력할 필드 목록
        fields = ['name', 'address', 'open_time', 'close_time', 'holiday', 'phone', 'lat', 'lng','category', 'image_url']

        # 폼 필드에 대한 추가 설정 (라벨 한글화)
        labels = {
            'name': '식당 이름',
            'address': '주소',
            'open_time': '오픈 시간',
            'close_time': '마감 시간',
            'holiday': '휴무일',
            'phone': '전화번호',
            'lat': '위도',
            'lng': '경도',
            'category': '카테고리',
            'image_url': '대표 이미지 URL',
        }

        # 폼 위젯 설정
        widgets = {
            # HTML5의 time picker를 사용
            'open_time': forms.TimeInput(attrs={'type': 'time', 'value': '09:00'}),
            'close_time': forms.TimeInput(attrs={'type': 'time', 'value': '22:00'}),
            'address': forms.TextInput(attrs={'placeholder': '예) 서울특별시 강남구'}),
            'phone': forms.TextInput(attrs={'placeholder': '예) 02-1234-5678'}),
            'image_url': forms.URLInput(attrs={'placeholder': '예) https://.../image.jpg'}),
        }


# web/forms.py


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        # 사용자가 직접 입력해야 하는 필드만 나열 (작성자, 식당 정보는 뷰에서 자동으로 넣음)
        fields = ['rating', 'content']

        # (선택 사항) 위젯 설정으로 HTML 스타일링
        widgets = {
            'rating': forms.Select(attrs={'class': 'form_select'}),
            'content': forms.Textarea(attrs={'class': 'form_input', 'rows': 5, 'placeholder': '솔직한 후기를 남겨주세요.'}),
        }
        labels = {
            'rating': '별점',
            'content': '후기 내용',
        }

#게시글 작성 폼 추가
class PostForm(forms.ModelForm):
    """게시판 글 작성 폼"""

    class Meta:
        model = Post
        fields = ['title', 'content']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '제목을 입력하세요'
            }),
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 10,
                'placeholder': '내용을 입력하세요'
            }),
        }