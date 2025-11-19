from django import forms
from web.models import Restaurant
from django import forms
from web.models import Review

class RestaurantForm(forms.ModelForm):
    """
    식당 등록을 위한 모델 폼 (관리자용)
    """

    class Meta:
        model = Restaurant
        # 사용자가 입력할 필드 목록
        fields = ['name', 'address', 'open_time', 'close_time', 'holiday', 'phone', 'image_url']

        # 폼 필드에 대한 추가 설정 (라벨 한글화)
        labels = {
            'name': '식당 이름',
            'address': '주소',
            'open_time': '오픈 시간',
            'close_time': '마감 시간',
            'holiday': '휴무일',
            'phone': '전화번호',
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