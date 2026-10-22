#!/bin/bash
if [ $# -eq 0 ]; then
  echo "사용법: $0 [이름]"
  exit 1
fi
echo "안녕하세요, $1님! (인자 개수: $#)"
