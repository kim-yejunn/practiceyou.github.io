# 베이스 이미지 설정 (Node.js와 Python이 함께 포함된 이미지 사용)
FROM python:3.12-slim

# Node.js 설치
RUN apt-get update && \
    apt-get install -y curl && \
    curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && \
    apt-get install -y nodejs

# 작업 디렉토리 설정
WORKDIR /app

# 필요한 파일 복사
COPY . .

# Python 및 Node.js 의존성 설치
RUN pip install -r requirements.txt
RUN npm install

# 애플리케이션 실행
CMD ["python", "app.py"]
