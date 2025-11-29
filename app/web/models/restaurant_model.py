from django.db import models
from django.utils import timezone
from datetime import time
from django.conf import settings  # settings.py의 AUTH_USER_MODEL을 가져오기 위함
from .base_model import User

class Restaurant(models.Model):
    """
    식당 모델
    """
    # 카테고리 선택을 위한 CHOICES 추가
    CATEGORY_CHOICES = [
        ('restaurant', '식당'),
        ('cafe', '카페'),
        ('play', '놀거리'),
    ]

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
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='restaurant')
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
        현재 시간이 영업시간 안인지 + 오늘이 휴무일인지 체크
        """
        # 현재 시간(타임존 반영)
        now = timezone.localtime()
        current_time = now.time()

        # 오늘 요일을 DAY_CHOICES 코드(MON, TUE...) 로 변환
        weekday_codes = ['MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT', 'SUN']
        today_code = weekday_codes[now.weekday()]   # 0=월 -> 'MON'

        # 1) 휴무 요일이면 무조건 영업 종료
        if self.holiday and self.holiday == today_code:
            return False

        # 2) 일반적인 경우: 같은 날 안에서 영업 종료 (예: 09:00 ~ 22:00)
        if self.open_time < self.close_time:
            return self.open_time <= current_time < self.close_time

        # 3) 자정을 넘기는 경우 (예: 18:00 ~ 02:00)
        #    → open_time 이후 자정까지 또는 자정~close_time 까지
        else:
            return current_time >= self.open_time or current_time < self.close_time

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
    title = models.CharField(max_length=200, default='')
    content = models.TextField(default='')
    rating = models.PositiveSmallIntegerField(default=3)
    image = models.ImageField(upload_to='reviews/%Y/%m/%d/', null=True, blank=True)  # ⭐ 추가
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
    통합 커뮤니티 게시글 모델
    """
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    title = models.CharField(max_length=255)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    images = models.ImageField(upload_to='board', null=True, blank=True)

    def __str__(self):
        return f"{self.title} (작성자: {self.author.username})"


class PostLike(models.Model):
    """
    게시글 좋아요 모델
    """
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='likes')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('post', 'user')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} likes {self.post.title}"


class Comment(models.Model):
    """
    댓글 모델
    """
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"{self.author.username}: {self.content[:20]}"
