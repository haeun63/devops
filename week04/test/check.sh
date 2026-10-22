#!/bin/bash
FILE="$1"
if [ -z "$FILE" ]; then
  echo "파일명을 입력하세요"; exit 1
fi
if [ -f "$FILE" ]; then
  echo "파일"
elif [ -d "$FILE" ]; then
  echo "디렉터리"
else 
  echo "없음"; exit 1
fi
