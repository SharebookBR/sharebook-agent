#!/usr/bin/env python3
"""
Upload, list, and manage ebook PDFs on the Sharebook production S3 bucket.

Usage:
  python3 sharebook_aws_s3.py list                    # List all ebooks
  python3 sharebook_aws_s3.py upload <local_path> <key>  # Upload/replace
  python3 sharebook_aws_s3.py delete <key>             # Delete an ebook
  python3 sharebook_aws_s3.py download <key> [output]  # Download from S3
  python3 sharebook_aws_s3.py slug <title>             # Show slug for a title

The slug is the filename (without .pdf) used in the bucket.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ENV_PATH = Path(__file__).resolve().parent.parent / ".env"


def load_env() -> dict[str, str]:
    values: dict[str, str] = {}
    for raw_line in ENV_PATH.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip()
    return values


def get_s3_client():
    try:
        import boto3
    except ImportError:
        raise SystemExit("boto3 não está instalado. Rode: pip install boto3")

    env = load_env()
    return boto3.client(
        "s3",
        aws_access_key_id=env.get("AWS_S3_ACCESS_KEY", ""),
        aws_secret_access_key=env.get("AWS_S3_SECRET_KEY", ""),
        region_name=env.get("AWS_S3_REGION", "sa-east-1"),
    )


def bucket_name() -> str:
    return load_env().get("AWS_S3_BUCKET", "sharebook-ebooks-prod")


def title_to_slug(title: str) -> str:
    """Convert a book title to the S3 filename slug."""
    slug = title.lower()
    slug = re.sub(r"[^\w\s-]", "", slug)
    slug = re.sub(r"[\s_]+", "-", slug)
    slug = slug.strip("-")
    return slug


def cmd_list(args: argparse.Namespace) -> None:
    s3 = get_s3_client()
    bucket = bucket_name()
    prefix = args.prefix or "ebooks/"
    total = 0

    paginator = s3.get_paginator("list_objects_v2")
    for page in paginator.paginate(Bucket=bucket, Prefix=prefix):
        for obj in page.get("Contents", []):
            print(f"{obj['Key']}  {obj['Size']/1024/1024:.1f} MB")
            total += 1

    print(f"\nTotal: {total} objects")


def cmd_upload(args: argparse.Namespace) -> None:
    s3 = get_s3_client()
    bucket = bucket_name()
    local_path = Path(args.local_path)
    if not local_path.exists():
        raise SystemExit(f"Arquivo não encontrado: {local_path}")

    key = args.key
    if not key.endswith(".pdf"):
        key += ".pdf"
    if not key.startswith("ebooks/"):
        key = f"ebooks/{key}"

    size_mb = local_path.stat().st_size / 1024 / 1024
    print(f"Uploading {local_path.name} ({size_mb:.1f} MB) → s3://{bucket}/{key}")

    with open(local_path, "rb") as f:
        s3.upload_fileobj(f, bucket, key, ExtraArgs={"ContentType": "application/pdf"})

    resp = s3.head_object(Bucket=bucket, Key=key)
    print(f"OK! {resp['ContentLength']/1024/1024:.1f} MB — ETag: {resp['ETag']}")


def cmd_delete(args: argparse.Namespace) -> None:
    s3 = get_s3_client()
    bucket = bucket_name()
    key = args.key
    if not key.startswith("ebooks/"):
        key = f"ebooks/{key}"

    s3.delete_object(Bucket=bucket, Key=key)
    print(f"Deleted s3://{bucket}/{key}")


def cmd_download(args: argparse.Namespace) -> None:
    s3 = get_s3_client()
    bucket = bucket_name()
    key = args.key
    if not key.startswith("ebooks/"):
        key = f"ebooks/{key}"

    output = args.output or Path(key).name
    print(f"Downloading s3://{bucket}/{key} → {output}")
    s3.download_file(bucket, key, output)
    size = Path(output).stat().st_size
    print(f"OK! {size/1024/1024:.1f} MB")


def cmd_slug(args: argparse.Namespace) -> None:
    slug = title_to_slug(args.title)
    print(f"{slug}.pdf")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Gerencia ebooks no S3 do Sharebook")
    sub = parser.add_subparsers(dest="command", required=True)

    list_p = sub.add_parser("list", help="Listar ebooks no bucket")
    list_p.add_argument("--prefix", default="ebooks/", help="Prefixo S3 (default: ebooks/)")

    up = sub.add_parser("upload", help="Upload/substituir PDF no bucket")
    up.add_argument("local_path", help="Caminho do arquivo local")
    up.add_argument("key", help="Chave S3 (slug sem extensão)")

    dp = sub.add_parser("delete", help="Deletar do bucket")
    dp.add_argument("key", help="Chave S3")

    dl = sub.add_parser("download", help="Download do bucket")
    dl.add_argument("key", help="Chave S3")
    dl.add_argument("output", nargs="?", help="Caminho de saída (default: nome do arquivo)")

    sl = sub.add_parser("slug", help="Gerar slug a partir do título")
    sl.add_argument("title", help="Título do livro")

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    commands = {
        "list": cmd_list,
        "upload": cmd_upload,
        "delete": cmd_delete,
        "download": cmd_download,
        "slug": cmd_slug,
    }

    cmd_fn = commands.get(args.command)
    if cmd_fn:
        cmd_fn(args)
    return 0


if __name__ == "__main__":
    sys.exit(main())
