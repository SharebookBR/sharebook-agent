"""Inspeciona a estrutura da página de listagem do BaixeLivros para entender
paginação e padrão de URLs de livros individuais."""
import ssl
import urllib.request
import re

URL = "https://www.baixelivros.com.br/biblioteca/quadrinhos"
UA  = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"

ctx = ssl._create_unverified_context()

def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=30, context=ctx) as r:
        return r.read().decode("utf-8", errors="replace")

html = fetch(URL)

# 1. Links de livros individuais
book_links = re.findall(r'href="(https://www\.baixelivros\.com\.br/[^"]+)"', html)
book_links = [l for l in book_links if "/biblioteca/" not in l and "/categoria/" not in l
              and not l.endswith("/biblioteca/quadrinhos")]
book_links = sorted(set(book_links))
print(f"=== Links de livros encontrados na página 1: {len(book_links)} ===")
for l in book_links[:10]:
    print(" ", l)
if len(book_links) > 10:
    print(f"  ... e mais {len(book_links)-10}")

# 2. Padrão de paginação
pagination = re.findall(r'href="([^"]*(?:page|pagina|p=)[^"]*)"', html, re.IGNORECASE)
pagination += re.findall(r'href="(https://www\.baixelivros\.com\.br/biblioteca/quadrinhos[^"]*)"', html)
print(f"\n=== Links de paginação candidatos ===")
for p in sorted(set(pagination))[:15]:
    print(" ", p)

# 3. Total de livros / páginas mencionado
totals = re.findall(r'(\d+)\s*(?:livros?|títulos?|resultados?)', html, re.IGNORECASE)
print(f"\n=== Menções de total ===", totals[:5])

# 4. Trecho do HTML ao redor de um link de livro (para debug de padrão)
sample = re.search(r'.{0,200}href="(https://www\.baixelivros\.com\.br/[^"]{10,})"[^>]*>.{0,100}', html)
if sample:
    print(f"\n=== Amostra de HTML ao redor de link ===\n{sample.group(0)[:400]}")
