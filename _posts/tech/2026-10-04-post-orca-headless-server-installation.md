---
layout: post
title: "Orca ADE Headless Server 설치 및 설정 가이드"
date: 2026-10-04 15:30:00 +0900
categories: tech
tags: [orca, ubuntu, headless, server, devops]
---

본 문서는 Ubuntu Linux (ARM64/aarch64) 환경의 서버에 **Orca ADE (Agent Development Environment)** Headless 서버를 설치하고 systemd 서비스로 등록 및 운영하는 절차를 정리한 문서입니다.

---

## 1. 서버 환경 정보

- **OS**: Ubuntu 20.04.6 LTS (Focal Fossa)
- **아키텍처**: aarch64 (ARM64)
- **기본 포트**: 4200 (TCP)

---

## 2. 필수 의존성 패키지 설치

Orca ADE는 Electron 기반 AppImage로 배포되며, GUI 환경이 없는 Headless 서버 환경에서는 가상 프레임버퍼(xvfb), libfuse2, 그리고 GUI 렌더링에 필요한 공유 라이브러리가 필요합니다.

```bash
sudo apt-get update
sudo apt-get install -y \
  curl file jq xvfb zlib1g-dev ca-certificates git \
  libfuse2 libgtk-3-0 libnss3 libatk1.0-0 libatk-bridge2.0-0 libgbm1 libasound2 \
  libxtst6 libcups2 libdrm2 libxkbcommon0 libpango-1.0-0 libcairo2 \
  libxcomposite1 libxdamage1 libxfixes3 libxrandr2 libxrender1 libx11-xcb1 \
  libxcb-dri3-0 libxss1
```

---

## 3. Orca ADE 바이너리 다운로드 및 설치

GitHub 릴리즈에서 최신 ARM64 AppImage 바이너리를 다운로드하여 실행 권한을 부여하고, 전역 명령어 심볼릭 링크를 생성합니다.

```bash
# 설치 디렉토리 생성
sudo mkdir -p /opt/orca

# 최신 ARM64 AppImage 다운로드
sudo curl -fL https://github.com/stablyai/orca/releases/latest/download/orca-linux-arm64.AppImage -o /opt/orca/orca.AppImage

# 실행 권한 부여
sudo chmod +x /opt/orca/orca.AppImage

# 심볼릭 링크 생성 (GNOME orca 화면낭독기와의 충돌 방지를 위해 orca-ide 및 orca로 연결)
sudo ln -sf /opt/orca/orca.AppImage /usr/local/bin/orca-ide
sudo ln -sf /opt/orca/orca.AppImage /usr/local/bin/orca
```

---

## 4. systemd 서비스 등록 및 자동 실행 설정

서버 재부팅 시에도 백그라운드에서 상시 실행될 수 있도록 systemd 서비스로 등록합니다.

### 4.1 서비스 파일 생성 (`/etc/systemd/system/orca.service`)

```ini
[Unit]
Description=Orca ADE Headless Server
After=network.target

[Service]
Type=simple
User=ubuntu
Environment=NODE_ENV=production
Environment=LIBGL_ALWAYS_SOFTWARE=1
ExecStart=/usr/local/bin/orca-ide serve --host 0.0.0.0 --port 4200
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

### 4.2 서비스 활성화 및 시작

```bash
# 데몬 리로드 및 부팅 시 자동 시작 등록
sudo systemctl daemon-reload
sudo systemctl enable orca

# 서비스 시작
sudo systemctl start orca
```

---

## 5. 서비스 상태 및 포트 확인

```bash
# 서비스 상태 확인
sudo systemctl status orca

# 포트 리스닝 확인 (4200 포트)
ss -tulpn | grep 4200

# 실시간 로그 확인
sudo journalctl -u orca -f
```

---

## 6. 서비스 관리 명령어

| 작업 | 명령어 |
| :--- | :--- |
| **상태 확인** | `sudo systemctl status orca` |
| **서비스 재시작** | `sudo systemctl restart orca` |
| **서비스 중지** | `sudo systemctl stop orca` |
| **서비스 시작** | `sudo systemctl start orca` |
| **최근 로그 확인** | `sudo journalctl -u orca -n 50 --no-pager` |

---

## 7. 로컬 PC에서 클라이언트 연결 방법

### 방법 1. SSH 포트 포워딩 (권장)

로컬 PC의 터미널에서 4200 포트를 포워딩합니다:

```bash
ssh -L 4200:localhost:4200 ubuntu@<서버_IP_또는_호스트명>
```

### 방법 2. 웹 UI 접속 및 페어링

1. 웹 브라우저에서 `http://localhost:4200/web-index.html` 로 접속합니다.
2. 페어링 토큰 및 URL은 서버 로그(`sudo journalctl -u orca -n 30`)에 출력된 Pairing URL 또는 Web client URL 해시 파라미터를 사용합니다.

---

## 8. Antigravity CLI (`agy`) 설치 정보

서버에 Antigravity CLI가 함께 설치되었습니다.

```bash
# 공식 설치 스크립트 실행
curl -fsSL https://antigravity.google/cli/install.sh | bash

# 전역 심볼릭 링크 설정
sudo ln -sf /home/ubuntu/.local/bin/agy /usr/local/bin/agy
sudo ln -sf /home/ubuntu/.local/bin/agy /usr/local/bin/antigravity
```

### 실행 확인
- `agy --version` 또는 `antigravity --version`
- 실행: `agy`

---

## 9. 페어링 코드 및 접속 URL 확인 방법

Orca Headless 서버 구동 시 생성되는 페어링 코드(Pairing URL) 및 Web Client URL은 systemd 서비스 로그에서 확인할 수 있습니다.

```bash
# 페어링 URL 및 전체 접속 URL 확인
sudo journalctl -u orca | grep -E 'Pairing URL|Web client URL' | tail -n 2

# 또는 최근 로그 전체 확인
sudo journalctl -u orca -n 30 --no-pager
```
