import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.1/howto/deployment/checklist/

# !! SECRET_KEY를 환경 변수에서 읽어오도록 수정 !!
SECRET_KEY = os.environ.get('SECRET_KEY')

# !! DEBUG 모드를 환경 변수에서 읽어오도록 수정 !!
DEBUG = os.environ.get('DEBUG', '0') == '1'

ALLOWED_HOSTS = ['*'] # 개발 중에는 모든 호스트 허용


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'web',  # <-- 'web' 앱 등록
]

# app/campuslog_project/settings.py

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware', # <- 관리자(admin)에 필요
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware', # <- 관리자(admin)에 필요
    'django.contrib.messages.middleware.MessageMiddleware', # <- 관리자(admin)에 필요
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'campuslog_project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [], # 'web' 앱 내부의 templates 폴더를 사용
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'campuslog_project.wsgi.application'


# Database
# !! docker-compose.yml의 환경 변수를 사용하도록 수정 !!
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME'),
        'USER': os.environ.get('DB_USER'),
        'PASSWORD': os.environ.get('DB_PASSWORD'),
        'HOST': os.environ.get('DB_HOST'),
        'PORT': os.environ.get('DB_PORT'),
    }
}


# Password validation
# ... (기본 설정 유지) ...


# Internationalization
# ... (기본 설정 유지) ...
LANGUAGE_CODE = 'ko-kr'
TIME_ZONE = 'Asia/Seoul'
USE_I18N = True
USE_L10N = True
USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.1/howto/static-files/

STATIC_URL = '/static/'

# 미디어 파일 설정 (사용자 업로드 파일) - 여기에 추가!
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

LOGIN_REDIRECT_URL = '/'  # 로그인 성공 시 이동할 URL (메인 페이지)
LOGOUT_REDIRECT_URL = '/' # 로그아웃 성공 시 이동할 URL (메인 페이지)
AUTH_USER_MODEL = 'web.CustomUser'
# Default primary key field type
# (Django 3.1에는 이 설정이 없습니다. 3.2부터 추가됨)