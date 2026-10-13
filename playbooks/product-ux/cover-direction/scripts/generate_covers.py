#!/usr/bin/env python3
"""Generate multiple local cover variations for visual comparison."""

import argparse
import json
import subprocess
import sys
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Gera múltiplas variações locais de capa para comparação."
    )
    parser.add_argument("title", help="Título do livro")
    parser.add_argument("author", nargs="?", default="", help="Autor do livro")
    parser.add_argument(
        "--output-dir", "-d", type=Path, default=Path.cwd(), help="Diretório de saída"
    )
    parser.add_argument("--prefix", default="cover-var", help="Prefixo dos arquivos")
    parser.add_argument("--count", "-n", type=int, default=6, help="Quantidade de variações")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.count < 1:
        raise SystemExit("--count deve ser maior que zero")

    generator = Path(__file__).with_name("cover_generate.py")
    args.output_dir.mkdir(parents=True, exist_ok=True)
    results = []

    for variation in range(1, args.count + 1):
        output = args.output_dir / f"{args.prefix}-{variation}.jpg"
        command = [sys.executable, str(generator), args.title]
        if args.author:
            command.append(args.author)
        command.extend(["--output", str(output), "--json"])

        result = subprocess.run(command, capture_output=True, text=True, timeout=30)
        try:
            data = json.loads(result.stdout) if result.stdout else {}
        except json.JSONDecodeError:
            data = {}
        data.update(
            variation=variation,
            output=str(output),
            returncode=result.returncode,
            stderr=result.stderr.strip(),
        )
        results.append(data)
        print(
            f"VAR {variation}: palette={data.get('palette', '?')} "
            f"output={output} returncode={result.returncode}"
        )

    print("\n=== SUMMARY ===")
    for item in results:
        print(
            f"Var {item['variation']}: palette={item.get('palette', '?')}, "
            f"output={item['output']}"
        )
    return 1 if any(item["returncode"] != 0 for item in results) else 0


if __name__ == "__main__":
    raise SystemExit(main())
