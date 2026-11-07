#!/usr/bin/env bash
# Git pre-commit hook to sync images to Cloudflare R2 before committing

ROOT_DIR="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
SYNC_SCRIPT="$ROOT_DIR/scripts/sync_r2.py"

if [ -f "$SYNC_SCRIPT" ]; then
    python3 "$SYNC_SCRIPT"
    SYNC_STATUS=$?
    
    if [ $SYNC_STATUS -ne 0 ]; then
        echo "❌ [Pre-commit] R2 이미지 동기화에 실패하여 커밋이 중단되었습니다."
        echo "👉 .env 파일의 API 키를 확인하거나 수동으로 python3 scripts/sync_r2.py 를 실행해 주세요."
        exit 1
    fi
fi

exit 0
