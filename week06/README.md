# 6주차 - Dockerfile 및 이미지 배포

## 1. 실습 목표
Dockerfile을 이용해 직접 이미지를 빌드하고 GitHub Container Registry에 배포한다.

## 2. Dockerfile 실습
- 방명록 이미지 빌드 및 실행
- Dockerfile 명령어 확인
- Docker 빌드 캐시 비교
- GitHub Container Registry 배포

## 3. Dockerfile 주요 명령어
- FROM: 기반 이미지 설정
- WORKDIR: 작업 디렉터리 지정
- COPY: 파일 복사
- RUN: 이미지 빌드 과정에서 명령 실행
- ENV: 환경 변수 설정
- EXPOSE: 사용 포트 선언
- CMD: 컨테이너 시작 시 실행할 명령

## 4. 실습 결과
- V1 이미지 빌드 및 배포
- V2 이미지 커스터마이징 및 배포
- 기존 이미지를 이용한 커스텀 이미지 생성
- 환경 변수 우선순위 확인

## 5. 이미지 주소
- V1: `ghcr.io/haeun63/guestbook:v1`
- V2: `ghcr.io/haeun63/guestbook:v2`

## 6. 정리
Dockerfile을 통해 실행 환경을 코드로 관리할 수 있으며, 빌드된 이미지는 다른 환경에서도 재사용할 수 있다.

설정 우선순위는 코드 기본값 < Dockerfile ENV < docker run -e 순서이다.
