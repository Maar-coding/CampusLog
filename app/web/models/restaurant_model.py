from django.db import models
from django.utils import timezone
from datetime import time
from django.conf import settings  # settings.py의 AUTH_USER_MODEL을 가져오기 위함
from .base_model import User

class Restaurant(models.Model):
    """
    식당 모델
    """
    # 요일 선택을 위한 CHOICES
    DAY_CHOICES = [
        ('MON', '월요일'),
        ('TUE', '화요일'),
        ('WED', '수요일'),
        ('THU', '목요일'),
        ('FRI', '금요일'),
        ('SAT', '토요일'),
        ('SUN', '일요일'),
        ]

    name = models.CharField(max_length=100)
    image_url = models.URLField(max_length=500, null=True, blank=True)
    address = models.CharField(max_length=200, default='')
    open_time = models.TimeField(default=time(9, 0))  # 기본값: 오전 9시
    close_time = models.TimeField(default=time(22, 0))  # 기본값: 오후 10시
    holiday = models.CharField(max_length=3, choices=DAY_CHOICES, null=True, blank=True)
    phone = models.CharField(max_length=20, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # 식당 위치도 지도에 표시하기 위해 lat, lng 추가
    lat = models.FloatField(null=True, blank=True)
    lng = models.FloatField(null=True, blank=True)

    def __str__(self):
        return self.name

    @property
    def holiday_display(self):
        """
           템플릿에서 'restaurant.holiday_display'로 사용하기 위한 프로퍼티
            choices의 값을 표시 (예: 'MON' -> '월요일')
        """
        return self.get_holiday_display()

    @property
    def is_open(self):
        """
            템플릿에서 'restaurant.is_open'으로 현재 영업 상태 확인
        """
        now = timezone.now().time()
        today_weekday = timezone.now().strftime('%a').upper()  # MON, TUE ...

            # 오늘이 휴무일인지 확인
        if self.holiday == today_weekday:
          return False

        # 영업 시간 확인
        return self.open_time <= now <= self.close_time

        # 참고: 템플릿의 'avg_rating'과 'review_count'는
        # 뷰(views.py)에서 annotate를 통해 동적으로 추가하는 것이 효율적입니다.

class Menu(models.Model):
    """
    식당의 메뉴 모델
    """
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='menus')
    name = models.CharField(max_length=100)
    image_url = models.URLField(max_length=500, null=True, blank=True)
    price = models.PositiveIntegerField()

    def __str__(self):
        return f'[{self.restaurant.name}] {self.name}'

class Review(models.Model):
    """
    식당 후기 모델
    """
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='reviews')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200, default='')  # 기본값: 빈 문자열
    content = models.TextField(default='')  # 기본값: 빈 문자열
    rating = models.PositiveSmallIntegerField(default=3)  # 기본값: 3점
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']  # 최신순 정렬

    def __str__(self):
        return f'[{self.restaurant.name}] {self.title} ({self.rating}점)'

    @property
    def author_nickname(self):
        """
        템플릿에서 'review.author_nickname'으로 사용
        User 모델에 nickname 필드가 없다면 username을 반환합니다.
        """
        # User 모델에 'nickname' 필드가 있다면
        # return self.author.nickname
        # 없다면 username을 사용합니다.
        return self.author.username














class Post(models.Model):
    """
    (신규) 커뮤니티 게시글 모델
    /board/{category} 에서 사용됩니다.
    """
    # 1. '누가' 썼는지 (User와 N:1 관계)
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    # 2. '어느' 게시판인지 (URL의 {category}에 해당)
    category = models.CharField(max_length=100)  # 예: "notice", "free"

    title = models.CharField(max_length=255)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"[{self.category}] {self.title} (작성자: {self.author.username})"