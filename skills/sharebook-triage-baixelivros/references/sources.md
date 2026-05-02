# Fontes conhecidas

## ebook_foundation

- **Origem**: Curadoria manual de links do Archive.org e outros repositórios
- **Padrão de URL**: `https://archive.org/details/<identifier>` ou URLs de projetos (Google Code, GitHub Pages)
- **Metadata**: Pobre — geralmente só título e URL. Autor frequentemente vazio.
- **Riscos conhecidos**:
  - Links do Google Code (encerrado em 2016) — página é JS-rendered, mas downloads podem estar vivos no Google Cloud Storage
  - Archive.org pode ter removido itens por DMCA
  - Material pode ser scan não-autorizado (pirataria)
- **Comportamento esperado**: Aceitar metadata enxuta como normal

### Como baixar PDF do Google Code Archive

O Google Code Archive renderiza a página com JavaScript Angular. O curl/python não consegue extrair os links de download da página. Mas os arquivos estão acessíveis diretamente no Google Cloud Storage:

```
https://storage.googleapis.com/google-code-archive-downloads/v2/code.google.com/<project>/<arquivo>
```

**Fluxo para identificar o arquivo:**
1. O Raffa pode ver os nomes dos arquivos no navegador (a página funciona com JS)
2. Com o nome do arquivo, montar a URL do Cloud Storage
3. Testar com `curl -sI <url>` — se voltar HTTP 200, o download funciona
4. Fazer o download com `curl -sL <url> -o /tmp/<arquivo>`

**Exemplo (projeto vimbook, PDF):**
```bash
curl -sI "https://storage.googleapis.com/google-code-archive-downloads/v2/code.google.com/vimbook/vimbook-31-08-2009.pdf"
# HTTP/2 200
```

## baixelivros

- **Origem**: Site brasileiro de domínio público
- **Padrão de URL**: `https://www.baixelivros.com.br/<categoria>/<slug>`
- **Metadata**: Rica — título, autor, descrição, categoria
- **Riscos conhecidos**:
  - Usa proteção anti-download (retorna HTML disfarçado de PDF)
  - Links diretos do WordPress necessários
- **Comportamento esperado**: Já processado (111 done, 17 duplicate, 5 source_blocked)
