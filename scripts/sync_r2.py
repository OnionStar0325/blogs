#!/usr/bin/env python3
"""
Cloudflare R2 Asset Sync Script for Onion & Star Blog
Synchronizes local images from assets/images/ to Cloudflare R2 bucket.
"""

import os
import sys
import mimetypes
from pathlib import Path

try:
    import boto3
    from botocore.config import Config
    from botocore.exceptions import ClientError
except ImportError:
    print("❌ Error: boto3 is not installed. Please run: pip3 install boto3")
    sys.exit(1)

try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None


def main():
    root_dir = Path(__file__).resolve().parent.parent
    env_file = root_dir / ".env"
    
    if load_dotenv and env_file.exists():
        load_dotenv(dotenv_path=env_file)

    account_id = os.getenv("R2_ACCOUNT_ID", "770744414f537ddcf75129c9ee21fa86")
    bucket_name = os.getenv("R2_BUCKET_NAME", "blogs-assets")
    access_key = os.getenv("R2_ACCESS_KEY_ID")
    secret_key = os.getenv("R2_SECRET_ACCESS_KEY")

    images_dir = root_dir / "assets" / "images"

    if not images_dir.exists() or not any(images_dir.rglob("*")):
        print("ℹ️  [R2 Sync] 'assets/images/' 폴더에 업로드할 로컬 이미지가 없습니다. (동기화 완료)")
        sys.exit(0)

    # Collect all image files
    files_to_sync = [
        f for f in images_dir.rglob("*") 
        if f.is_file() and not f.name.startswith(".")
    ]

    if not files_to_sync:
        print("ℹ️  [R2 Sync] 업로드할 새 이미지 파일이 없습니다.")
        sys.exit(0)

    if not access_key or not secret_key:
        print("\n⚠️  [R2 Sync 경고] Cloudflare R2 API 키가 설정되지 않았습니다.")
        print("👉 '.env' 파일에 R2_ACCESS_KEY_ID 와 R2_SECRET_ACCESS_KEY 를 입력해 주세요.")
        print("👉 파일 위치: /home/ubuntu/projects/blogs-basslet/.env\n")
        sys.exit(1)

    endpoint_url = f"https://{account_id}.r2.cloudflarestorage.com"
    
    s3_client = boto3.client(
        "s3",
        endpoint_url=endpoint_url,
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        config=Config(signature_version="s3v4"),
        region_name="auto"
    )

    print(f"\n🚀 [R2 Sync] Cloudflare R2 ('{bucket_name}') 버킷으로 이미지 동기화를 시작합니다...")
    print(f"📁 대상 로컬 폴더: {images_dir}")

    uploaded_count = 0
    skipped_count = 0
    error_count = 0

    for file_path in files_to_sync:
        rel_path = file_path.relative_to(images_dir).as_posix()
        content_type, _ = mimetypes.guess_type(str(file_path))
        if not content_type:
            content_type = "application/octet-stream"

        try:
            # Check if file already exists in R2 with exact size
            local_size = file_path.stat().st_size
            try:
                head = s3_client.head_object(Bucket=bucket_name, Key=rel_path)
                remote_size = head.get("ContentLength", -1)
                if local_size == remote_size:
                    print(f"  ⚡ [스킵] {rel_path} (이미 R2에 동일한 크기로 존재함)")
                    skipped_count += 1
                    continue
            except ClientError as e:
                # 404 Not Found is expected for new files
                if e.response.get("Error", {}).get("Code") not in ("404", "NoSuchKey"):
                    pass

            # Upload file
            s3_client.upload_file(
                str(file_path),
                bucket_name,
                rel_path,
                ExtraArgs={"ContentType": content_type}
            )
            print(f"  ✅ [업로드 성공] {rel_path} ({content_type})")
            uploaded_count += 1

        except Exception as err:
            print(f"  ❌ [업로드 실패] {rel_path}: {err}")
            error_count += 1

    print("\n" + "=" * 50)
    print(f"🎉 [R2 동기화 결과] 신규 업로드: {uploaded_count}건 | 기존 유지: {skipped_count}건 | 실패: {error_count}건")
    print(f"🌐 CDN 접속 주소 예시: https://cdn.onionstar.co.kr/<경로>")
    print("=" * 50 + "\n")

    if error_count > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
