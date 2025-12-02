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
            'name': '업체 이름',
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
        fields = ['title', 'content', 'rating', 'image']  # title, image 포함
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '리뷰 제목을 입력하세요'
            }),
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': '리뷰 내용을 입력하세요',
                'rows': 5
            }),
            'rating': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'max': 5
            }),
            'image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            })
        }
        labels = {
            'title': '제목',
            'content': '내용',
            'rating': '별점 (1~5)',
            'image': '사진 (선택)'
        }

#게시글 작성 폼 추가
class PostForm(forms.ModelForm):
    """게시판 글 작성 폼"""

    class Meta:
        model = Post
        fields = ['title', 'content', 'images']  # ← images 추가!
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
            'images': forms.FileInput(attrs={  # ← 추가
                'class': 'form-control',
                'accept': 'image/*'
            })
        }