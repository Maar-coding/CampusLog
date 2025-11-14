import os
import psycopg2
import time
import sys
import subprocess  # os.execvp를 사용하기 위해 os를 임포트 (sys도 필요)

# .env 파일에서 설정한 환경 변수들을 읽어옵니다.
db_name = os.environ.get('DB_NAME')
db_user = os.environ.get('DB_USER')
db_pass = os.environ.get('DB_PASSWORD')
db_host = os.environ.get('DB_HOST')  # 'db'
db_port = os.environ.get('DB_PORT', 5432)

print("DB 연결 테스트를 시작합니다...")
print(f"Host: {db_host}, Port: {db_port}, DB: {db_name}, User: {db_user}")

retries = 10  # 대기 시간 10회 (총 50초)
while retries > 0:
    try:
        # DB 연결 시도
        conn = psycopg2.connect(
            dbname=db_name,
            user=db_user,
            password=db_pass,
            host=db_host,
            port=db_port
        )
        conn.close()

        # 연결 성공
        print("\n✅ [성공] PostgreSQL DB에 성공적으로 연결되었습니다.")

        # (중요) 연결이 성공하면, runserver 명령어를 실행합니다.
        # os.execvp는 현재 스크립트 프로세스를 새 프로세스(runserver)로 대체합니다.
        # 이것이 컨테이너의 메인 프로세스가 됩니다.
        print("Django 서버(runserver)를 시작합니다...")

        # Dockerfile의 command를 대체할 명령어
        args = ['python', 'manage.py', 'runserver', '0.0.0.0:8000']
        os.execvp(args[0], args)

        # os.execvp는 실행되면 아래 코드는 도달하지 않습니다.
        break

    except psycopg2.OperationalError as e:
        print(f"\n❌ [실패] DB 연결 실패. (에러: {e})")
        print("DB 컨테이너가 아직 준비중일 수 있습니다. 5초 후 재시도합니다...")
        retries -= 1
        time.sleep(5)

    except Exception as e:
        print(f"\n❌ [오류] 예기치 못한 오류 발생: {e}")
        sys.exit(1)  # 오류 발생 시 스크립트 종료 (컨테이너 종료)

if retries == 0:
    print("\n❌ [최종 실패] DB에 연결할 수 없습니다. .env 파일과 DB 컨테이너 로그를 확인하세요.")
    sys.exit(1)  # 최종 실패 시 컨테이너 종료