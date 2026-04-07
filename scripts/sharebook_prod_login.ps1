param(
    [switch]$Force
)

$tokenVar = "SHAREBOOK_PROD_ACCESS_TOKEN"
$currentToken = [Environment]::GetEnvironmentVariable($tokenVar, "Process")

if (-not $Force -and $currentToken) {
    Write-Output "$tokenVar ja esta carregado na sessao atual."
    Write-Output "Se quiser renovar, rode: . .\\codex-scripts\\sharebook_prod_login.ps1 -Force"
    return
}

$script = @'
import sys
from pathlib import Path

repo_root = Path(r"C:/REPOS/SHAREBOOK")
scripts_dir = repo_root / "codex-scripts"
sys.path.insert(0, str(scripts_dir))

from sharebook_prod_auth import get_token, load_env, save_env_value

env_values = load_env(repo_root)
token = get_token(env_values, force_refresh=True)
save_env_value(repo_root, "SHAREBOOK_PROD_ACCESS_TOKEN", token)
print(token, end="")
'@

$token = $script | python -
if (-not $token) {
    throw "Falha ao obter token da API do Sharebook."
}

$env:SHAREBOOK_PROD_ACCESS_TOKEN = $token.Trim()
Write-Output "$tokenVar carregado na sessao atual e salvo no .env."
Write-Output "Use dot-source para renovar e reaproveitar o token: . .\\codex-scripts\\sharebook_prod_login.ps1 -Force"
