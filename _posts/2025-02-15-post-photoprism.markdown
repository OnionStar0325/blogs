---
layout: post
title:  PhotoPrism 셋업방법 (WSL2 + CloudFlare Tunnel + Nginx)
categories: it
---

---

# **Windows SubLinuxSystem(WSL2) 환경에서 Podman-Compose를 사용하여 PhotoPrism을 구동하고, Nginx를 Reverse Proxy로 설정하여 외부에서 안전하게 접근할 수 있도록 구성하는 방법을 기록한다.**

## **사전 준비 사항**
    - Debian 12 버전이 설치된 WSL2 시스템
    - nginx
    - podman
    - podman-compose
    - DNS

> podman-compose는 Debian 12(Bookworm) 버전부터 패키지매니저에서 지원한다.

## **시스템 구성도**

```mermaid!
graph LR
    A[사용자 웹 브라우저] -->|HTTPS Request| B[Cloudflare Tunnel]
    B -->|Local Request| C[Nginx Reverse Proxy]
    C -->|Proxy to Container| D[PhotoPrism 컨테이너]
```

## **구성 절차**

### **PhotoPrism 구성**

1. **PhotoPrism Docker Compose 파일 다운로드**:
    - PhotoPrism 공식 사이트에서 제공하는 구성 파일 다운로드:

    ```bash
    mkdir -p ~/apps/photoprism && cd ~/apps/photoprism
    wget https://dl.photoprism.app/podman/docker-compose.yml
    ```

2. **구성 파일 수정**:
    - `docker-compose.yml` 파일을 열어 필요한 설정 변경:

        ```yaml
        ports:
        - "2342:2342" # HTTP 포트 설정

        environment:
        PHOTOPRISM_ADMIN_PASSWORD: "your_secure_password" # 관리자 비밀번호 설정
        PHOTOPRISM_ORIGINALS_LIMIT: 50000 # 원본 파일 크기 제한 (MB)

        volumes:
        - "~/Pictures:/photoprism/originals" # 원본 사진 경로 연결
        - "./storage:/photoprism/storage" # 캐시 및 데이터 저장소 경로 연결
        ```
    - 경로를 WSL 내 적절한 디렉토리로 변경한다.

---

### **PhotoPrism 실행**

1. **Podman-Compose로 컨테이너 실행**:
    ```bash
    podman-compose up -d
    ```
2. **서비스 상태 확인**:
    ```bash
    podman-compose ps
    ```
3. **브라우저에서 접속**:
    - http://localhost:2342 에 접속하여 PhotoPrism 인터페이스를 확인한다.

---

### **업데이트 및 유지보수**

1. **PhotoPrism 업데이트**:
    ```bash
    podman-compose pull
    podman-compose down && podman-compose up -d
    ```
2. **컨테이너 관리**:
    - 중지: `podman-compose down`
    - 재시작: `podman-compose up -d`

---

### **Nginx를 사용한 Reverse Proxy 설정**


PhotoPrism에 대한 Reverse Proxy 설정을 포함한 Nginx 구성 파일을 생성한다.

1. `/etc/nginx/sites-available/photoprism` 파일 생성:

    ```bash
    sudo nano /etc/nginx/sites-available/photoprism
    ```

2. 설정 내용 작성

    ```nginx
    server {
        listen 3000 ssl; # Cloudflare 터널로 수신할 포트를 작성한다. http 형식으로 통신할 경우 ssl 키워드는 제거한다.
        listen [::]:3000 ssl; # Cloudflare 터널로 수신할 포트를 작성한다. http 형식으로 통신할 경우 ssl 키워드는 제거한다.
        server_name photos.mydomain.com;
        client_max_body_size 500M;

        # 인증키 정보는 Cloudflare 터널과 https 로 통신할 경우 작성한다.
        ssl_certificate /etc/ssl/cert.pem;
        ssl_certificate_key /etc/ssl/key.pem;
        ssl_client_certificate /etc/ssl/cloudflare.crt;

        location / {
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header Host $host;

            proxy_pass http://localhost:2342;

            proxy_buffering off;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
        }
    }
    ```

3. 심볼릭 링크 생성:
    ```bash
    sudo ln -s /etc/nginx/sites-available/photoprism /etc/nginx/sites-enabled/
    ```

4. Nginx 서비스 재시작

    구성을 적용하기 위해 Nginx를 재시작

    ```bash
    sudo nginx -t  # 구성 파일 테스트
    sudo systemctl restart nginx
    ```

---

### **Cloudflare tunnel 설정**

1. Cloudflare tunnel을 생성/수정한다.
    ```text
        Tunnel과 nginx가 http로 통신함. http://localhost:3000
        Tunnel과 nginx가 https로 통신함. https://localhost:3000
    ```
2. 웹 브라우저로 DNS로 접속하여, 서비스 동작여부를 확인한다. 