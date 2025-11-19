from django.db import models
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    # 기본 필드(username, password)는 이미 존재함
    # HTML의 'loginId'는 Django의 'username' 필드에 매핑할 예정입니다.

    nickname = models.CharField(max_length=50)

    # 직업 선택지 (DB저장값, 보여줄값)
    JOB_CHOICES = [
        ('STUDENT', '학부생'),
        ('GRAD', '대학원생'),
        ('PROFESSOR', '교수님'),
    ]
    job = models.CharField(max_length=20, choices=JOB_CHOICES, blank=True, null=True)

    # 가입 경로 선택지
    PATH_CHOICES = [
        ('SEARCH', '검색'),
        ('AD', '광고'),
        ('FRIEND', '지인 추천'),
        ('ETC', '기타'),
    ]
    # Python 변수명 규칙(snake_case)에 따라 join_path로 만듭니다.
    join_path = models.CharField(max_length=20, choices=PATH_CHOICES, blank=True, null=True)

    def __str__(self):
        return self.username