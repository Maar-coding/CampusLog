# 1. 요청하신 Python 3.10.4 버전 이미지
FROM python:3.10.4-slim

# 2. 환경 변수 설정
ENV PYTHONTDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# 3. 작업 디렉터리 설정
WORKDIR /app

# 4. 의존성 파일 복사
COPY requirements.txt .

# 5. 의존성 설치
# (!! 경고: 이 단계에서 빌드 오류가 발생할 확률이 높습니다 !!)
RUN pip install -r requirements.txt

# 6. 소스 코드 복사
COPY . .