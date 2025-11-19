from django.db import models
from django.conf import settings

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

# 'django.contrib.auth.models.User' 대신 settings.AUTH_USER_MODEL 사용을 권장합니다.
User = settings.AUTH_USER_MODEL