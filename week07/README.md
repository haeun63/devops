
# 7주차 - Docker Compose

## 1. 실습 목표
Docker Compose를 이용하여 웹 애플리케이션과 Redis를 연결하고 여러 컨테이너를 관리한다.

## 2. 주요 실습
- compose.yaml 작성 및 실행
- Web과 Redis 컨테이너 연결
- Docker 네트워크 격리 확인
- Volume을 이용한 데이터 유지
- .env 파일을 통한 환경 변수 관리
- Healthcheck 설정
- nginx를 이용한 요청 분배
- Web 컨테이너 3개 Scale 실행
- Watch를 이용한 변경사항 자동 반영

## 3. 컨테이너 구성
- nginx: 외부 요청 수신 및 전달
- web: 방명록 애플리케이션 (3개)
- redis: 방명록 데이터 저장 (1개)

## 4. 데이터 유지 실습
- docker compose down: 컨테이너와 네트워크가 삭제되지만 볼륨은 유지된다.
- docker compose down -v: 볼륨까지 삭제되어 방명록 데이터가 사라진다.

## 5. Web 컨테이너 3개 유지 방법
docker compose up -d --scale web=3

위 명령어를 사용하여 Web 컨테이너 3개를 실행한다.

하나를 수동으로 중지해도 나머지 컨테이너가 요청을 처리할 수 있다. 다만 Docker Compose는 수동으로 중지한 컨테이너를 항상 자동 복구하지는 않으므로 관리자가 다시 실행해야 한다.

## 6. .env 파일을 GitHub에 올리지 않는 이유
.env 파일에는 Redis 비밀번호 같은 민감한 정보가 저장되어 있다.

GitHub에 공개하면 정보가 노출될 수 있으므로 .gitignore에 등록하고 .env.example 파일만 공유한다.

## 7. 실습 결과
Docker Compose를 이용해 웹 서버와 Redis를 분리하고, nginx를 통해 3개의 웹 컨테이너에 요청을 전달하도록 구성하였다.

## 8. 실습 화면
![Docker Compose 상태](./images/compose-ps.png)
![Web 1](./images/web1.png)
![Web 2](./images/web2.png)
![Web 3](./images/web3.png)
