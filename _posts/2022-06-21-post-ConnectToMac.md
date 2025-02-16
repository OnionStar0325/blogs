---
layout: post
title: 외부에 공개되어 있지 않은 Mac에 ssh 접속환경 만들기
categories: it
---
  크롬북을 구매하고 나서, 생각보다 쾌적한 사용성과 기능에 만족을 하였지만, 태생적인 하드웨어의 한계로 인하여, 크롬북은 단말기의 역할 그리고 Jekyll 기반의 블로그 작성에만 사용하기로 결정했다. (결정적인 계기는 크롬북에 RDBMS를 설치하기에는 무리라고 생각되어서이다)
  그래서 출장등으로 밖에 나와 있을 때에는 집에 있는 맥북에 SSH로 접속하여, 필요한 작업을 하기로 결정을 했다. 평소대로라면, 맥에 ssh포트를 열어두고, 공유기에서 포트포워딩을 했을텐데 크롬북이라는 특수성과 집에서 사용하고 있는 공유기에서 하기의 문제가 발생하였다.
  - 집에 사용하는 공유기는 아파트에 기본으로 설치되어 있는 공유기인데 해당 공유기에서 포트포워딩을 설정하여도 맥으로 신호가 전달되지 않음.(이유를 찾지 못함)
  - 크롬북의 리눅스 시스템은 한글입력을 지원하지 않고, 안드로이드 터미널앱은 구동이 불안정함
  - 맥북에는 Jump Desktop 서버가 구동중이지만, 안드로이드 클라이언트 앱은 지원이 중단됨. 
  위와 같은 문제를 해결하기 위해, Terminal을 웹 환경에서 사용할 수 있게하는 [ttyd](https://github.com/tsl0922/ttyd)를 집 내부에 구동시켜 놓고, 집에서 구동중인 Nginx의 reverse proxy 기능을 활용하여 크롬북에서 웹을 통하여 Mac에 접속하는 환경을 구축하였다.

### 작업절차
- Nginx에서 접속할 수 있고 Mac에 접속 가능한 PC에 ttyd설치(podman 이용)
```text
podman run -d -p 7681:7681 --name ttyd \
    docker.io/tsl0922/ttyd
``` 

- ttyd 컨테이너에 환경설정  
```text
# 컨테이너의 쉘 프롬프트 오픈
podman exec -it ttyd sh
```
```text
# ssh client 설치
apt-get update
apt-get install ssh-client  
```
```text
# root의 .bashrc에 하기내용 추가. 마지막 exit는 container 제어권 획득을 막기 위함
export LANG='ko_KR.UTF-8'
export LC_ALL='ko_KR.UTF-8'
ssh {mac account}@{mac 내부 IP 주소}
exit
```

- nginx server configuration 설정
```text
server {
 ...

    location /{address}/ {
        proxy_pass   http://{ttyd container ip}:7681/$1;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Forwarded-Port $server_port;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
```

- nginx syntax 검사 및 설정 반영
```text
nginx -t
service nginx reload
```

### Test
```text
https://{dns or ip address}/{ttyd url}
```
![Test Image](/assets/images/20220621-test_result.gif)

