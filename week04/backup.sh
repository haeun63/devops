#!/bin/bash
# ============================================
# 백업 스크립트
# 사용법: ./backup.sh [백업할_폴더]
# ============================================

cd "$(dirname "$0")" || exit 1

SOURCE_DIR=${1:-test}	# 인자 없으면 test 디렉터리
BACKUP_DIR="backups"
TODAY=$(date +%Y%m%d_%H%M%S)
FILENAME="${TODAY}_$$.tar.gz" # 이름 충돌 가능성 줄이기
				   # $$: 현재 셀의 PID
# 1) 원본 확인
if [ ! -d "$SOURCE_DIR" ]; then
  echo "오류: '$SOURCE_DIR' 디렉터리가 없습니다."
  exit 1
fi
# 2) 백업 폴더 준비
mkdir -p "$BACKUP_DIR" || exit 1

# 3) 압축
echo "백업 시작: $SOURCE_DIR → $BACKUP_DIR/$FILENAME"
tar -czf "$BACKUP_DIR/$FILENAME" "$SOURCE_DIR"

# 4) 결과 확인
if [ $? -eq 0 ]; then
  SIZE=$(du -sh "$BACKUP_DIR/$FILENAME" | cut -f1)
  echo "백업 완료! (크기: $SIZE)"
else
  echo "백업 실패"
  exit 1
fi

# 5) 목록
echo "현재 보관 중인 백업:"
ls -1 "$BACKUP_DIR"	# 한 줄에 하나씩 출력
