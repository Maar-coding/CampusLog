from django.db import models
from django.conf import settings  # settings.py의 AUTH_USER_MODEL을 가져오기 위함


# settings.AUTH_USER_MODEL은 Django의 기본 User 모델을 가리킵니다.
# (django.contrib.auth.models.User)


class UserLocation(models.Model):
    """
    (기존 모델) 사용자의 실시간 위치 정보를 저장합니다.
    User 모델과 1:1 관계입니다.
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,  # 유저가 탈퇴하면 위치 정보도 삭제
        primary_key=True  # 유저를 이 모델의 기본 키로 사용
    )
    lat = models.FloatField(null=True, blank=True)  # 위도
    lng = models.FloatField(null=True, blank=True)  # 경도

    def __str__(self):
        return f"{self.user.username}의 위치 ({self.lat}, {self.lng})"


class Restaurant(models.Model):
    """
    (신규) 식당 정보 모델
    /restaurant/{id}, /api/restaurants 에서 사용됩니다.
    """
    name = models.CharField(max_length=255)
    address = models.CharField(max_length=255, null=True, blank=True)
    # 식당 위치도 지도에 표시하기 위해 lat, lng 추가
    lat = models.FloatField(null=True, blank=True)
    lng = models.FloatField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Review(models.Model):
    """
    (신규) 식당 리뷰 모델
    /restaurant/{id}/reviews 에서 사용됩니다.
    """
    # 1. '어떤' 식당에 대한 리뷰인지 (Restaurant과 N:1 관계)
    restaurant = models.ForeignKey(
        Restaurant,
        on_delete=models.CASCADE,  # 식당이 삭제되면 리뷰도 삭제
        related_name='reviews'  # restaurant.reviews로 리뷰 목록을 가져올 수 있음
    )

    # 2. '누가' 썼는지 (User와 N:1 관계)
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE  # 유저가 탈퇴하면 리뷰도 삭제
    )

    content = models.TextField()
    rating = models.SmallIntegerField()  # 별점 (예: 1~5)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.restaurant.name} - {self.author.username} ({self.rating}점)"


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