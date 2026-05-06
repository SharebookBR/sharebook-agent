#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
import os
import ssl
import urllib.error
import urllib.request
from pathlib import Path


SSL_CONTEXT = ssl._create_unverified_context()


def load_env(repo_root: Path) -> dict[str, str]:
    env_path = repo_root / ".env"
    values: dict[str, str] = {}
    for line in env_path.read_text(encoding="utf-8").splitlines():
        if not line or line.lstrip().startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip()
    return values


def main() -> int:
    parser = argparse.ArgumentParser(description="Gera uma capa autoral via OpenAI Images API.")
    prompt_group = parser.add_mutually_exclusive_group(required=True)
    prompt_group.add_argument("--prompt", help="Prompt da imagem.")
    prompt_group.add_argument("--prompt-file", help="Arquivo UTF-8 com o prompt da imagem.")
    parser.add_argument("--output", required=True, help="Arquivo de saida PNG.")
    parser.add_argument("--size", default="1024x1536", help="Tamanho da imagem.")
    parser.add_argument("--quality", default="high", help="Qualidade da geracao.")
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[1]
    env_values = load_env(repo_root)
    api_key = env_values.get("OPENAI_API_KEY") or os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise SystemExit("OPENAI_API_KEY nao encontrado no .env.")

    prompt = args.prompt
    if args.prompt_file:
        prompt = Path(args.prompt_file).read_text(encoding="utf-8").strip()

    body = json.dumps(
        {
            "model": "gpt-image-1",
            "prompt": prompt,
            "size": args.size,
            "quality": args.quality,
            "background": "opaque",
        },
        ensure_ascii=False,
    ).encode("utf-8")

    request = urllib.request.Request(
        "https://api.openai.com/v1/images/generations",
        data=body,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=180, context=SSL_CONTEXT) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as error:
        details = error.read().decode("utf-8", errors="replace")
        raise SystemExit(f"OpenAI Images API retornou HTTP {error.code}: {details}") from error

    image_b64 = payload["data"][0]["b64_json"]
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_bytes(__import__("base64").b64decode(image_b64))

    print(str(output_path.resolve()))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
