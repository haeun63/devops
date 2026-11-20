# Week 11 - 쿠버네티스 설정과 상태 점검

## 1. ConfigMap & Secret
- ConfigMap과 Secret 생성
- Secret 비밀번호 base64 디코딩 확인
- base64는 암호화가 아닌 인코딩이므로 쉽게 복원 가능

![Secret 확인](images/secret.png)

## 2. Redis & ConfigMap
- Redis와 guestbook 배포 및 연결 성공
- ConfigMap으로 제목과 색상 변경
- 이미지 재빌드 없이 설정 변경 확인

![ConfigMap 변경](images/configmap.png)

## 3. Probe 실습
- **readiness:** Redis 중지 후 `READY 0/1` 확인
- **liveness:** 잘못된 경로 설정 후 `RESTARTS` 증가 확인
- 실험 후 정상 상태로 복구

![readiness 실패](images/readiness.png)

![liveness 실패](images/liveness.png)

## 4. 트러블슈팅
**확인 순서:** `get → describe → logs`

- **문제 1:** Minikube API 서버 실행 실패
  - 해결: 새로운 `week11` 클러스터 생성
- **문제 2:** Redis DNS 연결 실패
  - 해결: DNS 상태 확인 및 guestbook 재시작
