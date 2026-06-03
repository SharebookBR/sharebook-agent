# GA4 Analytics Agent Bootstrap

Este arquivo documenta o processo de configuração do acesso programático ao Google Analytics 4 (GA4). Use este guia como referência para novos projetos ou se precisar reconstruir o acesso no Sharebook.

---

## 🚀 Missão
Habilitar o Agente (IA) para ler métricas de negócio do GA4 via API, ignorando a interface web complexa do Google.

## 🛠️ Pré-requisitos (No Google Cloud Console)

1.  **Habilitar APIs:**
    *   Vá em [APIs & Services > Library](https://console.cloud.google.com/apis/library).
    *   Pesquise e ative a **"Google Analytics Data API"**.

2.  **Conta de Serviço (IAM):**
    *   Crie uma Conta de Serviço (Ex: `analytics-agent`).
    *   Gere uma chave **JSON** e baixe-a.
    *   **Segurança:** Adicione o nome desse arquivo ao `.gitignore` imediatamente.

## 🧙‍♂️ O "Gatilho de Mestre" (Bypass de Bug na UI)

Em 2026, a interface web do GA4 apresenta um bug onde não reconhece e-mails de contas de serviço (`.gserviceaccount.com`) ao tentar adicionar permissões manualmente.

**Solução Programática (Via API Explorer):**
1.  Pegue o **Property ID** (9 dígitos) no GA4 (Administrador > Configurações da Propriedade).
2.  Acesse o [API Explorer: Create Access Binding](https://developers.google.com/analytics/devguides/config/admin/v1/rest/v1alpha/properties.accessBindings/create).
3.  Preencha `parent` como `properties/SEU_ID_AQUI`.
4.  No **Request Body**, use este JSON:
    ```json
    {
      "user": "seu-email-da-conta-de-servico@projeto.iam.gserviceaccount.com",
      "roles": ["predefinedRoles/viewer"]
    }
    ```
5.  Clique em **Execute** e autorize com sua conta Admin. O retorno `200 OK` confirma o acesso que a UI bloqueou.

## 💻 Configuração do Ambiente do Agente

1.  **Variáveis de Ambiente (.env):**
    ```env
    GA4_PROPERTY_ID=SEU_ID
    GA4_KEY_FILE_PATH=caminho/para/chave.json
    GA4_MEASUREMENT_SECRET=seu_secret_se_usar_protocolo_de_medicao
    ```

2.  **Dependências Python:**
    ```bash
    pip install google-analytics-data python-dotenv
    ```

## 📐 Implementação no Frontend (SSR Friendly)

Ao migrar do Universal Analytics (UA) para o GA4 em ambientes com **Server-Side Rendering (SSR)**:

1.  **Remover snippet legado** (`analytics.js`) do `index.html`.
2.  **Injetar `gtag.js`** com o novo ID `G-`.
3.  **Trava de Segurança SSR:** Garanta que o serviço de Analytics no Angular tenha a checagem `if (!this.platformService.isBrowser()) { return; }` para evitar que o Node.js tente executar funções de browser (`window`, `document`).
4.  **Rastreio de SPA:** Como o Angular não recarrega a página, você deve escutar `NavigationEnd` do Router e disparar o `config` do `gtag` manualmente para contar pageviews.

## 📊 Eventos de Negócio (Quick Wins)
Rastreie sempre as ações que geram valor real, não apenas visitas:
*   `ebook_download`
*   `social_share` (com parâmetro `method` para o canal)
*   `book_request_success` (final do funil de doação)

---
*Documentado em 20 de maio de 2026, após uma sessão de engenharia de elite.*
